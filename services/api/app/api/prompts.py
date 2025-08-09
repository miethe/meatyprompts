import logging
import uuid
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.prompt import Prompt, PromptCreate, PromptListResponse
from app.services import prompt_service
from app.api.deps import get_current_user, csrf_protect
from app.models.user import UserORM

logger = logging.getLogger(__name__)

router = APIRouter(dependencies=[Depends(get_current_user)])


@router.post(
    "/prompts",
    response_model=Prompt,
    status_code=201,
    dependencies=[Depends(csrf_protect)],
)
def create_new_prompt(
    prompt: PromptCreate,
    db: Session = Depends(get_db),
    current_user: UserORM = Depends(get_current_user),
):
    """Create a new prompt."""

    try:
        return prompt_service.create_prompt(db=db, prompt=prompt, owner_id=current_user.id)
    except Exception as exc:  # pragma: no cover - defensive
        logger.exception("prompts.create failed", exc_info=exc)
        raise HTTPException(status_code=400, detail=str(exc))


@router.get("/prompts", response_model=PromptListResponse)
def get_prompts(
    q: Optional[str] = None,
    tags: Optional[List[str]] = Query(default=None),
    favorite: Optional[bool] = None,
    archived: Optional[bool] = None,
    target_models: Optional[List[str]] = Query(default=None),
    providers: Optional[List[str]] = Query(default=None),
    purposes: Optional[List[str]] = Query(default=None, alias="use_cases"),
    collection_id: Optional[uuid.UUID] = None,
    sort: str = "updated_desc",
    limit: int = 20,
    after: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: UserORM = Depends(get_current_user),
):
    """Search and filter prompts owned by the current user."""

    try:
        return prompt_service.list_prompts(
            db=db,
            owner_id=current_user.id,
            q=q,
            tags=tags,
            favorite=favorite,
            archived=archived,
            target_models=target_models,
            providers=providers,
            purposes=purposes,
            collection_id=collection_id,
            sort=sort,
            limit=limit,
            after=after,
        )
    except Exception as exc:  # pragma: no cover - defensive
        logger.exception("prompts.list failed", exc_info=exc)
        raise HTTPException(status_code=400, detail=str(exc))


@router.get("/prompts/{prompt_id}", response_model=Prompt)
def get_prompt(prompt_id: uuid.UUID, db: Session = Depends(get_db)):
    """Retrieve a prompt by its identifier."""

    prompt_obj = prompt_service.get_prompt_by_id(db=db, prompt_id=prompt_id)
    if prompt_obj is None:
        raise HTTPException(status_code=404, detail="Prompt not found")
    return prompt_obj


@router.put(
    "/prompts/{prompt_id}",
    response_model=Prompt,
    dependencies=[Depends(csrf_protect)],
)
def update_existing_prompt(
    prompt_id: uuid.UUID, prompt: PromptCreate, db: Session = Depends(get_db)
):
    """Update the latest version of a prompt."""

    updated_prompt = prompt_service.update_prompt(
        db=db, prompt_id=prompt_id, prompt_update=prompt
    )
    if updated_prompt is None:
        raise HTTPException(status_code=404, detail="Prompt not found")
    return updated_prompt
