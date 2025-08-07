from __future__ import annotations

"""Service helpers for metadata operations."""

from functools import lru_cache
from pathlib import Path
from typing import Dict
import json
import os

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
    config_dir: str | None = os.environ.get("CONFIG_DIR")
    if config_dir is not None:
        config_path: Path = Path(config_dir) / "field_help.json"
    else:
        # Fallback: use a path relative to the current file (up 2 levels to project root, then config/)
        config_path: Path = Path(__file__).resolve().parent.parent.parent / "config" / "field_help.json"
    with config_path.open("r", encoding="utf-8") as f:
        data: Dict[str, str] = json.load(f)
    return FieldHelp(**data)
