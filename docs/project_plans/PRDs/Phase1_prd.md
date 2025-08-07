# PRD — Phase 1: Manual MVP (MeatyPrompts)

## 1) Summary

**Goal:** Ship a lovable MVP that makes it fast and pleasant to **create, organize, and reuse prompts manually**, with just enough polish and opinionated UX to stick.
**Outcome:** Creators can sign in, add/edit prompts with a markdown editor, tag and search them, copy to clipboard, and manage a small personal vault. Limited “future-ready” scaffolding (API shape, schema hooks) ensures rapid evolution into AI-assisted and execution features next phase.

---

## 2) Problem & Objectives

### Problems to solve now

* Prompt sprawl: Users lose track of “that good prompt,” wasting time and tokens.
* Friction to reuse: Copy/paste workflows are clunky; no quick view/copy behavior.
* Zero structure: No consistent tags, models, or fields that help sort and filter.

### Phase 1 Objectives (what “good” looks like)

1. **Prompt capture that feels great**: quick create, rich editing, keyboard-first.
2. **Findability**: tags + fast text search; sensible default sorting.
3. **Reusability**: copy-to-clipboard variants; easy duplication/version bump.
4. **Trust & continuity**: auth, stable schema, and migration path to later phases.
5. **Shareability (limited)**: optional unlisted view-only link (feature-flag) to test virality.

**North-star metric (Phase 1):** ≥60% of weekly active users create or update ≥3 prompts/week and reuse (copy) at least one.

---

## 3) In-Scope (Phase 1)

* **Auth**: Email magic link + GitHub OAuth (choose one default; both supported).
* **Prompt CRUD** (create, read, update, archive, delete).
* **Markdown editor** for body with basic toolbar + keyboard shortcuts.
* **Metadata**: title, tags (multi), target models (multi-select), link (single URL), access control (enum), favorite flag, archive flag.
* **System fields**: created\_at, updated\_at (auto), version (int; starts at 1).
* **Prompt cards** list/grid + detail page with copy actions.
* **Search & Filter**: full-text (title/body), filter by tags, favorites, archived.
* **Copy variations**: copy body only; copy with front-matter; copy JSON payload for programmatic use.
* **Duplicate prompt**: “Save as new” with incremented version.
* **Collections (lightweight)**: optional grouping (e.g., “Marketing”, “Coding”).
* **Import/Export (minimum)**: CSV/JSON import of prompts/tags/models; export user’s library.
* **Unlisted read-only share link** (feature-flag, off by default; no indexing).
* **Telemetry**: prompt\_created, prompt\_edited, prompt\_copied, search\_performed, share\_link\_created; PSR (perceived success rating) 1–5 on a prompt.
* **Zero-trust posture**: no provider keys yet; private vault by default.

---

## 4) Out of Scope (Phase 1)

* AI generation of prompts; AI auto-tagging; execution against model providers.
* Prompt Blocks composer / DSL (schema hooks allowed).
* Team workspaces, RBAC beyond single-owner access.
* Public API keys and webhooks (documented shape, not enabled).
* Payments/Marketplace.

---

## 5) Users & Use Cases

* **Indie builders / PMs / DevRels**: collect and refine prompts for repeated tasks.
* **Content creators/marketers**: house style guides and campaign prompts.
* **Analysts/researchers**: store structured prompts for repeat analyses.

**Primary flows**

1. **Quick capture** → Add prompt → Tag → Save → Copy later.
2. **Find & reuse** → Search by keyword/tag → Open → Copy variant.
3. **Iterate** → Duplicate → Edit → Version bump → Replace in collection.
4. **Light share (optional)** → Create unlisted link → Send to colleague.

---

## 6) Experience & UX Notes

* **Home (Vault):** search bar, tag chips, sort (recently updated, A–Z, favorites), responsive grid of prompt cards.
* **Card**: title, first line of body (truncated), tags, target models icons, favorite star, quick copy button.
* **Editor:** split-pane (editor/preview), markdown toolbar, autosave, dirty-state, keyboard shortcuts (⌘S, ⌘/ for preview).
* **Copy menu:** “Copy body”, “Copy body + front-matter”, “Copy JSON”.
* **Empty states:** opinionated examples + “Create from template” (starter pack).

