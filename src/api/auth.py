"""
Authentication Manager for Voxel API
Handles JWT token generation, validation, and password hashing.
"""

import os
import secrets
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import logging

import jwt
from passlib.context import CryptContext

logger = logging.getLogger(__name__)


class AuthManager:
    """
    Manages authentication operations including:
    - Password hashing and verification
    - JWT token generation and validation
    - Token refresh
    """

    def __init__(
        self,
        secret_key: Optional[str] = None,
        algorithm: str = "HS256",
        access_token_expire_minutes: int = 60,
        refresh_token_expire_days: int = 30,
    ):
        """
        Initialize authentication manager.

        Args:
            secret_key: Secret key for JWT signing (auto-generated if not provided)
            algorithm: JWT algorithm (default: HS256)
            access_token_expire_minutes: Access token expiration time
            refresh_token_expire_days: Refresh token expiration time
        """
        self.secret_key = secret_key or os.getenv("JWT_SECRET_KEY") or secrets.token_urlsafe(32)
        self.algorithm = algorithm
        self.access_token_expire_minutes = access_token_expire_minutes
        self.refresh_token_expire_days = refresh_token_expire_days

        # Password hashing context (bcrypt)
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

        logger.info("AuthManager initialized")

    # ==================== PASSWORD OPERATIONS ====================

    def hash_password(self, password: str) -> str:
        """
        Hash a password using bcrypt.

        Args:
            password: Plain text password

        Returns:
            Hashed password string
        """
        return self.pwd_context.hash(password)

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """
        Verify a password against its hash.

        Args:
            plain_password: Plain text password to verify
            hashed_password: Stored password hash

        Returns:
            True if password matches, False otherwise
        """
        try:
            return self.pwd_context.verify(plain_password, hashed_password)
        except Exception as e:
            logger.error(f"Password verification error: {e}")
            return False

    # ==================== TOKEN OPERATIONS ====================

    def create_access_token(
        self,
        user_id: str,
        email: str,
        username: str,
        subscription_tier: str = "free",
        expires_delta: Optional[timedelta] = None,
    ) -> str:
        """
        Create a JWT access token.

        Args:
            user_id: User identifier
            email: User email
            username: Username
            subscription_tier: User subscription level
            expires_delta: Custom expiration time (optional)

        Returns:
            Encoded JWT token string
        """
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=self.access_token_expire_minutes)

        to_encode = {
            "sub": user_id,  # Subject (user identifier)
            "email": email,
            "username": username,
            "subscription_tier": subscription_tier,
            "exp": expire,  # Expiration time
            "iat": datetime.utcnow(),  # Issued at
            "type": "access",
        }

        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        logger.debug(f"Created access token for user {user_id}")
        return encoded_jwt

    def create_refresh_token(self, user_id: str) -> str:
        """
        Create a JWT refresh token.

        Args:
            user_id: User identifier

        Returns:
            Encoded JWT refresh token string
        """
        expire = datetime.utcnow() + timedelta(days=self.refresh_token_expire_days)

        to_encode = {
            "sub": user_id,
            "exp": expire,
            "iat": datetime.utcnow(),
            "type": "refresh",
        }

        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        logger.debug(f"Created refresh token for user {user_id}")
        return encoded_jwt

    def verify_token(self, token: str) -> Optional[Dict[str, Any]]:
        """
        Verify and decode a JWT token.

        Args:
            token: JWT token string

        Returns:
            Decoded token payload if valid, None otherwise
        """
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])

            # Check if token is expired
            exp = payload.get("exp")
            if exp and datetime.fromtimestamp(exp) < datetime.utcnow():
                logger.warning("Token has expired")
                return None

            return payload
        except jwt.ExpiredSignatureError:
            logger.warning("Token has expired")
            return None
        except jwt.InvalidTokenError as e:
            logger.warning(f"Invalid token: {e}")
            return None
        except Exception as e:
            logger.error(f"Token verification error: {e}")
            return None

    def verify_access_token(self, token: str) -> Optional[Dict[str, Any]]:
        """
        Verify an access token.

        Args:
            token: JWT access token

        Returns:
            Decoded payload if valid access token, None otherwise
        """
        payload = self.verify_token(token)
        if payload and payload.get("type") == "access":
            return payload
        return None

    def verify_refresh_token(self, token: str) -> Optional[Dict[str, Any]]:
        """
        Verify a refresh token.

        Args:
            token: JWT refresh token

        Returns:
            Decoded payload if valid refresh token, None otherwise
        """
        payload = self.verify_token(token)
        if payload and payload.get("type") == "refresh":
            return payload
        return None

    def refresh_access_token(self, refresh_token: str, user_data: Dict[str, Any]) -> Optional[str]:
        """
        Generate a new access token from a refresh token.

        Args:
            refresh_token: Valid refresh token
            user_data: User information for creating new access token

        Returns:
            New access token if refresh token is valid, None otherwise
        """
        payload = self.verify_refresh_token(refresh_token)
        if not payload:
            return None

        # Verify user_id matches
        if payload.get("sub") != user_data.get("user_id"):
            logger.warning("User ID mismatch in refresh token")
            return None

        # Create new access token
        return self.create_access_token(
            user_id=user_data["user_id"],
            email=user_data["email"],
            username=user_data["username"],
            subscription_tier=user_data.get("subscription_tier", "free"),
        )

    def get_current_user_id(self, token: str) -> Optional[str]:
        """
        Extract user ID from an access token.

        Args:
            token: JWT access token

        Returns:
            User ID if token is valid, None otherwise
        """
        payload = self.verify_access_token(token)
        if payload:
            return payload.get("sub")
        return None

    def get_token_expiration(self, token: str) -> Optional[datetime]:
        """
        Get the expiration time of a token.

        Args:
            token: JWT token

        Returns:
            Expiration datetime if valid, None otherwise
        """
        payload = self.verify_token(token)
        if payload and "exp" in payload:
            return datetime.fromtimestamp(payload["exp"])
        return None

    def is_token_expired(self, token: str) -> bool:
        """
        Check if a token is expired.

        Args:
            token: JWT token

        Returns:
            True if expired or invalid, False if valid
        """
        expiration = self.get_token_expiration(token)
        if not expiration:
            return True
        return expiration < datetime.utcnow()

    # ==================== UTILITY FUNCTIONS ====================

    def generate_secure_token(self, nbytes: int = 32) -> str:
        """
        Generate a secure random token (for password reset, email verification, etc.).

        Args:
            nbytes: Number of random bytes

        Returns:
            URL-safe random token string
        """
        return secrets.token_urlsafe(nbytes)

    def create_token_response(
        self,
        user_id: str,
        email: str,
        username: str,
        subscription_tier: str = "free",
    ) -> Dict[str, Any]:
        """
        Create a complete token response with both access and refresh tokens.

        Args:
            user_id: User identifier
            email: User email
            username: Username
            subscription_tier: User subscription level

        Returns:
            Dictionary with access_token, refresh_token, token_type, and expires_in
        """
        access_token = self.create_access_token(user_id, email, username, subscription_tier)
        refresh_token = self.create_refresh_token(user_id)

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "expires_in": self.access_token_expire_minutes * 60,  # in seconds
        }


