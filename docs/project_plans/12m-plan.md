# 🎯 Strategic Framing

We are **re-starting from zero code** but with a clear vision, validated market need, and an initial architecture sketched out in the earlier concept deck. The core business goal is unchanged: *ship a production-ready prompt-engineering SaaS that delights individual builders first, then scales up-market*. The plan below resets the backlog, layers in your new ideas, and maps a straight line to revenue.

---

## 1 · Release Roadmap (12-month horizon)

| Phase                              | Sprint Windows\* | Primary Epics (↑ = new idea)                                                                                                                        | Key Deliverables                          | Exit Criteria                                 |
| ---------------------------------- | ---------------- | --------------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------- | --------------------------------------------- |
| **0 · Foundations**                | S0 (2 wks)       | • Repo & CI baseline<br>• Postgres schema v0 <br>• Access Control middleware (RBAC)<br>• Telemetry scaffold                                         | Running dev env + GitHub Actions pipeline | All tests green, auto-deploy to staging       |
| **1 · Manual MVP**                 | S1–S3 (6 wks)    | • **Prompt CRUD UI** (web/mobile)<br>• Prompt Vault search & tags<br>• Auth (magic link + OAuth)<br>• Basic prompt cards styling                    | Internal alpha                            | Create / edit / list prompts; basic analytics |
| **2 · AI Assist Alpha**            | S4–S6 (6 wks)    | ↑ **LLM-assisted Prompt Generator** (few-shot + form-fill)<br>↑ **Auto-tag & cluster** (pgvector similarity)<br>• Model Adapter v1 (OpenAI, Gemini) | Private beta w/ 25 users                  | >70 % “Useful” rating on generated drafts     |
| **3 · Integration Beta**           | S7–S9 (6 wks)    | ↑ **Run-Prompt Engine** (execute against selected model w/ user API key)<br>• Prompt cost & latency stats<br>• Import/Export CSV+JSON               | Public wait-list beta                     | 1k MAU, PSR≥70 %                              |
| **4 · Modular Blocks & API**       | S10–S12 (6 wks)  | ↑ **Prompt Blocks DSL & composer UI**<br>↑ Public REST/GraphQL API<br>↑ Webhooks + Zapier connector                                                 | v1.0 GA                                   | Paying customers; docs & TOS finished         |
| **5 · Monetisation & Marketplace** | S13–S16 (8 wks)  | • Stripe billing + seat mgmt<br>↑ Template marketplace (rev-share)<br>• SOC-2 prep backlog                                                          | v1.5                                      | \$1 M ARR run-rate target                     |

\*Two-week sprints; adjust cadence if AI-agent velocity exceeds estimates.

Roadmap re-uses the phased cadence proven in the earlier draftbut merges your new feature requests (▲) into Phases 2–5.

---

## 2 · Epic Highlights & Technical Notes

| Epic                              | Architectural Changes                                                                                                                           | Test/Docs Needed                                                                  |
| --------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------- |
| **LLM-assisted Prompt Generator** | Extend Prompt Engine core; add `generation_strategy` enum (`manual`, `ai_seeded`). Reuse Model Adapter for provider-specific syntax.            | PRD, unit + integration tests pretending to be each provider; latency budget doc. |
| **Auto-tag & Cluster**            | Background Celery worker that embeds prompt text (OpenAI Embeddings) into `prompt_embedding` column (pgvector). K-Means or HDBSCAN nightly.     | Evaluation notebook measuring clustering purity.                                  |
| **Run-Prompt Engine**             | Secure per-user “credential vault” table (encrypted at rest). Add `/execute` endpoint that proxies to provider with rate-limit & cost tracking. | Token-usage regression tests; GDPR DPIA.                                          |
| **Prompt Blocks**                 | New `block` table; each block has `type`, `content`, `order`, `parent_prompt_id`. Front-end drag-and-drop composer (dnd-kit).                   | UX doc, JSON schema for blocks, e2e tests for reorder.                            |
| **Public API**                    | FastAPI routers under `/v1`; API keys signed w/ HMAC.                                                                                           | OpenAPI spec, Postman collection.                                                 |
| **Marketplace & Billing**         | Stripe Connect; `template` table cross-links creator ID. Payment webhooks micro-service.                                                        | Fin-ops runbook, SOC-2 control mapping.                                           |

---

## 3 · High-Level Sprint Backlog (first 4 sprints)

| Sprint | Stories                                                                                                                        | Acceptance Snippet                                                     |
| ------ | ------------------------------------------------------------------------------------------------------------------------------ | ---------------------------------------------------------------------- |
| **S0** | • Docker-Compose stack<br>• Pre-commit + Ruff, Black<br>• Alembic baseline<br>• GitHub Actions CI<br>• Terraform staging infra | “`make dev` spins up API + DB with zero manual steps.”                 |
| **S1** | • Prompt model (SQLAlchemy)<br>• Basic FastAPI CRUD routes<br>• React prompt form<br>• Tag multi-select                        | “User can create a prompt and see it listed in dashboard immediately.” |
| **S2** | • Global search (ILIKE + trigram)<br>• Card grid with Tailwind cards v1<br>• JWT auth flow                                     | “Logged-out users redirected; search returns ≤100 ms.”                 |
| **S3** | • Minimal analytics (PSR stub)<br>• First batch of Cypress tests                                                               | “Dashboard shows success histogram placeholder.”                       |

---

## 4 · Resourcing & Calendar

* **Solo founder + AI pair-programming agents** until Sprint 6.
* Hire **1 FE contractor** (React Native/Next.js) at Sprint 7 and **1 BE contractor** (FastAPI) at Sprint 8.
* 16-week v1.0 schedule aligns with earlier cost/timeline study—\$60 K burn to GA.

---

## 5 · Market Feasibility Checkpoints

| Milestone                         | KPI Gate                         | Capitalisation Option                                                     |
| --------------------------------- | -------------------------------- | ------------------------------------------------------------------------- |
| **Private Beta (Month 3)**        | 25 design-partners, PSR≥70 %     | Angel SAFE \$250 K for runway extension                                   |
| **Public Beta (Month 5)**         | 1 k MAU, <\$0.002 avg token cost | Seed round \$1–2 M at \$8 M pre; de-risk via traction & TAM \$1.13 B 2025 |
| **v1.0 GA (Month 6)**             | \$10 K MRR, churn < 5 %          | Revenue-share debt or small SaaS M\&A interest                            |
| **Marketplace Launch (Month 10)** | 20 % prompts from marketplace    | Series A for enterprise/SOC-2 push (\$5–7 M)                              |

The market’s 32 %+ CAGR and large SAM in adjacent AI-coding tools (USD 12.6 B by 2028) support aggressive scaling once product-market fit is validated.

---

## 6 · Risk Radar

* **Provider policy shifts** → Continue “bring your own key” design.
* **LLM cost spikes** → Add cost-aware routing + local model option.
* **Feature creep** → Lock sprint scope; uncommitted ideas flow into Phase 5 backlog.
* **Security/PII** → Encrypt creds, adopt “no-log” mode.

---

## 7 · Next Actions (this week)

1. Freeze backlog for **Sprint 0**; create GitHub issues & project board.
2. Draft **PRDs** for Prompt model & CRUD API.
3. Book user interviews for beta design-partner cohort.
4. Kick off branding sprint for new prompt-card visuals.

---

**Outcome**: by **Month 6** we ship a revenue-generating, AI-augmented prompt platform with extensibility baked in—positioned to capture an outsized share of a billion-dollar market and primed for either venture scaling or profitable indie growth.
