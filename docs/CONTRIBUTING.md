# Contributing Guide

Thank you for considering a contribution to this template!  This document
outlines the process for submitting changes and best practices to follow.

## Development Workflow

1. **Create a branch**:  Use a descriptive branch name following the pattern
   `type/short-description` (e.g. `feat/add-auth-provider`).  Types should
   align with [Conventional Commits](https://www.conventionalcommits.org):
   `feat`, `fix`, `chore`, `docs`, `test`, etc.
2. **Make your changes**:  Ensure your editor has the configured linters
   enabled.  Run `scripts/verify.sh` locally before committing to catch
   linting, type checking, and testing errors.
3. **Commit messages**:  Write commits according to the Conventional
   Commits specification.  Example:
   ```
   feat: add health check endpoint to API

   Adds `/healthz` route to FastAPI service returning status OK.  Includes
   unit test and documentation updates.
   ```
4. **Open a pull request**:  Use the [PR template](../.github/PULL_REQUEST_TEMPLATE.md).
   Provide context for your changes and link any related issues.
5. **Review process**:  At least one approval is required before merge.  All
   checks must be green (CI, CodeQL, etc.).  Address feedback promptly.

## Local Development

### Prerequisites

* Node.js LTS with [pnpm](https://pnpm.io/) installed globally.
* Python 3.11 or later with [uv](https://github.com/astral-sh/uv) installed.
* [pre‑commit](https://pre-commit.com/) installed to run hooks automatically.

### Setup

Run the following commands in the repository root:

```bash
pnpm -r install       # install JS/TS dependencies
uv sync --project services/api  # install Python dependencies
pre-commit install    # install git hooks
```

See `docs/DEVELOPER_GUIDE.md` for full instructions.