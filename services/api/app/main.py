"""Main entrypoint for the FastAPI service."""
from __future__ import annotations

import os
from fastapi import FastAPI
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
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.get("/healthz", tags=["health"])
    async def health() -> dict[str, str]:
        """Simple health check endpoint."""
        return {"status": "ok"}

    return app


app = create_app()