"""Session context helpers for row-level security."""
from __future__ import annotations

from contextvars import ContextVar
from typing import Callable

from fastapi import Request
from sqlalchemy import event

from .session import engine

USER_ID_CTX: ContextVar[str | None] = ContextVar("app_user_id", default=None)
TENANT_ID_CTX: ContextVar[str | None] = ContextVar("app_tenant_id", default=None)


@event.listens_for(engine, "checkout")
def apply_session_context(dbapi_conn, conn_record, conn_proxy) -> None:
    """Set per-connection session variables for RLS."""
    user_id = USER_ID_CTX.get()
    tenant_id = TENANT_ID_CTX.get()
    cursor = dbapi_conn.cursor()
    if user_id:
        cursor.execute("SET app.user_id = %s", (user_id,))
    else:
        cursor.execute("RESET app.user_id")
    if tenant_id:
        cursor.execute("SET app.tenant_id = %s", (tenant_id,))
    else:
        cursor.execute("RESET app.tenant_id")
    cursor.close()


async def rls_middleware(request: Request, call_next: Callable):
    """Middleware that applies RLS session variables per request."""
    token_user = USER_ID_CTX.set(request.headers.get("X-User-Id"))
    token_tenant = TENANT_ID_CTX.set(request.headers.get("X-Tenant-Id"))
    try:
        response = await call_next(request)
    finally:
        USER_ID_CTX.reset(token_user)
        TENANT_ID_CTX.reset(token_tenant)
    return response
