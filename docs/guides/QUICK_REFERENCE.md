# MeatyPrompts: Quick Reference Guide

This guide provides a high-level orientation for the MeatyPrompts codebase and a quick reference for common development tasks. For a complete technical and architectural summary, read the [PROJECT_OVERVIEW.md](PROJECT_OVERVIEW.md) first.

## Repository Layout

The project is a monorepo managed with `pnpm` workspaces.

```graphql
/ (repo root)
├── apps/
│   ├── web/            # Next.js web application
│   └── mobile/         # React Native mobile application
├── services/
│   └── api/            # FastAPI backend services and background worker
├── packages/
│   ├── ui/             # Shared React components
│   └── ts-config/      # Shared TypeScript configurations
├── docs/               # Documentation (ADRs, guides, etc.)
├── makefile            # Convenience commands for development
└── ...                 # Root configurations
```

## Backend Structure (`services/api/`)

- **api** – FastAPI application entry point. Versioned routes live under `api/v1/endpoints`.
- **core** – Shared models (`models.py`), database setup (`database.py`), and configuration (`config.py`).
- **ai** – The core AI logic, including the `ModelAdapter` and `PromptEngine`.
  - `prompt_registry/` – Version-controlled YAML prompt templates.
- **prompts**, **collections** – Feature-specific modules, primarily containing Pydantic schemas (`schemas.py`).
- **services** – Business logic layer, orchestrating repositories and other components.
- **repositories** – Data access layer using SQLAlchemy models from `core/models.py`.
- **worker** – Celery app and tasks for background jobs.
- **tests** – `pytest` unit and integration tests mirroring the application structure.

### Services vs. Domain-Specific Packages

The `services/` directory contains high-level business logic. Each service coordinates repositories and other components to fulfill a feature's requirements. Domain-specific directories like `prompts/` or `collections/` primarily define the Pydantic schemas that represent the data contracts for that domain.

**Guideline:** New workflow logic that calls repositories or interacts with external systems belongs in a service in the `services/` directory. New data definitions (API request/response shapes) belong in a `schemas.py` file within the appropriate domain directory (e.g., `prompts/schemas.py`).

## Frontend Structure (`apps/web/`)

- **src/app** – Top-level pages and layouts (using Next.js App Router).
- **src/components** – Page-specific, non-reusable components.
- **src/services** – API client functions for interacting with the backend.
- **src/hooks** – Custom React hooks used across components.
- **src/lib** – General utility functions.
- **packages/ui** – **Primary location for shared, reusable components** used by both `web` and `mobile` apps.

## Typical Development Workflow

1. Start all services with `make dev-up` (requires Docker).
2. Run backend tests while developing features via `make backend-test`.
3. Lint and format with `make backend-lint` and `make backend-format` before committing.
4. Run frontend tests via `pnpm test` from within the `apps/web` directory.

## Adding Backend Features

1. **Define Schemas** – Create or extend Pydantic models under the relevant domain directory (e.g., `services/api/prompts/schemas.py`).
2. **Update Database Model** – If needed, modify `services/api/core/models.py` and run `make backend-makemigrations`.
3. **Implement Repository Logic** – Add methods in a repository module within `services/api/repositories/`.
4. **Create/Update a Service** – Place business logic in `services/api/services/` and inject the necessary repositories.
5. **Expose API Routes** – Add a router in `services/api/api/v1/endpoints/`.
6. **Write Tests** – Add unit and API tests under `services/api/tests/`.

## Adding Frontend Views

1. **Update API Client** – If the backend exposes a new route, add a corresponding function in `apps/web/src/services/`.
2. **Build Shared Components** – Create reusable UI elements in `packages/ui/`.
3. **Assemble Page** – Create a new page in `apps/web/src/app/` using shared and page-specific components.
4. **Create Hooks/Context** – If necessary, create custom hooks or context providers for state management.
5. **Write Tests** – Add tests co-located with the new components and pages.

## AI Integration: Model Adapter & Prompt Engine

The core AI logic lives in `services/api/ai/`.

- **Model Adapter**: A key component that translates a generic instruction into the specific syntax and parameters required by a target LLM (e.g., OpenAI vs. Claude). It is designed to be extensible.
- **Prompt Engine**: The service that uses the Model Adapter to perform tasks like scaffolding new prompts from templates or executing them against a chosen model.
- To add a new AI feature, you will likely interact with the `PromptEngine` from a higher-level service.

## Python File Archetypes

- **API endpoint modules** (`api/v1/endpoints/*.py`):
  - Import FastAPI components, Pydantic schemas, and the relevant service.
  - Define an `APIRouter` and use `Depends` to inject services.
  - Define route handlers that call service methods and return Pydantic models.
- **Service modules** (`services/*.py`):
  - Import repository classes and other services.
  - Define a service class with injected dependencies in its `__init__`.
  - Methods contain the core business logic and orchestrate data access.
- **Repository modules** (`repositories/*.py`):
  - Import SQLAlchemy models from `core/models.py` and `Session` from `sqlalchemy.orm`.
  - Implement classes with methods that perform direct database queries.
  - Methods typically return SQLAlchemy ORM model instances to the service layer.
- **Schema modules** (e.g., `prompts/schemas.py`):
  - Import `BaseModel` from `pydantic`.
  - Define data contracts for API validation and serialization. Use separate classes for create, update, and read operations.

## Testing and CI

The project relies on `pytest` for backend testing and `Vitest`/`Jest` for frontend testing. New functionality must include tests. All CI checks on a pull request must pass before it can be merged.

```bash
# Run all backend tests
make backend-test
```

## Further Reading

- [Project Overview](PROJECT_OVERVIEW.md)
- [ADR-001: Authentication Strategy](architecture/ADRs/ADR-001-Authentication.md)
- [Data Guide: Core Schemas and Data Flow](guides/data/README.md)
