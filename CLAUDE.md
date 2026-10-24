# AI-First React-TS + FastAPI Boilerplate

Monorepo: a FastAPI backend and a React + TypeScript frontend, built spec-first from Jira stories.
Claude Code is the primary AI tool; GitHub Copilot in VS Code reads these same files.

## Stack

- **Backend** (`backend/`): Python 3.13, FastAPI, Pydantic v2, SQLAlchemy 2.0 async, Flyway SQL migrations,
  PostgreSQL, uv. Gates: black, isort, pylint (numpy docstrings), mypy `--strict`, pytest.
- **Frontend** (`frontend/`): React, TypeScript `strict`, Vite, Tailwind CSS, React Router, TanStack Query
  (behind hooks), typed OpenAPI client, pnpm. Gates: prettier, eslint, tsc, vitest + Testing Library + MSW.
- **Deploy**: AWS. One backend image runs on ECS Fargate or Lambda; the SPA goes to S3 + CloudFront.

## Repository map

| Path | What | More context |
|------|------|--------------|
| `backend/` | API, migrations (`db/migrations`), tests | `backend/CLAUDE.md` |
| `frontend/` | SPA, generated API client (`src/api`) | `frontend/CLAUDE.md` |
| `docs/` | Blueprint, ADRs, setup guides, per-story specs (`docs/specs`) | `docs/README.md` |
| `.claude/` | Rules, skills, agents, settings for Claude Code | `docs/03-ai-first/` |
| `.github/` | CI workflows, CODEOWNERS, Copilot pointer, PR template | `docs/06-delivery/ci.md` |

## Commands (run from the repository root)

- `just setup` installs everything and the git hooks (once).
- `just db-up` starts Postgres and applies migrations (Docker).
- `just dev-backend` / `just dev-frontend` run the servers with reload.
- `just check` runs every gate CI runs. Run it before saying work is done.
- `just lint-backend`, `just lint-frontend`, `just test-backend`, `just test-frontend` run one gate.
- `just api-gen` re-exports the OpenAPI schema and regenerates the TypeScript client.
- `just db-new <name>` creates a new Flyway migration file.

Use `uv run ...` for Python and `pnpm ...` for Node. Never call bare `pip` or `npm`.

## Workflow

1. Every change maps to a Jira key shaped like `AIFS-0001` (4-letter project code, hyphen, 4 digits).
2. Branch: `type/AIFS-0001/short-slug`, where type is feature, fix, refactor, chore, docs, test or ci.
3. Requirements and acceptance criteria (`AC-1`...) come from Jira; the spec is `docs/specs/AIFS-0001.md`.
   Do not implement a story whose spec is not approved.
4. Write a failing test for each AC first, then the code.
5. Commits and PR titles: `feat(scope): summary (AIFS-0001)` (Conventional Commits).

## Definition of done

- `just check` passes, coverage is at least 80%, and every AC has a test that asserts it.
- Docs, rules and skills are updated in the same change when a convention changes.

## Hard rules

- Never edit `frontend/src/api/schema.d.ts` (generated: run `just api-gen`).
- Never edit an applied Flyway migration in `backend/db/migrations/`; add a new one.
- Never commit `.env` files or secrets; use `.env.example` and environment variables.
- Keep layers clean: backend router -> service -> model; frontend page -> hook -> service -> client.
- AI access is controlled (ADR-0009): never put secrets, PII, production data or customer-confidential
  material into prompts, fixtures, logs or screenshots. Do not add MCP servers, plugins or other AI tools;
  ask a maintainer. Ask before any outbound network call to a host the task does not name.

## Working economically (details: `docs/03-ai-first/cost-and-context-optimization.md`)

- Pick the model and effort once at session start; switching mid-task discards the prompt cache.
- Run `/clear` between stories. Delegate noisy test or lint runs to the `test-triage` subagent.
- Use `/goal` only with a turn cap. Agent teams and workflows need maintainer approval; `ultracode` stays off.
- Subagents: `code-reviewer`, `spec-verifier`, `test-triage`. Skills are listed by `/` autocomplete.

## Where to read more (open on demand; do not import into context)

- Architecture: `docs/02-architecture/`
- Quality gates and thresholds: `docs/05-quality-gates.md`
- Spec-driven workflow with Jira: `docs/04-spec-driven-development/jira-workflow.md`
- How these instruction files are organised: `docs/03-ai-first/context-strategy.md`
