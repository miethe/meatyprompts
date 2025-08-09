# Development Guide

## Clerk Configuration

Set the following environment variables for local development:

- `NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY` – publishable key for the frontend.
- `CLERK_SECRET_KEY` – backend secret key.
- `CLERK_JWT_VERIFICATION_KEY` – key used to verify Clerk-issued JWTs.
- `CLERK_WEBHOOK_SECRET` – secret for verifying webhook signatures.

Copy the provided `.env.example` files in `apps/web` and `services/api` to `.env`
and fill in the appropriate values.
