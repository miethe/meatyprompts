# Governance

This document defines the roles, responsibilities, and decision‑making
processes for maintaining this template.

## Roles

| Role             | Responsibilities                                    |
|------------------|-----------------------------------------------------|
| Maintainer       | Oversees the project, reviews PRs, and merges them. |
| Contributor      | Submits issues and PRs following the guidelines.     |
| Security Team    | Handles vulnerability reports and disclosures.       |

## Decision Process

* Minor changes (docs, small fixes) may be approved and merged by a single
  maintainer.
* Major changes (architecture, tooling) require consensus from at least two
  maintainers and, if applicable, an ADR documenting the decision.

## Release Process

We follow [Semantic Versioning](https://semver.org/).  Releases are cut
following these steps:

1. Merge all changes intended for the release into `main`.
2. Update `CHANGELOG.md` using `scripts/release-notes.sh`.
3. Create a git tag (e.g. `v0.1.0`) and push it.
4. Publish a GitHub release with the changelog notes.