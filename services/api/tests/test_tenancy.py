"""Tests for tenancy foundations and RLS helpers."""
from __future__ import annotations

from pathlib import Path
import uuid

import pytest
import sqlalchemy as sa
from alembic import command
from alembic.config import Config
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, inspect, text

from services.api.app.core.config import settings

TEST_DB = settings.DATABASE_URL_TEST
if not TEST_DB:
    raise RuntimeError("DATABASE_URL_TEST is not set in the environment or .env file.")

BASE_DIR = Path(__file__).resolve().parents[1]

def run_migrations() -> None:
    cfg = Config(str(BASE_DIR / "alembic.ini"))
    cfg.set_main_option("sqlalchemy.url", TEST_DB)
    command.upgrade(cfg, "head")


@pytest.fixture(scope="module")
def engine():
    engine = create_engine(TEST_DB, isolation_level="AUTOCOMMIT")
    with engine.begin() as conn:
        conn.execute(text("DROP SCHEMA public CASCADE; CREATE SCHEMA public;"))
    run_migrations()
    yield engine
    engine.dispose()


def test_tables_and_enums(engine):
    insp = inspect(engine)
    assert "organizations" in insp.get_table_names()
    assert "resources" in insp.get_table_names()
    type_col = next(c for c in insp.get_columns("resources") if c["name"] == "type")
    assert isinstance(type_col["type"], sa.Enum)


def test_current_tenant_function(engine):
    tid = "00000000-0000-0000-0000-000000000000"
    with engine.begin() as conn:
        conn.execute(text("SET app.tenant_id = :t"), {"t": tid})
        result = conn.execute(text("SELECT current_tenant()"))
    assert result.scalar() == uuid.UUID(tid)


def test_caller_principals(engine):
    user_id = uuid.uuid4()
    principal_id = uuid.uuid4()
    with engine.begin() as conn:
        conn.execute(
            text("INSERT INTO principals(id,user_id,type) VALUES (:p,:u,'user')"),
            {"p": principal_id, "u": user_id},
        )
        conn.execute(text("SET app.user_id = :u"), {"u": str(user_id)})
        res = conn.execute(text("SELECT caller_principals()"))
    assert res.scalar() == [principal_id]


def test_rls_shadow_policies(engine):
    tenant = uuid.uuid4()
    workspace = uuid.uuid4()
    resource_id = uuid.uuid4()
    with engine.begin() as conn:
        conn.execute(
            text(
                "INSERT INTO resources(id,tenant_id,workspace_id,type) VALUES (:i,:t,:w,'prompt')"
            ),
            {"i": resource_id, "t": tenant, "w": workspace},
        )
        count = conn.execute(text("SELECT count(*) FROM resources")).scalar()
        assert count == 1
        conn.execute(text("ALTER TABLE resources ENABLE ROW LEVEL SECURITY"))
        conn.execute(text("SET app.tenant_id = :tid"), {"tid": str(uuid.uuid4())})
        count = conn.execute(text("SELECT count(*) FROM resources")).scalar()
        assert count == 0
        conn.execute(text("SET app.tenant_id = :tid"), {"tid": str(tenant)})
        count = conn.execute(text("SELECT count(*) FROM resources")).scalar()
        assert count == 1
        conn.execute(text("ALTER TABLE resources DISABLE ROW LEVEL SECURITY"))


def test_middleware_sets_session_vars(engine):
    from app.main import create_app
    import os

    os.environ.setdefault("DATABASE_URL", TEST_DB)
    os.environ.setdefault("AUTH_SIGNING_SECRET", "secret")
    os.environ.setdefault("GITHUB_CLIENT_ID", "id")
    os.environ.setdefault("GITHUB_CLIENT_SECRET", "secret")

    app = create_app()
    client = TestClient(app)
    t1 = "11111111-1111-1111-1111-111111111111"
    r1 = client.get("/_int/tenancy/ping", headers={"X-Tenant-Id": t1})
    assert r1.json()["tenant_id"] == t1
    t2 = "22222222-2222-2222-2222-222222222222"
    r2 = client.get("/_int/tenancy/ping", headers={"X-Tenant-Id": t2})
    assert r2.json()["tenant_id"] == t2
