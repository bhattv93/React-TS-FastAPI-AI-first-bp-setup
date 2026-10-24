# Task runner for the whole repository. Run `just` from the repository root.
# Install just:  Windows `winget install Casey.Just`   macOS `brew install just`
# Every recipe is one command per line so it behaves the same in PowerShell and POSIX shells.

set windows-shell := ["powershell.exe", "-NoLogo", "-NoProfile", "-Command"]

# List all recipes.
default:
    @just --list

# ---------------------------------------------------------------- setup

# One-time setup: install backend + frontend dependencies and the git hooks.
setup: setup-backend setup-frontend hooks

[working-directory: 'backend']
setup-backend:
    uv sync

[working-directory: 'frontend']
setup-frontend:
    pnpm install

# Install pre-commit hooks (code gates on commit, conventional-commit check on the message).
hooks:
    uv run --project backend pre-commit install --install-hooks --hook-type pre-commit --hook-type commit-msg

# ---------------------------------------------------------------- run

# Start the database and apply migrations (Docker required).
db-up:
    docker compose up -d db flyway

db-down:
    docker compose down

# Re-apply migrations to the running local database.
db-migrate:
    docker compose run --rm flyway

# Create a new empty Flyway migration, e.g. `just db-new create_items`.
db-new name:
    uv run --project backend python backend/scripts/new_migration.py {{name}}

# API with hot reload on http://localhost:8000 (run `just db-up` first).
[working-directory: 'backend']
dev-backend:
    uv run uvicorn --factory app.main:create_app --reload --port 8000

# SPA with hot reload on http://localhost:5173 (proxies /api to the backend).
[working-directory: 'frontend']
dev-frontend:
    pnpm dev

# Start the database, then print how to run both servers (each needs its own terminal).
dev: db-up
    @echo "Database ready. In two terminals run:  just dev-backend   and   just dev-frontend"

# ---------------------------------------------------------------- quality gates

# Everything CI runs. Run this before opening a PR.
check: check-backend check-frontend api-check check-ai-policy check-ai-config

# Fail if AI instruction files break their context budgets (sizes, scoped rules, pinned subagent models).
check-ai-config:
    uv run --project backend python scripts/check_ai_config.py

# Dependency health: lockfiles current, packages compatible, peers resolve, no known vulnerabilities.
# Needs network access (vulnerability databases), so it is not part of `check`; CI runs it on every PR and weekly.
deps-check:
    uv run --project backend python scripts/check_deps.py

# Fail if MCP servers or Claude plugins drift outside .github/ai-policy.json (ADR-0009).
check-ai-policy:
    uv run --project backend python scripts/check_ai_policy.py

check-backend: lint-backend test-backend

check-frontend: lint-frontend test-frontend

# Backend: formatting, imports, lint (numpy docstrings), strict types.
[working-directory: 'backend']
lint-backend:
    uv run black --check .
    uv run isort --check-only .
    uv run pylint src
    uv run mypy src

# Frontend: formatting, lint, types.
[working-directory: 'frontend']
lint-frontend:
    pnpm format:check
    pnpm lint
    pnpm typecheck

# Backend tests with the 80% coverage gate (integration tests need Docker and skip without it).
[working-directory: 'backend']
test-backend:
    uv run pytest

# Frontend tests with the 80% coverage gate.
[working-directory: 'frontend']
test-frontend:
    pnpm test

# Fail if the committed API client is out of date with the backend.
api-check: api-gen
    git diff --exit-code -- frontend/src/api

# Auto-format everything.
[working-directory: 'backend']
fmt-backend:
    uv run isort .
    uv run black .

[working-directory: 'frontend']
fmt-frontend:
    pnpm format

fmt: fmt-backend fmt-frontend

# ---------------------------------------------------------------- API contract

# Export the backend OpenAPI schema to frontend/src/api/openapi.json.
api-export:
    uv run --project backend python backend/scripts/export_openapi.py

# Regenerate the typed TypeScript client from the exported schema.
api-gen: api-export
    pnpm --dir frontend api:gen
