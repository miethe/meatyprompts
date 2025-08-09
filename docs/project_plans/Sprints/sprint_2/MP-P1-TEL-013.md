# User Story MP-P1-TEL-013 — **Telemetry & PSR (Prompt Satisfaction Rating)**

> **Epic:** Phase 1 — Manual MVP
> **As a** product team, **we want** privacy-safe telemetry and a lightweight Prompt Satisfaction Rating (PSR 1–5) flow, **so that** we can measure feature usage, performance, and prompt quality without storing sensitive content.

---

## 1) Summary / Narrative

We will implement:

1. **Telemetry**: a small, pluggable event pipeline (FE → BE → sink) with a **strict event whitelist**, basic **OTel traces**, and **no PII** (no prompt bodies).
2. **PSR**: a **1–5 rating** with optional 280-char note, offered contextually after high-intent actions (e.g., Copy). PSR is **owner-visible only** (internal analytics) and **feature-flagged** to control rollout.

---

## 2) Acceptance Criteria

| ID   | Criteria                                                                                                                                                                                                                                      |
| ---- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| AC-1 | Frontend can `track()` any **whitelisted event** and see it persist to the configured sink (dev: console; prod: HTTP -> BE -> sink).                                                                                                          |
| AC-2 | **Event schema**: `{event, ts, user_id, session_id, prompt_id?, version?, source?, variant?, latency_ms?, filter_hash?}`; events outside the whitelist are rejected (400) server-side.                                                        |
| AC-3 | **PII guardrails**: no bodies, no email; token values and queries are hashed; comments are clamped to ≤280 chars; payload size ≤4KB.                                                                                                          |
| AC-4 | **OTel traces** wrap key paths: create/update, search, copy, duplicate, import/export; traces correlate via `trace_id` returned in response headers.                                                                                          |
| AC-5 | **PSR**: A non-blocking inline dialog appears after **Copy** (and optionally Duplicate) with 1–5 stars and an optional note; submitting persists and toasts success; dismissible; never shown more than **once per prompt per user per day**. |
| AC-6 | **APIs**: `POST /telemetry/events` accepts batches (1–50) of whitelisted events; `POST /psr` stores a single rating (owner-scoped); both require auth; rate-limits apply.                                                                     |
| AC-7 | **Perf**: ingest p95 < 100 ms; PSR write p95 < 100 ms; FE `track()` never blocks UI (fire-and-forget with timeout ≤ 200 ms).                                                                                                                  |
| AC-8 | **Docs**: event catalog, redaction policy, PSR data dictionary, and rollout plan are published.                                                                                                                                               |

---

## 3) Context & Dependencies

* **Depends on**:

  * MP-P1-AUTH-001 (sessions & `/me`) for `user_id`, `session_id`.
  * MP-P1-API-003 baseline routes (we will add OTel & event hooks).
* **Integrates with** (emit events from):

  * UI stories (UI-004), Editor (ED-005), Tags (TAG-006), Search (SRCH-007), Copy (COPY-008), Duplicate (DUP-009), Collections (COLL-010), Import/Export (IMEX-011), Share (SHARE-012).
* **Flags**: `features.telemetry` (ON) and `features.psr` (default: OFF in prod, ON in staging).

---

## 4) Architecture & Implementation

## 4.1 Data Model (Alembic)

* **psr\_ratings**

  * `id UUID PK`
  * `owner_id UUID NOT NULL` (FK → users)
  * `prompt_id UUID NOT NULL` (FK → prompts)
  * `version TEXT NULL` (latest if null; future-proof for frozen shares)
  * `rating SMALLINT NOT NULL CHECK 1<=rating<=5`
  * `note TEXT NULL CHECK length(note)<=280`
  * `source TEXT NOT NULL`  // `copy|duplicate|manual|other`
  * `created_at TIMESTAMPTZ DEFAULT now()`
  * **Uniq soft-cap** (enforced in app): at most 1 submission / (owner\_id,prompt\_id) per day.
* **telemetry\_events** (optional, only if we choose DB sink for MVP; otherwise skip)

  * `id UUID PK`, `owner_id UUID`, `event TEXT`, `payload JSONB`, `ts TIMESTAMPTZ`, `trace_id TEXT`, `session_id TEXT`
  * **TTL policy**: table is **ephemeral** (auto-vacuum or 7-day retention job) to avoid bloat.

