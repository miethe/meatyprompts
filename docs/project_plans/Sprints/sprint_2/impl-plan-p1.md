# Implementation Plan for: Phase 1 — Manual MVP (MeatyPrompts)

> *Copy the Feature Name from the PRD header.*

1. **General Overview**
   A lovable MVP that lets users **manually create, organize, search, and reuse prompts** with a polished, opinionated UX (cards, markdown editor, copy actions). It establishes a stable schema, basic telemetry, and feature-flagged share links to de-risk and pave the way for later AI-assist and execution phases.&#x20;

2. **Acceptance Criteria**

   |   ID  | Criteria                                                                                                   |
   | :---: | ---------------------------------------------------------------------------------------------------------- |
   |  AC-1 | As a signed-in user, I can create/edit a prompt (title + markdown body), and edits persist on refresh.     |
   |  AC-2 | As a user, I can tag prompts, set target models, and filter/search by keyword, tag, favorite, or archived. |
   |  AC-3 | As a user, I can one-click copy the body and choose copy variants (front-matter, JSON).                    |
   |  AC-4 | As a user, I can duplicate a prompt, which increments the version and updates timestamps.                  |
   |  AC-5 | As a user, I can create/view collections and filter the vault by collection.                               |
   |  AC-6 | As a user, I can import CSV/JSON (with field mapping) and export my library as JSON.                       |
   |  AC-7 | As an owner (if flag on), I can generate a revocable **unlisted** read-only share link.                    |
   |  AC-8 | Performance: search P95 < 150 ms @ ≤5k prompts/user; list render P95 < 200 ms; availability ≥ 99.5%.       |
   |  AC-9 | Telemetry: create/edit/copy/search/favorite/archive/share events recorded; PSR capture available.          |
   | AC-10 | Security/privacy: private by default; robots **noindex** on shared pages; strong session handling.         |

3. **Expected Output**

   * **User-facing**

     * Vault home with search, tag chips, sorting; responsive **prompt cards** showing title, preview, tags, model icons, favorite star, and copy button.
     * Full **Markdown editor** with split preview, toolbar, autosave, and keyboard shortcuts (⌘S, ⌘/).
     * Filters: tags, favorites, archived; sorting by `updated_at` (default), `created_at`, `title`.
     * **Copy** menu: body, body + front-matter, JSON. **Duplicate** with version bump. Collections CRUD/filters.
     * **Import/Export** (CSV/JSON). **Unlisted share** page (read-only) behind feature flag.&#x20;
   * **System-facing**

     * Postgres schema per PRD (prompts, tags, models, collections, share\_tokens, system fields, reserved columns).
     * FastAPI endpoints for auth, CRUD, search, copy variants, import/export, share (flagged).
     * Trigram/FTS search; pgvector installed but unused.
     * Telemetry events + PSR (1–5) storage; OpenAPI spec published; feature-flag scaffolding.&#x20;

