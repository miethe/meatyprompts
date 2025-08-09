# User Story MP-P1-SHARE-012 — **Unlisted Share (Feature-Flag)**

> **Epic:** Phase 1 — Manual MVP
> **As an** owner of a prompt, **I want** to generate a **revocable, unlisted, read-only** link for a prompt, **so that** I can share it with collaborators without exposing my whole vault or requiring auth.&#x20;

---

## 1 · Narrative

*When the feature flag is ON,* the owner can create a **tokenized share link** for a single prompt. The public page shows **title, body, tags** in read-only mode, is **noindex** for robots, and can be **revoked** at any time. This ships in P1 behind a flag to de-risk rollout and keep scope contained. &#x20;

---

## 2 · Acceptance Criteria

| #    | Behaviour                                                                                                                     | Measure / Test                                                                                   |
| ---- | ----------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------ |
| AC-1 | If **Share flag** enabled, Prompt Detail and Card actions include a **“Create share link”** control.                          | UI renders control only when flag is true; unit test toggles flag and asserts presence/absence.  |
| AC-2 | Creating a link returns a **unique tokenized URL**; clicking it shows a **public read-only page** with **title, body, tags**. | API returns token; E2E opens `/s/{token}` and asserts read-only render.                          |
| AC-3 | Owner can **revoke** an existing link; public page becomes **410 Gone** thereafter.                                           | E2E: revoke → GET `/s/{token}` returns 410.                                                      |
| AC-4 | **Robots**: shared page emits `<meta name="robots" content="noindex">`.                                                       | SSR test snapshots markup for `noindex`.                                                         |
| AC-5 | **Security**: No auth needed to view the shared page; **only owner** can create/revoke; token unguessable.                    | API tests: 401 for unauthenticated create/revoke; 403 for non-owner; public GET succeeds.        |
| AC-6 | **Telemetry**: `share_created`, `share_viewed`, `share_revoked` events recorded (counts only, no body).                       | Unit test asserts event emission; payloads exclude content.                                      |
| AC-7 | **NFRs**: p95 public page render <200ms; availability ≥99.5%.                                                                 | Perf smoke and uptime check.                                                                     |

---

## 3 · Context & Dependencies

* **Depends on**

  * **Auth baseline** (sessions + `/me`) for owner checks.&#x20;
  * **DB baseline**: prompts + versions already exist. &#x20;
  * **Feature-flag framework** (ADR-004) before SHARE story. &#x20;
* **Forward hooks / future**

  * Freeze-to-version option (share a specific version vs. “latest”).
  * Team/shared collections (later) may add scoped sharing.

---

## 4 · Architecture & Implementation Details

## 4.1 Database & Schema (Alembic)

Add a minimal table for tokenized links. The PRD/plan already envisions **`share_tokens`** at the system level.&#x20;

**Table: `share_tokens`**

* `id UUID PK`
* `owner_id UUID NOT NULL` (FK → users.id)
* `prompt_id UUID NOT NULL` (FK → prompts.id)
* `version STRING NULL` (optional; null means “latest”)
* `token TEXT UNIQUE NOT NULL` (>=128-bit entropy)
* `created_at TIMESTAMPTZ DEFAULT now()`
* `revoked_at TIMESTAMPTZ NULL`
* **Indexes:** `(token)` unique; `(prompt_id, revoked_at)`; `(owner_id, created_at DESC)`

> Notes
> • P1 shares **latest** version; `version` kept for future “freeze” option.
> • Prompts split header/version fields; `access_control` stays on version; sharing bypasses private access via tokenized GET only.&#x20;

## 4.2 API Endpoints (FastAPI)

**File:** `api/routes/share.py` (new)

* `POST /prompts/{prompt_id}/share` → `{ url, token, created_at }`
  *Auth required (owner).* Creates (or rotates) a token.
* `DELETE /share/{token}` → `204`
  *Auth required (owner).* Sets `revoked_at` (soft-delete).
* `GET /s/{token}` → **Public** read-only prompt payload for render (SSR/SPA). Returns `410` if revoked.

**Prompt payload on public GET:**
`{ title, body, tags, version, updated_at }` (subset only; no internal IDs, no governance internals). Source data comes from existing models/joins used by list/hydrate.&#x20;

**Security / Privacy**

* Token verification performed server-side; if `revoked_at` set → 410.
* No CORS credentialed calls; rate limit GET by IP.
* Robots **`noindex`** explicitly set by page.&#x20;

## 4.3 Backend Services

**`share_service.py` (new)**

* `create_share(owner_id, prompt_id, freeze_version: bool=False) -> ShareToken`
* `revoke_share(owner_id, token) -> None`
* `resolve_token(token) -> PublicPrompt | None` (enforces revoked\_at)

Re-use prompt hydration to fetch **latest** version when `version IS NULL`; ensure **header + version** join matches the existing list path.&#x20;

## 4.4 Frontend (Next.js + shadcn)

