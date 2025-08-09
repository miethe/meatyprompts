#!/usr/bin/env python3
"""Seed a personal organization and workspace for testing."""
from __future__ import annotations

import uuid
from sqlalchemy import create_engine, text

from services.api.app.core.config import settings

DATABASE_URL = settings.DATABASE_URL_TEST
if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL_TEST is not set in the environment or .env file.")

def main() -> None:
    engine = create_engine(DATABASE_URL)
    user_id = uuid.uuid4()
    org_id = uuid.uuid4()
    workspace_id = uuid.uuid4()
    principal_id = uuid.uuid4()
    with engine.begin() as conn:
        conn.execute(
            text("INSERT INTO organizations(id,name) VALUES (:id,'Personal Org') ON CONFLICT DO NOTHING"),
            {"id": org_id},
        )
        conn.execute(
            text("INSERT INTO principals(id,user_id,type) VALUES (:p,:u,'user')"),
            {"p": principal_id, "u": user_id},
        )
        conn.execute(
            text("INSERT INTO org_members(org_id,principal_id) VALUES (:o,:p) ON CONFLICT DO NOTHING"),
            {"o": org_id, "p": principal_id},
        )
        conn.execute(
            text("INSERT INTO workspaces(id,org_id,name) VALUES (:w,:o,'Personal Workspace') ON CONFLICT DO NOTHING"),
            {"w": workspace_id, "o": org_id},
        )
    print("Seeded personal org and workspace for user", user_id)


if __name__ == "__main__":
    main()
