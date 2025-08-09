# ADR-001: Migrate Authentication to Clerk

*Status: Accepted*

This ADR records the decision to replace the bespoke cookie-based authentication system with Clerk.
The migration is implemented in user story MP-AUTH-INT-001.

Clerk provides hosted sign-in and sign-up flows, issues stateless JWTs for API access,
and sends webhooks to synchronize user data with the local database.