* **PromptDetailModal**: add **Share** button in footer (beside Edit/Close). Click → creates token and shows copyable URL. (Appears only under flag.)&#x20;
* **PromptCard**: overflow menu → “Share” (optional for P1).
* **Public page**: `pages/s/[token].tsx`

  * SSR or CSR fetch from `GET /s/{token}`.
  * Render **title/body/tags** in read-only layout; show “This is a shared, view-only prompt” banner.
  * `<meta name="robots" content="noindex" />`.&#x20;
* **State**: TanStack Query keys `['share', prompt_id]` for create/revoke; optimistic toast.

## 4.5 Observability & Flags

* **Flag**: `features.share` default **off** in prod; **on** in staging. ADR-004 will record defaults.&#x20;
* **Telemetry events** (client send):
  `share_created {prompt_id}`, `share_viewed {token_hash}`, `share_revoked {prompt_id}`. Counts only; **never** include prompt body.&#x20;
* **Tracing**: `share.create`, `share.resolve`, `share.revoke`; include `{prompt_id, owner_id?}` on private spans.

---

## 5 · Non-Functional Requirements

* **Performance**: public page p95 < 200ms; search budgets unchanged.&#x20;
* **Security/Privacy**: HTTPS, CSRF on private routes, row-level checks; **private by default**; warning on share creation; **noindex** on shared pages.&#x20;
* **Availability**: 99.5% MVP target; degrade gracefully if telemetry sink down.&#x20;
* **Accessibility**: read-only page meets WCAG 2.1 AA.&#x20;

---

## 6 · Testing Strategy

| Layer             | Tooling            | Coverage                                                                                                                                    |
| ----------------- | ------------------ | ------------------------------------------------------------------------------------------------------------------------------------------- |
| Unit (BE)         | pytest             | token generation entropy & uniqueness; revoke sets `revoked_at`; resolve returns latest version when `version NULL`.                        |
| Integration (API) | FastAPI TestClient | `POST /prompts/{id}/share` → 201 (owner only); `GET /s/{token}` → 200 with minimal payload; `DELETE /share/{token}` → 204 then `GET` → 410. |
| Unit (FE)         | Jest + RTL         | Share control hidden when flag off; on create shows URL; copy button puts URL on clipboard.                                                 |
| E2E               | Cypress            | Create share → open public URL shows title/body/tags → revoke → public URL 410.                                                             |
| A11y/SEO          | axe + snapshot     | Public page has no interactive editors; `<meta robots="noindex">` present.                                                                  |
| Perf              | Lighthouse         | TTI < 2s; minimal JS on public page.                                                                                                        |

---

## 7 · Documentation & Artifacts

| File / Location                       | Update / Create                                                                           |
| ------------------------------------- | ----------------------------------------------------------------------------------------- |
| `docs/adr/004_feature_flags_share.md` | Default state, rollout plan, kill-switch.                                                 |
| `docs/api.md`                         | Add `POST /prompts/{id}/share`, `GET /s/{token}`, `DELETE /share/{token}` with examples.  |
| `docs/data-model.md`                  | ERD: `share_tokens` + relationships.                                                      |
| `docs/guides/sharing.md`              | UX guide: create, copy, revoke; security notes (`noindex`).                               |
| `docs/runbooks/feature_flags.md`      | Rollout and rollback SOP.                                                                 |

---

## 8 · Risks & Mitigations

| Risk                                    | Impact             | Mitigation                                                                                       |
| --------------------------------------- | ------------------ | ------------------------------------------------------------------------------------------------ |
| Token leakage outside intended audience | Unwanted access    | Clear **warning** on creation; easy revoke; rotate token on re-enable; `noindex`.                |
| Sharing stale vs. latest content        | Confusion          | P1 documents “latest” behaviour; add **freeze-to-version** option later (uses `version` column). |
| Accidental discoverability              | SEO exposure       | `noindex` meta + no internal links; long random tokens.                                          |
| Flag misconfiguration                   | Premature exposure | Feature flag default OFF in prod; runbook for toggling; CI gating with env checks.               |

---

## 9 · Implementation Tasks (Dev-Ready)

**DB**

* [ ] Alembic migration for `share_tokens` (schema above) + downgrade.

**Backend**

* [ ] `share_service.py`: create/revoke/resolve.
* [ ] `api/routes/share.py`: POST/DELETE/GET endpoints.
* [ ] Extend OpenAPI; add rate-limit config for public GET.

**Frontend**

* [ ] Add Share button (flag-gated) to **PromptDetailModal** footer; modal shows URL + “Revoke link”.&#x20;
* [ ] `pages/s/[token].tsx` read-only public page with `noindex`.
* [ ] Telemetry calls for create/view/revoke.

**QA / Observability**

* [ ] Tests per Section 6; Sentry breadcrumb on resolve; traces added.

---

## 10 · Open Questions

1. P1 default flag state in prod? (Recommend **OFF**; enable per-tenant for design partners.)&#x20;
2. Should creating a new token **rotate** (invalidate previous) or allow multiple active tokens? (Recommend **single active** per prompt.)
3. Public page shows **only** title/body/tags—do we also show version badge? (Useful; low risk.)

---

# Definition of Done

* Feature flag in place; owner can **create** and **revoke** share links; **public read-only** page works; **noindex** is present.&#x20;
* Security and NFR budgets satisfied; telemetry events recorded; docs & ADR merged.
