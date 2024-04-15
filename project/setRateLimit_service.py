from datetime import datetime, timedelta

import prisma
import prisma.models
from pydantic import BaseModel


class SetRateLimitResponse(BaseModel):
    """
    Describes the outcome of configuring the rate limiting rules, including whether the operation was successful and details about the new rate limit settings.
    """

    success: bool
    message: str
    target: str
    max_requests: int
    duration_in_seconds: int


async def setRateLimit(
    target: str, max_requests: int, duration_in_seconds: int
) -> SetRateLimitResponse:
    """
    Configures rate limiting rules for a particular domain or user.

    Args:
    target (str): The target for rate limiting configuration, which can be a domain name or a user ID.
    max_requests (int): The maximum number of requests that are allowed within the specified duration.
    duration_in_seconds (int): The duration, in seconds, for which the specified maximum number of requests applies.

    Returns:
    SetRateLimitResponse: Describes the outcome of configuring the rate limiting rules, including whether the operation was successful and details about the new rate limit settings.
    """
    try:
        user_or_domain = await prisma.models.User.prisma().find_unique(
            where={"email": target}
        )
        if user_or_domain is None:
            user_or_domain_id = None
        else:
            user_or_domain_id = user_or_domain.id
        reset_at = datetime.now() + timedelta(seconds=duration_in_seconds)
        rate_limit = await prisma.models.RateLimit.prisma().create(
            data={
                "userId": user_or_domain_id,
                "requests": 0,
                "limit": max_requests,
                "resetAt": reset_at,
            }
        )
        success_msg = "Rate limit configuration successful."
        return SetRateLimitResponse(
            success=True,
            message=success_msg,
            target=target,
            max_requests=max_requests,
            duration_in_seconds=duration_in_seconds,
        )
    except Exception as e:
        error_msg = f"Error configuring rate limit: {str(e)}"
        return SetRateLimitResponse(
            success=False,
            message=error_msg,
            target=target,
            max_requests=max_requests,
            duration_in_seconds=duration_in_seconds,
        )
