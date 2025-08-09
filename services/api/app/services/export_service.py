"""Utilities for streaming prompt exports."""
from __future__ import annotations

import json
from typing import Iterator, Optional
from uuid import UUID

from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.models.prompt import Prompt
from app.services import prompt_service


def iter_prompts(
    db: Session, owner_id: UUID, collection_id: Optional[UUID] = None
) -> Iterator[Prompt]:
    """Yield prompts for the given owner, optionally filtered by collection."""

    cursor: Optional[str] = None
    while True:
        resp = prompt_service.list_prompts(
            db=db,
            owner_id=owner_id,
            q=None,
            tags=None,
            favorite=None,
            archived=None,
            target_models=None,
            providers=None,
            purposes=None,
            collection_id=collection_id,
            sort="updated_desc",
            limit=100,
            after=cursor,
        )
        for item in resp.items:
            yield item
        if not resp.next_cursor:
            break
        cursor = resp.next_cursor


def stream_json(items: Iterator[Prompt]) -> StreamingResponse:
    """Return a streaming JSON array response for prompt objects."""

    def _gen() -> Iterator[str]:
        yield "["
        first = True
        for prompt in items:
            if not first:
                yield ","
            else:
                first = False
            yield json.dumps(prompt.model_dump())
        yield "]"

    return StreamingResponse(_gen(), media_type="application/json")
