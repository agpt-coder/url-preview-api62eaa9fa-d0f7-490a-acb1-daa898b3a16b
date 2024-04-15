from typing import Optional

import prisma
import prisma.models
from passlib.context import CryptContext
from pydantic import BaseModel


class UserAuthenticationResponse(BaseModel):
    """
    This model defines the structure of the response following an authentication attempt. It will convey whether the authentication was successful and provide an authentication token for successful logins.
    """

    success: bool
    token: Optional[str] = None
    message: str


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


async def authenticateUser(email: str, password: str) -> UserAuthenticationResponse:
    """
    Authenticates a user's credentials to provide access to MetaSnip's services.

    Args:
      email (str): The email of the user trying to authenticate.
      password (str): The password of the user for authentication.

    Returns:
      UserAuthenticationResponse: This model defines the structure of the response following an authentication attempt. It will convey whether the authentication was successful and provide an authentication token for successful logins.
    """
    user = await prisma.models.User.prisma().find_unique(where={"email": email})
    if not user:
        return UserAuthenticationResponse(
            success=False, message="Authentication failed. User not found."
        )
    if not pwd_context.verify(password, user.hashedPassword):
        return UserAuthenticationResponse(
            success=False, message="Authentication failed. Incorrect password."
        )
    fake_token = "generated_fake_token_for_demo_purposes"
    return UserAuthenticationResponse(
        success=True, token=fake_token, message="User authenticated successfully."
    )
