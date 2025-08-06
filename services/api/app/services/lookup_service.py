from sqlalchemy.orm import Session
from ..models.lookup import ModelLookupORM, ToolLookupORM, PlatformLookupORM, PurposeLookupORM
from typing import Type, Union
import uuid

LookupORM = Union[Type[ModelLookupORM], Type[ToolLookupORM], Type[PlatformLookupORM], Type[PurposeLookupORM]]

def get_lookup_table(lookup_type: str) -> LookupORM:
    if lookup_type == "models":
        return ModelLookupORM
    elif lookup_type == "tools":
        return ToolLookupORM
    elif lookup_type == "platforms":
        return PlatformLookupORM
    elif lookup_type == "purposes":
        return PurposeLookupORM
    else:
        raise ValueError(f"Invalid lookup type: {lookup_type}")

async def list_lookup_values(db: Session, lookup_type: str):
    table = get_lookup_table(lookup_type)
    return db.query(table).all()

async def create_lookup_value(db: Session, lookup_type: str, value: str):
    table = get_lookup_table(lookup_type)

    # Check if the value already exists
    existing_value = db.query(table).filter(table.value == value).first()
    if existing_value:
        return existing_value

    new_value = table(id=uuid.uuid4(), value=value)
    db.add(new_value)
    db.commit()
    db.refresh(new_value)
    return new_value
