"""API routes for collection management."""
from __future__ import annotations

import uuid
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Response
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.collection import Collection, CollectionCreate
from app.models.prompt import PromptListResponse
from app.models.user import UserORM
from app.services import collection_service, prompt_service

router = APIRouter(dependencies=[Depends(get_current_user)])


@router.get("/collections", response_model=List[Collection])
def list_collections(
    include: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: UserORM = Depends(get_current_user),
) -> List[Collection]:
    """Return collections owned by the current user."""

    include_count = include == "count"
    return collection_service.list_collections(
        db=db, owner_id=current_user.id, include_count=include_count
    )


@router.post(
    "/collections",
    response_model=Collection,
    status_code=201,
)
def create_collection(
    payload: CollectionCreate,
    db: Session = Depends(get_db),
    current_user: UserORM = Depends(get_current_user),
) -> Collection:
    """Create a new collection."""

    try:
        return collection_service.create_collection(
            db=db, owner_id=current_user.id, name=payload.name
        )
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc))


@router.patch(
    "/collections/{collection_id}",
    response_model=Collection,
)
def rename_collection(
    collection_id: uuid.UUID,
    payload: CollectionCreate,
    db: Session = Depends(get_db),
    current_user: UserORM = Depends(get_current_user),
) -> Collection:
    """Rename an existing collection."""

    try:
        updated = collection_service.rename_collection(
            db=db,
            owner_id=current_user.id,
            collection_id=collection_id,
            name=payload.name,
        )
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc))
    if updated is None:
        raise HTTPException(status_code=404, detail="Collection not found")
    return updated


@router.delete(
    "/collections/{collection_id}",
    status_code=204,
    response_class=Response,
)
def delete_collection(
    collection_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: UserORM = Depends(get_current_user),
) -> Response:
    """Delete a collection."""

    ok = collection_service.delete_collection(
        db=db, owner_id=current_user.id, collection_id=collection_id
    )
    if not ok:
        raise HTTPException(status_code=404, detail="Collection not found")
    return Response(status_code=204)


@router.get(
    "/collections/{collection_id}/prompts",
    response_model=PromptListResponse,
)
def list_collection_prompts(
    collection_id: uuid.UUID,
    limit: int = 20,
    after: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: UserORM = Depends(get_current_user),
) -> PromptListResponse:
    """List prompts within a collection."""

    return prompt_service.list_prompts(
        db=db,
        owner_id=current_user.id,
        collection_id=collection_id,
        limit=limit,
        after=after,
    )


class CollectionPromptPayload(BaseModel):
    """Payload for adding a prompt to a collection."""

    prompt_id: uuid.UUID


@router.post(
    "/collections/{collection_id}/prompts",
)
def add_prompt(
    collection_id: uuid.UUID,
    payload: CollectionPromptPayload,
    db: Session = Depends(get_db),
    current_user: UserORM = Depends(get_current_user),
) -> dict[str, bool]:
    """Add a prompt to a collection."""

    try:
        collection_service.add_prompt(
            db=db,
            owner_id=current_user.id,
            collection_id=collection_id,
            prompt_id=payload.prompt_id,
        )
    except PermissionError:
        raise HTTPException(status_code=403, detail="Forbidden")
    return {"ok": True}


@router.delete(
    "/collections/{collection_id}/prompts/{prompt_id}",
    status_code=204,
    response_class=Response,
)
def remove_prompt(
    collection_id: uuid.UUID,
    prompt_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: UserORM = Depends(get_current_user),
) -> Response:
    """Remove a prompt from a collection."""

    try:
        collection_service.remove_prompt(
            db=db,
            owner_id=current_user.id,
            collection_id=collection_id,
            prompt_id=prompt_id,
        )
    except PermissionError:
        raise HTTPException(status_code=403, detail="Forbidden")
    return Response(status_code=204)
