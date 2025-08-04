# Developer Guide

This guide explains how to set up your environment, run the apps locally, and
debug common issues.

## Environment Setup

### JavaScript/TypeScript

Install [pnpm](https://pnpm.io/) (v8 or newer) globally.  Then install
dependencies for all JS/TS packages:

```bash
pnpm -r install
```

### Python

Install [uv](https://github.com/astral-sh/uv) using pip:

```bash
pip install uv
```

Then install dependencies for the API service:

```bash
uv sync --project services/api
```

### Pre‑Commit Hooks

Install pre‑commit and set up git hooks:

```bash
pip install pre-commit
pre-commit install
```

## Running the Applications

### Mobile App

```bash
cd apps/mobile
pnpm start
```

This will launch the Expo development server.  Follow the prompts in the
terminal to run on iOS or Android simulators or physical devices.

### API Server

```bash
cd services/api
uv run uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`.  Interactive docs are at
`/docs` (Swagger) and `/redoc` (ReDoc).

### Web App (Optional)

If you enabled the `use_web` option when scaffolding, you can run the Next.js
app as follows:

```bash
cd apps/web
pnpm dev
```

The web app will be available at `http://localhost:3000`.

## Testing

* **Unit tests (JS/TS)**: `pnpm -r test`
* **Unit tests (Python)**: `uv run pytest -q services/api/app/tests`

## Debugging Tips

* If dependency installation fails, ensure the correct versions of Node.js and
  Python are installed.  Delete `node_modules` and retry `pnpm install`.
* Use `scripts/verify.sh` to run all quality checks in one command.
* For Expo, install the Expo Go app on your device or use a simulator for
  faster iteration.