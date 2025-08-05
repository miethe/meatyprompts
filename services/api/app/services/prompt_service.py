from sqlalchemy.orm import Session
from app.models.prompt import PromptCreate, PromptHeader, PromptVersion
import uuid

def create_prompt(db: Session, prompt: PromptCreate):
    # Create the prompt header
    prompt_header = PromptHeader(
        id=uuid.uuid4(),
        created_by=None, # TODO: Add user ID when auth is implemented
    )
    db.add(prompt_header)
    db.commit()
    db.refresh(prompt_header)

    # Create the first prompt version
    prompt_version = PromptVersion(
        id=uuid.uuid4(),
        prompt_id=prompt_header.id,
        version=1,
        **prompt.dict()
    )
    db.add(prompt_version)
    db.commit()
    db.refresh(prompt_version)

    # Update the prompt header with the latest version
    prompt_header.latest_version_id = prompt_version.id
    db.commit()

    return prompt_version
