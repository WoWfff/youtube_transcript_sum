"""
JWT token utilities for authentication.

This module provides functions for creating and decoding JWT (JSON Web Token)
tokens used for user authentication. JWT tokens are stateless and contain
user information that can be verified without database lookups.
"""

from datetime import datetime, timedelta
from typing import Any

from jose import jwt
from jose.exceptions import JWTError

from app.configs.app_config import JWT_ACCESS_TOKEN_EXPIRE_MINUTES, JWT_ALGORITHM, JWT_SECRET_KEY


def create_access_token(data: dict[str, Any], expires_delta: timedelta | None = None) -> str:
    """
    Create a JWT access token.

    This function creates a signed JWT token containing user data.
    The token includes expiration time (exp) and issued at time (iat) claims.

    Args:
        data: Dictionary containing user data (typically user ID in 'sub' claim)
        expires_delta: Optional custom expiration time. If not provided,
                     uses JWT_ACCESS_TOKEN_EXPIRE_MINUTES from config.

    Returns:
        Encoded JWT token as string

    Example:
        token = create_access_token(data={"sub": "123", "username": "john"})
    """
    to_encode = data.copy()

    # Set expiration time
    # If custom expiration is provided, use it; otherwise use default from config
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=JWT_ACCESS_TOKEN_EXPIRE_MINUTES)

    # Add standard JWT claims
    # 'exp' (expiration) and 'iat' (issued at) are standard JWT claims
    to_encode.update({"exp": expire, "iat": datetime.utcnow()})

    # Encode and sign the token
    # The secret key is used to sign the token, ensuring it hasn't been tampered with
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
    return encoded_jwt


def decode_access_token(token: str) -> dict[str, Any] | None:
    """
    Decode and validate a JWT access token.

    This function decodes a JWT token and verifies its signature.
    It automatically checks expiration and signature validity.

    Args:
        token: Encoded JWT token string

    Returns:
        Decoded token payload as dictionary if valid, None otherwise

    Note:
        Returns None if:
        - Token signature is invalid
        - Token is expired
        - Token format is incorrect
        - Any other JWT validation error occurs
    """
    try:
        # Decode and verify the token
        # This automatically checks expiration and signature
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        return payload
    except JWTError:
        # Return None for any JWT error (expired, invalid signature, etc.)
        # This allows the caller to handle the error appropriately
        return None
