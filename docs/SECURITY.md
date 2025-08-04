# Security Policy

We take security seriously.  If you discover a vulnerability in this
template or in applications generated from it, please follow the
responsible disclosure guidelines below.

## Reporting a Vulnerability

1. **Do not open a public issue**.  Instead, email the maintainers at
   `<security@example.com>` with a detailed description of the issue and
   instructions to reproduce.
2. We will acknowledge receipt within 2 business days and will work with
   you to understand and resolve the issue.
3. Once the vulnerability is resolved, we will publish a security
   advisory and credit you (if desired).

## Dependency Policy

Dependencies are kept up to date via Dependabot.  High‑risk
vulnerabilities will trigger an immediate patch release.

## Secret Management

Secrets must **not** be committed to the repository.  Use environment
variables and GitHub encrypted secrets for CI/CD.  Example secret names:

- `EXPO_TOKEN` – used for Expo EAS builds (optional).
- `DATABASE_URL` – used by the API service in production.