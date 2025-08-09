from datetime import datetime
import uuid

from app.services import search_service


class DummyHeader:
    def __init__(self, id, updated, created, title):
        self.id = id
        self.updated_at = updated
        self.created_at = created
        self.title = title


def test_cursor_round_trip():
    now = datetime.utcnow()
    header = DummyHeader(uuid.uuid4(), now, now, "alpha")
    cursor = search_service.encode_cursor((None, header), search_service.SearchSort.updated_desc)
    key, pid = search_service.decode_cursor(cursor)
    assert pid == header.id
    assert key == now.isoformat()
