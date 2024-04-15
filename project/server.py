import logging
from contextlib import asynccontextmanager
from datetime import datetime
from typing import Dict, List, Optional

import project.authenticateUser_service
import project.authorizeAccess_service
import project.extractMetadata_service
import project.fetchContent_service
import project.handleDynamicContent_service
import project.setRateLimit_service
import project.updateCompliancePolicies_service
from fastapi import FastAPI
from fastapi.encoders import jsonable_encoder
from fastapi.responses import Response
from prisma import Prisma

logger = logging.getLogger(__name__)

db_client = Prisma(auto_register=True)


@asynccontextmanager
async def lifespan(app: FastAPI):
    await db_client.connect()
    yield
    await db_client.disconnect()


app = FastAPI(
    title="URL Preview API",
    lifespan=lifespan,
    description="To accomplish the task of creating an endpoint that accepts a URL, retrieves webpage content, extracts relevant metadata, generates a preview snippet including the page title, description, and thumbnail image, and returns the structured preview data for use in link sharing and embedding, the following plan is proposed based on the information gathered and tools available:\n\n1. **Tech Stack**:\n- Programming Language: Python\n- API Framework: FastAPI\n- Database: PostgreSQL\n- ORM: Prisma\n\n2. **Requirements Summary**:\n- High accuracy and efficiency in extracting text, images, and other media while preserving the original structure.\n- Supports various content types across different web technologies.\n- Extracts important metadata accurately such as keywords, descriptions, authorship, publication dates, and provides options for content localization.\n- Handles dynamic content loaded with JavaScript.\n- Scalable, with robust error handling and ease of integration into existing systems.\n- Custom extraction rules to accommodate special needs.\n\n3. **Solution Approach**:\n- Utilize the 'Requests' library for retrieving webpage content.\n- Implement 'Beautiful Soup' for parsing HTML content and extracting text, images, and other media.\n- Use 'Scrapy' for more comprehensive web scraping needs, handling dynamic JavaScript-loaded content, and efficient crawling of required metadata.\n- Leverage HTML parsing libraries, with particular attention to meta tags like Open Graph (OG) tags, Twitter Cards, for extracting metadata that aids in generating preview snippets.\n- Incorporate server-side rendering techniques for single-page applications to ensure metadata is accessible.\n- Validate extracted metadata for accuracy and completeness.\n- Adhere to respectful web scraping guidelines, including obeying robots.txt directives and rate limiting requests.\n\n4. **Challenges & Considerations**:\n- Ensuring the accuracy of metadata extraction is prioritized over the speed of retrieval and processing.\n- Regularly updating extraction logic to adapt to changes in web technologies.\n- Maintaining privacy and security in handling extracted data.\n\n5. **Example Target URLs**: Consumer forums, product review sites (e.g., Capterra, G2 Crowd), and industry news portals (e.g., TechCrunch, Wired).\n\n6. **Best Practices**:\n- Utilizing meta tags for consistent and accurate information.\n- Employing HTML parsing libraries for metadata extraction, handling exceptions gracefully.\n- Validating extracted metadata, providing fallbacks where necessary, ensuring user privacy, and updating extraction logic regularly.\n\nThis comprehensive plan outlines the technology, strategies, and considerations necessary to develop a reliable and efficient tool for webpage content retrieval and metadata extraction. It's designed to meet the specific needs and priorities of the user, focusing on accuracy, scalability, and ease of integration.",
)


@app.post(
    "/access/authorize",
    response_model=project.authorizeAccess_service.AuthorizeAccessResponse,
)
async def api_post_authorizeAccess(
    user_id: str, api_key: str, resource: str
) -> project.authorizeAccess_service.AuthorizeAccessResponse | Response:
    """
    Grants or denies access to specific features or data based on user roles.
    """
    try:
        res = await project.authorizeAccess_service.authorizeAccess(
            user_id, api_key, resource
        )
        return res
    except Exception as e:
        logger.exception("Error processing request")
        res = dict()
        res["error"] = str(e)
        return Response(
            content=jsonable_encoder(res),
            status_code=500,
            media_type="application/json",
        )


