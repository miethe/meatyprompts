import pytest
from unittest.mock import MagicMock
from sqlalchemy.orm import Session
from app.services.lookup_service import list_lookup_values, create_lookup_value, get_lookup_table
from app.models.lookup import ModelLookupORM

@pytest.mark.asyncio
async def test_list_lookup_values():
    mock_db = MagicMock(spec=Session)
    mock_query = mock_db.query.return_value
    mock_query.all.return_value = [ModelLookupORM(value="test-model")]

    result = await list_lookup_values(mock_db, "models")

    assert len(result) == 1
    assert result[0].value == "test-model"
    mock_db.query.assert_called_once_with(ModelLookupORM)

@pytest.mark.asyncio
async def test_create_lookup_value_new():
    mock_db = MagicMock(spec=Session)
    mock_db.query.return_value.filter.return_value.first.return_value = None

    new_value = "new-model"
    result = await create_lookup_value(mock_db, "models", new_value)

    assert result.value == new_value
    mock_db.add.assert_called_once()
    mock_db.commit.assert_called_once()
    mock_db.refresh.assert_called_once()

@pytest.mark.asyncio
async def test_create_lookup_value_existing():
    mock_db = MagicMock(spec=Session)
    existing_model = ModelLookupORM(value="existing-model")
    mock_db.query.return_value.filter.return_value.first.return_value = existing_model

    result = await create_lookup_value(mock_db, "models", "existing-model")

    assert result.value == "existing-model"
    mock_db.add.assert_not_called()

def test_get_lookup_table_invalid():
    with pytest.raises(ValueError):
        get_lookup_table("invalid_type")
