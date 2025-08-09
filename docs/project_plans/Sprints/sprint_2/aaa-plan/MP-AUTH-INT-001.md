# User Story MP-AUTH-INT-001 — **Migrate Authentication to Clerk**

> **Epic:** Phase 1 — Manual MVP
> **As a** Lead Architect, **I want** to replace the current bespoke cookie-based auth system with a managed Clerk integration, **so that** we can accelerate development, enhance security, and provide a unified auth experience for our web and future mobile clients.

---

## 1 · Narrative

*As the* **architectural lead**, *I want* to **migrate our entire authentication and session management system from the current in-house solution to Clerk**, *so that* **we can remove brittle, high-maintenance code and instead leverage a robust, feature-rich platform.** This change will eliminate our need to manage password hashing, OAuth callbacks, and session tokens manually. It will provide us with pre-built UI components for a polished user experience out of the box, secure our API with industry-standard stateless JWTs, and de-risk our future roadmap by providing a clear path to team-based features ("Organizations"). This migration is a foundational step detailed in **ADR-001** and unblocks all subsequent user-facing development.

---

## 2 · Acceptance Criteria

| #    | Behaviour                                                                                                                              | Measure / Test                                                                                                                      |
| :--- | :--------------------------------------------------------------------------------------------------------------------------------------- | :---------------------------------------------------------------------------------------------------------------------------------- |
| AC-1 | Users can sign up and sign in using Clerk's pre-built, hosted UI components.                                                             | The `Login.tsx` page is removed and navigating to a protected route redirects to the Clerk-hosted sign-in page.                   |
| AC-2 | After a successful login, the user is redirected back to the application and has an active session.                                      | The Clerk `useAuth()` hook returns `{ isSignedIn: true }` and the `useUser()` hook returns the user's profile data.                 |
| AC-3 | The frontend `apiRequest` client automatically attaches a valid Clerk JWT to the `Authorization` header for all protected API requests. | Intercept an API call in dev tools or Cypress and assert the presence of `Authorization: Bearer <jwt>`.                             |
| AC-4 | The FastAPI backend `get_current_user` dependency successfully validates the Clerk JWT and identifies the user.                        | An API test with a valid mock JWT passes; a test with an invalid or missing JWT fails with a 401 Unauthorized error.              |
| AC-5 | A new user signing up via Clerk triggers a webhook that creates a corresponding record in our local `users` table.                      | After a new user signs up, a `SELECT` query on the `users` table finds a new row with the matching `clerk_user_id`.              |
| AC-6 | The old, cookie-based auth code is removed from the codebase.                                                                            | The files `auth/github.py` and `api/deps.py` are removed or completely refactored. `auth_service.py` is significantly simplified. |
| AC-7 | The logout functionality correctly signs the user out of their Clerk session and clears all local session state.                       | Clicking "Logout" calls `clerk.signOut()` and redirects the user to the public home/login page.                                     |

---

## 3 · Context & Dependencies

* **Depends on:**
  * A MeatyPrompts project must be created in the Clerk dashboard.
  * Clerk API keys and environment variables must be configured for local development.
* **Forward hooks / future features:**
  * This implementation lays the groundwork for **Team/Organization functionality** (a core Clerk feature).
  * It enables **Role-Based Access Control (RBAC)** by allowing us to store roles in our local DB, linked to the Clerk user ID.
  * It simplifies the addition of other **social providers** (Google, etc.) and **MFA**, which can be configured directly in the Clerk dashboard with no code changes.

---

## 4 · Architecture & Implementation Details

## 4.1 Database & Schema

* **Migration file:** `services/api/alembic/versions/{YYYYMMDD}_migrate_to_clerk_auth.py`
* **Model changes (in `core/models.py`):**
  * **`UserORM`:** Simplify this model. The `name` and `avatar_url` will now be primarily managed by Clerk. We can keep them for caching purposes, but the source of truth is Clerk. Add a non-nullable, unique `clerk_user_id` column.
  * **`UserIdentityORM`:** This table and its corresponding ORM model can be **deleted entirely**. Its purpose (storing provider-specific IDs and tokens) is now fully handled by Clerk.
* **Required Action:** A new Alembic migration will be created to `DROP TABLE user_identities` and `ADD COLUMN clerk_user_id TEXT NOT NULL UNIQUE` to the `users` table.

## 4.2 API Endpoints

* **File:** `api/routes/webhooks.py` (New file)
* **New route / handler:**
  * `POST /webhooks/clerk`: This endpoint will receive webhook events from Clerk. It must be protected by verifying the webhook signature using Clerk's `svix` library. It will handle `user.created` and `user.updated` events to sync data to our local `users` table.
