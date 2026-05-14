import secrets
from typing import Dict, Optional

from fastapi import Header, HTTPException, status

from accounts.models import User, store


_tokens: Dict[str, str] = {}  # token -> username


def login(username: str, password: str) -> Optional[User]:
    user = store.get(username)
    if user is None or user.password != password:
        return None
    # soft-deleted accounts cannot log in
    if user.deleted_at is not None:
        return None
    return user


def issue_token(user: User) -> str:
    token = secrets.token_urlsafe(24)
    _tokens[token] = user.username
    return token


def resolve(token: str) -> Optional[User]:
    username = _tokens.get(token)
    if username is None:
        return None
    return store.get(username)


def current_user(authorization: Optional[str] = Header(default=None)) -> User:
    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="missing bearer token",
        )
    token = authorization.split(" ", 1)[1].strip()
    user = resolve(token)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="invalid token",
        )
    return user


def require_admin(user: User) -> None:
    if not user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="admin only",
        )


def _clear_tokens() -> None:
    """Test-only helper for state reset between tests."""
    _tokens.clear()
