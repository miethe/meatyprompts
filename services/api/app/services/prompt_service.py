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
        purpose=prompt.purpose if prompt.purpose else None,
        models=prompt.models,
        tools=prompt.tools if prompt.tools else None,
        platforms=prompt.platforms if prompt.platforms else None,
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

def list_prompts(db: Session, model: str = None, tool: str = None, purpose: str = None):
    query = db.query(PromptVersionORM)

    if model:
        query = query.filter(PromptVersionORM.models.any(model))
    if tool:
        query = query.filter(PromptVersionORM.tools.any(tool))
    if purpose:
        query = query.filter(PromptVersionORM.purpose.any(purpose))

    # This is a simplified list function. A real implementation would need to handle
    # fetching only the latest version of each prompt, pagination, etc.
    # For now, it returns all versions matching the filter.
    return query.order_by(PromptVersionORM.created_at.desc()).all()


def update_prompt(db: Session, prompt_id: uuid.UUID, prompt_update: PromptCreate):
    # For this implementation, we'll find the latest version and update it.
    # A more robust versioning system would create a new version.
    latest_version = db.query(PromptVersionORM)\
        .filter(PromptVersionORM.prompt_id == prompt_id)\
        .order_by(PromptVersionORM.version.desc())\
        .first()

    if not latest_version:
        return None

    update_data = prompt_update.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(latest_version, key, value)

    latest_version.created_at = datetime.utcnow() # To reflect the update time
    db.commit()
    db.refresh(latest_version)

    return latest_version
