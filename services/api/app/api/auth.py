"""Authentication routes."""
from __future__ import annotations

import logging
import os
import requests
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import JSONResponse, RedirectResponse
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.config import settings
from app.core.database import get_db
from app.models.user import AuthProvider, UserORM, User
from app.services import auth_service

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/auth/github/login")
def github_login() -> RedirectResponse:
    """Initiate the GitHub OAuth flow."""
    github_auth_url = (
        "https://github.com/login/oauth/authorize"
        f"?client_id={settings.GITHUB_CLIENT_ID}"
        f"&redirect_uri=http://localhost:8000/auth/github/callback"
        f"&scope=read:user user:email"
    )
    return RedirectResponse(url=github_auth_url)


@router.get("/auth/github/callback")
def github_callback(request: Request, db: Session = Depends(get_db)) -> RedirectResponse:
    """Handle GitHub OAuth callback, exchange code for token, fetch user info, and issue session."""
    code = request.query_params.get("code")
    if not code:
        raise HTTPException(status_code=400, detail="Missing code from GitHub callback")

    # Exchange code for access token
    token_resp = requests.post(
        "https://github.com/login/oauth/access_token",
        headers={"Accept": "application/json"},
        data={
            "client_id": settings.GITHUB_CLIENT_ID,
            "client_secret": settings.GITHUB_CLIENT_SECRET,
            "code": code,
            "redirect_uri": "http://localhost:8000/auth/github/callback",
        },
        timeout=10,
    )
    token_resp.raise_for_status()
    token_data = token_resp.json()
    access_token = token_data.get("access_token")
    if not access_token:
        raise HTTPException(status_code=400, detail="Failed to obtain access token from GitHub")

    # Fetch user info from GitHub
    user_resp = requests.get(
        "https://api.github.com/user",
        headers={"Authorization": f"Bearer {access_token}"},
        timeout=10,
    )
    user_resp.raise_for_status()
    user_data = user_resp.json()

    # Fetch user email (may be private)
    email = user_data.get("email")
    if not email:
        emails_resp = requests.get(
            "https://api.github.com/user/emails",
            headers={"Authorization": f"Bearer {access_token}"},
            timeout=10,
        )
        emails_resp.raise_for_status()
        emails = emails_resp.json()
        primary_email = next((e["email"] for e in emails if e.get("primary") and e.get("verified")), None)
        email = primary_email or (emails[0]["email"] if emails else None)

    if not email:
        raise HTTPException(status_code=400, detail="Could not determine GitHub user email")

    user = auth_service.get_or_create_user(
        db,
        email=email,
        name=user_data.get("name") or user_data.get("login"),
        avatar_url=user_data.get("avatar_url"),
        provider=AuthProvider.github,
        provider_user_id=str(user_data["id"]),
        access_token_encrypted=access_token,
    )
    session_token = auth_service.create_session(user.id)
    csrf_token = auth_service.generate_csrf_token()
    response = RedirectResponse(url="http://localhost:3000/")
    response.set_cookie(
        settings.AUTH_COOKIE_NAME,
        session_token,
        httponly=True,
        # secure=True,  # REMOVE for local dev
        samesite="lax",
        domain="localhost",
    )
    response.set_cookie(
        "csrf_token",
        csrf_token,
        httponly=False,
        # secure=True,  # REMOVE for local dev
        samesite="lax",
        domain="localhost",
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
def magic_link_verify(token: str, db: Session = Depends(get_db)) -> RedirectResponse:
    """Verify a magic link token (disabled by feature flag)."""
    if not settings.FF_AUTH_MAGIC_LINK:
        raise HTTPException(status_code=404, detail="Magic link disabled")
    user = auth_service.get_or_create_user(
        db,
        email="ml@example.com",
        name=None,
        avatar_url=None,
        provider=AuthProvider.magic,
        provider_user_id="magic-link-token",
    )
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
