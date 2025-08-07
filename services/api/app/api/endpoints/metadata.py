from fastapi import APIRouter, HTTPException
from json import JSONDecodeError

from ...services.metadata_service import get_field_help, FieldHelp

router = APIRouter()


@router.get("/fields", response_model=FieldHelp)
async def field_help() -> FieldHelp:
    """Return tooltip help text for known form fields."""
    try:
        return get_field_help()
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    except JSONDecodeError as exc:
        raise HTTPException(status_code=500, detail=str(exc))