# ==================== FASTAPI DEPENDENCY ====================

def get_current_user_from_token(token: str, auth_manager: AuthManager) -> Optional[Dict[str, Any]]:
    """
    FastAPI dependency for extracting user from token.

    Args:
        token: Bearer token from Authorization header
        auth_manager: AuthManager instance

    Returns:
        User data from token payload or None
    """
    payload = auth_manager.verify_access_token(token)
    if not payload:
        return None

    return {
        "user_id": payload.get("sub"),
        "email": payload.get("email"),
        "username": payload.get("username"),
        "subscription_tier": payload.get("subscription_tier"),
    }


# ==================== EXAMPLE USAGE ====================

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    # Initialize auth manager
    auth = AuthManager()

    # Hash a password
    password = "SecurePassword123!"
    hashed = auth.hash_password(password)
    print(f"Hashed password: {hashed[:50]}...")

    # Verify password
    is_valid = auth.verify_password(password, hashed)
    print(f"Password valid: {is_valid}")

    # Create tokens
    tokens = auth.create_token_response(
        user_id="user_123",
        email="test@example.com",
        username="testuser",
        subscription_tier="pro",
    )
    print(f"\nAccess token: {tokens['access_token'][:50]}...")
    print(f"Refresh token: {tokens['refresh_token'][:50]}...")
    print(f"Expires in: {tokens['expires_in']} seconds")

    # Verify access token
    access_payload = auth.verify_access_token(tokens["access_token"])
    print(f"\nAccess token payload: {access_payload}")

    # Extract user ID
    user_id = auth.get_current_user_id(tokens["access_token"])
    print(f"User ID from token: {user_id}")

    # Check expiration
    expiration = auth.get_token_expiration(tokens["access_token"])
    print(f"Token expires at: {expiration}")
    print(f"Is expired: {auth.is_token_expired(tokens['access_token'])}")

    # Refresh access token
    user_data = {
        "user_id": "user_123",
        "email": "test@example.com",
        "username": "testuser",
        "subscription_tier": "pro",
    }
    new_access_token = auth.refresh_access_token(tokens["refresh_token"], user_data)
    print(f"\nNew access token: {new_access_token[:50]}...")
