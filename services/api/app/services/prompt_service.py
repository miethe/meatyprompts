"""Service layer for prompt CRUD operations."""

from __future__ import annotations

from datetime import datetime
import logging
import time
import uuid
import re
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


_TAG_RE = re.compile(r"^[a-z0-9._-]{1,32}$")


def _normalize_tags(tags: List[str] | None) -> List[str] | None:
    """Normalize, validate, and deduplicate tag values."""

    if not tags:
        return None
    cleaned: List[str] = []
    for tag in tags:
        norm = tag.strip().lower()
        if not _TAG_RE.fullmatch(norm):
            raise ValueError(
                "Invalid tag: must be 1-32 characters, lowercase letters, digits, dots (.), underscores (_), or hyphens (-) only."
            )
        if norm not in cleaned:
            cleaned.append(norm)
    if len(cleaned) > 20:
        raise ValueError("too many tags (maximum 20 allowed)")
    return cleaned


def _normalize_models(models: List[str] | None) -> List[str] | None:
    """Trim and deduplicate model identifiers with basic validation."""

    if not models:
        return None
    cleaned: List[str] = []
    for model in models:
        norm = model.strip()
        if not (1 <= len(norm) <= 64):
            raise ValueError("invalid target model: must be 1-64 characters")
        if norm not in cleaned:
            cleaned.append(norm)
    if len(cleaned) > 20:
        raise ValueError("too many target models (maximum 20 allowed)")
    return cleaned


def _to_prompt(version: PromptVersionORM, header: PromptHeaderORM) -> Prompt:
    """Hydrate ORM objects into a :class:`Prompt` model."""

    return Prompt(
        id=version.id,
        prompt_id=version.prompt_id,
        owner_id=header.owner_id,
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


def create_prompt(db: Session, prompt: PromptCreate, owner_id: UUID) -> Prompt:
    """Create a new prompt and its initial version."""
    tags = _normalize_tags(prompt.tags)
    models = _normalize_models(prompt.target_models)

    prompt_header = PromptHeaderORM(
        id=uuid.uuid4(),
        owner_id=owner_id,
        title=prompt.title,
        tags=tags,
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
        access_control=prompt.access_control.lower() if prompt.access_control else None,
        target_models=models,
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
        extra={"prompt_id": str(prompt_header.id), "user_id": str(owner_id)},
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


def duplicate_prompt(db: Session, prompt_id: UUID) -> Prompt | None:
    """Create a new version of a prompt by duplicating the latest version."""

    start = time.perf_counter()

    latest_version: PromptVersionORM | None = (
        db.query(PromptVersionORM)
        .filter(PromptVersionORM.prompt_id == prompt_id)
        .order_by(PromptVersionORM.version.desc())
        .first()
    )
    if latest_version is None:
        return None

    header: PromptHeaderORM | None = (
        db.query(PromptHeaderORM)
        .filter(PromptHeaderORM.id == prompt_id)
        .first()
    )
    if header is None:
        return None

    try:
        new_version = str(int(latest_version.version) + 1)
    except ValueError:
        logger.warning(
            "prompts.duplicate.non_numeric_version",
            extra={"prompt_id": str(prompt_id), "version": latest_version.version},
        )
        new_version = "1"

    version_copy = PromptVersionORM(
        id=uuid.uuid4(),
        prompt_id=prompt_id,
        version=new_version,
        body=latest_version.body,
        access_control=latest_version.access_control,
        target_models=latest_version.target_models,
        providers=latest_version.providers,
        integrations=latest_version.integrations,
        use_cases=latest_version.use_cases,
        category=latest_version.category,
        complexity=latest_version.complexity,
        audience=latest_version.audience,
        status=latest_version.status,
        input_schema=latest_version.input_schema,
        output_format=latest_version.output_format,
        llm_parameters=latest_version.llm_parameters,
        success_metrics=latest_version.success_metrics,
        sample_input=latest_version.sample_input,
        sample_output=latest_version.sample_output,
        related_prompt_ids=latest_version.related_prompt_ids,
        link=latest_version.link,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )
    db.add(version_copy)

    base_title = re.sub(r"\s\(v\d+\)$", "", header.title)
    header.title = f"{base_title} (v{new_version})"
    header.updated_at = datetime.utcnow()

    db.commit()
    db.refresh(version_copy)
    db.refresh(header)

    elapsed_ms = (time.perf_counter() - start) * 1000
    logger.info(
        "prompts.duplicate",
        extra={"prompt_id": str(prompt_id), "user_id": "unknown"},
    )
    logger.info(
        "events.prompt_duplicated",
        extra={
            "prompt_id": str(prompt_id),
            "new_version": new_version,
            "elapsed_ms": round(elapsed_ms, 2),
        },
    )
    return _to_prompt(version_copy, header)


def update_prompt(db: Session, prompt_id: UUID, prompt_update: PromptCreate) -> Prompt | None:
    """Update the latest version of a prompt without version bump."""

    start = time.perf_counter()

    latest_version: PromptVersionORM | None = (
        db.query(PromptVersionORM)
        .filter(PromptVersionORM.prompt_id == prompt_id)
        .order_by(PromptVersionORM.version.desc())
        .first()
    )
    if latest_version is None:
        return None

    header = (
        db.query(PromptHeaderORM)
        .filter(PromptHeaderORM.id == prompt_id)
        .first()
    )
    if header is None:
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
            if key == "target_models":
                setattr(latest_version, key, _normalize_models(value))
            else:
                setattr(latest_version, key, value)

    if "tags" in update_data:
        header.tags = _normalize_tags(update_data["tags"])

    latest_version.updated_at = datetime.utcnow()
    header.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(latest_version)
    db.refresh(header)

    elapsed_ms = (time.perf_counter() - start) * 1000
    body_bytes = len((latest_version.body or "").encode("utf-8"))

    logger.info(
        "prompts.update",
        extra={"prompt_id": str(prompt_id), "user_id": "unknown"},
    )
    logger.info(
        "events.prompt_edited",
        extra={
            "prompt_id": str(prompt_id),
            "bytes": body_bytes,
            "elapsed_ms": round(elapsed_ms, 2),
        },
    )
    return _to_prompt(latest_version, header)
