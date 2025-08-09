"""API endpoints for tag suggestions."""
from __future__ import annotations

from typing import List, Optional
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ...db.session import get_db
from ...services import tags_service
from ...models.tag import TagCount

router = APIRouter()


@router.get("", response_model=List[TagCount])
async def list_tags(
    limit: int = 20,
    query: Optional[str] = None,
    db: Session = Depends(get_db),
) -> List[TagCount]:
    """Return tag suggestions based on existing prompts."""
    return tags_service.top_tags(db=db, limit=limit, query=query)
