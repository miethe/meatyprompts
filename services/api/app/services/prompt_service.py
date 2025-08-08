"""Service layer for prompt CRUD operations."""

from __future__ import annotations

from datetime import datetime
import logging
import uuid
from typing import List
from uuid import UUID

from sqlalchemy.orm import Query, Session

from app.models.prompt import (
    Prompt,
    PromptCreate,
    PromptHeaderORM,
    PromptVersionORM,
)

logger = logging.getLogger(__name__)


def _clean_array(values: List[str] | None) -> List[str]:
    """Remove ``None`` values from arrays returned by SQLAlchemy."""

    return [v for v in values or [] if v is not None]


def _to_prompt(version: PromptVersionORM, header: PromptHeaderORM) -> Prompt:
    """Hydrate ORM objects into a :class:`Prompt` model."""

    return Prompt(
        id=version.id,
        prompt_id=version.prompt_id,
        version=version.version,
        title=header.title,
        body=version.body,
        use_cases=_clean_array(version.use_cases),
        access_control=version.access_control,
        target_models=_clean_array(version.target_models),
        providers=_clean_array(version.providers),
        integrations=_clean_array(version.integrations),
        category=version.category,
        complexity=version.complexity,
        audience=version.audience,
        status=version.status,
        input_schema=version.input_schema,
        output_format=version.output_format,
        llm_parameters=version.llm_parameters,
        success_metrics=version.success_metrics,
        sample_input=version.sample_input,
        sample_output=version.sample_output,
        related_prompt_ids=version.related_prompt_ids,
        link=version.link,
        tags=_clean_array(header.tags),
        created_at=version.created_at,
        updated_at=version.updated_at,
    )


def create_prompt(db: Session, prompt: PromptCreate) -> Prompt:
    """Create a new prompt and its initial version."""

    prompt_header = PromptHeaderORM(
        id=uuid.uuid4(),
        title=prompt.title,
        tags=prompt.tags or None,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )
    db.add(prompt_header)
    db.commit()
    db.refresh(prompt_header)

    version_orm = PromptVersionORM(
        id=uuid.uuid4(),
        prompt_id=prompt_header.id,
        version="1",
        body=prompt.body,
        description=None,
        access_control=prompt.access_control,
        target_models=prompt.target_models or None,
        providers=prompt.providers or None,
        integrations=prompt.integrations or None,
        use_cases=prompt.use_cases,
        category=prompt.category,
        complexity=prompt.complexity,
        audience=prompt.audience,
        status=prompt.status,
        input_schema=prompt.input_schema,
        output_format=prompt.output_format,
        llm_parameters=prompt.llm_parameters,
        success_metrics=prompt.success_metrics,
        sample_input=prompt.sample_input,
        sample_output=prompt.sample_output,
        related_prompt_ids=prompt.related_prompt_ids or None,
        link=prompt.link,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )
    db.add(version_orm)
    db.commit()
    db.refresh(version_orm)

    logger.info(
        "prompts.create",
        extra={"prompt_id": str(prompt_header.id), "user_id": "unknown"},
    )
    return _to_prompt(version_orm, prompt_header)


def list_prompts(
    db: Session,
    model: str | None = None,
    provider: str | None = None,
    use_case: str | None = None,
) -> List[Prompt]:
    """List prompts applying optional filters."""

    query: Query[PromptVersionORM] = db.query(PromptVersionORM).join(PromptHeaderORM)

    if model:
        query = query.filter(PromptVersionORM.target_models.any(model))
    if provider:
        query = query.filter(PromptVersionORM.providers.any(provider))
    if use_case:
        query = query.filter(PromptVersionORM.use_cases.any(use_case))

    orm_objs: List[PromptVersionORM] = (
        query.order_by(PromptVersionORM.created_at.desc()).all()
    )
    prompt_ids = [obj.prompt_id for obj in orm_objs]
    headers: List[PromptHeaderORM] = (
        db.query(PromptHeaderORM).filter(PromptHeaderORM.id.in_(prompt_ids)).all()
    )
    header_map = {header.id: header for header in headers}

    logger.info("prompts.list", extra={"user_id": "unknown"})

    return [
        _to_prompt(orm_obj, header_map[orm_obj.prompt_id])
        for orm_obj in orm_objs
        if orm_obj.prompt_id in header_map
    ]


def get_prompt_by_id(db: Session, prompt_id: UUID) -> Prompt | None:
    """Return the latest version of a prompt by its identifier."""

    version = (
        db.query(PromptVersionORM)
        .filter(PromptVersionORM.prompt_id == prompt_id)
        .order_by(PromptVersionORM.version.desc())
        .first()
    )
    if version is None:
        return None

    header = (
        db.query(PromptHeaderORM)
        .filter(PromptHeaderORM.id == prompt_id)
        .first()
    )
    if header is None:
        return None

    logger.info(
        "prompts.get", extra={"prompt_id": str(prompt_id), "user_id": "unknown"}
    )
    return _to_prompt(version, header)


def update_prompt(db: Session, prompt_id: UUID, prompt_update: PromptCreate) -> Prompt | None:
    """Update the latest version of a prompt without version bump."""

    latest_version: PromptVersionORM | None = (
        db.query(PromptVersionORM)
        .filter(PromptVersionORM.prompt_id == prompt_id)
        .order_by(PromptVersionORM.version.desc())
        .first()
    )
    if latest_version is None:
        return None

    update_data = prompt_update.model_dump(exclude_unset=True)
    allowed_fields = {
        "body",
        "use_cases",
        "access_control",
        "target_models",
        "providers",
        "integrations",
        "category",
        "complexity",
        "audience",
        "status",
        "input_schema",
        "output_format",
        "llm_parameters",
        "success_metrics",
        "sample_input",
        "sample_output",
        "related_prompt_ids",
        "link",
    }

    for key, value in update_data.items():
        if key in allowed_fields:
            setattr(latest_version, key, value)

    latest_version.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(latest_version)

    header = (
        db.query(PromptHeaderORM)
        .filter(PromptHeaderORM.id == prompt_id)
        .first()
    )
    if header is None:
        return None

    logger.info(
        "prompts.update",
        extra={"prompt_id": str(prompt_id), "user_id": "unknown"},
    )
    return _to_prompt(latest_version, header)

