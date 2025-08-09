"""Tests for prompt duplication telemetry and performance."""

from __future__ import annotations

from datetime import datetime
import sys
import uuid
from pathlib import Path
BASE_DIR = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(BASE_DIR))
from unittest.mock import MagicMock, patch

import pytest
from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session
from typing import Generator

from app.models.prompt import PromptHeaderORM, PromptVersionORM
from app.services.prompt_service import duplicate_prompt

TEST_DB = "postgresql://test_user:password@/meatyprompts"


def run_migrations() -> None:
    """Apply all alembic migrations."""
    sys.path.insert(0, str(BASE_DIR))
    cfg = Config(str(BASE_DIR / "alembic.ini"))
    cfg.set_main_option("sqlalchemy.url", TEST_DB)
    command.upgrade(cfg, "head")


@pytest.fixture(scope="module")
def engine() -> Generator[Engine, None, None]:
    """Prepare a clean database and run migrations."""
    engine = create_engine(TEST_DB, isolation_level="AUTOCOMMIT")
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
    except Exception:
        pytest.skip("database not available")
    with engine.begin() as conn:
        conn.execute(text("DROP SCHEMA public CASCADE; CREATE SCHEMA public;"))
    run_migrations()
    yield engine
    engine.dispose()


def test_duplicate_prompt_emits_event_and_latency() -> None:
    """Ensure duplicate_prompt logs telemetry with elapsed time."""
    mock_db = MagicMock(spec=Session)
    prompt_id = uuid.uuid4()

    latest_version = PromptVersionORM(
        id=uuid.uuid4(),
        prompt_id=prompt_id,
        version="1",
        body="body",
        access_control="private",
        use_cases=["u"],
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )
    header = PromptHeaderORM(
        id=prompt_id,
        owner_id=uuid.uuid4(),
        title="t",
        tags=None,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )

    query_version = MagicMock()
    query_header = MagicMock()
    mock_db.query.side_effect = [query_version, query_header]
    query_version.filter.return_value.order_by.return_value.first.return_value = latest_version
    query_header.filter.return_value.first.return_value = header

    with patch("app.services.prompt_service.time.perf_counter", side_effect=[1.0, 1.05]):
        with patch("app.services.prompt_service.logger") as mock_logger:
            duplicate_prompt(mock_db, prompt_id)

    mock_logger.info.assert_any_call(
        "events.prompt_duplicated",
        extra={
            "prompt_id": str(prompt_id),
            "new_version": "2",
            "elapsed_ms": 50.0,
        },
    )


def test_latest_version_lookup_performance(engine: Engine) -> None:
    """Latest-version lookup should be indexed and under p95 latency."""
    prompt_uuid = "11111111-1111-1111-1111-111111111111"
    user_uuid = "00000000-0000-0000-0000-000000000000"
    with engine.begin() as conn:
        conn.execute(
            text(
                """
                INSERT INTO users(id,email) VALUES (:uid,'a@b.com');
                INSERT INTO prompts(id, owner_id, title, updated_at)
                VALUES (:pid, :uid, 't', now());
                """
            ),
            {"uid": user_uuid, "pid": prompt_uuid},
        )
        for i in range(1, 101):
            conn.execute(
                text(
                    """
                    INSERT INTO prompt_versions(id, prompt_id, version, body, access_control, use_cases, created_at, updated_at)
                    VALUES (:vid, :pid, :ver, 'b', 'private', '{"u"}', now(), now());
                    """
                ),
                {"vid": str(uuid.uuid4()), "pid": prompt_uuid, "ver": i},
            )
        plan = conn.execute(
            text(
                "EXPLAIN ANALYZE SELECT * FROM prompt_versions WHERE prompt_id=:pid ORDER BY version DESC LIMIT 1"
            ),
            {"pid": prompt_uuid},
        ).fetchall()

    assert any("ix_prompt_versions_prompt_desc" in row[0] for row in plan)
    exec_line = next(row[0] for row in plan if "Execution Time" in row[0])
    exec_ms = float(exec_line.split("Execution Time: ")[1].split(" ms")[0])
    assert exec_ms < 150.0