> **Sink strategy**: Start with **dual sink** (structured logs + optional DB), add OTLP/Segment/PostHog adapter later via config.

## 4.2 API (FastAPI)

* `POST /telemetry/events`  *(auth required)*

  * Body: `{ events: TelemetryEvent[] }`, 1–50 items
  * Validate against **whitelist** (see 4.4); drop anything non-conforming; return `{ accepted, rejected, trace_id }`.
  * Rate limit: e.g., **120 req/min/user**; per-request ≤ 50 events.
* `POST /psr`  *(auth required)*

  * Body: `{ prompt_id, version?, rating: 1..5, note?, source }`
  * Enforce once/day rule (by owner\_id,prompt\_id, DATE(created\_at)); upsert-like behavior (replace latest same-day rating).
  * Returns aggregate snippet `{ avg_rating, total_ratings }` for the prompt (optional; can be null in P1).

**Security / Privacy**

* 401/403 as appropriate; strip/ignore unknown fields; hash large free-text inputs client-side when applicable (e.g., search query → `sha256(q)`); reject any payload whose JSON includes `body` key.

## 4.3 Backend Services

* `telemetry_service.py`

  * `validate_and_redact(event) -> event|error`
  * `ingest_batch(owner_id, events)` (fan-out to sinks: logs, DB, OTLP if enabled)
* `psr_service.py`

  * `submit(owner_id, prompt_id, version, rating, note, source)`
  * `aggregate(prompt_id)` (optional for future dashboards)

## 4.4 Event Catalog (Whitelist)

*All names lowercase, dot-separated; only the following are accepted in P1.*

* **auth**: `auth.login.success`, `auth.login.failure`, `auth.logout`
* **vault**: `vault.search_performed` *(attrs: result\_count, filter\_hash, query\_len, latency\_ms)*, `vault.filtered_collection`
* **prompt lifecycle**:
  `prompts.create`, `prompts.update`, `prompts.duplicate`, `prompts.delete` *(if added later)*
  attrs (subset): `{prompt_id, version, latency_ms, source}`
* **copy/share**:
  `prompt_copied` *(attrs: prompt\_id, variant \[body|front\_matter|json], source \[card|detail])*
  `share.created`, `share.viewed`, `share.revoked`
* **metadata**:
  `tags.added`, `tags.removed` (batched or with counts), `models.selected`
* **imex**:
  `import.started`, `import.completed` *(attrs: created, skipped, error\_count)*, `export.requested`, `export.completed`

*Any other event → 400 (rejected).*

**Common attribute rules**

* `user_id` (server-derived), `session_id` (cookie), `prompt_id` (UUID), `version` (string), `source` (enum), `variant` (enum), `latency_ms` (int), `result_count` (int), `filter_hash` (sha256 on normalized filters), `query_len` (int).
* **Never** include `title`, `body`, `note` > 280, email, or tokens.

## 4.5 Frontend (React) — Client SDK

* `lib/analytics.ts`

  * `track(event: EventName, props?: Props)` → queues events (in-memory), flush on idle/visibility change (or every 5s), `keepAlive: true`, `timeout: 200ms`.
  * Bounded queue (e.g., 200 events) with drop policy (oldest first).
  * **Env-driven sink**: dev → console; staging/prod → `/telemetry/events`.
* **PSR UI**

  * `components/psr/PsrPrompt.tsx` (non-blocking tooltip/modal with 1–5 stars + optional textarea).
  * Trigger after **Copy success**; frequency capping via `localStorage('psr:last:{prompt_id}')` and server duplicate-per-day guard.
  * Submit → `POST /psr` → toast; on error → silent fail (log).

## 4.6 Observability

* **OpenTelemetry** (server)

  * Add middleware to start trace spans per request; expose `traceparent` in responses; annotate spans in: create/update prompt, search, duplicate, import/export, share resolve.
* **Structured logging**

  * JSON logs with `event`, `trace_id`, `user_id`, `prompt_id?`, sizes, durations; redact inputs.

---

## 5) Non-Functional Requirements

* **Performance**: ingest endpoints stay p95 <100 ms; FE tracking never block paints; PSR modal show/hide <16 ms main-thread cost.
* **Security/Privacy**: strict server validation; deny unrecognized keys; sanitize strings; length caps; no raw content.
* **Reliability**: if sink fails, drop gracefully (no retries that block UI); best-effort telemetry.
* **Compliance**: `noindex` remains on public share pages (from SHARE story); telemetry complies with internal privacy policy.

