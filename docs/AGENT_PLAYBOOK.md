# Agent Playbook

This document describes how AI agents should interact with this repository and
its associated processes.  Agents are expected to follow these guidelines
when generating product requirements, ADRs, implementation plans, and other
artefacts.

## Responsibilities

1. **Generate specifications**:  Use the templates in `docs/TEMPLATES` to
   produce Product Requirement Documents (PRDs), User Stories, and
   Implementation Plans based on high‑level ideas.  Follow the prompts
   included in `docs/PROMPTS_LIBRARY.md`.
2. **Maintain quality**:  Ensure that any generated code or documentation
   adheres to the linting and type checking requirements.  Run
   `scripts/verify.sh` before opening a pull request.
3. **Document assumptions**:  If information is missing, list your
   assumptions explicitly rather than fabricating details.
4. **Cite sources**:  When reusing assets from external repositories (e.g.
   Daily Joe), include the source path and commit SHA in the PR description
   and CHANGELOG entries.

## Workflow

1. Open a new branch for your work.
2. Generate the required artefacts using the prompts in the prompts library.
3. Commit your changes with conventional commit messages.
4. Submit a PR and ensure all CI checks pass.