import uuid
from sqlalchemy import Column, String
from sqlalchemy.dialects.postgresql import UUID as SA_UUID
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class ModelLookupORM(Base):
    __tablename__ = 'models_lookup'
    id = Column(SA_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    value = Column(String, nullable=False, unique=True)

class ToolLookupORM(Base):
    __tablename__ = 'tools_lookup'
    id = Column(SA_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    value = Column(String, nullable=False, unique=True)

class PlatformLookupORM(Base):
    __tablename__ = 'platforms_lookup'
    id = Column(SA_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    value = Column(String, nullable=False, unique=True)

class PurposeLookupORM(Base):
    __tablename__ = 'purposes_lookup'
    id = Column(SA_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    value = Column(String, nullable=False, unique=True)
