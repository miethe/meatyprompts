"""Dependency utilities for API routes."""
from __future__ import annotations

from fastapi import Depends, HTTPException, Request
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db
from app.models.user import UserORM

import base64
import hmac
import json
import hashlib


def _decode_jwt(token: str, secret: str) -> dict[str, object]:
    """Decode a minimal HS256 JWT without external dependencies."""
    try:
        header_b64, payload_b64, sig_b64 = token.split(".")
    except ValueError as exc:  # not enough segments
        raise HTTPException(status_code=401, detail="Invalid token") from exc
    signing_input = f"{header_b64}.{payload_b64}".encode()
    expected_sig = base64.urlsafe_b64encode(
        hmac.new(secret.encode(), signing_input, hashlib.sha256).digest()
    ).rstrip(b"=")
    if not hmac.compare_digest(expected_sig, sig_b64.encode()):
        raise HTTPException(status_code=401, detail="Invalid token signature")
    padding = '=' * (-len(payload_b64) % 4)
    payload = json.loads(base64.urlsafe_b64decode(payload_b64 + padding))
    return payload


def get_current_user(request: Request, db: Session = Depends(get_db)) -> UserORM:
    """Retrieve the current user using a Clerk-issued JWT."""
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Not authenticated")
    token = auth_header.split(" ", 1)[1]
    payload = _decode_jwt(token, settings.CLERK_JWT_VERIFICATION_KEY)
    clerk_user_id = payload.get("sub")
    if clerk_user_id is None:
        raise HTTPException(status_code=401, detail="Invalid token payload")
    user = db.query(UserORM).filter_by(clerk_user_id=clerk_user_id).first()
    if user is None:
        raise HTTPException(status_code=401, detail="User not found")
    return user
