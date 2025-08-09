import logging
import uuid
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.prompt import Prompt, PromptCreate, PromptListResponse
from app.services import prompt_service
from app.api.deps import get_current_user
from app.models.user import UserORM

logger = logging.getLogger(__name__)

router = APIRouter(dependencies=[Depends(get_current_user)])


@router.post(
    "/prompts",
    response_model=Prompt,
    status_code=201,
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
    q: Optional[str] = Query(
        default=None, description="Full-text search applied to titles and bodies"
    ),
    tags: Optional[List[str]] = Query(
        default=None, description="Filter results to prompts tagged with any of these values"
    ),
    favorite: Optional[bool] = Query(
        default=None, description="If true, only return prompts marked as favorites"
    ),
    archived: Optional[bool] = Query(
        default=None, description="If true, only return prompts that have been archived"
    ),
    target_models: Optional[List[str]] = Query(
        default=None, description="Restrict prompts to those targeting the given LLM models"
    ),
    providers: Optional[List[str]] = Query(
        default=None, description="Restrict prompts to those from the specified model providers"
    ),
    purposes: Optional[List[str]] = Query(
        default=None,
        alias="use_cases",
        description="Filter by declared use cases for the prompt",
    ),
    collection_id: Optional[uuid.UUID] = Query(
        default=None, description="Limit results to a specific collection"
    ),
    sort: str = Query(
        default="updated_desc",
        description="Sort order for returned prompts (e.g., updated_desc)",
    ),
    limit: int = Query(
        default=20,
        ge=1,
        le=100,
        description="Maximum number of prompts to return per page",
    ),
    after: Optional[str] = Query(
        default=None,
        description=(
            "Cursor for pagination. Use the `next_cursor` value from a previous "
            "response to retrieve subsequent pages."
        ),
    ),
    db: Session = Depends(get_db),
    current_user: UserORM = Depends(get_current_user),
):
    """Search and filter prompts owned by the current user.

    Parameters
    ----------
    q:
        Full-text search term applied to prompt titles and bodies.
    tags:
        One or more tag names to filter by.
    favorite:
        When true, only return prompts marked as favorites.
    archived:
        When true, return only prompts that have been archived.
    target_models:
        Restrict prompts to those targeting the provided LLM model identifiers.
    providers:
        Restrict prompts to those originating from the given model providers.
    purposes:
        Filter by declared use cases for the prompt.
    collection_id:
        Limit results to prompts within the specified collection.
    sort:
        Sort order for returned prompts (e.g., ``updated_desc``).
    limit:
        Maximum number of prompts to return per page.
    after:
        Cursor for pagination. Pass the ``next_cursor`` value from a previous
        response to continue listing prompts.

    Returns
    -------
    PromptListResponse
        A paginated list of prompts matching the query.
    """

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


@router.post(
    "/prompts/{prompt_id}/duplicate",
    response_model=Prompt,
    status_code=201,
)
def duplicate_prompt(prompt_id: uuid.UUID, db: Session = Depends(get_db)):
    """Duplicate an existing prompt by creating a new version."""

    new_prompt = prompt_service.duplicate_prompt(db=db, prompt_id=prompt_id)
    if new_prompt is None:
        raise HTTPException(status_code=404, detail="Prompt not found")
    return new_prompt
