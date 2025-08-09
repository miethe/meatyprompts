"""Helper functions for importing prompts from structured data files."""
from __future__ import annotations

import csv
import io
import json
from typing import Any, Iterable, List, Tuple
from uuid import UUID

from pydantic import ValidationError
from sqlalchemy.orm import Session

from app.models.imex import (
    ImportMapping,
    ImportPreviewRow,
    ImportResult,
)
from app.models.prompt import PromptCreate
from app.services import prompt_service


ARRAY_FIELDS = {"tags", "target_models", "providers", "use_cases"}


def parse_csv(content: bytes) -> List[dict[str, str]]:
    """Parse CSV bytes into dictionaries keyed by header names."""

    text = content.decode("utf-8-sig")
    sample = text[:1024]
    try:
        dialect = csv.Sniffer().sniff(sample)
    except csv.Error:
        dialect = csv.excel
    reader = csv.DictReader(io.StringIO(text), dialect=dialect)
    return [row for row in reader]


def parse_json(content: bytes) -> List[dict[str, Any]]:
    """Parse JSON array or NDJSON into a list of dictionaries."""

    text = content.decode("utf-8-sig").strip()
    if not text:
        return []
    if text.startswith("["):
        data = json.loads(text)
        if not isinstance(data, list):  # pragma: no cover - defensive
            raise ValueError("JSON root must be an array")
        return data
    return [json.loads(line) for line in text.splitlines() if line.strip()]


def parse_file(content: bytes, filename: str | None) -> List[dict[str, Any]]:
    """Dispatch parsing based on filename extension."""

    if filename and filename.lower().endswith(".csv"):
        return parse_csv(content)
    return parse_json(content)


def _split_array(value: str) -> List[str]:
    return [v.strip() for v in value.split(",") if v.strip()]


def apply_mapping(
    rows: Iterable[dict[str, Any]], mapping: ImportMapping
) -> Tuple[List[ImportPreviewRow], List[PromptCreate]]:
    """Apply field mapping and validate each row."""

    field_map = mapping.model_dump(exclude_none=True)
    preview: List[ImportPreviewRow] = []
    valid: List[PromptCreate] = []
    for idx, row in enumerate(rows):
        data: dict[str, Any] = {}
        for field, column in field_map.items():
            value = row.get(column)
            if value in (None, ""):
                continue
            if field in ARRAY_FIELDS:
                items = _split_array(str(value))
                if field == "tags":
                    data[field] = [i.lower() for i in items]
                else:
                    data[field] = items
            else:
                data[field] = value
        try:
            prompt = PromptCreate(**data)
            preview.append(ImportPreviewRow(row_index=idx, valid=True, mapped=prompt))
            valid.append(prompt)
        except ValidationError as exc:
            errs = [e["msg"] for e in exc.errors()]
            preview.append(ImportPreviewRow(row_index=idx, valid=False, errors=errs))
    return preview, valid


def commit(
    db: Session, owner_id: UUID, prompts: Iterable[PromptCreate]
) -> ImportResult:
    """Persist valid prompts to the database."""

    created = 0
    total = 0
    errors: List[str] = []
    for prompt in prompts:
        total += 1
        try:
            prompt_service.create_prompt(db=db, prompt=prompt, owner_id=owner_id)
            created += 1
        except Exception as exc:  # pragma: no cover - defensive
            errors.append(str(exc))
    skipped = total - created
    return ImportResult(created=created, skipped=skipped, errors=errors)
