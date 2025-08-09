from app.models.imex import ImportMapping
from app.models.imex import ImportMapping
from app.services import import_service


def test_parse_json_ndjson():
    content = b'{"a":1}\n{"a":2}\n'
    rows = import_service.parse_json(content)
    assert rows == [{"a": 1}, {"a": 2}]


def test_apply_mapping_normalizes_tags():
    rows = [
        {
            "Title": "t",
            "Body": "b",
            "Use": "u",
            "Access": "private",
            "Tags": "One,Two",
        }
    ]
    mapping = ImportMapping(
        title="Title",
        body="Body",
        use_cases="Use",
        access_control="Access",
        tags="Tags",
    )
    preview, valid = import_service.apply_mapping(rows, mapping)
    assert preview[0].valid is True
    assert valid[0].tags == ["one", "two"]
