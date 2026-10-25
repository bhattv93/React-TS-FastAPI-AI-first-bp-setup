---
status: accepted
owner: tech-lead
last-reviewed: 2026-10-24
---

# ADR-0003: uv for Python, pnpm for the frontend

- **Status:** Accepted
- **Date:** 2026-10-24

## Context

We need reproducible installs, a committed lockfile, fast CI, and one obvious command an AI agent can run
on Windows, macOS and Linux.

## Decision

- **Backend:** [uv](https://docs.astral.sh/uv/). Covers the Python version (`.python-version` = 3.13), the
  virtualenv, `pyproject.toml` deps with `[dependency-groups] dev`, and a committed `uv.lock`. Commands are
  `uv sync` and `uv run <tool>`. CI uses `uv sync --locked`.
- **Frontend:** pnpm, pinned via `"packageManager"` in `package.json` with Corepack enabled. `pnpm-lock.yaml`
  is committed. CI uses `pnpm install --frozen-lockfile`.

## Alternatives considered

| Option | Pros | Cons |
|--------|------|------|
| Poetry | Mature | Slower; separate Python version management |
| pip + requirements.txt | Universal | No real lockfile/resolution story |
| npm | Default | Slower, larger `node_modules` |

## Consequences

- All docs, skills and CLAUDE.md examples use `uv run …` and `pnpm …`. Agents never call bare `pip` or `npm`.
- Dependabot supports both `uv` and `pnpm` ecosystems (see dependencies-and-versioning).
