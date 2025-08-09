# AGENTS.md

This document provides instructions for AI agents contributing to the **meatyprompts** repository. Its scope covers the entire repository unless a more specific `AGENTS.md` exists in a subdirectory.

## General Workflow
- Keep the working tree clean. Only commit files that are intentionally changed.
- Use [Conventional Commits](https://www.conventionalcommits.org/) for commit messages.
- Follow any additional `AGENTS.md` files found in subdirectories that contain the files you modify.

## Documentation & Testing
- Any change that alters functionality must include appropriate documentation updates and new or updated unit tests.
- Update relevant files in `docs/` when introducing new features or behavior.
- Before committing, run all applicable programmatic checks:
  - `pre-commit run --files <file1> <file2> ...`
  - `pnpm lint`
  - `pnpm typecheck`
  - `pnpm test`
  - For Python services: `cd services/api && pytest`

## Coding Standards
### Python
- Provide explicit type hints for all function parameters and return values.
- Include comprehensive docstrings using triple quotes.
- Follow [PEP 8](https://peps.python.org/pep-0008/) and project configuration (e.g., Ruff). Avoid inline comments that simply explain code additions or removals; use meaningful comments only when necessary.

### JavaScript / TypeScript
- Use existing linting and formatting rules (ESLint, Prettier) via `pnpm lint`.
- Prefer TypeScript for new modules when possible. Keep comments concise and relevant.

## Pull Requests
- Summaries must describe the rationale for changes and link to relevant documentation when available.
- Include a **Testing** section detailing the commands run and their results.
- Use file citations in summaries and terminal output citations in the testing section when creating the PR message.
