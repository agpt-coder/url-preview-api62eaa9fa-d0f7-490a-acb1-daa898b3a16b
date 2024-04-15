from typing import Optional

import requests
from pydantic import BaseModel


class FetchContentResponse(BaseModel):
    """
    Model representing the response of fetching webpage content.
    """

    success: bool
    content: Optional[str] = None
    error_message: Optional[str] = None
    status_code: int


def fetchContent(url: str) -> FetchContentResponse:
    """
    Fetches webpage content based on the provided URL and prepares it for further processing.

    Args:
        url (str): The URL of the webpage to be fetched.

    Returns:
        FetchContentResponse: Model representing the response of fetching webpage content.
    """
    try:
        response = requests.get(url)
        response.raise_for_status()
        fetched_content = response.text
        return FetchContentResponse(
            success=True, content=fetched_content, status_code=response.status_code
        )
    except requests.RequestException as e:
        status_code = (
            e.response.status_code
            if hasattr(e, "response") and e.response is not None
            else 0
        )
        return FetchContentResponse(
            success=False, error_message=str(e), status_code=status_code
        )
