from pydantic import BaseModel
from uuid import UUID
from datetime import datetime
from typing import List, Optional
from sqlalchemy import Column, String, TIMESTAMP, ForeignKey, ARRAY
from sqlalchemy.dialects.postgresql import UUID as SA_UUID
from sqlalchemy.ext.declarative import declarative_base
import uuid

Base = declarative_base()

class PromptBase(BaseModel):
    title: str
    purpose: Optional[List[str]] = None
    models: List[str]
    tools: Optional[List[str]] = None
    platforms: Optional[List[str]] = None
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
    purpose: Optional[List[str]] = None
    models: List[str]
    tools: Optional[List[str]] = None
    platforms: Optional[List[str]] = None
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

class PromptHeaderORM(Base):
    __tablename__ = 'prompts'
    id = Column(SA_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    slug = Column(String, nullable=True)
    latest_version_id = Column(SA_UUID(as_uuid=True), nullable=True)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False)
    created_by = Column(SA_UUID(as_uuid=True), nullable=True)

class PromptVersionORM(Base):
    __tablename__ = 'prompt_versions'
    id = Column(SA_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    prompt_id = Column(SA_UUID(as_uuid=True), ForeignKey('prompts.id'), nullable=False)
    version = Column(String, nullable=False)
    title = Column(String, nullable=False)
    purpose = Column(ARRAY(String), nullable=True)
    models = Column(ARRAY(String), nullable=False)
    tools = Column(ARRAY(String), nullable=True)
    platforms = Column(ARRAY(String), nullable=True)
    tags = Column(ARRAY(String), nullable=True)
    body = Column(String, nullable=False)
    visibility = Column(String, nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False)
