---
status: draft
owner: tech-lead
last-reviewed: 2026-10-24
---

# Blueprint Docs — React-TS + FastAPI AI-First Boilerplate

These docs describe the target state of this repository *before* it is built. They are the spec for the
scaffold, and their milestones and stories become the first Jira epics (see [08-roadmap.md](08-roadmap.md)).
The raw input they were derived from is [project-context.md](project-context.md).

## Reading order

| # | Doc | Read it when |
|---|-----|--------------|
| 0 | [00-start-here.md](00-start-here.md) | First: purpose, principles, the learning path (labs) and the speed-and-quality scorecard |
| 1 | [01-vision-and-scope.md](01-vision-and-scope.md) | You are new to the project |
| 2 | [02-architecture/](02-architecture/overview.md) | Before writing any backend/frontend code |
| 3 | [03-ai-first/](03-ai-first/context-strategy.md) | Before using Claude Code / Copilot on this repo, or authoring skills |
| 3b | [03-ai-first/ai-access-governance.md](03-ai-first/ai-access-governance.md) | Before adding any AI tool, MCP server or plugin; what data may never reach an AI |
| 3c | [cost-and-context-optimization](03-ai-first/cost-and-context-optimization.md), [usage-telemetry-and-chargeback](03-ai-first/usage-telemetry-and-chargeback.md), [agents-and-supervision](03-ai-first/agents-and-supervision.md), [self-improving-loop](03-ai-first/self-improving-loop.md) | Cost-aware operating model, per-team usage, which agent mechanism to use, and how the system learns |
| 4 | [04-spec-driven-development/](04-spec-driven-development/jira-workflow.md) | Before picking up a Jira story |
| 5 | [05-quality-gates.md](05-quality-gates.md) | Before opening a PR |
| 6 | [06-delivery/](06-delivery/ci.md) | When touching CI/CD, AWS, or observability |
| 7 | [07-engineering-process/](07-engineering-process/git-and-code-review.md) | Branching, reviews, bugs, dependencies, config |
| 7b | [07-engineering-process/vulnerability-management.md](07-engineering-process/vulnerability-management.md) | Vulnerability scanning cadence, severity SLAs, Wiz, dependency health |
| 8 | [08-roadmap.md](08-roadmap.md) | Planning sprints |
| 9 | [09-scaffold-spec.md](09-scaffold-spec.md) | Building the repo skeleton |
| 10 | [10-setup/](10-setup/README.md) | Setting up a developer machine |
| 11 | [11-adoption-playbook.md](11-adoption-playbook.md) | Reusing this repo as your own project and rolling it out safely |
| — | [adr/](adr/0000-template.md) | Understanding *why* a decision was made |
| — | [specs/](specs/README.md) | Per-story specs generated from Jira |

## Doc conventions

- Every doc starts with frontmatter: `status` (`draft` | `accepted` | `superseded`), `owner`, `last-reviewed`.
- **One fact, one place.** If a doc needs a fact owned by another doc, link to it — do not copy it.
- **Docs are for humans; AI reaches them on demand.** Never `@import` a doc into a `CLAUDE.md` — imports load
  in full every session. Skills and rules link to the specific doc section they need instead.
  See [03-ai-first/md-governance.md](03-ai-first/md-governance.md).
- Decisions live in [ADRs](adr/0000-template.md). Docs state the *what*; ADRs state the *why* and the alternatives.
- A change in convention updates the doc, the matching `.claude/rules/*` file, and the skill(s) that use it in
  the same PR.

## Requirements traceability matrix

Every requirement in [project-context.md](project-context.md) and the doc that covers it.

