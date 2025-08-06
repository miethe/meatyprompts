from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.models.prompt import Prompt, PromptCreate
from app.db.session import get_db
from app.services import prompt_service
from typing import List, Optional
import uuid

router = APIRouter()

@router.post("/prompts", response_model=Prompt, status_code=201)
def create_new_prompt(prompt: PromptCreate, db: Session = Depends(get_db)):
    try:
        return prompt_service.create_prompt(db=db, prompt=prompt)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/prompts", response_model=List[Prompt])
def get_prompts(
    model: Optional[str] = None,
    provider: Optional[str] = None,
    use_case: Optional[str] = None,
    db: Session = Depends(get_db),
):
    try:
        return prompt_service.list_prompts(
            db=db, model=model, provider=provider, use_case=use_case
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.put("/prompts/{prompt_id}", response_model=Prompt)
def update_existing_prompt(prompt_id: uuid.UUID, prompt: PromptCreate, db: Session = Depends(get_db)):
    updated_prompt = prompt_service.update_prompt(db=db, prompt_id=prompt_id, prompt_update=prompt)
    if updated_prompt is None:
        raise HTTPException(status_code=404, detail="Prompt not found")
    return updated_prompt
