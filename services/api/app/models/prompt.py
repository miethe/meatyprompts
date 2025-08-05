from pydantic import BaseModel
from uuid import UUID
from datetime import datetime
from typing import List, Optional

class PromptBase(BaseModel):
    title: str
    purpose: Optional[str] = None
    models: List[str]
    tools: Optional[List[str]] = None
    tags: Optional[List[str]] = None
    body: str
    visibility: str = 'private'

class PromptCreate(PromptBase):
    pass

class Prompt(PromptBase):
    id: UUID
    version: int
    created_at: datetime
    prompt_id: UUID

    class Config:
        orm_mode = True

class PromptVersion(BaseModel):
    id: UUID
    prompt_id: UUID
    version: int
    title: str
    purpose: Optional[str] = None
    models: List[str]
    tools: Optional[List[str]] = None
    tags: Optional[List[str]] = None
    body: str
    visibility: str
    created_at: datetime

    class Config:
        orm_mode = True

class PromptHeader(BaseModel):
    id: UUID
    slug: Optional[str] = None
    latest_version_id: Optional[UUID] = None
    created_at: datetime
    created_by: Optional[UUID] = None

    class Config:
        orm_mode = True
