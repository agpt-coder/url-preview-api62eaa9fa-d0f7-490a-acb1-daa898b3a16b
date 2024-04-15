from typing import Dict, List, Optional

import prisma
import prisma.models
import requests
from bs4 import BeautifulSoup
from pydantic import BaseModel


class DynamicContentFetchResponse(BaseModel):
    """
    The structure representing the result of processing a web page to extract metadata including dynamic content.
    """

    success: bool
    message: str
    extracted_metadata: Dict[str, str]


async def handleDynamicContent(
    url: str, content_selectors: Optional[List[str]] = None
) -> DynamicContentFetchResponse:
    """
    Processes web pages with dynamic content to allow for metadata extraction.

    Args:
    url (str): The URL of the web page to process.
    content_selectors (Optional[List[str]]): CSS selectors to specify which parts of the dynamically loaded content are of interest. Optional.

    Returns:
    DynamicContentFetchResponse: The structure representing the result of processing a web page to extract metadata including dynamic content.
    """
    try:
        response = requests.get(url)
        if response.status_code != 200:
            return DynamicContentFetchResponse(
                success=False,
                message=f"Failed to fetch the page: {response.status_code}",
                extracted_metadata={},
            )
        soup = BeautifulSoup(response.content, "html.parser")
        metadata = {"title": soup.title.string if soup.title else "No title found"}
        if content_selectors:
            for selector in content_selectors:
                extracted_content = soup.select_one(selector)
                if extracted_content:
                    metadata[selector] = extracted_content.text.strip()
        await prisma.models.PagePreview.prisma().create(
            data={
                "url": url,
                "title": metadata.get("title"),
                "description": metadata.get("description", "No description provided"),
                "imageUrl": metadata.get("img", "No image URL provided"),
                "userId": "associated_user_id",
            }
        )
        return DynamicContentFetchResponse(
            success=True,
            message="Metadata extracted successfully",
            extracted_metadata=metadata,
        )
    except Exception as e:
        return DynamicContentFetchResponse(
            success=False, message=f"An error occurred: {str(e)}", extracted_metadata={}
        )
