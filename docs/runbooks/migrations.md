# Migration Runbook

This runbook outlines how to apply and roll back database migrations.

1. Ensure PostgreSQL is running and accessible.
2. Set the database URL if different from `alembic.ini`.
3. Apply migrations:
   ```bash
   alembic upgrade head
   ```
4. To roll back the most recent migration:
   ```bash
   alembic downgrade -1
   ```
5. Extensions `pg_trgm` and `vector` are installed automatically during upgrades.