* **Routes to be DELETED:**
  * All routes in `api/routes/auth/github.py` (`/auth/github/login`, `/auth/github/callback`).
  * The `/auth/logout` and `/auth/magic-link` routes.

## 4.3 Backend Services & Tasks

* **Service layer (`services/user_service.py`):**
  * Create a new service function: `sync_user_from_clerk_webhook(payload: dict)`. This function will parse the webhook payload and perform an `UPSERT` on our local `users` table based on the `clerk_user_id`.
* **Service code to be DELETED (`services/auth_service.py`):**
  * The functions `get_or_create_user`, `create_session`, and `verify_session` will be **deleted**. The file will be mostly empty or removed.
* **Dependency (`api/deps.py`):**
  * The `get_current_user` dependency will be completely rewritten. It will no longer check cookies. Instead, it will extract the Bearer token from the `Authorization` header and use the `clerk-fastapi` SDK to verify the JWT.

## 4.4 Frontend (React/Next.js)

* **Root Layout (`app/layout.tsx`):**
  * Wrap the entire application in the `<ClerkProvider>`. This makes Clerk's hooks available everywhere.
* **Component to be DELETED:**
  * `Login.tsx`: This page is no longer needed.
* **New Auth Components:**
  * Create `<SignInButton />` and `<SignOutButton />` components that use Clerk's `useClerk()` hook.
  * Use Clerk's `<UserProfile />` component for the user settings page.
* **API Client (`lib/apiClient.ts`):**
  * This file requires a significant change. It must stop sending the `X-CSRF-Token`.
  * It will now use the `useAuth()` hook from `@clerk/nextjs` to get the session JWT: `const { getToken } = useAuth(); const token = await getToken();`
  * This `token` will be attached to the `Authorization: Bearer ${token}` header for every API request.

---

## 5 · Testing Strategy

| Layer           | Tool                                     | New Tests / Assertions                                                                                                                              |
| :-------------- | :--------------------------------------- | :-------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Unit (BE)**   | `pytest`                                 | Test the `sync_user_from_clerk_webhook` service logic. Test the JWT validation logic in `get_current_user` by providing valid and invalid mock JWTs. |
| **Integration** | `FastAPI TestClient`                     | Test protected API endpoints, asserting that they return 401 without a valid token and 200 with a valid mock token.                                   |
| **E2E**         | `Cypress`                                | Implement a custom Cypress command (`cy.login()`) that programmatically authenticates with Clerk to get a session cookie for the test environment.    |
| **Component**   | `React Testing Library` / `@clerk/testing` | Use Clerk's testing library to wrap components and mock different authentication states (`isSignedIn: true/false`).                                   |

---

## 6 · Documentation & Artifacts

| File / Location                       | Update / Create                                                                                    |
| :------------------------------------ | :------------------------------------------------------------------------------------------------- |
| `docs/architecture/ADR-001_Clerk.md`  | Mark this ADR as "Accepted" and link to this user story.                                           |
| `docs/guides/DEVELOPMENT_GUIDE.md`    | Add a new section on setting up Clerk environment variables (`CLERK_SECRET_KEY`, etc.).              |
| `docs/guides/PROJECT_OVERVIEW.md`     | Update the "Authentication" section to describe the new Clerk-based JWT flow.                      |
| `.env.example` files (frontend/backend) | Add placeholders for the required Clerk environment variables.                                     |

---

## 7 · Risks & Mitigations

| Risk                      | Impact                               | Mitigation                                                                                                                |
| :------------------------ | :----------------------------------- | :------------------------------------------------------------------------------------------------------------------------ |
| **Webhook Security**      | Malicious actor could create fake users. | Use the `svix` library as recommended by Clerk to verify the signature of every incoming webhook request. Reject any unverified requests. |
| **Vendor Lock-in**        | Difficult to move away from Clerk later. | Acknowledge this as an acceptable trade-off for MVP velocity. The abstraction (local `users` table) provides a seam for future migration if ever needed. |
| **Environment Variable Leak** | Compromised Clerk project.             | Use a secret management service (e.g., Doppler, GitHub Secrets) for production and CI/CD environments. Never commit keys to git.    |

---

## Definition of Done

* The old cookie-based authentication code is fully removed.
* A new user can sign up, sign in, and sign out using the Clerk UI.
* Authenticated API requests from the frontend to the backend are successfully authorized using Clerk-issued JWTs.
* The `users` table in our database is correctly populated via Clerk webhooks.
* All acceptance criteria are met, and all tests (unit, integration, E2E) are passing in CI.
* All relevant documentation has been updated to reflect the new authentication architecture.
