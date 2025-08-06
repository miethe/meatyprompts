from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Literal
from pydantic import BaseModel, UUID4
from ...services import lookup_service
from ...db.session import get_db

router = APIRouter()

LookupType = Literal["models", "tools", "platforms", "purposes"]

class LookupValue(BaseModel):
    id: UUID4
    value: str

    class Config:
        orm_mode = True

class CreateLookupValue(BaseModel):
    value: str

@router.get("/{lookup_type}", response_model=List[LookupValue])
async def list_lookups(lookup_type: LookupType, db: Session = Depends(get_db)):
    """
    Get a list of all available lookup values for a given type.
    """
    try:
        return await lookup_service.list_lookup_values(db=db, lookup_type=lookup_type)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/{lookup_type}", response_model=LookupValue)
async def create_lookup(lookup_type: LookupType, payload: CreateLookupValue, db: Session = Depends(get_db)):
    """
    Create a new lookup value. If it already exists, the existing value is returned.
    """
    try:
        return await lookup_service.create_lookup_value(db=db, lookup_type=lookup_type, value=payload.value)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
