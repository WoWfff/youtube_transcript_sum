"""Authentication router."""

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

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against a hash."""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Hash a password."""
    return pwd_context.hash(password)


@router.post("/auth/register", status_code=status.HTTP_201_CREATED)
async def register(user_data: UserRegister) -> UserResponse:
    """Register a new user."""
    try:
        # Check if username already exists
        existing_user = Select(model=UserBase, engine=engine).by_filter(username=user_data.username)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already registered"
            )

        # Hash password
        password_hash = get_password_hash(user_data.password)

        # Create new user
        new_user = Insert(model=UserBase, engine=engine).one(
            username=user_data.username,
            password_hash=password_hash,
            cookies=""  # Empty for new users
        )

        logger.info(f"User registered: {user_data.username}")

        return UserResponse(id=new_user.id, username=new_user.username)

    except HTTPException:
        raise
    except Exception as err:
        logger.error(f"Registration error: {err}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error during registration"
        ) from err


@router.post("/auth/login")
async def login(user_data: UserLogin, response: Response) -> TokenResponse:
    """Login user and return JWT token."""
    try:
        # Find user by username
        user = Select(model=UserBase, engine=engine).by_filter(username=user_data.username)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password"
            )

        # Verify password
        if not user.password_hash or not verify_password(user_data.password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password"
            )

        # Create access token
        access_token = create_access_token(data={"sub": str(user.id), "username": user.username})

        # Set HttpOnly cookie
        response.set_cookie(
            key="access_token",
            value=access_token,
            httponly=True,
            samesite="lax",
            secure=False,  # Set to True in production with HTTPS
            max_age=60 * 60 * 24  # 24 hours
        )

        logger.info(f"User logged in: {user_data.username}")

        return TokenResponse(
            access_token=access_token,
            token_type="bearer",
            user_id=user.id,
            username=user.username
        )

    except HTTPException:
        raise
    except Exception as err:
        logger.error(f"Login error: {err}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error during login"
        ) from err


@router.post("/auth/logout")
async def logout(response: Response) -> dict[str, str]:
    """Logout user by clearing the access token cookie."""
    response.delete_cookie(key="access_token", samesite="lax")
    return {"message": "Logged out successfully"}


@router.get("/auth/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: Annotated[UserBase, Depends(get_current_user)]
) -> UserResponse:
    """Get current user information."""
    return UserResponse(id=current_user.id, username=current_user.username)
