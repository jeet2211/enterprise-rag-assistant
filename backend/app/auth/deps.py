from __future__ import annotations
from fastapi import Cookie, Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session
from app.auth.tokens import decode_token
from app.models.user import User

security = HTTPBearer(auto_error=False)


def _get_session(request: Request):
    with request.app.state.session_factory() as session:
        yield session


def get_current_user(
    request: Request,
    credentials: HTTPAuthorizationCredentials | None = Depends(security),
    session: Session = Depends(_get_session),
) -> User:
    """Extract and validate JWT bearer token, return the authenticated User."""
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    settings = request.app.state.settings
    payload = decode_token(credentials.credentials, settings.secret_key, expected_type="access")
    user_id: str = payload["sub"]
    user = session.get(User, user_id)
    if user is None or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive",
        )
    return user


def require_admin(current_user: User = Depends(get_current_user)) -> User:
    """Require the authenticated user to have the admin role."""
    if current_user.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required")
    return current_user
