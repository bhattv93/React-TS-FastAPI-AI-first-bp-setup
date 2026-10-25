# AI-First React-TS + FastAPI Boilerplate

A gold-standard monorepo for products built on **React + TypeScript** and **FastAPI**, set up for
**AI-first development**: Claude Code as the primary tool, GitHub Copilot alongside, Jira as the source of
requirements, and automated quality gates that make AI-written code safe to merge.

## What you get

| Area | Included |
|------|----------|
| Backend | FastAPI, Pydantic v2, SQLAlchemy 2.0 async, Flyway SQL migrations, PostgreSQL, structured logging, request IDs, one error envelope |
| Frontend | React, strict TypeScript, Vite, Tailwind CSS, React Router, TanStack Query behind hooks, a typed client generated from the API |
| Quality gates | black, isort, pylint (numpy docstrings), mypy `--strict`, pytest; prettier, eslint, tsc, vitest + Testing Library; **80% coverage** |
| CI | GitHub Actions: path-filtered jobs and one required `gate` check |
| AI layer | `CLAUDE.md` hierarchy, Copilot pointer, shared VS Code settings, Jira over MCP |
| Delivery | One container image for ECS Fargate or Lambda, S3 + CloudFront for the SPA (blueprint) |

## Quick start

Prerequisites and step-by-step installation are in the setup guide:

- **Windows:** [docs/10-setup/windows.md](docs/10-setup/windows.md)
- **macOS:** [docs/10-setup/macos.md](docs/10-setup/macos.md) (planned)

Once the tools are installed, from the repository root:

```text
just setup        # install dependencies and git hooks (once)
just db-up        # Postgres + migrations (Docker)
just dev-backend  # API on http://localhost:8000
just dev-frontend # SPA on http://localhost:5173
just check        # every gate CI runs
```

Run `just` with no arguments to list all recipes.

## Repository layout

```text
backend/    FastAPI app (src/app), Flyway migrations (db/migrations), tests
frontend/   React app (src), generated API client (src/api)
docs/       Blueprint, ADRs, setup guides, per-story specs
.claude/    Shared Claude Code settings (rules, skills and agents are planned)
.github/    Workflows, CODEOWNERS, PR template, Copilot pointer
.vscode/    Shared editor settings and recommended extensions
```

## Documentation

Start at [docs/README.md](docs/README.md). It lists the reading order, the architecture, the AI-first
operating model, the quality gates, the delivery design and the roadmap.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md). Licensed under the [MIT License](LICENSE).
