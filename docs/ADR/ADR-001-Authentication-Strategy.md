# ADR-001: Authentication Strategy

**Status:** Proposed (Ready for acceptance)

**Date:** 2025-08-09

## **High-Level Recommendation**

My definitive recommendation is to adopt a managed **Auth-as-a-Service (AaaS)** provider. Specifically, **Clerk**.

While libraries like FastAPI Users are excellent for backend-only projects and NextAuth (Auth.js) is superb for Next.js-only projects, our stack's distributed nature (separate frontend, mobile, and backend) creates a challenge that these libraries are not optimally designed to solve.

An AaaS provider like Clerk solves the problem holistically by treating authentication as a separate, centralized service that our frontends and backend all talk to, rather than trying to build and synchronize auth logic within each part of our stack. This approach maximizes development speed, security, and future-readiness.

## **Context and Problem Statement**

MeatyPrompts requires a robust, secure, and scalable authentication system that supports both individual user accounts and future team-based (multi-tenant) functionality. The system must provide a seamless experience across three distinct clients:

1. A **Next.js web application**.
2. A **React Native mobile application**.
3. A **FastAPI backend** that serves as the single source of truth for business logic and data.

We need a solution that is fast to implement for our MVP, minimizes security burdens, and provides a clear path for scaling to support team features like invitations and role-based access control (RBAC).

## **Decision Drivers**

* **Speed to MVP:** How quickly can we implement secure user sign-up, sign-in, and session management?
* **Developer Experience (DX):** How much boilerplate code is required? How easy is it to integrate and maintain?
* **Web & Mobile Parity:** Does the solution provide a consistent authentication flow for both web and mobile clients without significant divergence in logic?
* **Security & Maintenance:** Who is responsible for password hashing, session token security, multi-factor authentication (MFA), and keeping up with security best practices?
* **Future-Proofing for Teams:** Does the solution have a clear path to supporting organizations, invitations, and team roles?

## **Considered Options**

## **Option 1: Backend-Driven Library (e.g., FastAPI Users)**

* **Description:** A Python library that provides all the backend logic for user management, including database models, password hashing, and OAuth provider integration. The frontend would be responsible for building all UI components and managing JWT session tokens manually.
* **Pros:**
  * High degree of control and flexibility.
  * Keeps all user data within our own database from the start.
  * Free and open-source.
* **Cons:**
  * **Slowest implementation time:** Requires us to build all UI for sign-in, sign-up, password reset, etc., from scratch for both web and mobile.
  * **High maintenance burden:** We are responsible for the security of the implementation.
  * **Poor DX for session management:** Manually handling JWT storage, refresh tokens, and secure attachment to API requests on the client is error-prone.
  * Team features would need to be built entirely from scratch.

## **Option 2: Frontend-Driven Library (e.g., NextAuth.js / Auth.js)**

* **Description:** A library that is tightly integrated with Next.js to provide a seamless auth experience for the web application. It would act as a "backend for frontend" for auth, proxying credentials to our FastAPI API.
* **Pros:**
  * Excellent developer experience *for the Next.js app*.
  * Handles session management and CSRF protection for the web.
  * Free and open-source.
* **Cons:**
  * **No mobile support:** The React Native app cannot use NextAuth, requiring a completely separate authentication flow. This violates the Web & Mobile Parity driver.
  * Creates a confusing split in logic, where some auth logic lives in the Next.js server and some in our FastAPI backend.
  * Still requires us to build the core user management logic (password hashing, etc.) in FastAPI for the "credentials" provider.

## **Option 3: Managed Auth-as-a-Service (e.g., Clerk, Supabase Auth, Auth0) - RECOMMENDED**

* **Description:** A third-party service that handles the entire user lifecycle. We integrate their SDKs into our frontends and backend. Clerk is the specific recommendation due to its modern DX and features.
* **Pros:**
  * **Fastest implementation time:** Provides pre-built, customizable React components (`<SignIn>`, `<SignUp>`, `<UserProfile>`) for both Next.js and React Native, reducing weeks of UI development to hours.
  * **Superior Security:** Outsourced to a specialized company that handles password policies, session hijacking prevention, MFA, and more.
  * **Excellent Web & Mobile Parity:** Both clients use the same JWT-based authentication flow against our FastAPI backend.
  * **Built-in Team Support:** Clerk has a first-class "Organizations" feature, perfectly aligning with our roadmap for team accounts and de-risking a major future epic.
  * **Simplified Backend:** The FastAPI backend's only auth responsibility is to *verify* stateless JWTs on incoming requests. It does not need to store passwords or manage sessions.
* **Cons:**
  * Dependency on a third-party service.
  * Financial cost at scale (though the free tier is generous and sufficient for the MVP).
  * Less control over the exact user model, though this is mitigated by syncing to our local DB.

## **Decision**

We will adopt **Clerk** as our primary authentication provider for MeatyPrompts.

This decision prioritizes development speed, security, and a unified experience across our web and mobile platforms. By outsourcing the complex, non-differentiating problem of authentication, we can focus our limited engineering resources on building our core product features. Clerk's built-in support for Organizations provides a significant strategic advantage by de-risking our future roadmap for team functionality.

## **Implementation Strategy**

1. **Frontend (Web & Mobile):**
    * Integrate the Clerk React/Next.js and React Native SDKs.
    * Use Clerk's pre-built components (`<ClerkProvider>`, `<SignIn>`, `<SignUp>`) to handle all user-facing auth UI.
    * The Clerk SDK will securely manage the session on the client. For API calls, the SDK will provide a short-lived JWT.

2. **Backend (FastAPI):**
    * Our API will be stateless. Every request to a protected endpoint must include the JWT from the Clerk SDK in the `Authorization: Bearer <token>` header.
    * We will create a reusable FastAPI dependency (`get_current_user`) that:
        a. Extracts the JWT from the request header.
        b. Fetches Clerk's public keys (JWKS) to verify the token's signature.
        c. Validates the token's claims (e.g., expiration time, issuer).
        d. Extracts the `sub` (user ID) claim from the validated token.
        e. (Optional) Loads our internal user model from our database using this ID.
        f. Injects the authenticated user object into the route handler.
    * This verification ensures that our API only responds to requests from valid, authenticated users.

3. **Database Synchronization:**
    * We will maintain a `users` table in our PostgreSQL database to store application-specific information and establish foreign key relationships (e.g., a prompt's `owner_id`).
    * This table will have a column `clerk_user_id` which is a unique key.
    * We will configure a **Clerk Webhook** to send an event to a special endpoint on our API whenever a new user signs up (`user.created`).
    * This endpoint will then create a new record in our local `users` table, effectively syncing our database with Clerk's user base.

## **Consequences**

* **Positive:**
  * Massively accelerated development timeline for the MVP.
  * Reduced security surface area and maintenance overhead.
  * A single, consistent auth flow for web, mobile, and API.
  * Team/Organization features are pre-built and ready for us when we need them.
* **Negative:**
  * We will have a hard dependency on Clerk.
  * There will be a recurring financial cost as we scale beyond the free tier. This is a known and accepted trade-off for the value provided.
