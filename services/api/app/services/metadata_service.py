from __future__ import annotations

"""Service helpers for metadata operations."""

from functools import lru_cache
from pathlib import Path
from typing import Dict
import json

from pydantic import BaseModel


class FieldHelp(BaseModel):
    """Mapping of field names to help text shown as tooltips."""

    target_models: str
    providers: str
    integrations: str


@lru_cache
def get_field_help() -> FieldHelp:
    """Load tooltip help text for form fields from the configuration file.

    Returns:
        FieldHelp: An object containing help text for each supported field.

    Raises:
        FileNotFoundError: If the configuration file does not exist.
        json.JSONDecodeError: If the configuration file contains invalid JSON.
    """
    base_dir = Path(__file__).resolve().parents[4]
    config_path = base_dir / "config" / "field_help.json"
    with config_path.open("r", encoding="utf-8") as f:
        data: Dict[str, str] = json.load(f)
    return FieldHelp(**data)
