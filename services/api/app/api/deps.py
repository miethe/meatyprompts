"""Dependency utilities for API routes."""
from __future__ import annotations

from fastapi import Depends, HTTPException, Request
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db  # This should be implemented to yield a Session
from app.models.user import UserORM
from app.services import auth_service


def get_current_user(
    request: Request, db: Session = Depends(get_db)
) -> UserORM:
    """Retrieve the currently authenticated user from the session cookie and DB."""
    token = request.cookies.get(settings.AUTH_COOKIE_NAME)
    if token is None:
        raise HTTPException(status_code=401, detail="Not authenticated")
    user_id = auth_service.verify_session(token)
    if user_id is None:
        raise HTTPException(status_code=401, detail="Invalid session")
    user = auth_service.get_user_by_id(db, user_id)
    if user is None:
        raise HTTPException(status_code=401, detail="User not found")
    return user


def csrf_protect(request: Request) -> None:
    """Validate CSRF token for state-changing requests."""
    header = request.headers.get("X-CSRF-Token")
    cookie = request.cookies.get("csrf_token")
    if not header or header != cookie:
        raise HTTPException(status_code=403, detail="CSRF token missing or invalid")
