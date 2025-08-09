# ADR 001: Authentication Strategy

## Status

Accepted

## Context

The application requires a simple authentication mechanism for the initial MVP.
GitHub OAuth provides a familiar flow for creators while keeping the system
low cost. A basic session cookie is sufficient to track authenticated users.

## Decision

Implement an in-house GitHub OAuth flow that issues a signed session cookie.
Server side session storage is deferred in favour of stateless cookies. A
feature-flagged magic link flow exists but is disabled by default.

## Consequences

* Keeps initial implementation lightweight with minimal dependencies.
* Sessions can be revoked by clearing cookies but full server-side revocation
  is not yet supported.
* Magic link login can be enabled later without changing the session model.
