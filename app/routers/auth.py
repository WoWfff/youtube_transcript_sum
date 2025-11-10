"""
Authentication router.

This module handles user authentication endpoints including registration,
login, logout, and user information retrieval. It uses JWT tokens stored
in HttpOnly cookies for secure authentication.
"""

import logging
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Response, status
from passlib.context import CryptContext

from app.dependencies import get_current_user
from app.models.db_models import UserBase
from app.models.pydantic_models import TokenResponse, UserLogin, UserRegister, UserResponse
from app.services.database.methods import Insert, Select, engine
from app.utils.jwt import create_access_token

logger = logging.getLogger(__name__)
router = APIRouter()

# Password hashing context using bcrypt
# bcrypt is a secure password hashing algorithm that automatically handles salting
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a plain password against a hashed password.

    Uses bcrypt to securely compare passwords without storing
    the plain text password.

    Args:
        plain_password: User-provided password in plain text
        hashed_password: Stored password hash from database

    Returns:
        True if passwords match, False otherwise
    """
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """
    Hash a password using bcrypt.

    This function creates a secure hash of the password that can be
    stored in the database. The hash includes a salt automatically.

    Args:
        password: Plain text password to hash

    Returns:
        Hashed password string (includes salt)
    """
    return pwd_context.hash(password)


@router.post("/auth/register", status_code=status.HTTP_201_CREATED)
async def register(user_data: UserRegister) -> UserResponse:
    """
    Register a new user.

    This endpoint creates a new user account with a username and password.
    The password is hashed using bcrypt before storage. Usernames must be unique.

    Args:
        user_data: User registration data (username and password)

    Returns:
        UserResponse: Created user information (id and username)

    Raises:
        HTTPException(400): If username already exists
        HTTPException(500): If registration fails
    """
    try:
        # Check if username already exists in database
        # Usernames must be unique to prevent conflicts
        existing_user = Select(model=UserBase, engine=engine).by_filter(username=user_data.username)
        if existing_user:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username already registered")

        # Hash the password before storing
        # Never store plain text passwords - always hash them
        password_hash = get_password_hash(user_data.password)

        # Create new user in database
        # cookies field is set to empty string for new users (legacy support)
        new_user = Insert(model=UserBase, engine=engine).one(
            username=user_data.username,
            password_hash=password_hash,
            cookies="",  # Empty for new users (legacy field)
        )

        logger.info(f"User registered: {user_data.username}")

        return UserResponse(id=new_user.id, username=new_user.username)

    except HTTPException:
        raise
    except Exception as err:
        logger.error(f"Registration error: {err}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error during registration"
        ) from err


@router.post("/auth/login")
async def login(user_data: UserLogin, response: Response) -> TokenResponse:
    """
    Login user and return JWT token.

    This endpoint authenticates a user and creates a JWT token that is
    stored in an HttpOnly cookie. The token is used for subsequent
    authenticated requests.

    Args:
        user_data: User login credentials (username and password)
        response: FastAPI Response object for setting cookies

    Returns:
        TokenResponse: JWT token and user information

    Raises:
        HTTPException(401): If username or password is incorrect
        HTTPException(500): If login fails
    """
    try:
        # Find user by username in database
        user = Select(model=UserBase, engine=engine).by_filter(username=user_data.username)
        if not user:
            # Don't reveal if username exists - same error for both cases
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect username or password")

        # Verify password against stored hash
        # Check if password_hash exists (for legacy users) and verify password
        if not user.password_hash or not verify_password(user_data.password, user.password_hash):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect username or password")

        # Create JWT access token
        # 'sub' (subject) claim stores user ID, following JWT standard
        access_token = create_access_token(data={"sub": str(user.id), "username": user.username})

        # Set HttpOnly cookie with JWT token
        # HttpOnly prevents JavaScript access, protecting against XSS attacks
        # SameSite=Lax provides CSRF protection
        # secure=False allows HTTP (set to True in production with HTTPS)
        response.set_cookie(
            key="access_token",
            value=access_token,
            httponly=True,  # Cookie not accessible via JavaScript
            samesite="lax",  # CSRF protection
            secure=False,  # Set to True in production with HTTPS
            max_age=60 * 60 * 24,  # 24 hours expiration
        )

        logger.info(f"User logged in: {user_data.username}")

        return TokenResponse(
            access_token=access_token,
            token_type="bearer",  # noqa: S106
            user_id=user.id,
            username=user.username,
        )

    except HTTPException:
        raise
    except Exception as err:
        logger.error(f"Login error: {err}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error during login") from err


@router.post("/auth/logout")
async def logout(response: Response) -> dict[str, str]:
    """Logout user by clearing the access token cookie."""
    response.delete_cookie(key="access_token", samesite="lax")
    return {"message": "Logged out successfully"}


@router.get("/auth/me", response_model=UserResponse)
async def get_current_user_info(current_user: Annotated[UserBase, Depends(get_current_user)]) -> UserResponse:
    """Get current user information."""
    return UserResponse(id=current_user.id, username=current_user.username)
