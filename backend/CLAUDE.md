# Backend (FastAPI)

Design reference: `docs/02-architecture/backend.md`. Run `just` recipes from the repository root, or
`uv run ...` from this folder.

## Layout (`src/app/`)

- `main.py`: `create_app()` factory. Run with `uvicorn --factory app.main:create_app`. Importing it never reads
  the environment.
- `api/router/<domain>.py`: HTTP only. Register each router in `api/routes.py`.
- `schemas/<domain>.py`: Pydantic v2 models (`XCreate`, `XUpdate`, `XRead`).
- `services/<domain>.py`: business logic and transactions. Never import FastAPI.
- `models/<aggregate>.py`: SQLAlchemy 2.0 `Mapped[...]` models on `Base`.
- `core/`: settings, DB session, logging, errors, middleware. `helpers/` app-aware glue; `utils/` pure functions.
- Dependencies point one way: `api -> services -> models`.

## Conventions

- Async everywhere (async routes, `AsyncSession`). Never block the event loop.
- Numpy-style docstrings on every public module, class and function, including `Parameters`, `Returns`, `Raises`.
- Full type annotations; mypy runs `--strict`. No bare `# type: ignore`; use a specific error code.
- Raise domain errors from `app/core/errors.py` (`NotFoundError`, `ConflictError`, ...). They become the standard
  envelope `{"error": {"code", "message", "details", "request_id"}}`.
- Read config only through `get_settings()`. A new setting also goes in `.env.example` (a test enforces this).
- Log with `structlog.get_logger(__name__)`; never log secrets or PII.
- All routes live under `/api/v1`. `/health` and `/ready` also exist at the root for load balancers.

## Database

- Schema changes are Flyway SQL in `db/migrations/V<yyyymmddHHMM>__<snake_name>.sql` (`just db-new <name>`).
- Update the matching ORM model in the same change. The schema drift test fails if they disagree.
- Use expand/contract for breaking changes; use `CREATE INDEX CONCURRENTLY` for large tables.

## Tests (`tests/`)

- `unit/` needs no database. `integration/` uses Testcontainers Postgres and skips itself without Docker.
- Override dependencies with `app.dependency_overrides`; use the `client` fixture from `tests/conftest.py`.
- Link a test to a Jira criterion with `@pytest.mark.ac("AIFS-0001", "AC-1")`.
- Coverage must stay at or above 80% (`--cov-fail-under` is configured in `pyproject.toml`).
