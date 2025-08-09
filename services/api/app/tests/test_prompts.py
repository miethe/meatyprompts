from datetime import datetime
import uuid
from unittest.mock import MagicMock, patch

import pytest
from pydantic import ValidationError
from sqlalchemy.orm import Session

from app.models.prompt import PromptCreate, PromptHeaderORM, PromptVersionORM
from app.services.prompt_service import (
    create_prompt,
    get_prompt_by_id,
    list_prompts,
    update_prompt,
)

def test_create_prompt():
    mock_db = MagicMock(spec=Session)
    prompt_data = PromptCreate(
        title="Test Prompt",
        body="This is a test prompt.",
        use_cases=["testing"],
        access_control="public",
        target_models=["gpt-3.5-turbo"],
    )

    prompt = create_prompt(db=mock_db, prompt=prompt_data)

    assert prompt.title == "Test Prompt"
    assert prompt.version == "1"
    assert mock_db.add.call_count == 2
    assert mock_db.commit.call_count == 2
    assert mock_db.refresh.call_count == 2


def test_create_prompt_normalizes_tags():
    mock_db = MagicMock(spec=Session)
    prompt_data = PromptCreate(
        title="T",
        body="B",
        use_cases=["u"],
        access_control="private",
        tags=[" Alpha ", "beta", "alpha"],
    )
    prompt = create_prompt(mock_db, prompt_data, owner_id=uuid.uuid4())
    assert prompt.tags == ["alpha", "beta"]


def test_missing_required_fields():
    with pytest.raises(ValidationError):
        PromptCreate(title="T", body="B", use_cases=["a"])


def test_empty_body_validation():
    with pytest.raises(ValidationError):
        PromptCreate(title="T", body="", use_cases=["a"], access_control="private")

def test_list_prompts_with_filters():
    mock_db = MagicMock(spec=Session)
    query_version = MagicMock()
    query_header = MagicMock()
    mock_db.query.side_effect = [query_version, query_header]

    query_version.filter.return_value = query_version
    query_version.join.return_value = query_version
    query_version.order_by.return_value.all.return_value = []
    query_header.filter.return_value.all.return_value = []

    list_prompts(mock_db, model="gpt-4", provider="openai", use_case="test")

    assert mock_db.query.call_args_list[0].args[0] is PromptVersionORM
    assert query_version.filter.call_count == 3

    # A more detailed test could inspect the call_args to ensure the
    # correct filter expressions were used, but this is a good start.


def test_get_prompt_by_id_returns_prompt():
    mock_db = MagicMock(spec=Session)
    prompt_id = uuid.uuid4()

    version = PromptVersionORM(
        id=uuid.uuid4(),
        prompt_id=prompt_id,
        version="1",
        body="body",
        access_control="private",
        use_cases=["test"],
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )
    header = PromptHeaderORM(
        id=prompt_id,
        title="title",
        tags=["t"],
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )

    query_version = MagicMock()
    query_header = MagicMock()
    mock_db.query.side_effect = [query_version, query_header]
    query_version.filter.return_value.order_by.return_value.first.return_value = version
    query_header.filter.return_value.first.return_value = header

    result = get_prompt_by_id(mock_db, prompt_id)
    assert result.title == "title"
    assert result.body == "body"


def test_get_prompt_by_id_not_found():
    mock_db = MagicMock(spec=Session)
    mock_db.query.return_value.filter.return_value.order_by.return_value.first.return_value = None

    result = get_prompt_by_id(mock_db, uuid.uuid4())
    assert result is None


def test_update_prompt_updates_fields():
    mock_db = MagicMock(spec=Session)
    prompt_id = uuid.uuid4()

    latest_version = PromptVersionORM(
        id=uuid.uuid4(),
        prompt_id=prompt_id,
        version="1",
        body="old",
        access_control="private",
        use_cases=["x"],
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )
    header = PromptHeaderORM(
        id=prompt_id,
        title="title",
        tags=["t"],
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )

    query_version = MagicMock()
    query_header = MagicMock()
    mock_db.query.side_effect = [query_version, query_header]
    query_version.filter.return_value.order_by.return_value.first.return_value = latest_version
    query_header.filter.return_value.first.return_value = header

    update = PromptCreate(
        title="title",
        body="new",
        use_cases=["y"],
        access_control="private",
        tags=["New"],
    )
    result = update_prompt(mock_db, prompt_id, update)

    assert result.body == "new"
    assert result.use_cases == ["y"]
    assert result.tags == ["new"]
    assert header.tags == ["new"]
    assert latest_version.version == "1"


def test_update_prompt_logs_event():
    mock_db = MagicMock(spec=Session)
    prompt_id = uuid.uuid4()

    latest_version = PromptVersionORM(
        id=uuid.uuid4(),
        prompt_id=prompt_id,
        version="1",
        body="old",
        access_control="private",
        use_cases=["x"],
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )
    header = PromptHeaderORM(
        id=prompt_id,
        title="title",
        tags=["t"],
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )

    query_version = MagicMock()
    query_header = MagicMock()
    mock_db.query.side_effect = [query_version, query_header]
    query_version.filter.return_value.order_by.return_value.first.return_value = latest_version
    query_header.filter.return_value.first.return_value = header

    update = PromptCreate(
        title="title",
        body="new",
        use_cases=["y"],
        access_control="private",
    )

    with patch("app.services.prompt_service.logger") as mock_logger:
        update_prompt(mock_db, prompt_id, update)
        assert mock_logger.info.call_count >= 2
        event_call = [c for c in mock_logger.info.call_args_list if c.args[0] == "events.prompt_edited"]
        assert event_call


def test_update_prompt_updates_header_tags():
    mock_db = MagicMock(spec=Session)
    prompt_id = uuid.uuid4()

    latest_version = PromptVersionORM(
        id=uuid.uuid4(),
        prompt_id=prompt_id,
        version="1",
        body="b",
        access_control="private",
        use_cases=["x"],
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )
    header = PromptHeaderORM(
        id=prompt_id,
        owner_id=uuid.uuid4(),
        title="t",
        tags=["old"],
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )

    query_version = MagicMock()
    query_header = MagicMock()
    mock_db.query.side_effect = [query_version, query_header]
    query_version.filter.return_value.order_by.return_value.first.return_value = latest_version
    query_header.filter.return_value.first.return_value = header

    update = PromptCreate(
        title="t",
        body="b",
        use_cases=["x"],
        access_control="private",
        tags=["new", "New"],
    )
    result = update_prompt(mock_db, prompt_id, update)
    assert result.tags == ["new"]
    assert header.tags == ["new"]


def test_update_prompt_not_found():
    mock_db = MagicMock(spec=Session)
    mock_db.query.return_value.filter.return_value.order_by.return_value.first.return_value = None

    update = PromptCreate(
        title="title",
        body="body",
        use_cases=["x"],
        access_control="private",
    )
    result = update_prompt(mock_db, uuid.uuid4(), update)
    assert result is None
