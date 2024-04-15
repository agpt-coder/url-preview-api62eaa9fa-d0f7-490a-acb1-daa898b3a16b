from typing import Optional

import prisma
import prisma.enums
import prisma.models
from pydantic import BaseModel


class AuthorizeAccessResponse(BaseModel):
    """
    Response model indicating the authorization result for accessing a specific feature or dataset.
    """

    access_granted: bool
    message: str
    error_code: Optional[str] = None


async def authorizeAccess(
    user_id: str, api_key: str, resource: str
) -> AuthorizeAccessResponse:
    """
    Grants or denies access to specific features or data based on user roles.

    Args:
        user_id (str): The unique identifier of the user requesting access.
        api_key (str): The API key used for validating the request, ensuring it's coming from an authenticated user or service.
        resource (str): The specific feature or dataset the user is attempting to access, defined by a unique name or identifier.

    Returns:
        AuthorizeAccessResponse: Response model indicating the authorization result for accessing a specific feature or dataset.
    """
    user = await prisma.models.User.prisma().find_unique(where={"id": user_id})
    if not user:
        return AuthorizeAccessResponse(
            access_granted=False, message="User not found.", error_code="USER_NOT_FOUND"
        )
    api_key_record = await prisma.models.ApiKey.prisma().find_unique(
        where={"key": api_key}
    )
    if not api_key_record or api_key_record.userId != user_id:
        return AuthorizeAccessResponse(
            access_granted=False,
            message="Invalid API key.",
            error_code="INVALID_API_KEY",
        )
    if resource == "premium_content" and user.role not in [
        prisma.enums.UserRole.ADMIN,
        prisma.enums.UserRole.DEVELOPER,
    ]:
        subscription = await prisma.models.Subscription.prisma().find_many(
            where={
                "userId": user_id,
                "type": {
                    "in": [
                        prisma.enums.SubscriptionType.MONTHLY,
                        prisma.enums.SubscriptionType.YEARLY,
                    ]
                },
                "endDate": {"gt": "CURRENT_DATE_PLACEHOLDER"},
            }
        )
        if not subscription:
            return AuthorizeAccessResponse(
                access_granted=False,
                message="Access denied. Valid subscription required for premium content.",
                error_code="SUBSCRIPTION_REQUIRED",
            )
    return AuthorizeAccessResponse(access_granted=True, message="Access granted.")
