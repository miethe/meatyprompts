#!/usr/bin/env bash
# Run the full quality gate locally.  This script is used by CI and should
# also be run by developers before pushing changes.

set -euo pipefail

echo "Running JavaScript/TypeScript linters..."
pnpm -r lint

echo "Running TypeScript type checks..."
pnpm -r typecheck

echo "Running JavaScript/TypeScript tests..."
pnpm -r test -- --ci

echo "Running Python linters and formatters..."
uv run ruff check services/api
uv run black --check services/api

echo "Running Python type checks..."
uv run mypy services/api/app

echo "Running Python tests..."
uv run pytest -q --maxfail=1 --disable-warnings services/api/app/tests