"""Main entrypoint for the FastAPI service."""
from __future__ import annotations

import os
from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware


def create_app() -> FastAPI:
    """Create and configure a FastAPI application."""
    app = FastAPI(
        title=os.environ.get("PROJECT_NAME", "{{ project_name }} API"),
        version=os.environ.get("API_VERSION", "0.1.0"),
    )

    # Allow all origins during development; adjust this for production.
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:3000"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.get("/healthz", tags=["health"])
    async def health() -> dict[str, str]:
        """Simple health check endpoint."""
        return {"status": "ok"}

    from app.api import auth, prompts
    from app.api.endpoints import lookups, metadata, tags
    app.include_router(auth.router)
    app.include_router(prompts.router, prefix="/api/v1")
    app.include_router(lookups.router, prefix="/api/v1/lookups", tags=["lookups"])
    app.include_router(metadata.router, prefix="/api/v1/metadata", tags=["metadata"])
    app.include_router(tags.router, prefix="/api/v1/tags", tags=["tags"])

    from app.api.deps import get_current_user
    from app.models.user import User

    @app.get("/me", response_model=User, tags=["auth"])
    async def read_me(user: User = Depends(get_current_user)) -> User:
        """Return the profile for the current user."""
        return user

    return app


app = create_app()
