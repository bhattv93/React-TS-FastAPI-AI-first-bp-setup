---
status: draft
owner: tech-lead
last-reviewed: 2026-10-24
---

# Vision and Scope

## Vision

A **gold-standard, AI-first boilerplate** for products built on **React + TypeScript** and **FastAPI**. It should
let a team start a new project and get:

1. A clean, conventional codebase that any developer, human or AI, can navigate on day one.
2. Quality gates that make AI-generated code safe to merge: lint, format, types, docstrings, tests, and
   coverage of at least 80%.
3. An AI layer, built Claude Code first with GitHub Copilot alongside, that turns a Jira story into a spec,
   code, tests and a PR with little friction.
4. A deployment path to AWS: Lambda or ECS for the backend, S3 + CloudFront for the frontend. Everything is
   automated through GitHub Actions.

## Who it is for

| Persona | Needs |
|---------|-------|
| Developer (primary Claude Code user) | Fast, correct generation; context that stays lean; skills for repeat work |
| Developer (Copilot in VS Code) | The same conventions without a second set of instructions |
| Tech lead / maintainer | Enforceable standards, reviewable AI output, ADRs, CODEOWNERS |
| Product owner / BA | Jira stories with acceptance criteria that drive the build directly |
| DevOps | One image, IaC, OIDC deploys, observability |

## In scope (v1)

- The monorepo skeleton (`backend/`, `frontend/`, `infra/`, `docs/`), with a working "reference feature"
  that demonstrates every layer.
- Backend quality gates (pylint, black, isort, mypy, numpy docstrings, pytest) and frontend gates (eslint,
  prettier, tsc, vitest + RTL), with coverage ≥80%.
- GitHub Actions for PR gates and CD to AWS (dev/staging/prod).
- The AI layer:
  - `CLAUDE.md` tree, `.claude/rules`, skills, subagents, hooks
  - MCP (Jira)
  - the Copilot pointer and VS Code settings
- Jira spec-driven workflow: templates, DoR/DoD, traceability.
- Observability baseline: structured logs, request IDs, CloudWatch, traces, health checks.

## Out of scope (v1)

- Auth provider integration (Cognito or OIDC). There is a placeholder dependency hook only, and it is a
  roadmap candidate.
- Multi-region and DR, beyond documented guidance.
- Mobile clients and SSR (Next.js); the frontend is a static SPA by design.
- LLM features *inside* the product. "AI-first" here means AI-first **development**.

## Scale assumptions

| Dimension | v1 assumption | Designed to grow to |
|-----------|---------------|---------------------|
| Team | 3–10 devs, one or two squads | Several squads, each owning a folder |
| Services | 1 API, 1 SPA | N services in the same monorepo (see [scaling path](03-ai-first/context-strategy.md#scaling-path)) |
| Traffic | Low to moderate | ECS autoscaling; Lambda for spiky workloads |
| AI usage | Most code AI-written, all of it human-reviewed | Same, with more automation (agents in CI) |

## Success criteria

- A new developer runs the app locally and opens a green PR within one day, with no tribal knowledge needed.
- A Jira story with good ACs reaches a reviewed PR mostly through skills.
- Every PR is gated; `main` is always deployable.
- Root `CLAUDE.md` stays at 150 lines or fewer, and no fact is duplicated across AI instruction files.
