"""Tests for OpenAPI documentation of the prompts endpoint."""

import os

os.environ.setdefault("DATABASE_URL", "sqlite://")
os.environ.setdefault("AUTH_SIGNING_SECRET", "secret")
os.environ.setdefault("GITHUB_CLIENT_ID", "dummy")
os.environ.setdefault("GITHUB_CLIENT_SECRET", "dummy")

from app.main import app


def test_prompts_pagination_documented() -> None:
    """The OpenAPI schema documents cursor based pagination."""
    schema = app.openapi()
    params = {
        p["name"]: p for p in schema["paths"]["/api/v1/prompts"]["get"]["parameters"]
    }
    after_param = params["after"]
    assert "cursor" in after_param["description"].lower()

    properties = schema["components"]["schemas"]["PromptListResponse"]["properties"]
    next_cursor = properties["next_cursor"]
    assert "cursor" in next_cursor["description"].lower()
