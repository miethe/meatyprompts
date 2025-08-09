"""Webhook routes for external services."""
from __future__ import annotations

import base64
import hmac
import hashlib
import json
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db
from app.services.user_service import sync_user_from_clerk_webhook

router = APIRouter()


@router.post("/webhooks/clerk")
async def clerk_webhook(request: Request, db: Session = Depends(get_db)) -> dict[str, str]:
    """Handle Clerk webhook events by syncing the user table."""
    payload = await request.body()
    signature = request.headers.get("svix-signature")
    if signature is None:
        raise HTTPException(status_code=400, detail="Missing signature")
    expected = base64.b64encode(
        hmac.new(settings.CLERK_WEBHOOK_SECRET.encode(), payload, hashlib.sha256).digest()
    ).decode()
    if not hmac.compare_digest(signature, expected):
        raise HTTPException(status_code=400, detail="Invalid signature")
    event = json.loads(payload.decode())
    sync_user_from_clerk_webhook(db, event)
    return {"status": "ok"}
