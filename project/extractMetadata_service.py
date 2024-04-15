from typing import Dict, Optional

import requests
from bs4 import BeautifulSoup
from pydantic import BaseModel


class ExtractMetadataResponse(BaseModel):
    """
    The response model provides the extracted metadata in a structured format, including the page title, description, and any found image URLs. It represents the outcome of the metadata extraction process.
    """

    title: str
    description: Optional[str] = None
    image_url: Optional[str] = None
    additional_metadata: Dict[str, str]


def extractMetadata(
    url: str, custom_rules: Dict[str, str], content_type: Optional[str]
) -> ExtractMetadataResponse:
    """
    Extracts metadata from the provided webpage content.

    Args:
    url (str): The URL of the webpage to extract metadata from.
    custom_rules (Dict[str, str]): Optional JSON object defining custom rules for metadata extraction to accommodate unique webpage structures.
    content_type (Optional[str]): An optional field specifying the type of content to focus the extraction on e.g., 'text/html', 'application/json'. This could enhance extraction accuracy for specific page types.

    Returns:
    ExtractMetadataResponse: The response model provides the extracted metadata in a structured format, including the page title, description, and any found image URLs. It represents the outcome of the metadata extraction process.
    """
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers)
    if content_type and response.headers["Content-Type"] != content_type:
        raise ValueError(
            f"Content type {response.headers['Content-Type']} does not match the expected {content_type}"
        )
    soup = BeautifulSoup(response.content, "html.parser")
    title = soup.title.string if soup.title else "No title found"
    description = None
    image_url = None
    additional_metadata = {}
    if "description" in custom_rules:
        description_selector = custom_rules["description"]
        description_tag = soup.select_one(description_selector)
        if description_tag:
            description = description_tag.text
    else:
        meta_desc = soup.find("meta", attrs={"name": "description"})
        if meta_desc:
            description = meta_desc["content"]
    if "image_url" in custom_rules:
        image_url_selector = custom_rules["image_url"]
        image_url_tag = soup.select_one(image_url_selector)
        if image_url_tag:
            image_url = image_url_tag["src"] if "src" in image_url_tag.attrs else None
    else:
        og_image = soup.find("meta", property="og:image")
        if og_image:
            image_url = og_image["content"]
    additional_metadata["url_length"] = str(len(url))
    return ExtractMetadataResponse(
        title=title,
        description=description,
        image_url=image_url,
        additional_metadata=additional_metadata,
    )