---

## 7) Functional Requirements

### 7.1 Auth

* Email magic link and GitHub OAuth.
* Single-user vault (owner-only). “Access Control” stored per prompt but only **Private** enabled; **Unlisted** enabled only if feature flag is on.

### 7.2 Prompt CRUD

* Create with validation (title required, body min length).
* Markdown with live preview; image/links allowed in body (stored as markdown).
* Duplicate creates new ID, increments `version` and appends “(vX)” to title.
* Archive removes from default lists, included in archived filter.

### 7.3 Tags & Target Models

* Freeform tags (normalized to lowercase); suggestions from existing.
* Target models list is user-managed (import baseline list; add/remove locally).

### 7.4 Search & Filters

* Full-text search across title/body; filter by tags, favorite, archived.
* Sort by updated\_at desc (default), created\_at, title, favorite.

### 7.5 Collections (light)

* One prompt may belong to multiple collections.
* CRUD on collections; filter display by collection.

### 7.6 Import/Export

* Import CSV/JSON with mapping UI (title, body, tags, target\_models, link).
* Export user library as JSON; per-collection export optional.

### 7.7 Share (feature-flag)

* Generate unlisted URL (read-only). No index headers. Revocable token.

### 7.8 Telemetry & PSR

* Event capture with minimal PII. PSR modal after copy or on detail page.

---

## 8) Non-Functional Requirements

* **Performance**: Search <150 ms P95 for ≤5k prompts/user; list render <200 ms P95.
* **Availability**: 99.5% for MVP; graceful degradation if telemetry fails.
* **Security**: HTTPS/TLS; no external keys stored; CSRF protection; strong session handling; row-level access checks.
* **Privacy**: Private by default; clear warning on unlisted link creation.
* **Observability**: Structured logs, request tracing, basic dashboards.

---

## 9) Data Model (initial)

**tables**

* `users(id, email, name, avatar_url, created_at)`
* `prompts(id, owner_id FK, title, body_md, access_control ENUM['private','unlisted'], link_url, is_favorite BOOL, is_archived BOOL, version INT DEFAULT 1, created_at, updated_at)`
* `prompt_tags(prompt_id FK, tag TEXT, PRIMARY KEY(prompt_id, tag))`
* `prompt_models(prompt_id FK, model_name TEXT, PRIMARY KEY(prompt_id, model_name))`
* `collections(id, owner_id FK, name, created_at, updated_at)`
* `collection_prompts(collection_id FK, prompt_id FK, PRIMARY KEY(collection_id, prompt_id))`
* `share_tokens(prompt_id FK, token, created_at, revoked_at NULL)` *(feature-flag)*

**future-ready fields (do NOT implement logic yet)**

* `prompts.block_count INT DEFAULT 0` (for Blocks)
* `prompts.embedding VECTOR NULL` (pgvector; reserved)
* `prompts.icon_url TEXT NULL` (card visuals)

Indexes: `prompts(owner_id, updated_at)`, GIN on `prompt_tags.tag`, trigram/FTS on `(title, body_md)`.

---

## 10) API (Phase 1, private)

* `POST /auth/magic-link` *(if applicable)*
* `GET /me`
* `GET /prompts?query=&tags=&collection=&favorite=&archived=`
* `POST /prompts` *(title, body\_md, tags\[], target\_models\[], link\_url)*
* `GET /prompts/:id`
* `PUT /prompts/:id`
* `POST /prompts/:id/duplicate`
* `POST /prompts/:id/favorite`
* `POST /prompts/:id/archive`
* `GET /tags` *(top N)*
* `GET/POST /collections`
* `POST /import`
* `GET /export`
* `POST /prompts/:id/share` *(feature-flag)*
* `DELETE /share/:token` *(revoke)*

OpenAPI spec generated; auth via session/JWT.

---

## 11) Analytics & Success Criteria

**Core events**: create, edit, copy, search, filter, favorite, archive, share\_create/revoke.
**Dashboards**: DAU/WAU, prompts per user, copy rate, search-to-open rate, PSR distribution.
**MVP success gates**:

* ≥60% of WAU copy a prompt each week.
* Median prompts/user ≥6 within 14 days.
* PSR ≥4.0 for ≥40% of prompts with ≥3 uses.

