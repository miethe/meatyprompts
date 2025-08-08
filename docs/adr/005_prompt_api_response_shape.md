# 005 Prompt API response shape

## Status
Accepted

## Context
Prompt endpoints previously returned different shapes across create, list and update operations. This inconsistency made it hard for clients to reuse responses and reason about prompt data.

## Decision
All prompt endpoints now return a fully hydrated `Prompt` model that combines header fields (`title`, `tags`) with the latest version data. A shared mapper in the service layer converts ORM objects into this unified schema.

## Consequences
* API consumers receive a consistent payload regardless of the endpoint.
* Future features such as versioning or duplication can rely on the mapper to keep responses aligned.
