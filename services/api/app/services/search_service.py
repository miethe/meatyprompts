from __future__ import annotations

import base64
import json
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import List, Optional, Tuple
from uuid import UUID

from sqlalchemy import and_, asc, desc, func, or_
from sqlalchemy.orm import Query, Session

from app.models.prompt import PromptHeaderORM, PromptVersionORM
from app.models.collection import CollectionPromptORM


class SearchSort(str, Enum):
    """Enumeration of supported sort orders for prompt search."""

    updated_desc = "updated_desc"
    created_desc = "created_desc"
    title_asc = "title_asc"
    relevance_desc = "relevance_desc"


@dataclass
class SearchFilters:
    """Container for search and filter parameters."""

    owner_id: UUID
    q: Optional[str] = None
    tags: Optional[List[str]] = None
    favorite: Optional[bool] = None
    archived: Optional[bool] = None
    target_models: Optional[List[str]] = None
    providers: Optional[List[str]] = None
    purposes: Optional[List[str]] = None
    collection_id: Optional[UUID] = None
    sort: SearchSort = SearchSort.updated_desc
    limit: int = 20
    after: Optional[str] = None


def encode_cursor(row: Tuple[PromptVersionORM, PromptHeaderORM], sort: SearchSort) -> str:
    """Encode a database row into an opaque cursor string.

    The cursor is a base64-encoded JSON payload containing the primary
    sort value and the prompt identifier.  The resulting string may be
    sent back by clients in the ``after`` query parameter to retrieve
    the next page of results.
    """

    header = row[1]
    if sort == SearchSort.created_desc:
        key = header.created_at.isoformat()
    elif sort == SearchSort.title_asc:
        key = header.title
    else:
        key = header.updated_at.isoformat()
    payload = json.dumps({"k": key, "id": str(header.id)})
    return base64.urlsafe_b64encode(payload.encode()).decode()


def decode_cursor(cursor: str) -> Tuple[str, UUID]:
    """Decode a cursor string into its sort key and identifier."""

    raw = base64.urlsafe_b64decode(cursor.encode()).decode()
    data = json.loads(raw)
    return data["k"], UUID(data["id"])


def _apply_after_clause(query: Query, filters: SearchFilters) -> Query:
    """Apply a cursor-based ``after`` filter to the query."""

    if not filters.after:
        return query
    key, pid = decode_cursor(filters.after)
    header = PromptHeaderORM
    if filters.sort == SearchSort.created_desc:
        key_dt = datetime.fromisoformat(key)
        clause = or_(
            header.created_at < key_dt,
            and_(header.created_at == key_dt, header.id < pid),
        )
    elif filters.sort == SearchSort.title_asc:
        clause = or_(
            header.title > key,
            and_(header.title == key, header.id < pid),
        )
    else:
        key_dt = datetime.fromisoformat(key)
        clause = or_(
            header.updated_at < key_dt,
            and_(header.updated_at == key_dt, header.id < pid),
        )
    return query.filter(clause)


def build_query(db: Session, filters: SearchFilters) -> Query:
    """Construct an SQLAlchemy query applying search filters and sorting."""

    latest = (
        db.query(
            PromptVersionORM.prompt_id.label("pid"),
            func.max(PromptVersionORM.version).label("maxv"),
        )
        .group_by(PromptVersionORM.prompt_id)
        .subquery()
    )

    query: Query = (
        db.query(PromptVersionORM, PromptHeaderORM)
        .join(PromptHeaderORM, PromptHeaderORM.id == PromptVersionORM.prompt_id)
        .join(
            latest,
            and_(
                PromptVersionORM.prompt_id == latest.c.pid,
                PromptVersionORM.version == latest.c.maxv,
            ),
        )
        .filter(PromptHeaderORM.owner_id == filters.owner_id)
    )

    if filters.q:
        pattern = f"%{filters.q}%"
        query = query.filter(
            or_(
                PromptHeaderORM.title.ilike(pattern),
                PromptVersionORM.body.ilike(pattern),
            )
        )
    if filters.tags:
        query = query.filter(PromptHeaderORM.tags.op('@>')(filters.tags))
    if filters.favorite is not None:
        query = query.filter(PromptHeaderORM.is_favorite == filters.favorite)
    if filters.archived is not None:
        query = query.filter(PromptHeaderORM.is_archived == filters.archived)
    if filters.target_models:
        query = query.filter(
            PromptVersionORM.target_models.contains(filters.target_models)
        )
    if filters.providers:
        query = query.filter(PromptVersionORM.providers.contains(filters.providers))
    if filters.purposes:
        query = query.filter(PromptVersionORM.use_cases.contains(filters.purposes))
    if filters.collection_id:
        query = query.join(
            CollectionPromptORM,
            CollectionPromptORM.prompt_id == PromptHeaderORM.id,
        ).filter(CollectionPromptORM.collection_id == filters.collection_id)

    query = _apply_after_clause(query, filters)

    if filters.sort == SearchSort.created_desc:
        query = query.order_by(desc(PromptHeaderORM.created_at), desc(PromptHeaderORM.id))
    elif filters.sort == SearchSort.title_asc:
        query = query.order_by(asc(PromptHeaderORM.title), desc(PromptHeaderORM.id))
    else:
        # relevance_desc falls back to updated_at sort without similarity scoring
        query = query.order_by(desc(PromptHeaderORM.updated_at), desc(PromptHeaderORM.id))

    limit = max(1, min(filters.limit, 50))
    return query.limit(limit + 1)
