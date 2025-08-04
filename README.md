# Template Factory – React Native & FastAPI Monorepo

This repository serves as a **template** for bootstrapping new mobile and web applications using **React Native (Expo managed)** and **FastAPI**.  It provides an opinionated monorepo structure, tooling, and documentation to help teams get started quickly with reproducible, high‑quality setups.

## Features

* **Monorepo layout** with separate app folders for mobile (Expo) and optional web (Next.js) alongside a Python service.
* **Copier‑based scaffolding** to instantiate a new project with customised variables (project name, bundle identifiers, database, etc.).
* **Preconfigured tooling**: pnpm workspaces, TypeScript strict mode, ESLint + Prettier, Jest, Detox stubs, uv + ruff + black + mypy, pytest, pre‑commit hooks, and GitHub Actions workflows for continuous integration.
* **Security and quality** gates: Dependabot, CodeQL, secret scanning, and branch protections enforced by default (when hosted on GitHub).
* **Comprehensive documentation**: architecture rationale, contributing guide, developer setup, agent playbook, prompts library, security policy, governance process, and templates for ADRs, PRDs, user stories, and implementation plans.

## Quick Start

1. **Use this template:** click **Use this template** on GitHub to create a new repository from it (or clone this repo if working locally).
2. **Run scaffold script:** execute `scripts/scaffold.sh` (or `copier copy`) and answer the prompts (project name, bundle ID, database, etc.).  This will generate a new project folder with your custom values.
3. **Install dependencies:**
   ```bash
   # Install JavaScript packages
   pnpm -r install
   # Install Python dependencies for the API service
   uv sync --project services/api
   ```
4. **Start development:**
   ```bash
   # Mobile app
   pnpm --filter "./apps/mobile" start
   # API server
   uv run --project services/api uvicorn app.main:app --reload
   ```

Refer to `docs/DEVELOPER_GUIDE.md` for detailed environment setup and commands.

## License

This template is provided under the terms of the [MIT License](LICENSE).  See the `LICENSE` file for details.