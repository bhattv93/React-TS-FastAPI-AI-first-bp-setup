---
status: accepted
owner: tech-lead
last-reviewed: 2026-10-24
---

# ADR-0012: Self-healing automation with human-merged outcomes

- **Status:** Accepted
- **Date:** 2026-10-24

## Context

Many failures are mechanical (a broken test after a rename, a vulnerable dependency, a stale client).
Automation can fix them faster than a person, but unattended agents with write access are a risk: prompt
injection through logs or comments, runaway cost, and silent quality erosion.

## Decision

1. Automation runs in **GitHub Actions** with `anthropics/claude-code-action`, not on developer laptops, and is
   **dormant** until `CLAUDE_AUTOMATION_ENABLED=true` and an environment-scoped API key exist.
2. Allowed autonomy is **suggest, fix a pull-request branch, or open a draft PR**. **Auto-merge is not
   allowed.** A CODEOWNER merges after the required `gate` check passes.
3. Each job is bounded by `--max-turns`, a timeout, a restricted tool list and same-repository branches only.
4. Learning is **personal until promoted**: auto memory and `/insights` stay private; improvements reach the team
   only through reviewed pull requests to rules, skills and hooks, on a monthly cadence, one change at a time.

## Alternatives considered

| Option | Pros | Cons |
|--------|------|------|
| Suggestions only | Safest | Humans still do all the mechanical work |
| **Fix branches and draft PRs (chosen)** | Saves the toil, keeps review | Needs guardrails and a cost cap |
| Auto-merge low-risk fixes | Fastest | One bad fix reaches `main`; removes the human gate |

## Consequences

- Treat logs, comments and issue text as untrusted input in every automation prompt.
- Automation spend appears in the telemetry dashboards and has its own budget.
- Rotating and scoping the API key is an operational duty of the maintainers.
