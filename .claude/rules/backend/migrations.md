---
paths:
  - "backend/db/migrations/**"
---

# Flyway migrations

- Create one with `just db-new <snake_name>`; the file is `V<yyyymmddHHMM>__<name>.sql`.
- **Applied migrations are immutable.** The guard hook blocks edits to committed `V*.sql` files; fix mistakes
  with a new migration.
- Use expand/contract for breaking changes: add nullable, backfill, enforce, and drop in a later release.
- `CREATE INDEX CONCURRENTLY` on large tables, in its own migration with
  `-- flyway:executeInTransaction=false`.
- Name constraints explicitly (`pk_<table>`, `fk_<table>_<col>_<ref>`, `uq_<table>_<col>`, `ix_<...>`) so the
  ORM naming convention matches.
- No destructive statements (`DROP`, `TRUNCATE`, unscoped `DELETE`) without an explicit acceptance criterion.
- Update the matching ORM model in the same change, then run `just test-backend` for the drift test.
