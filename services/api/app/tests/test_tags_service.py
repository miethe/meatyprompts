from unittest.mock import MagicMock
from sqlalchemy.orm import Session

from app.services.tags_service import top_tags
from app.models.tag import TagCount


def test_top_tags_returns_results():
    mock_db = MagicMock(spec=Session)
    mock_db.execute.return_value.fetchall.return_value = [
        {"tag": "alpha", "count": 3},
        {"tag": "beta", "count": 1},
    ]
    result = top_tags(mock_db, limit=5)
    assert result == [TagCount(tag="alpha", count=3), TagCount(tag="beta", count=1)]
    mock_db.execute.assert_called()
