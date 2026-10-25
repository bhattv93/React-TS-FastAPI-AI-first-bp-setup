---
name: new-db-migration
description: Create a Flyway SQL migration together with its SQLAlchemy model change and verify them with the schema drift test. Use when adding or changing tables, columns, indexes or constraints.
argument-hint: "[snake_case_description]"
---

# New database migration

**Canonical example:** `backend/db/migrations/V202610240001__create_app_meta.sql` with
`backend/src/app/models/app_meta.py`. Applied migrations are immutable; this skill only ever adds files.

## Steps

1. **Create the file:** `just db-new <snake_name>` (prints the new path under `backend/db/migrations/`).
2. **Write the SQL.** Name every constraint (`pk_`, `fk_`, `uq_`, `ix_`). Use expand/contract for anything
   breaking: add nullable, backfill, enforce, drop in a later release. Use
   `CREATE INDEX CONCURRENTLY` (own migration, `-- flyway:executeInTransaction=false`) on large tables.
   No `DROP`/`TRUNCATE`/unscoped `DELETE` unless an acceptance criterion requires it.
3. **Update the model** in `backend/src/app/models/<aggregate>.py` so column types, nullability and
   primary key match the SQL exactly, and export it from `models/__init__.py`.
4. **Verify:** `just db-up` applies the migration with the real Flyway image, then `just test-backend`
   runs the drift test (needs Docker). Fix the model or the SQL until it passes.
5. Mention in the PR that the migration is forward-only (the Community edition has no undo).

## Never

Edit an existing `V*.sql`, hand-edit `flyway_schema_history`, or run `flyway clean`.
