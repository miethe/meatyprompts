# User Story MP-P1-AUTH-001 — **Authentication & `/me` Profile**

> **Epic:** Phase 1 — Manual MVP
> **As a** signed-in creator, **I want** secure sign-in (GitHub OAuth, with optional Magic-Link behind a flag) and a stable `/me` endpoint, **so that** the app can protect private APIs and render user context (avatar/name) across the Vault.

---

## 1) Summary / Narrative

* Deliver **baseline auth** for Phase-1: provider login (GitHub), secure session, logout, and **`GET /me`**.
* Keep it **private-by-default**: all CRUD routes for prompts require an authenticated user.
* Implement a **feature-flagged Magic-Link** flow (email-based) that can ship later without reworking the session model.

---

## 2) Acceptance Criteria

| ID   | Criteria                                                                                                                                         |                                                                                     |
| ---- | ------------------------------------------------------------------------------------------------------------------------------------------------ | ----------------------------------------------------------------------------------- |
| AC-1 | As a visitor, I can **Sign in with GitHub**. On success, I’m redirected into the app with a valid session cookie.                                |                                                                                     |
| AC-2 | As an authenticated user, `GET /me` returns my **id, email, name, avatar\_url, created\_at, last\_login\_at**.                                   |                                                                                     |
| AC-3 | As an authenticated user, protected endpoints (e.g., `/prompts`) **reject** requests without a valid session (401) and **allow** with one (200). |                                                                                     |
| AC-4 | As a user, I can **Sign out**, which clears the session cookie and invalidates the server session.                                               |                                                                                     |
| AC-5 | Security hardening: **httpOnly, Secure, SameSite=Lax** cookies; CSRF protection on state-changing routes; **state/nonce** in OAuth.              |                                                                                     |
| AC-6 | **Audit/telemetry** events: \`auth.login.success                                                                                                 | failure`, `auth.logout`, `auth.signup\`. No PII beyond user\_id & provider in logs. |
| AC-7 | (Flagged) Magic-Link endpoints exist but are **disabled by default** behind `FF_AUTH_MAGIC_LINK`.                                                |                                                                                     |
| AC-8 | Documentation: **ADR-001 (Auth choice)** + **/me contract** + env vars & callback URLs.                                                          |                                                                                     |

---

## 3) Scope / Out of Scope

* **In**: GitHub OAuth, session cookies, `/me`, logout, auth middleware/dependency, DB for users + identities, minimal rate-limits.
* **Flagged**: Magic-Link (email send, token verify); enable later without schema change.
* **Out**: Orgs/RBAC, SSO (Okta/AAD), 2FA, password flows, account settings UI.

---

## 4) Architecture & Implementation

### 4.1 Data Model (Alembic migration)

* **users**

  * `id UUID PK`, `email TEXT UNIQUE NOT NULL`, `name TEXT NULL`, `avatar_url TEXT NULL`,
    `created_at TIMESTAMPTZ NOT NULL DEFAULT now()`, `updated_at TIMESTAMPTZ NOT NULL DEFAULT now()`,
    `last_login_at TIMESTAMPTZ NULL`
* **user\_identities** (OAuth bindings)

  * `id UUID PK`, `user_id UUID FK -> users(id)`, `provider TEXT CHECK IN ('github','magic')`,
    `provider_user_id TEXT`, `access_token_encrypted TEXT NULL`, `refresh_token_encrypted TEXT NULL`, `expires_at TIMESTAMPTZ NULL`,
    `created_at`, `updated_at`
  * Unique index on `(provider, provider_user_id)`
* **sessions** (server-side session registry; optional if using stateless signed cookies)

  * `id UUID PK`, `user_id UUID`, `created_at`, `expires_at`, `revoked_at NULL`, `ip_hash TEXT`, `ua_hash TEXT`
* **magic\_link\_tokens** (only if flag on)

  * `id UUID PK`, `email TEXT`, `token_hash TEXT`, `expires_at`, `consumed_at NULL`

> Note: Add `owner_id UUID FK -> users(id)` to **prompts** tables in MP-P1-DB-002 so auth can **scope data per user**.

### 4.2 Backend (FastAPI)

* **Libraries**: `authlib` (OAuth), `itsdangerous` or `jwcrypto` (cookie signing), `passlib` (hash), `pydantic` models.
* **Env/Config**

  * `AUTH_GITHUB_CLIENT_ID`, `AUTH_GITHUB_CLIENT_SECRET`, `AUTH_COOKIE_NAME`, `AUTH_COOKIE_DOMAIN`, `AUTH_SIGNING_SECRET`, `FF_AUTH_MAGIC_LINK` (bool), mail provider keys (if enabled).
* **Routes**

  * `GET /auth/github/login` → start OAuth (sets `state`, `nonce` in Redis/DB)
  * `GET /auth/github/callback` → exchange code, upsert user + identity, create session, set cookie, redirect to app
  * `POST /auth/logout` → revoke session (delete from sessions or rotate cookie), clear cookie
  * `GET /me` → return current user profile
  * (Flagged) `POST /auth/magic-link` → accepts email, creates token, sends email
  * (Flagged) `GET /auth/magic-link/verify?token=` → verifies, upserts user, creates session, redirect
* **Auth dependency/middleware**

  * `get_current_user()` checks signed cookie → loads session → loads user; raises `HTTPException(401)` if invalid.
  * Decorate/guard **all private routes** (e.g., `/prompts`, `/collections`).
* **Cookies**

  * **httpOnly**, **Secure**, **SameSite=Lax**, **Max-Age** 7d (configurable), domain set via env.
* **CSRF**

  * For state-changing requests (POST/PUT/DELETE), require header `X-CSRF-Token` that matches a non-httpOnly cookie; rotate on login.
* **Rate limits**

  * GitHub login start/callback and magic-link endpoints behind modest limits (e.g., 10/min per IP; 5/hour per email).

### 4.3 Frontend (Web)

* **AuthContext**: holds `user`, loading, error; fetches `GET /me` on app mount; exposes `loginWithGithub()`, `logout()`.
* **UI hooks**

  * If unauthenticated: show **“Sign in with GitHub”** CTA on landing; hide private screens.
  * Show avatar/name in header/sidebar; show **Sign out** in user menu.
* **Guards**

  * `<AuthGuard>` wrapper redirects to sign-in when `user == null`.
* **Callback landing**

  * A lightweight page that shows “Signing you in…” while the backend sets cookie (callback ends with 302 to this page).

### 4.4 Observability & Audit

* Structured logs with event names: `auth.oauth.start`, `auth.oauth.callback`, `auth.login.success`, `auth.login.failure`, `auth.logout`.
* **PII policy**: redact email in logs except in security/audit sink; never log tokens.
* Metrics: login success rate, 401 rate on protected endpoints.

### 4.5 ADRs / Decisions

* **ADR-001: Auth Strategy** — Implement **in-house GitHub OAuth** now (no vendor lock-in), cookie sessions; **Magic-Link behind flag**.

  * Rationale: simple, low-cost, aligns with Phase-1 privacy; can swap to a provider later via adapter.
* **ADR-002: Session Store** — Use **server-side sessions** (DB/Redis) for revocation; cookies store only a signed session id.

---

## 5) API Contracts (initial)

### `GET /me` → 200

```json
{
  "id": "uuid",
  "email": "user@example.com",
  "name": "Ada Lovelace",
  "avatar_url": "https://.../avatar.png",
  "created_at": "2025-08-08T14:03:11Z",
  "last_login_at": "2025-08-08T14:05:22Z"
}
```

### Errors

* `401` on `/me` when no/invalid session.
* `302` redirects during OAuth flows.
* `400/401` on callback if state/nonce invalid.

---

## 6) Non-Functional Requirements

* **Security**: OAuth state/nonce; PKCE (optional for web); cookie hardening; CSRF on mutating routes; email token hashing; secrets from env only.
* **Performance**: `/me` p95 < **100ms** (warm cache); login redirect roundtrip < **3s** p95.
* **Availability**: No auth → no app. Keep auth path isolated; clear fallbacks/UX for provider outages.
* **Compliance**: **noindex** on auth callback and sign-in pages; privacy policy link visible.

---

## 7) Testing Strategy

| Layer            | Tooling                             | Coverage                                                                                          |
| ---------------- | ----------------------------------- | ------------------------------------------------------------------------------------------------- |
| Unit             | pytest (backend), vitest (frontend) | user upsert, identity linkage, cookie signer/validator, `get_current_user` happy/deny paths       |
| Integration      | FastAPI TestClient + httpx          | OAuth callback exchange (mock GitHub), `/me` 200/401, logout revoke, CSRF on POST                 |
| E2E (happy path) | Playwright                          | Login → vault renders; reload persists session; logout clears session; unauthorized routes bounce |
| Security         | pytest                              | CSRF required on POST; cookie flags present; rate limits enforced; token replay rejected          |
| Load (light)     | k6 or Locust                        | `/me` under concurrent load (250 RPS) still p95 < 100ms                                           |

---

## 8) Documentation & DevOps

* **docs/adr/ADR-001-auth.md** — strategy & tradeoffs.
* **docs/api/auth.md** — routes, cookies, CSRF, error codes.
* **Runbook** — rotating secrets, revoking sessions, handling compromised tokens.
* **Env** — sample `.env.example` with all auth keys.
* **CI** — add smoke tests that ensure `/me` returns 401 without cookie and 200 with.

---

## 9) Dependencies & Sequencing

* **Pre-req**: MP-P1-DB-002 migration to add `users`, `user_identities`, optionally `sessions`; add `owner_id` to prompts.
* **Unblocks**: MP-P1-API-003 (protects CRUD), MP-P1-UI-004 (show user context), the rest of Phase-1 private endpoints.

---

## 10) Risks & Mitigations

| Risk                                     | Impact                        | Mitigation                                                                    |
| ---------------------------------------- | ----------------------------- | ----------------------------------------------------------------------------- |
| OAuth callback misconfig (URLs, secrets) | Login fails                   | Add health check & CI validation for env vars; document callback URIs clearly |
| CSRF/cookie misflags                     | Session fixation or rejection | Enforce cookie flags centrally; automate header tests                         |
| Vendor email deliverability (Magic-Link) | Login failures                | Keep feature **off** by default; test in staging; DKIM/SPF docs               |
| Missing `owner_id` on data               | Leaks across users            | Enforce authz via owner scoping in query layer; migration in DB-002           |

---

## 11) Open Questions / Clarifications (TBD)

1. Confirm **callback domains** for **local/staging/prod**.
2. Are we supporting **multi-tenant orgs** in Phase-1 (user belongs to org)? If yes, add `org_id` now.
3. Which **email provider** for Magic-Link (SendGrid/SES/Postmark)?
4. Do we want **PKCE** for the web flow (not required for confidential server, but recommended)?
5. Preferred **session TTL** (7d default) and **idle timeout**?

---

## 12) Definition of Done

* All ACs pass; `/me` stable and documented; CRUD endpoints require auth; cookies & CSRF verified; ADR-001 merged; tests green; staging login demo recorded.

> **Notes aligned with the updated backlog:** This is the **first blocker** for Phase-1, must expose `/me` and **session handling** before wiring UI and protecting `/prompts`. Magic-Link exists but stays **off** behind a feature flag until we’re ready to flip it.
