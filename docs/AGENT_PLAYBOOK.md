# Agent Playbook

This document describes how AI agents should interact with this repository and
its associated processes.  Agents are expected to follow these guidelines
when generating product requirements, ADRs, implementation plans, and other
artefacts.

## Responsibilities

Agents contributing to this template should adhere to the following
principles (inspired by the Daily Joe agent guide【380388811125184†L82-L91】):

1. **Spec‑first**:  Always request a clear specification before generating
   code or documentation.  Use the templates in `docs/TEMPLATES` to produce
   PRDs, user stories, implementation plans, and ADRs.  Follow the prompts
   in `docs/PROMPTS_LIBRARY.md`.
2. **Modular & Idempotent**:  Keep code modular (e.g. use repository and
   service layers) and ensure operations are idempotent wherever possible.
3. **Structured logging & error handling**:  Include structured logs and
   robust error handling in generated code.
4. **Test coverage**:  Provide unit tests for new features and verify
   that all CI checks pass by running `scripts/verify.sh` locally.
5. **Secret hygiene**:  Never hard‑code secrets.  Use environment variables
   and document how to configure them.
6. **Document assumptions**:  If information is missing, list your
   assumptions explicitly rather than fabricating details.
7. **Cite sources**:  When reusing assets from external repositories
   (e.g. Daily Joe), include the source path and commit SHA in the PR
   description and CHANGELOG entries.

## Workflow

1. Open a new branch for your work.
2. Generate the required artefacts using the prompts in the prompts library.
3. Commit your changes with conventional commit messages.
4. Submit a PR and ensure all CI checks pass.