---

## 6) Testing Strategy

| Layer             | Tooling            | Coverage                                                                                                              |
| ----------------- | ------------------ | --------------------------------------------------------------------------------------------------------------------- |
| Unit (BE)         | pytest             | Event whitelist validator; redaction (reject `body`, long strings); PSR upsert/day; hashing utilities.                |
| Integration (API) | FastAPI TestClient | `/telemetry/events` accepts only whitelisted events; batch size limits; rate-limit; `/psr` 200; 401 without auth.     |
| Contract          | Schema snapshot    | Event schema (names/attrs) and PSR payload shapes locked via snapshot; CI fails on drift.                             |
| Unit (FE)         | Jest               | `track()` queueing/flush; timeout path; PSR component frequency cap; star selection & note clamp.                     |
| E2E               | Cypress/Playwright | Copy → PSR prompt → submit → 200; subsequent copy same day → PSR does not reappear; telemetry batch posted on unload. |
| Perf              | Lighthouse + k6    | Ingest p95 <100 ms under 200 RPS; FE blocking time unchanged.                                                         |

---

## 7) Documentation & Artifacts

* **`docs/telemetry/events.md`** — event catalog, attribute dictionary, examples, redaction policy.
* **`docs/telemetry/architecture.md`** — adapters, sinks, failure modes, sampling.
* **`docs/psr.md`** — UX flow, API contract, frequency caps, data dictionary.
* **ADR**: `ADR-00X-telemetry-adapter.md` — “Pluggable telemetry sink (logs | DB | OTLP)”; `ADR-00Y-psr-rollout.md` — “PSR flag, frequency cap, scope.”

---

## 8) Risks & Mitigations

| Risk                              | Impact                    | Mitigation                                                                                     |
| --------------------------------- | ------------------------- | ---------------------------------------------------------------------------------------------- |
| Payload creep (PII/Content leaks) | Privacy & compliance risk | Whitelist + server validation; reject unknown keys; fuzz tests; code owners for event catalog. |
| Over-collecting (performance)     | UI jank / server load     | Client queue + batch; rate-limit server; drop on backpressure.                                 |
| Low signal PSR (spammy prompts)   | Noisy data                | Frequency cap; optional require “used copy” beforehand; small note length; internal only.      |
| Sink outages                      | Lost events               | Best-effort logging; do not retry synchronously; metrics on accept/reject counts.              |

---

## 9) Implementation Tasks (Dev-Ready)

**DB / Migrations**

* [ ] Create `psr_ratings` (and optional `telemetry_events` if DB sink needed) with indexes; add retention job if used.

**Backend**

* [ ] `telemetry_service.py` validator + ingester; `psr_service.py` submit + guard.
* [ ] `api/routes/telemetry.py` (`POST /telemetry/events`) & `api/routes/psr.py` (`POST /psr`).
* [ ] OTel middleware & span annotations in key endpoints.
* [ ] Config: `TELEMETRY_SINK=(logs|db|otlp)`, `FEATURES_PSR=true|false`, rate-limit settings.

**Frontend**

* [ ] `lib/analytics.ts` with queue/flush; respect `NEXT_PUBLIC_FEATURES_TELEMETRY`.
* [ ] PSR component; trigger after Copy; frequency cap; `POST /psr`.
* [ ] Wire initial events in existing flows (create/update/copy/search/duplicate/import/export/share).

**QA & Docs**

* [ ] Tests per Section 6; dashboards (basic) for accept/reject counts.
* [ ] Publish docs/ADRs; add event lint rule in CI (disallow non-whitelisted events).

---

## 10) Open Questions (TBD)

1. **Sink choice for P1**: logs-only + OTel traces vs. also DB mirror? (Recommend logs + OTel; DB optional with 7-day TTL.)
2. **PSR visibility**: surface averages in UI later (Phase-2), or keep analytics-only in P1? (Recommend analytics-only.)
3. **Search query policy**: hash client-side or server-side? (Recommend client-side hash + length only.)
4. **Sampling**: 100% capture in P1 or sample high-volume events (e.g., `prompt_copied`)? (Recommend 100% with rate-limits; revisit later.)

---

# Definition of Done

* Telemetry pipeline live with whitelist validation, OTel traces, and docs; FE events wired in target flows.
* PSR UI available (flag-controlled), writes to DB with caps; no PII/content stored; tests and perf checks pass; rollout plan documented.
