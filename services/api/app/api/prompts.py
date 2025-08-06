from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.models.prompt import Prompt, PromptCreate
from app.db.session import get_db
from app.services.prompt_service import create_prompt

router = APIRouter()

@router.post("/prompts", response_model=Prompt, status_code=201)
def create_new_prompt(prompt: PromptCreate, db: Session = Depends(get_db)):
    try:
        return create_prompt(db=db, prompt=prompt)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
