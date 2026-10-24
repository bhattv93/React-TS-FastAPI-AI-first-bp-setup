---
status: draft
owner: tech-lead
last-reviewed: 2026-10-24
---

# Start Here

This repository is two things at once:

1. **A tutorial.** A step-by-step path that teaches a team how to build with GenAI (Claude Code and GitHub
   Copilot) on a FastAPI + React TypeScript stack.
2. **A reusable framework.** A working project you can copy, with the guardrails already in place: quality
   gates, spec-driven workflow, controlled AI access, cost visibility and a self-improving loop.

The goal is **faster time to market and faster technical completion, without lowering the quality of what you
ship.** Speed and quality are measured together; one never buys the other.

## Five principles

| # | Principle | What enforces it here |
|---|-----------|----------------------|
| 1 | **Spec first.** Jira is the source of requirements; a reviewed spec is the contract | Spec template, `/jira-story-to-spec`, approval before `/implement-from-spec` |
| 2 | **Tests are the proof.** Every acceptance criterion has a test that can fail | Test-first skills, `spec-verifier`, 80% coverage gates |
| 3 | **Gates are non-negotiable.** AI output meets the same bar as human output | `just check`, CI `gate`, security scans, pre-commit |
| 4 | **Small, cheap context.** Pay only for what the task needs | Path-scoped rules, lazy skills, model routing, [cost guide](03-ai-first/cost-and-context-optimization.md) |
| 5 | **Humans own the merge.** AI proposes and checks; people decide | CODEOWNERS, no auto-merge ([ADR-0012](adr/0012-self-healing-automation-boundaries.md)) |

## The learning path

Work through the labs in order. Each has an objective, the steps, and a check that proves you got it. Allow
about a half day for labs 1 to 4 and a day for the full path.

| Lab | Objective | Do this | Check |
|-----|-----------|---------|-------|
| **1. Set up** | A working machine | Follow [10-setup/windows.md](10-setup/windows.md) (macOS planned) | `just check` is green |
| **2. Read the system** | Know where things live | Skim [02-architecture/overview.md](02-architecture/overview.md), then open `CLAUDE.md`, `.claude/rules/` and `justfile` | You can explain the layers and the two commands you will use most |
| **3. Meet the gates** | Feel what "quality" means here | Break a type, a format rule and a test on purpose; run `just lint-backend` and `just test-backend` | You can name which gate catches which mistake |
| **4. Spec a story** | Turn a Jira story into a spec | Run `/jira-story-to-spec` on a sample story ([templates](04-spec-driven-development/templates/story.md)); review it | A draft spec with every AC in the test plan and no invented criteria |
| **5. Build test-first** | Implement an approved spec | Run `/implement-from-spec`, optionally with `/goal ... or stop after 15 turns` | Every AC has a passing test; `spec-verifier` reports no gaps |
| **6. Change the schema** | Add a table safely | Use the `new-db-migration` skill, then `just db-up` and the drift test | Migration applied by Flyway; model and SQL agree |
| **7. Review and ship** | Hand over a reviewable PR | Run `/pr-ready`; read the `code-reviewer` findings | A PR body with an AC-to-test table; all gates green |
| **8. See the cost** | Understand where tokens go | Run `/usage`; read [cost guide](03-ai-first/cost-and-context-optimization.md); try `test-triage` vs raw output | You can say which habit would save the most on your last session |
| **9. Improve** | Close the loop | Run `/insights`; fill the [insights review](templates/insights-review.md); propose one rule/skill change by PR | One concrete, testable improvement |
| **10. Operate** (later) | Deploy and observe | [CI](06-delivery/ci.md), [AWS](06-delivery/aws-backend.md), [observability](06-delivery/observability.md) | Planned with milestones M5 and M6 |

> Labs 4 to 7 need a Jira story and the Atlassian MCP connection. Without Jira access, paste the story text;
> the skills accept it.

## The scorecard

Judge every change to the process on **all three groups together**. A faster pipeline that raises defects, or a
cheaper one that raises rework, is not an improvement.

| Group | Metric | Where it comes from |
|-------|--------|---------------------|
| **Speed** | Lead time from story start to merge | Jira and Git timestamps |
| | PRs merged per developer per week | GitHub |
| | Time from "approved spec" to first green CI | CI history |
| **Quality** | Change failure rate (deploys that need a fix or rollback) | CD pipeline, incidents |
| | Escaped defects (bugs found after release) | Jira bug tickets |
| | Review rework (rounds of change requests per PR) | GitHub |
| | Coverage held at 80% or more; mutation spot-checks on AI-written tests | CI |
| **Cost** | Cost per merged PR, by team | [Telemetry](03-ai-first/usage-telemetry-and-chargeback.md) |
| | Cache hit rate; share of spend by skill and subagent | Telemetry, `/usage` |
| | Time-to-fix for vulnerabilities vs the 7/30/90-day targets | [Vulnerability policy](07-engineering-process/vulnerability-management.md) |

Take a **baseline for four weeks before adopting**, then compare monthly. Numbers in these docs are starting
points; replace them with your own.

## Where to go next

- Reusing this in your organisation: [11-adoption-playbook.md](11-adoption-playbook.md)
- The full document map: [README.md](README.md)
- Why the AI layer looks the way it does: [03-ai-first/context-strategy.md](03-ai-first/context-strategy.md)
