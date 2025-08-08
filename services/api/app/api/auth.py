"""Authentication routes."""
from __future__ import annotations

import logging

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse, RedirectResponse

from app.api.deps import get_current_user
from app.core.config import settings
from app.models.user import User
from app.services import auth_service

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/auth/github/login")
def github_login() -> RedirectResponse:
    """Initiate the (mock) GitHub OAuth flow."""
    return RedirectResponse(url="https://github.com/login/oauth/authorize")


@router.get("/auth/github/callback")
def github_callback() -> RedirectResponse:
    """Mock OAuth callback that issues a session cookie."""
    user = auth_service.get_or_create_user(
        email="user@example.com",
        name="Example User",
        avatar_url="https://example.com/avatar.png",
    )
    session_token = auth_service.create_session(user.id)
    csrf_token = auth_service.generate_csrf_token()
    response = RedirectResponse(url="/")
    response.set_cookie(
        settings.AUTH_COOKIE_NAME,
        session_token,
        httponly=True,
        secure=True,
        samesite="lax",
    )
    response.set_cookie(
        "csrf_token",
        csrf_token,
        httponly=False,
        secure=True,
        samesite="lax",
    )
    logger.info("auth.login.success", extra={"user_id": str(user.id), "provider": "github"})
    return response


@router.post("/auth/logout")
def logout(user: User = Depends(get_current_user)) -> JSONResponse:
    """Log the user out by clearing session cookies."""
    response = JSONResponse({"detail": "ok"})
    response.delete_cookie(settings.AUTH_COOKIE_NAME)
    response.delete_cookie("csrf_token")
    logger.info("auth.logout", extra={"user_id": str(user.id)})
    return response


@router.post("/auth/magic-link")
def magic_link_request() -> None:
    """Magic link entry point (disabled by feature flag)."""
    if not settings.FF_AUTH_MAGIC_LINK:
        raise HTTPException(status_code=404, detail="Magic link disabled")
    return None


@router.get("/auth/magic-link/verify")
def magic_link_verify(token: str) -> RedirectResponse:
    """Verify a magic link token (disabled by feature flag)."""
    if not settings.FF_AUTH_MAGIC_LINK:
        raise HTTPException(status_code=404, detail="Magic link disabled")
    user = auth_service.get_or_create_user(email="ml@example.com")
    session_token = auth_service.create_session(user.id)
    response = RedirectResponse(url="/")
    response.set_cookie(
        settings.AUTH_COOKIE_NAME,
        session_token,
        httponly=True,
        secure=True,
        samesite="lax",
    )
    return response
