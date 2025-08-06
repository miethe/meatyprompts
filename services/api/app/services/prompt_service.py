from sqlalchemy.orm import Session
from app.models.prompt import PromptCreate, PromptHeaderORM, PromptVersion, PromptVersionORM
import uuid
from datetime import datetime

def create_prompt(db: Session, prompt: PromptCreate):
    # Create the prompt header
    prompt_header = PromptHeaderORM(
        id=uuid.uuid4(),
        created_by=None, # TODO: Add user ID when auth is implemented
        created_at=datetime.utcnow(),
    )
    db.add(prompt_header)
    db.commit()
    db.refresh(prompt_header)

    # Create the first prompt version
    prompt_version_orm = PromptVersionORM(
        id=uuid.uuid4(),
        prompt_id=prompt_header.id,
        version=1,
        title=prompt.title,
        purpose=prompt.purpose,
        models=prompt.models,
        tools=prompt.tools if prompt.tools else None,
        tags=prompt.tags if prompt.tags else None,
        body=prompt.body,
        visibility=prompt.visibility,
        created_at=datetime.utcnow(),
    )
    db.add(prompt_version_orm)
    db.commit()
    db.refresh(prompt_version_orm)

    # Update the prompt header with the latest version
    prompt_header.latest_version_id = prompt_version_orm.id
    db.commit()

    # Return Pydantic model for serialization
    return PromptVersion(
        id=prompt_version_orm.id,
        prompt_id=prompt_version_orm.prompt_id,
        version=prompt_version_orm.version,
        title=prompt_version_orm.title,
        purpose=prompt_version_orm.purpose,
        models=prompt_version_orm.models,
        tools=prompt_version_orm.tools if prompt_version_orm.tools else [],
        tags=prompt_version_orm.tags if prompt_version_orm.tags else [],
        body=prompt_version_orm.body,
        visibility=prompt_version_orm.visibility,
        created_at=prompt_version_orm.created_at,
    )
