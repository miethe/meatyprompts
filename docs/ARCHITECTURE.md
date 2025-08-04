# Architecture

This document provides an overview of the template's structure and the
rationale behind key design choices.  It should be kept up to date as the
template evolves.

## Monorepo Layout

The repository is organised into three primary top‑level areas:

| Path                 | Purpose                                                |
|----------------------|--------------------------------------------------------|
| `apps/mobile`        | Expo managed React Native application.                |
| `apps/web`           | Optional Next.js application (disabled by default).    |
| `services/api`       | FastAPI backend service with SQLAlchemy and Alembic.   |
| `packages/ui`        | Shared UI components for mobile and web.              |
| `scripts`            | Utilities for bootstrapping, scaffolding and testing. |
| `docs`               | Documentation suite and templates.                    |

### Mobile Application

The mobile app is built with **Expo Managed Workflow**.  It uses TypeScript,
strict linting and type checking, and includes a basic navigation setup in
`src/app`.  Tests are written with Jest and React Testing Library; a Detox stub
is provided for future end‑to‑end testing.

### Web Application

The optional web app uses **Next.js** with the App Router and is disabled by
default via the `use_web` Copier variable.  If enabled, it shares UI
components from `packages/ui` and uses Playwright (stub) for end‑to‑end tests.

### API Service

The FastAPI service is a Python project managed by **uv** with PEP 621
metadata in `pyproject.toml`.  It follows modern best practices: strict
type checking via `mypy`, linting via `ruff` and formatting via `black`.
SQLAlchemy 2.x models live under `app/db`, and API routes live under `app/api`.
Unit and integration tests use `pytest` and `httpx`.

## Dependency Management

JavaScript/TypeScript dependencies are managed via **pnpm workspaces** at the
repo root.  Python dependencies are locked by **uv** (see `uv.lock`).  This
approach ensures reproducible builds across environments.

## Continuous Integration

GitHub Actions workflows in `.github/workflows` run linters, type checkers, and
tests for both JS/TS and Python code.  CodeQL and Dependabot are enabled by
default (when hosted on GitHub) to ensure security and dependency updates.