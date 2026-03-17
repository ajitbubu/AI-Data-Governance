"""
JWT authentication and role-based access control (RBAC) middleware.

Provides FastAPI dependencies for authentication and authorization,
supporting JWTs and a development bypass mode.
"""
from dataclasses import dataclass
from typing import Optional, Set
from datetime import datetime, timezone, timedelta
import uuid
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials as HTTPAuthCredentials
from jose import JWTError, jwt
import structlog
from ..config import get_settings
from .request_context import set_user_id, set_user_email

settings = get_settings()
logger = structlog.get_logger(__name__)

# Valid roles in the system
VALID_ROLES = {"admin", "compliance_officer", "risk_manager", "auditor", "viewer"}

# Security scheme for OpenAPI documentation
security = HTTPBearer(scheme_name="Bearer")


@dataclass
class CurrentUser:
    """Authenticated user context."""

    id: str
    """User UUID"""

    email: str
    """User email address"""

    roles: Set[str]
    """Set of role strings"""

    org_id: Optional[str] = None
    """Organization ID if applicable"""

    def has_role(self, role: str) -> bool:
        """Check if user has specific role."""
        return role in self.roles

    def has_any_role(self, roles: Set[str]) -> bool:
        """Check if user has any of the specified roles."""
        return bool(self.roles & roles)

    def has_all_roles(self, roles: Set[str]) -> bool:
        """Check if user has all of the specified roles."""
        return roles.issubset(self.roles)


def _create_mock_admin_user() -> CurrentUser:
    """Create a mock admin user for development/testing."""
    return CurrentUser(
        id=str(uuid.uuid4()),
        email="dev-admin@datasafeguard.local",
        roles={"admin"},
        org_id=None,
    )


async def get_current_user(
    credentials: HTTPAuthCredentials = Depends(security),
) -> CurrentUser:
    """
    Dependency to extract and validate current user from JWT.

    Args:
        credentials: HTTP Bearer token from request

    Returns:
        CurrentUser object with authenticated user data

    Raises:
        HTTPException: If token is invalid or expired
    """
    # Development bypass mode
    if settings.AUTH_DEV_BYPASS:
        logger.debug("auth_dev_bypass_enabled")
        return _create_mock_admin_user()

    token = credentials.credentials

    try:
        # Decode JWT
        payload = jwt.decode(
            token,
            settings.AUTH_SECRET_KEY,
            algorithms=[settings.ALGORITHM],
        )

        # Extract claims
        user_id: str | None = payload.get("user_id")
        email: str | None = payload.get("email")
        roles: list[str] | None = payload.get("roles", [])
        org_id: str | None = payload.get("org_id")

        if not user_id or not email:
            logger.warning("jwt_missing_required_claims", token_payload=payload)
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token: missing required claims",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Validate roles
        if not roles:
            roles = ["viewer"]
        roles_set = {role for role in roles if role in VALID_ROLES}
        if not roles_set:
            roles_set = {"viewer"}

        # Create user context
        user = CurrentUser(
            id=user_id,
            email=email,
            roles=roles_set,
            org_id=org_id,
        )

        # Store in context for logging middleware
        set_user_id(user_id)
        set_user_email(email)

        logger.debug("jwt_validated", user_id=user_id, email=email, roles=list(roles_set))

        return user

    except JWTError as e:
        logger.warning("jwt_decode_error", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except Exception as e:
        logger.error("jwt_validation_error", error=str(e), exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication failed",
            headers={"WWW-Authenticate": "Bearer"},
        )


def require_role(required_role: str):
    """
    Factory function to create a dependency that requires a specific role.

    Args:
        required_role: Role string required to proceed

    Returns:
        Dependency function for use with FastAPI Depends()

    Example:
        @app.post("/admin")
        async def admin_only(current_user: CurrentUser = Depends(require_role("admin"))):
            return {"message": "Admin access granted"}
    """
    async def _require_role(
        current_user: CurrentUser = Depends(get_current_user),
    ) -> CurrentUser:
        if not current_user.has_role(required_role):
            logger.warning(
                "authorization_denied",
                user_id=current_user.id,
                required_role=required_role,
                user_roles=list(current_user.roles),
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"This action requires '{required_role}' role",
            )
        return current_user

    return _require_role


def require_any_role(required_roles: Set[str]):
    """
    Factory function to create a dependency that requires any of specified roles.

    Args:
        required_roles: Set of role strings (user needs at least one)

    Returns:
        Dependency function for use with FastAPI Depends()
    """
    async def _require_any_role(
        current_user: CurrentUser = Depends(get_current_user),
    ) -> CurrentUser:
        if not current_user.has_any_role(required_roles):
            logger.warning(
                "authorization_denied",
                user_id=current_user.id,
                required_any_roles=list(required_roles),
                user_roles=list(current_user.roles),
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"This action requires one of: {', '.join(required_roles)}",
            )
        return current_user

    return _require_any_role


def require_all_roles(required_roles: Set[str]):
    """
    Factory function to create a dependency that requires all specified roles.

    Args:
        required_roles: Set of role strings (user needs all of them)

    Returns:
        Dependency function for use with FastAPI Depends()
    """
    async def _require_all_roles(
        current_user: CurrentUser = Depends(get_current_user),
    ) -> CurrentUser:
        if not current_user.has_all_roles(required_roles):
            logger.warning(
                "authorization_denied",
                user_id=current_user.id,
                required_all_roles=list(required_roles),
                user_roles=list(current_user.roles),
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"This action requires all of: {', '.join(required_roles)}",
            )
        return current_user

    return _require_all_roles


def create_access_token(
    user_id: str,
    email: str,
    roles: Set[str],
    org_id: Optional[str] = None,
    expires_delta: Optional[timedelta] = None,
) -> str:
    """
    Create a JWT access token.

    Args:
        user_id: User UUID
        email: User email
        roles: Set of role strings
        org_id: Optional organization ID
        expires_delta: Token expiration time (defaults to ACCESS_TOKEN_EXPIRE_MINUTES)

    Returns:
        JWT token string
    """
    if expires_delta is None:
        expires_delta = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    now = datetime.now(timezone.utc)
    expires_at = now + expires_delta

    payload = {
        "user_id": user_id,
        "email": email,
        "roles": list(roles),
        "org_id": org_id,
        "iat": now,
        "exp": expires_at,
    }

    encoded_jwt = jwt.encode(
        payload,
        settings.AUTH_SECRET_KEY,
        algorithm=settings.ALGORITHM,
    )

    return encoded_jwt
