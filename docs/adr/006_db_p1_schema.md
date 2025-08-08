# 006 DB P1 schema

## Status
Accepted

## Context
Phase 1 requires a prompt vault that supports owner scoping, versioned content and tagging. Normalising tag and model data was considered but deferred to keep the MVP lean.

## Decision
Adopt a header + version schema. Multi-value fields such as tags and target models remain as text arrays. Reserved columns `block_count`, `embedding` and `icon_url` are added for future features. Trigram indexes enable starter search performance.

## Consequences
* Simple schema that supports CRUD with basic filters.
* Future stories can normalise arrays or leverage pgvector without further structural changes.
