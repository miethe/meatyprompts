# MeatyPrompts: Project Overview

## Introduction

MeatyPrompts is a sophisticated SaaS platform designed to streamline the entire lifecycle of prompt engineering. Our mission is to *make world-class prompt-crafting as simple, repeatable, and measurable as spell-check.*

The application provides a centralized **Prompt Vault** for individuals and teams to create, version, test, and organize prompts. The core workflow begins with a manual but powerful UI and progressively integrates AI-assisted generation, a "Model-Aware" engine that adapts prompts to specific LLMs, and a robust analytics suite to measure prompt effectiveness via our North-Star metric: **Prompt Success Rate (PSR)**.

This document serves as the primary technical guide to the project's architecture, development workflows, and core conventions.

## Table of Contents

- [MeatyPrompts: Project Overview](#meatyprompts-project-overview)
  - [Introduction](#introduction)
  - [Table of Contents](#table-of-contents)
  - [Project Structure](#project-structure)
  - [Backend Architecture](#backend-architecture)
    - [Core Backend Technologies](#core-backend-technologies)
    - [Request Lifecycle](#request-lifecycle)
    - [Service Layer and Domain Organization](#service-layer-and-domain-organization)
    - [Backend Directory-Specific Structures](#backend-directory-specific-structures)
    - [Common Python File Archetypes in Backend](#common-python-file-archetypes-in-backend)
    - [AI Integration: The Model Adapter \& Prompt Engine](#ai-integration-the-model-adapter--prompt-engine)
    - [Database Migrations](#database-migrations)
  - [Frontend Architecture](#frontend-architecture)
    - [Core Frontend Technologies](#core-frontend-technologies)
    - [Component-Based Architecture](#component-based-architecture)
    - [Interacting with the Backend API](#interacting-with-the-backend-api)
    - [State Management](#state-management)
  - [Typical Development Workflow](#typical-development-workflow)
    - [Making Additions](#making-additions)
      - [Adding Backend Features](#adding-backend-features)
      - [Adding Frontend Views](#adding-frontend-views)
  - [Adding New Features (End-to-End Example)](#adding-new-features-end-to-end-example)
    - [1. Backend Changes](#1-backend-changes)
    - [2. Frontend Changes](#2-frontend-changes)
    - [3. Testing](#3-testing)
  - [Testing](#testing)
    - [Backend Testing](#backend-testing)
    - [Frontend Testing](#frontend-testing)
  - [Development Setup](#development-setup)
    - [Prerequisites](#prerequisites)
    - [Initial Setup Steps](#initial-setup-steps)
    - [Running the Application with Docker Compose](#running-the-application-with-docker-compose)
  - [Deployment](#deployment)
    - [Backend Deployment](#backend-deployment)
    - [Frontend Deployment](#frontend-deployment)
    - [CI/CD](#cicd)
  - [Contributing Guidelines](#contributing-guidelines)
  - [Further Reading](#further-reading)

## Project Structure

The project is a monorepo managed with `pnpm` workspaces to facilitate code sharing between the web and mobile frontends.

```graphql
/ (repo root)
├── apps/
│   ├── web/            # Next.js web application
│   └── mobile/         # React Native mobile application
├── services/
│   └── api/            # FastAPI backend, including Celery worker and DB logic
├── packages/
│   ├── ui/             # Shared React components for web and mobile
│   └── ts-config/      # Shared TypeScript configurations
├── docs/               # Project documentation (ADRs, guides, etc.)
├── makefile            # Convenience commands for development
└── ...                 # Root configurations (pnpm, turbo, prettier, etc.)
```

- `/apps/web`: The primary user-facing web application built with **Next.js**.
- `/apps/mobile`: The **React Native** mobile application for on-the-go access.
- `/services/api`: The core **FastAPI** backend, which handles all business logic, data persistence, and AI integrations.
- `/packages/ui`: A shared library of React components styled with Tailwind CSS/NativeWind, used by both `web` and `mobile` apps for a consistent look and feel.
- `/docs`: All project documentation, including this overview, Architectural Decision Records (ADRs), feature guides, and more.

## Backend Architecture

The backend (`services/api`) is a modern Python application built with FastAPI, designed for performance, scalability, and maintainability.

### Core Backend Technologies

- **FastAPI**: A high-performance web framework for building APIs with standard Python type hints. It handles routing, validation, and serialization.
- **SQLAlchemy**: The core ORM for all database interactions. Models are defined in `services/api/core/models.py`.
- **Alembic**: Manages database schema migrations, ensuring changes are version-controlled and repeatable.
- **Pydantic**: Used extensively by FastAPI for data validation and by the application for defining clear data contracts (schemas).
- **Celery & Redis**: The asynchronous task queue for handling background jobs like embedding generation for semantic search or running batch analytics.
- **PostgreSQL**: Our primary relational database.
- **pgvector**: A PostgreSQL extension for vector similarity search, used for features like "find similar prompts."

### Request Lifecycle

1. A request from a client (web or mobile app) hits the FastAPI application.
2. FastAPI routes the request to the appropriate endpoint function in `/services/api/api/v1/endpoints/`.
3. The endpoint uses FastAPI's dependency injection to acquire necessary dependencies, such as a database session (`db: Session`) and an instance of the relevant service class (e.g., `PromptService`).
4. The endpoint calls a method on the service class to execute business logic.
5. The service orchestrates operations, calling repository methods (`PromptRepository`) to interact with the database.
6. The repository executes SQLAlchemy queries to fetch or persist data.
7. The result is returned up the chain, and FastAPI serializes the response (typically a Pydantic model) into JSON.

### Service Layer and Domain Organization

- **`services/api/services/`**: This directory contains the core business logic. Each service (e.g., `PromptService`, `CollectionService`) orchestrates data access and business rules, acting as a bridge between the API layer and the data layer.
- **Domain-Specific Directories** (e.g., `services/api/prompts/`, `services/api/collections/`): These directories primarily contain the Pydantic schemas (`schemas.py`) that define the data contracts for a specific feature or domain. This keeps the data definitions organized and co-located with the feature they represent.
- **`services/api/repositories/`**: This is the data access layer. Repositories (e.g., `PromptRepository`) contain the raw SQLAlchemy query logic, abstracting database interactions away from the services.

### Backend Directory-Specific Structures

- `services/api/api/`: FastAPI application setup and endpoint definitions, versioned under `v1/`.
- `services/api/core/`: Shared components: `config.py` (settings), `database.py` (DB session management), `models.py` (SQLAlchemy ORM models).
- `services/api/ai/`: Home of the AI integration logic, including the `ModelAdapter` and `PromptEngine`.
  - `prompt_registry/`: YAML files defining standard prompt templates.
- `services/api/worker/`: Celery application setup and task definitions (`tasks.py`).
- `services/api/alembic/`: Database migration scripts.
- `services/api/tests/`: `pytest` unit and integration tests, mirroring the application structure.

### Common Python File Archetypes in Backend

- **API Endpoint Files** (`api/v1/endpoints/*.py`): Define `APIRouter`s, handle HTTP logic, and depend on services.
- **Service Files** (`services/*.py`): Classes that contain business logic, orchestrating repositories.
- **Repository Files** (`repositories/*.py`): Classes that implement direct database interaction using SQLAlchemy.
- **Schema Files** (`prompts/schemas.py`, etc.): Define Pydantic models for API request/response validation.
- **Model Files** (`core/models.py`): Define SQLAlchemy ORM classes that map to database tables.

### AI Integration: The Model Adapter & Prompt Engine

Our key differentiator is our intelligent approach to AI interaction, housed in `services/api/ai/`.

- **Model Adapter**: This is a core component responsible for translating a generic prompt instruction into the specific format and parameter set required by a target LLM (e.g., OpenAI vs. Anthropic vs. Gemini). It uses a system of configuration files and strategy classes to remain extensible.
- **Prompt Engine**: This service uses the `ModelAdapter` to perform its functions. In its initial form, it helps scaffold new prompts. In its advanced form, it will execute prompts against different models and analyze the results.
- **Prompt Registry**: A version-controlled collection of high-quality prompt templates stored in `ai/prompt_registry/`, used to seed the "Genesis Prompt Pack" for new users and for AI-assisted generation.

### Database Migrations

Database schema changes are managed via Alembic.

- To generate a new migration: `make backend-makemigrations msg="your message"`
- To apply migrations: `make backend-migrate`

## Frontend Architecture

The frontend consists of a web app (`apps/web`) and a mobile app (`apps/mobile`), both built on modern JavaScript principles.

### Core Frontend Technologies

- **React**: The foundational UI library.
- **Next.js (Web)**: A React framework providing Server-Side Rendering (SSR), static site generation, and a robust routing system for the web app.
- **React Native (Mobile)**: For building a truly native mobile application from a shared React codebase.
- **TypeScript**: Ensures type safety across the entire frontend stack.
- **Tailwind CSS / NativeWind**: Provides a consistent, utility-first styling system across both web and mobile platforms via the shared `packages/ui` library.
- **React Query (TanStack Query)**: For managing server state, caching, and data fetching.

### Component-Based Architecture

The UI is composed of reusable components located in `packages/ui`. This ensures visual and functional consistency between the web and mobile apps while maximizing code reuse. Larger, screen-level components reside within their respective `apps/` directory.

### Interacting with the Backend API

A dedicated API client service in the frontend abstracts all HTTP requests to the backend. This service uses `React Query` to handle caching, re-fetching, and optimistic updates, providing a smooth and responsive user experience.

### State Management

- **Server State**: Managed almost exclusively by `React Query`.
- **Global UI State**: Managed by React Context for cross-cutting concerns like authentication status and the current theme.
- **Local Component State**: Managed with standard React hooks like `useState` and `useReducer`.

## Typical Development Workflow

1. Start the entire stack: `make dev-up`.
2. Run backend tests while developing: `make backend-test`.
3. Before committing, lint and format code using `make backend-lint` and `make backend-format`.

### Making Additions

#### Adding Backend Features

1. **Define Schema**: Create/update Pydantic models in the relevant domain directory (e.g., `services/api/prompts/schemas.py`).
2. **Update Model (if needed)**: Modify `core/models.py` and generate an Alembic migration.
3. **Implement Repository**: Add data access logic in `repositories/`.
4. **Implement Service**: Add business logic in `services/`.
5. **Expose API Route**: Add the endpoint in `api/v1/endpoints/`.
6. **Write Tests**: Add unit and integration tests in `tests/`.

#### Adding Frontend Views

1. **Update API Client**: Add a new function in the API service to call the new backend endpoint.
2. **Create Components**: Build reusable UI elements in `packages/ui` or page-specific components in `apps/web/components/`.
3. **Create Page**: Assemble components into a new page in `apps/web/pages/` (or using the App Router).
4. **Write Tests**: Add component and integration tests.

## Adding New Features (End-to-End Example)

Let's illustrate the workflow by adding a **"Collections"** feature, allowing users to group prompts together.

### 1. Backend Changes

- **Database Models (`core/models.py`):**
  - Create a `Collection` model (`id`, `name`, `description`, `owner_id`).
  - Create a `prompt_collections` many-to-many join table (`prompt_id`, `collection_id`).
- **Alembic Migration:**
  - Run `make backend-makemigrations msg="add collections feature"` to generate the migration script. Apply it with `make backend-migrate`.
- **Pydantic Schemas (`services/api/collections/schemas.py`):**
  - Define `CollectionCreate`, `CollectionUpdate`, and `CollectionRead` schemas.
- **Repository (`services/api/repositories/collection_repository.py`):**
  - Create `CollectionRepository` with methods like `create`, `get_by_id`, `add_prompt_to_collection`, etc.
- **Service (`services/api/services/collection_service.py`):**
  - Create `CollectionService` to orchestrate repository calls and handle business logic (e.g., checking ownership before allowing a prompt to be added).
- **API Endpoints (`services/api/api/v1/endpoints/collections.py`):**
  - Create a new router for `/collections` with `POST`, `GET`, `PUT`, `DELETE` endpoints, as well as an endpoint for adding/removing prompts from a collection.

### 2. Frontend Changes

- **API Client (`apps/web/services/apiClient.ts`):**
  - Add functions like `createCollection(data)`, `getCollections()`, `addPromptToCollection(collectionId, promptId)`.
- **UI Components (`packages/ui/`):**
  - Create a `CollectionCard.tsx` component.
  - Create a `CollectionModal.tsx` for creating/editing collections.
- **Vault Page (`apps/web/pages/vault.tsx`):**
  - Add a UI element (e.g., a sidebar or filter dropdown) to list the user's collections.
  - Allow users to filter the prompt list by the selected collection.
  - Add a "Add to Collection" option in the menu for each prompt card.

### 3. Testing

- **Backend**: Add `pytest` tests for the `CollectionService`, `CollectionRepository`, and the new API endpoints.
- **Frontend**: Add React Testing Library tests for the new components and user flows.

## Testing

### Backend Testing

- **Framework**: `pytest`.
- **Location**: `services/api/tests/`. The structure mirrors the main application.
- **Database**: Tests run against a dedicated test database, created and torn down automatically, to ensure isolation.
- **Execution**: `make backend-test`

### Frontend Testing

- **Frameworks**: `Vitest`/`Jest` for running tests, and `React Testing Library` for rendering and interacting with components.
- **Location**: Tests are co-located with the code they test (e.g., `MyComponent.test.tsx` alongside `MyComponent.tsx`).
- **Execution**: `pnpm test` from within the `apps/web` or `apps/mobile` directory.

## Development Setup

### Prerequisites

- Docker & Docker Compose
- Node.js (LTS version) & `pnpm`
- Python 3.12+ (optional, for running backend commands outside Docker)

### Initial Setup Steps

1. Clone the repository.
2. Configure environment variables by copying `.env.example` to `.env` in `services/api` and `apps/web`.
3. Fill in the required values (database credentials, auth provider keys, etc.).

### Running the Application with Docker Compose

The simplest way to run the entire stack for local development.

1. **Start all services**:

    ```bash
    make dev-up
    ```

2. **Access services**:
    - **Web App**: `http://localhost:3000`
    - **Backend API Docs**: `http://localhost:8000/docs`
3. **Stop all services**:

    ```bash
    make dev-down
    ```

## Deployment

### Backend Deployment

- **Platform**: The backend (API and Celery worker) is containerized with Docker and designed for deployment on platforms like Fly.io or Google Cloud Run.
- **Process**: Deployments are automated via GitHub Actions. On a push to the `main` branch, a new Docker image is built and pushed to a container registry, and the cloud provider is instructed to deploy the new version.
- **Secrets**: All secrets are managed through the hosting provider's secret management system.

### Frontend Deployment

- **Platform**: The Next.js web app is deployed to a platform optimized for it, such as Vercel or Netlify.
- **Process**: Vercel/Netlify is connected to our GitHub repository, automatically deploying every push to `main` to production and creating preview deployments for every pull request.

### CI/CD

Continuous Integration and Deployment are managed by **GitHub Actions**. The workflow (`.github/workflows/ci.yml`) runs linters, type checkers, tests, and builds for all pushes and pull requests.

## Contributing Guidelines

Please adhere to the established architectural patterns and code styles. All new features must be accompanied by tests. Pull requests must pass all CI checks before being considered for merging.

## Further Reading

- [ADR-001: Authentication Strategy](docs/architecture/ADRs/ADR-001-Authentication.md)
- [Feature Guide: Prompt Blocks DSL](docs/guides/features/prompt-blocks.md)
- [Data Guide: Core Schemas and Data Flow](docs/guides/data/README.md)