| # | Requirement (from project-context.md) | Covered in |
|---|---------------------------------------|------------|
| R1 | React + TypeScript frontend | [02-architecture/frontend.md](02-architecture/frontend.md) |
| R2 | FastAPI backend, Python 3.13+, Pydantic v2 | [02-architecture/backend.md](02-architecture/backend.md) |
| R3 | ORM usage | [02-architecture/data-and-migrations.md](02-architecture/data-and-migrations.md), [ADR-0004](adr/0004-flyway-over-alembic.md) |
| R4 | Backend folder structure (app/models/api/router/services/utils/helpers/schemas/tests) | [02-architecture/overview.md](02-architecture/overview.md#repository-layout) |
| R5 | Frontend folder structure (components/pages/services/utils/hooks/tests) | [02-architecture/frontend.md](02-architecture/frontend.md#folder-structure) |
| R6 | Skills that simplify and accelerate the build | [03-ai-first/skills-catalog.md](03-ai-first/skills-catalog.md), [03-ai-first/skill-authoring-guide.md](03-ai-first/skill-authoring-guide.md) |
| R7 | Backend gates: pylint, black, isort, mypy, numpy docstrings, pytest | [05-quality-gates.md](05-quality-gates.md#backend) |
| R8 | Frontend gates: eslint, prettier, vitest + React Testing Library | [05-quality-gates.md](05-quality-gates.md#frontend) |
| R9 | Every PR runs the gates via GitHub Actions | [06-delivery/ci.md](06-delivery/ci.md) |
| R10 | README, CONTRIBUTING, CODEOWNERS, LICENSE | [09-scaffold-spec.md](09-scaffold-spec.md#repository-root) |
| R11 | Usable from both Claude Code and GitHub Copilot; `.github/copilot-instructions.md` | [03-ai-first/tool-parity.md](03-ai-first/tool-parity.md), [ADR-0002](adr/0002-claude-native-instructions-copilot-reads.md) |
| R12 | AI-first enablement folder with examples (codegen, testing, other tasks) | [03-ai-first/ai-workflows-playbook.md](03-ai-first/ai-workflows-playbook.md), [09-scaffold-spec.md](09-scaffold-spec.md#ai-enablement-examples) |
| R13 | Claude Code as primary tool, Copilot as secondary | [03-ai-first/tool-parity.md](03-ai-first/tool-parity.md) |
| R14 | VS Code: recommended extensions + standard settings in `.vscode/` | [09-scaffold-spec.md](09-scaffold-spec.md#vscode) |
| R15 | Backend deploy: local, AWS Lambda, AWS ECS (ECR images) | [06-delivery/aws-backend.md](06-delivery/aws-backend.md), [ADR-0006](adr/0006-dual-backend-target-lambda-and-ecs.md) |
| R16 | Frontend deploy: static hosting on S3 (or other provider) | [06-delivery/aws-frontend.md](06-delivery/aws-frontend.md) |
| R17 | CI/CD pipeline: build, test, deploy | [06-delivery/ci.md](06-delivery/ci.md), [06-delivery/cd-and-environments.md](06-delivery/cd-and-environments.md) |
| R18 | Monitoring and logging | [06-delivery/observability.md](06-delivery/observability.md) |
| R19 | AWS as the core cloud platform | [06-delivery/aws-backend.md](06-delivery/aws-backend.md), [ADR-0007](adr/0007-iac-tool.md) |
| R20 | Jira + agile; user stories on top of the setup | [04-spec-driven-development/jira-workflow.md](04-spec-driven-development/jira-workflow.md), [08-roadmap.md](08-roadmap.md) |
| R21 | Roadmap and milestones | [08-roadmap.md](08-roadmap.md) |
| R22 | Architecture, design patterns, best-practice documentation | [02-architecture/](02-architecture/overview.md) |
| R23 | Jira as the requirements/AC source — spec-driven development | [04-spec-driven-development/jira-workflow.md](04-spec-driven-development/jira-workflow.md) |
| R24 | Test coverage ≥ 80% | [05-quality-gates.md](05-quality-gates.md#coverage) |
| R25 | Code review and approval process | [07-engineering-process/git-and-code-review.md](07-engineering-process/git-and-code-review.md) |
| R26 | Bug and issue handling process | [07-engineering-process/bugs-and-issues.md](07-engineering-process/bugs-and-issues.md) |
| R27 | Scale call-out and Claude methodology; folder-level CLAUDE.md; context management | [03-ai-first/context-strategy.md](03-ai-first/context-strategy.md), [ADR-0001](adr/0001-monorepo-with-folder-scoped-context.md) |
| R28 | Path to scale up later | [03-ai-first/context-strategy.md](03-ai-first/context-strategy.md#scaling-path) |
| R29 | Dependency management and versioning | [07-engineering-process/dependencies-and-versioning.md](07-engineering-process/dependencies-and-versioning.md), [ADR-0003](adr/0003-uv-and-pnpm.md) |
| R30 | Configuration and environment variables per environment | [07-engineering-process/config-and-secrets.md](07-engineering-process/config-and-secrets.md) |
| R31 | Structure and management of the AI `.md` files | [03-ai-first/md-governance.md](03-ai-first/md-governance.md) |
| R32 | Controlled access to GenAI and its tools | [03-ai-first/ai-access-governance.md](03-ai-first/ai-access-governance.md), [ADR-0009](adr/0009-controlled-genai-access.md) |
| R35 | Repo is a tutorial and a reusable framework that speeds delivery without lowering quality | [00-start-here.md](00-start-here.md), [11-adoption-playbook.md](11-adoption-playbook.md) |
| R36 | Lower AI cost and optimal results: context efficiency, model routing, caching, the right technique per task | [03-ai-first/cost-and-context-optimization.md](03-ai-first/cost-and-context-optimization.md), [ADR-0011](adr/0011-tiered-ai-operating-model.md) |
| R37 | Monitor which team uses AI and what it costs | [03-ai-first/usage-telemetry-and-chargeback.md](03-ai-first/usage-telemetry-and-chargeback.md) |
| R38 | Subagents, advisor, agent teams, goal, loop, schedule and workflows, each used where it fits, under supervision | [03-ai-first/agents-and-supervision.md](03-ai-first/agents-and-supervision.md) |
| R39 | Self-healing and learning from previous sessions (insights, memory, automation) | [03-ai-first/self-improving-loop.md](03-ai-first/self-improving-loop.md), [ADR-0012](adr/0012-self-healing-automation-boundaries.md) |
| R34 | Scheduled vulnerability scanning (Wiz, Dependabot, npm audit, pip-audit) and resolvable, harmonious dependencies | [07-engineering-process/vulnerability-management.md](07-engineering-process/vulnerability-management.md), [ADR-0010](adr/0010-vulnerability-and-dependency-health.md) |
| R33 | Step-by-step developer setup (Windows first, then macOS), no machine-specific paths | [10-setup/](10-setup/README.md) |
