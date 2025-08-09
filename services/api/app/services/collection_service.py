"""Service layer for collection management."""
from __future__ import annotations

import logging
import uuid
from datetime import datetime
from typing import List
from uuid import UUID

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.collection import (
    Collection,
    CollectionORM,
    CollectionPromptORM,
)
from app.models.prompt import PromptHeaderORM

logger = logging.getLogger(__name__)


def list_collections(db: Session, owner_id: UUID, include_count: bool = False) -> List[Collection]:
    """Return collections owned by ``owner_id``."""

    query = (
        db.query(CollectionORM)
        .filter(CollectionORM.owner_id == owner_id)
        .order_by(CollectionORM.name.asc())
    )
    rows = query.all()
    results: List[Collection] = []
    if include_count:
        for row in rows:
            count = (
                db.query(func.count(CollectionPromptORM.prompt_id))
                .filter(CollectionPromptORM.collection_id == row.id)
                .scalar()
            )
            results.append(
                Collection.from_orm(row).model_copy(update={"count": int(count)})
            )
    else:
        results = [Collection.from_orm(r) for r in rows]
    logger.info(
        "collections.list", extra={"user_id": str(owner_id), "count": len(results)}
    )
    return results


def create_collection(db: Session, owner_id: UUID, name: str) -> Collection:
    """Create a new collection ensuring name uniqueness per owner."""

    existing = (
        db.query(CollectionORM)
        .filter(CollectionORM.owner_id == owner_id, CollectionORM.name == name)
        .first()
    )
    if existing:
        raise ValueError("collection name already exists")
    obj = CollectionORM(
        id=uuid.uuid4(),
        owner_id=owner_id,
        name=name.strip(),
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )
    db.add(obj)
    db.commit()
    db.refresh(obj)
    logger.info(
        "collections.create", extra={"user_id": str(owner_id), "collection_id": str(obj.id)}
    )
    return Collection.from_orm(obj)


def rename_collection(
    db: Session, owner_id: UUID, collection_id: UUID, name: str
) -> Collection | None:
    """Rename an existing collection."""

    obj = (
        db.query(CollectionORM)
        .filter(CollectionORM.id == collection_id, CollectionORM.owner_id == owner_id)
        .first()
    )
    if obj is None:
        return None
    conflict = (
        db.query(CollectionORM)
        .filter(
            CollectionORM.owner_id == owner_id,
            CollectionORM.name == name,
            CollectionORM.id != collection_id,
        )
        .first()
    )
    if conflict:
        raise ValueError("collection name already exists")
    obj.name = name.strip()
    obj.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(obj)
    logger.info(
        "collections.rename", extra={"user_id": str(owner_id), "collection_id": str(obj.id)}
    )
    return Collection.from_orm(obj)


def delete_collection(db: Session, owner_id: UUID, collection_id: UUID) -> bool:
    """Delete a collection owned by ``owner_id``."""

    obj = (
        db.query(CollectionORM)
        .filter(CollectionORM.id == collection_id, CollectionORM.owner_id == owner_id)
        .first()
    )
    if obj is None:
        return False
    db.delete(obj)
    db.commit()
    logger.info(
        "collections.delete", extra={"user_id": str(owner_id), "collection_id": str(collection_id)}
    )
    return True


def add_prompt(db: Session, owner_id: UUID, collection_id: UUID, prompt_id: UUID) -> None:
    """Add ``prompt_id`` to ``collection_id`` verifying ownership."""

    collection = (
        db.query(CollectionORM)
        .filter(CollectionORM.id == collection_id, CollectionORM.owner_id == owner_id)
        .first()
    )
    prompt = (
        db.query(PromptHeaderORM)
        .filter(PromptHeaderORM.id == prompt_id, PromptHeaderORM.owner_id == owner_id)
        .first()
    )
    if not collection or not prompt:
        raise PermissionError("forbidden")
    existing = (
        db.query(CollectionPromptORM)
        .filter(
            CollectionPromptORM.collection_id == collection_id,
            CollectionPromptORM.prompt_id == prompt_id,
        )
        .first()
    )
    if existing is None:
        db.add(
            CollectionPromptORM(
                collection_id=collection_id,
                prompt_id=prompt_id,
            )
        )
        db.commit()
    logger.info(
        "collections.add_prompt",
        extra={
            "user_id": str(owner_id),
            "collection_id": str(collection_id),
            "prompt_id": str(prompt_id),
        },
    )


def remove_prompt(db: Session, owner_id: UUID, collection_id: UUID, prompt_id: UUID) -> None:
    """Remove ``prompt_id`` from ``collection_id`` verifying ownership."""

    collection = (
        db.query(CollectionORM)
        .filter(CollectionORM.id == collection_id, CollectionORM.owner_id == owner_id)
        .first()
    )
    prompt = (
        db.query(PromptHeaderORM)
        .filter(PromptHeaderORM.id == prompt_id, PromptHeaderORM.owner_id == owner_id)
        .first()
    )
    if not collection or not prompt:
        raise PermissionError("forbidden")
    link = (
        db.query(CollectionPromptORM)
        .filter(
            CollectionPromptORM.collection_id == collection_id,
            CollectionPromptORM.prompt_id == prompt_id,
        )
        .first()
    )
    if link:
        db.delete(link)
        db.commit()
    logger.info(
        "collections.remove_prompt",
        extra={
            "user_id": str(owner_id),
            "collection_id": str(collection_id),
            "prompt_id": str(prompt_id),
        },
    )