4. **Backlog of User Stories**

   |     Story ID    | Title                                | Brief Description                                                             | AC Reference |
   | :-------------: | ------------------------------------ | ----------------------------------------------------------------------------- | ------------ |
   |  MP-P1-AUTH-001 | Email/GitHub Auth                    | Implement magic link + GitHub OAuth, session handling, `/me`.                 | AC-10        |
   |   MP-P1-DB-002  | Baseline Schema + Indexes            | Create all Phase-1 tables, enums, system fields, indexes, reserved columns.   | AC-8, AC-10  |
   |  MP-P1-API-003  | Prompts CRUD API                     | `POST/GET/PUT/DELETE /prompts` incl. duplicate/version, favorite, archive.    | AC-1, AC-4   |
   |   MP-P1-UI-004  | Vault List/Grid + Cards              | Render cards, favorite star, quick copy; empty states with starter templates. | AC-1, AC-3   |
   |   MP-P1-ED-005  | Markdown Editor + Split Preview      | Editor with toolbar, autosave, dirty state, shortcuts.                        | AC-1         |
   |  MP-P1-TAG-006  | Tags & Target Models                 | Multi-tag, model chips, suggestions from existing.                            | AC-2         |
   |  MP-P1-SRCH-007 | Search/Filter/Sort                   | Full-text search, tag/favorite/archived filters; sort options.                | AC-2, AC-8   |
   |  MP-P1-COPY-008 | Copy Variants                        | Body, body+front-matter, JSON payload; toasts.                                | AC-3         |
   |  MP-P1-DUP-009  | Duplicate & Version Bump             | “Save as new” increments version, suffix title `(vX)`.                        | AC-4         |
   |  MP-P1-COLL-010 | Collections CRUD + Filter            | Collections data model, assign multi, filter vault by collection.             | AC-5         |
   |  MP-P1-IMEX-011 | Import/Export                        | CSV/JSON import with mapping UI; export library JSON.                         | AC-6         |
   | MP-P1-SHARE-012 | Unlisted Share (Feature-Flag)        | Tokenized read-only page, revoke; robots noindex; owner-only.                 | AC-7, AC-10  |
   |  MP-P1-TEL-013  | Telemetry + PSR                      | Capture events, PSR 1–5 prompt rating flow, basic dashboard wiring.           | AC-9         |
   |  MP-P1-NFR-014  | Perf & A11y Hardening                | Hit P95 budgets, Lighthouse/a11y fixes, guardrails for 5k prompts.            | AC-8         |
   |  MP-P1-DOC-015  | OpenAPI, Data Dictionary, User Guide | Publish spec, update docs, runbooks for migrations & flags.                   | —            |

5. **Architectural Artifacts & Key Decisions**

   * **ADRs needed**

     * ADR-001: Auth approach (Clerk/Supabase vs. in-house magic link + GitHub OAuth).&#x20;
     * ADR-002: Search strategy (pg\_trgm FTS now; pgvector reserved for Phase 2).&#x20;
     * ADR-003: Markdown editor selection (TipTap vs. CodeMirror blend) and portability.&#x20;
     * ADR-004: Feature-flag framework and default state for **Share** (off for GA?).&#x20;
     * ADR-005: Telemetry event schema & PSR storage.
   * **Decisions to log**

     * Copy-variant payload shape (front-matter keys), export format guarantees.
     * Collections semantics (multi-membership, ordering, and naming rules).&#x20;
   * **Dependencies**

     * Auth provider ready before MP-P1-API-003.
     * DB migration (MP-P1-DB-002) before any CRUD stories.
     * Feature-flag infra before SHARE story; telemetry sink before TEL story.&#x20;

6. **Overall Non-Functional Requirements**

   * **Performance:** Search <150 ms p95 @ ≤5k prompts/user; list render <200 ms p95.&#x20;
   * **Availability:** 99.5% MVP target; graceful degradation if telemetry fails.&#x20;
   * **Security/Privacy:** HTTPS/TLS, CSRF protection, strong sessions, row-level access checks; private by default; warning on share creation; **noindex** for shared pages.&#x20;
   * **Observability:** Structured logs, traces, basic dashboards; Sentry.&#x20;
   * **Accessibility:** Meet WCAG 2.1 AA on new screens (editor, vault, share).
   * **Scalability:** Indexing strategy + pagination; pgvector installed but unused in P1.&#x20;
   * **Portability/Data Freedom:** Import/Export guarantees; avoid vendor lock-in on auth/editor via adapters.&#x20;

7. **Open Questions / Clarifications**

   * Q1: **Starter pack** — do we seed 10–20 curated prompts at first run? If yes, which categories? (TBD rollout/ownership.)&#x20;
   * Q2: **Share links** — GA in P1 or stay invite-only behind flag through P1? Default flag state?&#x20;
   * Q3: **Clients** — confirm **web-only** for P1; any minimal RN view-only considered?&#x20;
   * Q4: **Tag taxonomy** — enforce normalization (pluralization/casing) in UI or keep freeform?&#x20;
   * Q5: **Auth** — finalize provider vs. in-house by end of Sprint 1 to avoid rework.&#x20;

---

**Notes for Grooming:** Map stories to the PRD’s Sprint plan (S1: Auth/DB/CRUD; S2: Editor/Search/Copy/Duplicate/Favorites; S3: Collections/Import-Export/Telemetry/Share-flag + polish). Keep scope inside the “MVP wall”; reserve embeddings/blocks/marketplace for Phase 2+.&#x20;