---

## 12) Tech & System Architecture (baseline)

* **Frontend**: Next.js (web) with Tailwind + Radix; dnd-kit reserved later.
* **Editor**: TipTap/CodeMirror markdown + preview.
* **Backend**: FastAPI + SQLAlchemy; Alembic migrations.
* **DB**: Postgres 15; pg\_trgm for search. (pgvector installed but unused).
* **Auth**: Clerk/Supabase Auth or self-hosted magic-link + GitHub OAuth.
* **Infra**: Docker Compose for dev; Render/Fly/Heroku for MVP staging; GitHub Actions CI.
* **Observability**: OpenTelemetry traces; basic logs; Sentry.

---

## 13) Risks & Mitigations

* **Scope creep** → Feature flags + “MVP wall” (strict acceptance criteria).
* **Search quality** → Start with trigram + ranking; reserve embeddings for Phase 2.
* **Unlisted links leakage** → Clear warnings, revocation, token rotation, robots noindex.
* **Vendor lock-in (auth/editor)** → Abstract adapters; keep data portable via export.

---

## 14) Dependencies

* Auth provider (or in-house magic link).
* Hosting choice for staging/prod.
* Design tokens & component library decision (Tailwind + Radix).
* CSV/JSON import mapping library.

---

## 15) Open Questions

1. Do we seed an official **starter pack** (10–20 curated prompts by category)?
2. Should unlisted links be in Phase 1 GA or kept behind invite?
3. Will web be the only client for MVP, or do we prototype a minimal RN view-only app?
4. Do we enforce a **tag taxonomy** (pluralization/casing rules) in UI?

---

## 16) Acceptance Criteria (per capability)

* **Create/Edit**: User can create a prompt with title+body; autosave works; refresh persists; updated\_at changes.
* **Markdown**: Toolbar works; preview matches output; links render; images preserved in markdown (no upload in P1).
* **Tags/Models**: Add/remove inline; chips render on card; filter by tag.
* **Search**: Keyword search returns expected prompts; P95 <150 ms at 5k prompts.
* **Copy**: One-click copy (body); menu variants work; toast confirms.
* **Duplicate/Version**: Duplicate increments version and title suffix; timestamps updated.
* **Collections**: Create/list; assign via multiselect; filter by collection.
* **Import/Export**: Import CSV/JSON with mapping; export full library JSON.
* **Share (flagged)**: Generate revocable token; public page shows title/body/tags read-only; owner can revoke.
* **Auth**: New user can sign up and land in empty state with starter templates visible.

---

## 17) Timeline (Phase 1 ≈ 6 weeks, three 2-week sprints)

* **Sprint 1**: Auth, DB schema, Prompt CRUD API, basic list/detail, tags/models.
* **Sprint 2**: Markdown editor + preview, search/filters/sort, copy variants, duplicate/version, favorites/archiving.
* **Sprint 3**: Collections, import/export, telemetry + PSR, (feature-flag) unlisted share, polish & docs.

---

## 18) Documentation & Ops

* Developer setup (`make dev`), API reference (OpenAPI), data dictionary.
* User guide: quick start, import/export, copy variants.
* Runbooks: migrations, rollback, feature-flag toggles.

---

## 19) Future-Ready Hooks (explicitly added now)

* `access_control` field standardized (**Visibility → Access Control**).
* Auto timestamps (`created_at`, `updated_at`) per record.
* `link_url` field on prompt.
* Reserved columns: `block_count`, `embedding`, `icon_url`.
* pgvector installed, disabled by default.
* Draft `/v1` route layout for upcoming public API; not exposed publicly.

---

## 20) Go/No-Go for Phase 2

* WAU≥100, copy-rate≥60%, PSR median≥4.0, crash-free sessions≥99%.
* At least 5 design partners actively using import/export or collections.
* Telemetry confirms repeated reuse (≥3 times) for ≥40% of created prompts.

---

**This PRD defines the smallest compelling surface for MeatyPrompts that users will actually keep using—while quietly laying track for AI-assist, execution, and blocks without rework.** Next step: convert into an implementation plan with sprint-scoped user stories and acceptance tests.
