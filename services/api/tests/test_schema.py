"""Tests for baseline database schema."""

from pathlib import Path

import pytest
import sqlalchemy as sa
from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine, inspect, text
import sys

TEST_DB = "postgresql://root@/meatyprompts"
BASE_DIR = Path(__file__).resolve().parents[1]


def run_migrations() -> None:
    """Apply all alembic migrations."""
    sys.path.insert(0, str(BASE_DIR))
    cfg = Config(str(BASE_DIR / "alembic.ini"))
    cfg.set_main_option("sqlalchemy.url", TEST_DB)
    command.upgrade(cfg, "head")


@pytest.fixture(scope="module")
def engine():
    """Prepare a clean database and run migrations."""
    engine = create_engine(TEST_DB, isolation_level="AUTOCOMMIT")
    with engine.begin() as conn:
        conn.execute(text("DROP SCHEMA public CASCADE; CREATE SCHEMA public;"))
    run_migrations()
    yield engine
    engine.dispose()


def test_tables_created(engine) -> None:
    """Ensure core tables exist after migration."""
    insp = inspect(engine)
    tables = insp.get_table_names()
    for name in ["prompts", "prompt_versions", "collections", "collection_prompts", "share_tokens"]:
        assert name in tables


def test_version_column_integer(engine) -> None:
    """The version column should be stored as an integer."""
    insp = inspect(engine)
    cols = insp.get_columns("prompt_versions")
    version_col = next(col for col in cols if col["name"] == "version")
    assert isinstance(version_col["type"], sa.Integer)


def test_indexes_exist(engine) -> None:
    """Expected indexes are created for performance."""
    insp = inspect(engine)
    prompt_idx = {idx["name"] for idx in insp.get_indexes("prompts")}
    assert "ix_prompts_owner_updated" in prompt_idx
    assert "ix_prompts_title_trgm" in prompt_idx

    pv_idx = {idx["name"] for idx in insp.get_indexes("prompt_versions")}
    assert "ix_prompt_versions_body_trgm" in pv_idx


def test_owner_updated_index_usage(engine) -> None:
    """Query plan should use the owner/updated_at index."""
    with engine.begin() as conn:
        conn.execute(
            text(
                """
                INSERT INTO users(id,email) VALUES ('00000000-0000-0000-0000-000000000000','a@b.com');
                INSERT INTO prompts(id, owner_id, title, updated_at)
                VALUES ('11111111-1111-1111-1111-111111111111','00000000-0000-0000-0000-000000000000','t', now());
                """
            )
        )
        plan = conn.execute(
            text(
                "EXPLAIN SELECT * FROM prompts WHERE owner_id='00000000-0000-0000-0000-000000000000' ORDER BY updated_at DESC"
            )
        ).fetchall()
    assert any("ix_prompts_owner_updated" in row[0] for row in plan)
