---
status: accepted
owner: tech-lead
last-reviewed: 2026-10-24
---

# ADR-0001: Monorepo with folder-scoped AI context

- **Status:** Accepted
- **Date:** 2026-10-24

## Context

Backend and frontend ship together and share an API contract. The team relies heavily on AI agents to write
code. The repo will start small but must scale to more services. In a monorepo, one flat instruction file
grows without limit, costs context in every session, and mixes Python and TypeScript guidance.

## Decision

One Git monorepo (`backend/`, `frontend/`, `infra/`, `docs/`). AI context is **scoped to folders**:

- A lean root `CLAUDE.md` (≤150 lines) holds only repo-wide facts.
- `backend/CLAUDE.md`, `frontend/CLAUDE.md` and `infra/CLAUDE.md` load on demand, when an agent works in
  that folder.
- `.claude/rules/<area>/*.md` with `paths:` globs load only for matching files.
- Procedures live in skills, which load only when invoked.

Full design: [03-ai-first/context-strategy.md](../03-ai-first/context-strategy.md).

## Alternatives considered

| Option | Pros | Cons |
|--------|------|------|
| Polyrepo (frontend / backend separate) | Smaller context per repo | Contract drift, cross-repo PRs, duplicated AI config |
| Monorepo with a single root CLAUDE.md | Simple | Context bloat, lower adherence past ~200 lines, irrelevant rules loaded |
| **Monorepo + folder-scoped context** | Lean sessions, scales per service | More files to govern (see md-governance) |

## Consequences

- Each new service gets its own `CLAUDE.md`, rules folder and (optionally) nested `.claude/skills/`.
- Requires the governance process in [md-governance.md](../03-ai-first/md-governance.md) to prevent drift.
- CI uses path filters so backend-only PRs don't run frontend jobs.
