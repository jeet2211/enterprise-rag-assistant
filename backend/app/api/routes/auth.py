from __future__ import annotations
import logging
import uuid
from datetime import datetime
from fastapi import APIRouter, Body, Cookie, Depends, HTTPException, Request, Response, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr, field_validator
from app.auth.deps import _get_session, get_current_user
from app.auth.password import hash_password, verify_password
from app.auth.tokens import create_access_token, create_refresh_token, decode_token
from app.models.user import User
from app.core.rate_limit import limiter
from app.config.settings import get_settings

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/auth", tags=["auth"])

REFRESH_COOKIE = "refresh_token"


class SignupRequest(BaseModel):
    email: EmailStr
    password: str

    @field_validator("password")
    @classmethod
    def password_strength(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters")
        return v


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: str
    email: str
    role: str


class PasswordResetRequest(BaseModel):
    email: EmailStr


class PasswordResetConfirm(BaseModel):
    token: str
    new_password: str

    @field_validator("new_password")
    @classmethod
    def password_strength(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters")
        return v


def _issue_tokens(user: User, settings, response: Response) -> TokenResponse:
    """Issue access + refresh tokens. Refresh token is set as an httpOnly cookie."""
    access = create_access_token(
        subject=user.id,
        secret_key=settings.secret_key,
        expires_minutes=settings.access_token_expire_minutes,
    )
    refresh = create_refresh_token(
        subject=user.id,
        secret_key=settings.secret_key,
        expires_days=settings.refresh_token_expire_days,
    )
    response.set_cookie(
        key=REFRESH_COOKIE,
        value=refresh,
        httponly=True,
        secure=True,
        samesite="lax",
        max_age=settings.refresh_token_expire_days * 86400,
        path="/api/v1/auth",
    )
    return TokenResponse(
        access_token=access,
        user_id=user.id,
        email=user.email,
        role=user.role,
    )


@router.post("/signup", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
@limiter.limit(get_settings().rate_limit_signup)
def signup(
    request: Request,
    response: Response,
    payload: SignupRequest = Body(...),
    session: Session = Depends(_get_session),
):
    """Create a new user account and return tokens."""
    existing = session.query(User).filter(User.email == payload.email).first()
    if existing:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already registered")
    user = User(
        id=str(uuid.uuid4()),
        email=payload.email,
        password_hash=hash_password(payload.password),
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    logger.info('{"event":"signup","user_id":"%s"}', user.id)
    return _issue_tokens(user, request.app.state.settings, response)


@router.post("/login", response_model=TokenResponse)
@limiter.limit(get_settings().rate_limit_login)
def login(
    request: Request,
    response: Response,
    payload: LoginRequest = Body(...),
    session: Session = Depends(_get_session),
):
    """Authenticate user credentials and return tokens."""
    user = session.query(User).filter(User.email == payload.email).first()
    if user is None or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Account is disabled")
    logger.info('{"event":"login","user_id":"%s"}', user.id)
    return _issue_tokens(user, request.app.state.settings, response)


@router.post("/logout")
def logout(response: Response):
    """Clear the refresh token cookie."""
    response.delete_cookie(key=REFRESH_COOKIE, path="/api/v1/auth")
    return {"message": "Logged out"}


@router.post("/refresh", response_model=TokenResponse)
def refresh_token(
    request: Request,
    response: Response,
    refresh_token: str | None = Cookie(default=None, alias=REFRESH_COOKIE),
    session: Session = Depends(_get_session),
):
    """Exchange a valid refresh token cookie for a new access token."""
    if refresh_token is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="No refresh token")
    settings = request.app.state.settings
    payload = decode_token(refresh_token, settings.secret_key, expected_type="refresh")
    user = session.get(User, payload["sub"])
    if user is None or not user.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    return _issue_tokens(user, settings, response)


@router.post("/password-reset/request", status_code=status.HTTP_202_ACCEPTED)
def password_reset_request(
    request: Request,
    payload: PasswordResetRequest = Body(...),
    session: Session = Depends(_get_session),
):
    """Stub: log password reset token. Wire real SMTP in production."""
    user = session.query(User).filter(User.email == payload.email).first()
    if user:
        # Generate a short-lived token (1 hour)
        settings = request.app.state.settings
        token = create_access_token(subject=user.id, secret_key=settings.secret_key, expires_minutes=60)
        # TODO: Send email with reset link containing token
        logger.info('{"event":"password_reset_requested","user_id":"%s","token":"%s"}', user.id, token)
    # Always return 202 to avoid user enumeration
    return {"message": "If that email exists, a reset link has been sent"}


@router.post("/password-reset/confirm")
def password_reset_confirm(
    request: Request,
    payload: PasswordResetConfirm = Body(...),
    session: Session = Depends(_get_session),
):
    """Consume a reset token and set a new password."""
    settings = request.app.state.settings
    token_payload = decode_token(payload.token, settings.secret_key, expected_type="access")
    user = session.get(User, token_payload["sub"])
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    user.password_hash = hash_password(payload.new_password)
    user.updated_at = datetime.utcnow()
    session.commit()
    logger.info('{"event":"password_reset_confirmed","user_id":"%s"}', user.id)
    return {"message": "Password updated successfully"}


@router.get("/me", response_model=TokenResponse)
def get_me(current_user: User = Depends(get_current_user)):
    """Return the currently authenticated user's profile."""
    return TokenResponse(
        access_token="",  # Don't re-issue token on /me
        user_id=current_user.id,
        email=current_user.email,
        role=current_user.role,
    )
