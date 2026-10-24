---
status: draft
owner: backend-lead
last-reviewed: 2026-10-24
---

# Data Layer and Migrations

Decision: [ADR-0004](../adr/0004-flyway-over-alembic.md). SQLAlchemy 2.0 is the ORM. Flyway SQL owns the schema.

## ORM

- `app/core/db.py`: `create_async_engine(settings.database_url, pool_pre_ping=True)`,
  `async_sessionmaker(expire_on_commit=False)`, and `get_session()` dependency.
- `app/models/base.py`: `class Base(DeclarativeBase)` with a naming convention for constraints, which keeps
  index and constraint names identical to the ones in the SQL migrations.
- Models use typed columns: `id: Mapped[int] = mapped_column(primary_key=True)`.
- Every table has `created_at`/`updated_at` (`timestamptz`, server defaults), defined via a mixin and in SQL.
- Services own transactions (`async with session.begin():`). Routers never commit.

## Flyway

| Item | Convention |
|------|------------|
| Location | `backend/db/migrations/` |
| Versioned | `V202610241530__create_orders.sql`, a timestamp version that avoids merge collisions between branches |
| Repeatable | `R__views_order_summary.sql` for views and functions |
| Config | `backend/db/flyway.toml`, with the URL, user and password from env (`FLYWAY_URL`, `FLYWAY_USER`, `FLYWAY_PASSWORD`) |
| Validation | `flyway validate` in CI; `validateMigrationNaming=true`; `outOfOrder=false` in prod |
| Immutability | Applied migrations are never edited. A Claude `PreToolUse` hook blocks edits to existing `V*.sql`; Flyway checksums catch the rest |
| Rollback | Forward-fix only (Community edition): write a new `V…__revert_x.sql` |

### Where Flyway runs

| Environment | How |
|-------------|-----|
| Local | `docker compose up db flyway`; the `flyway` service runs `migrate` and exits |
| Tests | Testcontainers Postgres in a session fixture, then the `flyway/flyway` container runs `migrate` against it |
| CI | A Postgres service container, then the `flyway/flyway` container runs `migrate`, then pytest |
| AWS | The deploy job runs Flyway as a **one-off ECS task** (or a CodeBuild/GHA job inside the VPC) *before* rolling out the new app version |

## ORM ↔ schema drift test

`tests/integration/test_schema_drift.py`:

1. Applies Flyway to a fresh test DB.
2. Reflects the DB with `sqlalchemy.inspect` (tables, columns, types, nullability, FKs, indexes).
3. Compares the result with `Base.metadata` and fails with a readable diff.

Any PR that changes `models/` without a migration fails, and so does any migration without a matching model
change.

## Migration safety checklist (in the `new-db-migration` skill)

- Expand/contract for breaking changes: add nullable column → backfill → enforce → remove the old column in
  a later release.
- Create indexes on large tables with `CREATE INDEX CONCURRENTLY`, in its own migration with
  `-- flyway:executeInTransaction=false`.
- No data-destroying statements without an explicit Jira AC and reviewer sign-off.