@app.post(
    "/content/retrieve",
    response_model=project.fetchContent_service.FetchContentResponse,
)
async def api_post_fetchContent(
    url: str,
) -> project.fetchContent_service.FetchContentResponse | Response:
    """
    Fetches webpage content based on the provided URL and prepares it for further processing.
    """
    try:
        res = project.fetchContent_service.fetchContent(url)
        return res
    except Exception as e:
        logger.exception("Error processing request")
        res = dict()
        res["error"] = str(e)
        return Response(
            content=jsonable_encoder(res),
            status_code=500,
            media_type="application/json",
        )


@app.post(
    "/user/authenticate",
    response_model=project.authenticateUser_service.UserAuthenticationResponse,
)
async def api_post_authenticateUser(
    email: str, password: str
) -> project.authenticateUser_service.UserAuthenticationResponse | Response:
    """
    Authenticates a user's credentials to provide access to MetaSnip's services.
    """
    try:
        res = await project.authenticateUser_service.authenticateUser(email, password)
        return res
    except Exception as e:
        logger.exception("Error processing request")
        res = dict()
        res["error"] = str(e)
        return Response(
            content=jsonable_encoder(res),
            status_code=500,
            media_type="application/json",
        )


@app.post(
    "/metadata/extract",
    response_model=project.extractMetadata_service.ExtractMetadataResponse,
)
async def api_post_extractMetadata(
    url: str, custom_rules: Dict[str, str], content_type: Optional[str]
) -> project.extractMetadata_service.ExtractMetadataResponse | Response:
    """
    Extracts metadata from the provided webpage content.
    """
    try:
        res = project.extractMetadata_service.extractMetadata(
            url, custom_rules, content_type
        )
        return res
    except Exception as e:
        logger.exception("Error processing request")
        res = dict()
        res["error"] = str(e)
        return Response(
            content=jsonable_encoder(res),
            status_code=500,
            media_type="application/json",
        )


@app.post(
    "/rate-limit/set", response_model=project.setRateLimit_service.SetRateLimitResponse
)
async def api_post_setRateLimit(
    target: str, max_requests: int, duration_in_seconds: int
) -> project.setRateLimit_service.SetRateLimitResponse | Response:
    """
    Configures rate limiting rules for a particular domain or user.
    """
    try:
        res = await project.setRateLimit_service.setRateLimit(
            target, max_requests, duration_in_seconds
        )
        return res
    except Exception as e:
        logger.exception("Error processing request")
        res = dict()
        res["error"] = str(e)
        return Response(
            content=jsonable_encoder(res),
            status_code=500,
            media_type="application/json",
        )


@app.post(
    "/dynamic/handle",
    response_model=project.handleDynamicContent_service.DynamicContentFetchResponse,
)
async def api_post_handleDynamicContent(
    url: str, content_selectors: Optional[List[str]]
) -> project.handleDynamicContent_service.DynamicContentFetchResponse | Response:
    """
    Processes web pages with dynamic content to allow for metadata extraction.
    """
    try:
        res = await project.handleDynamicContent_service.handleDynamicContent(
            url, content_selectors
        )
        return res
    except Exception as e:
        logger.exception("Error processing request")
        res = dict()
        res["error"] = str(e)
        return Response(
            content=jsonable_encoder(res),
            status_code=500,
            media_type="application/json",
        )


@app.patch(
    "/compliance/update",
    response_model=project.updateCompliancePolicies_service.UpdateCompliancePoliciesResponse,
)
async def api_patch_updateCompliancePolicies(
    policy_id: str, new_requirements: str, justification: str, effective_date: datetime
) -> project.updateCompliancePolicies_service.UpdateCompliancePoliciesResponse | Response:
    """
    Updates compliance policies based on new legal requirements.
    """
    try:
        res = await project.updateCompliancePolicies_service.updateCompliancePolicies(
            policy_id, new_requirements, justification, effective_date
        )
        return res
    except Exception as e:
        logger.exception("Error processing request")
        res = dict()
        res["error"] = str(e)
        return Response(
            content=jsonable_encoder(res),
            status_code=500,
            media_type="application/json",
        )
