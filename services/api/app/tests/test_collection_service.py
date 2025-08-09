from unittest.mock import MagicMock
import uuid
import pytest
from sqlalchemy.orm import Session

from app.services import collection_service
from app.models.collection import CollectionORM


def test_create_collection_conflict():
    db = MagicMock(spec=Session)
    db.query.return_value.filter.return_value.first.return_value = object()
    with pytest.raises(ValueError):
        collection_service.create_collection(db, uuid.uuid4(), "dup")


def test_add_prompt_checks_ownership():
    db = MagicMock(spec=Session)

    def query_side_effect(model):
        mock = MagicMock()
        if model is CollectionORM:
            mock.filter.return_value.first.return_value = None
        else:
            mock.filter.return_value.first.return_value = MagicMock()
        return mock

    db.query.side_effect = query_side_effect
    with pytest.raises(PermissionError):
        collection_service.add_prompt(db, uuid.uuid4(), uuid.uuid4(), uuid.uuid4())
