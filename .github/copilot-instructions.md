# Copilot instructions

This is a monorepo: a FastAPI + Pydantic v2 + SQLAlchemy 2 (async) backend in `backend/` and a React +
TypeScript (strict) + Vite + Tailwind frontend in `frontend/`. Python 3.13, uv and pnpm.

Project conventions live in `CLAUDE.md`, `backend/CLAUDE.md`, `frontend/CLAUDE.md` and `.claude/rules/`.
Follow them; do not duplicate them here.

Non-negotiables (also enforced by CI via `just check`):

- Backend layering is router -> service -> model. Routers never touch the DB; services never import FastAPI.
- Frontend layering is page -> hook -> service -> generated client. Components never call `fetch`.
- numpy-style docstrings on every public Python object; mypy `--strict`; black + isort; pylint clean.
- TypeScript `strict`; ESLint and Prettier clean. Use hooks over `services/` directly in components.
- Every change ships with tests. Coverage must stay at or above 80%.
- Never edit `frontend/src/api/schema.d.ts` (generated) or an already-applied Flyway migration in
  `backend/db/migrations/`. Add a new migration instead.
- No secrets in the repo. Configuration comes from environment variables. Never put PII, production data
  or customer-confidential material into code, fixtures, logs or prompts.

Every PR references a Jira key such as `AIFS-0001`, and acceptance criteria live in
`docs/specs/<KEY>.md`. Branches are named `type/AIFS-0001/short-slug`. PR titles look like
`feat(scope): summary (AIFS-0001)`.
