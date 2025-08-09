"""Endpoints for importing and exporting prompts."""
from __future__ import annotations

import uuid
from typing import Union

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, Query
from sqlalchemy.orm import Session

from app.api.deps import csrf_protect, get_current_user
from app.db.session import get_db
from app.models.imex import ImportMapping, ImportPreview, ImportResult
from app.models.user import UserORM
from app.services import import_service, export_service

router = APIRouter(dependencies=[Depends(get_current_user)])


@router.post(
    "/import",
    response_model=Union[ImportPreview, ImportResult],
    dependencies=[Depends(csrf_protect)],
)
async def import_prompts(
    file: UploadFile = File(...),
    mapping: ImportMapping = Depends(),
    dry_run: bool = True,
    db: Session = Depends(get_db),
    current_user: UserORM = Depends(get_current_user),
) -> Union[ImportPreview, ImportResult]:
    """Import prompts from an uploaded CSV or JSON file."""

    content = await file.read()
    try:
        rows = import_service.parse_file(content, file.filename)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    preview, valid_prompts = import_service.apply_mapping(rows, mapping)
    if dry_run:
        valid_count = sum(1 for r in preview if r.valid)
        error_count = len(preview) - valid_count
        return ImportPreview(
            rows=preview[:20], valid_count=valid_count, error_count=error_count
        )
    result = import_service.commit(db, current_user.id, valid_prompts)
    return result


@router.get("/export")
def export_prompts(
    collection_id: uuid.UUID | None = Query(default=None),
    db: Session = Depends(get_db),
    current_user: UserORM = Depends(get_current_user),
):
    """Export prompts owned by the current user as a JSON array."""

    iterator = export_service.iter_prompts(
        db=db, owner_id=current_user.id, collection_id=collection_id
    )
    return export_service.stream_json(iterator)
