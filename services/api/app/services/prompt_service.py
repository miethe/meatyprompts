"""Service layer for prompt CRUD operations."""

from datetime import datetime
import uuid
from uuid import UUID
from typing import List

from sqlalchemy.orm import Session, Query

from app.models.prompt import (
    Prompt,
    PromptCreate,
    PromptHeaderORM,
    PromptVersionORM,
)


def _clean_array(values: List[str] | None) -> List[str]:
    """Remove ``None`` values from arrays returned by SQLAlchemy."""

    return [v for v in values or [] if v is not None]


def create_prompt(db: Session, prompt: PromptCreate) -> Prompt:
    """Create a new prompt and its initial version.

    Args:
        db: Active database session.
        prompt: Payload describing the prompt.

    Returns:
        Prompt: Serialized prompt version including header fields.
    """

    prompt_header: PromptHeaderORM = PromptHeaderORM(
        id=uuid.uuid4(),
        title=prompt.title,
        tags=prompt.tags or None,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )
    db.add(prompt_header)
    db.commit()
    db.refresh(prompt_header)

    version_orm: PromptVersionORM = PromptVersionORM(
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

    return Prompt(
        id=version_orm.id,
        prompt_id=version_orm.prompt_id,
        version=version_orm.version,
        title=prompt_header.title,
        body=version_orm.body,
        use_cases=_clean_array(version_orm.use_cases),
        access_control=version_orm.access_control,
        target_models=_clean_array(version_orm.target_models),
        providers=_clean_array(version_orm.providers),
        integrations=_clean_array(version_orm.integrations),
        category=version_orm.category,
        complexity=version_orm.complexity,
        audience=version_orm.audience,
        status=version_orm.status,
        input_schema=version_orm.input_schema,
        output_format=version_orm.output_format,
        llm_parameters=version_orm.llm_parameters,
        success_metrics=version_orm.success_metrics,
        sample_input=version_orm.sample_input,
        sample_output=version_orm.sample_output,
        related_prompt_ids=version_orm.related_prompt_ids,
        link=version_orm.link,
        tags=_clean_array(prompt_header.tags),
        created_at=version_orm.created_at,
        updated_at=version_orm.updated_at,
    )


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

    results: List[Prompt] = []
    orm_objs: List[PromptVersionORM] = query.order_by(PromptVersionORM.created_at.desc()).all()
    prompt_ids = [obj.prompt_id for obj in orm_objs]
    headers: List[PromptHeaderORM] = db.query(PromptHeaderORM).filter(PromptHeaderORM.id.in_(prompt_ids)).all()
    header_map = {header.id: header for header in headers}
    for orm_obj in orm_objs:
        header: PromptHeaderORM | None = header_map.get(orm_obj.prompt_id)
        results.append(
            Prompt(
                id=orm_obj.id,
                prompt_id=orm_obj.prompt_id,
                version=orm_obj.version,
                title=header.title if header else "",
                body=orm_obj.body,
                use_cases=_clean_array(orm_obj.use_cases),
                access_control=orm_obj.access_control,
                target_models=_clean_array(orm_obj.target_models),
                providers=_clean_array(orm_obj.providers),
                integrations=_clean_array(orm_obj.integrations),
                category=orm_obj.category,
                complexity=orm_obj.complexity,
                audience=orm_obj.audience,
                status=orm_obj.status,
                input_schema=orm_obj.input_schema,
                output_format=orm_obj.output_format,
                llm_parameters=orm_obj.llm_parameters,
                success_metrics=orm_obj.success_metrics,
                sample_input=orm_obj.sample_input,
                sample_output=orm_obj.sample_output,
                related_prompt_ids=orm_obj.related_prompt_ids,
                link=orm_obj.link,
                tags=_clean_array(header.tags) if header else [],
                created_at=orm_obj.created_at,
                updated_at=orm_obj.updated_at,
            )
        )

    return results


def update_prompt(db: Session, prompt_id: uuid.UUID, prompt_update: PromptCreate):
    """Update the latest version of a prompt."""

    latest_version: PromptVersionORM | None = (
        db.query(PromptVersionORM)
        .filter(PromptVersionORM.prompt_id == prompt_id)
        .order_by(PromptVersionORM.version.desc())
        .first()
    )

    if not latest_version:
        return None

    update_data = prompt_update.model_dump(exclude_unset=True)
    # Whitelist of allowed fields to update on PromptVersionORM
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

    return latest_version
