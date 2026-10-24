---
status: accepted
owner: tech-lead
last-reviewed: 2026-10-24
---

# ADR-0011: A tiered, cost-aware AI operating model

- **Status:** Accepted
- **Date:** 2026-10-24

## Context

AI-assisted development is fast, but cost grows with context size, turns and model price, and the stronger
mechanisms (agent teams, workflows) can multiply spend. A single technique applied everywhere is either too
expensive or too weak. We also need to see which team spends what, and prove that speed does not cost quality.

## Decision

1. Use the **cheapest mechanism that works**, climbing a ladder: hygiene, model routing, deterministic hooks,
   subagents, advisor, agent teams and workflows, then supervision
   ([cost-and-context-optimization.md](../03-ai-first/cost-and-context-optimization.md),
   [agents-and-supervision.md](../03-ai-first/agents-and-supervision.md)).
2. **Route models explicitly:** Sonnet as the default, Haiku for read-heavy subagents, Opus for reasoning that
   changes the outcome. Every subagent pins a model; the AI-config lint enforces it.
3. **Pilot the advisor** (Sonnet main plus Opus advisor) and keep it only if cost per merged PR improves without
   more rework or escaped defects.
4. **Agent teams stay off by default**, allowed for three named cases, capped at three Sonnet teammates.
5. **`/goal` always has a turn cap; workflows start with a small-slice trial; `ultracode` stays off.**
6. **Measure per team** with OpenTelemetry labels (`team.id`, `cost_center`) delivered through managed settings
   and exported to CloudWatch via ADOT
   ([usage-telemetry-and-chargeback.md](../03-ai-first/usage-telemetry-and-chargeback.md)).
7. Judge changes on a **scorecard** of speed, quality and cost together.

## Alternatives considered

| Option | Pros | Cons |
|--------|------|------|
| Strongest model and every feature for everyone | Simple, fast to start | Unpredictable cost; no evidence it improves quality |
| Cheapest model everywhere | Lowest bill | Quality and rework suffer where reasoning matters |
| **Tiered, measured (chosen)** | Cost matches the task; evidence drives changes | Needs telemetry, discipline and a quarterly review |

## Consequences

- Telemetry must be delivered by managed settings (the repo cannot enable it), so adoption needs an owner.
- The access path (seats, API or Bedrock) is still open and changes advisor availability and the cost source.
- Budgets in the docs are starting points from Anthropic's published averages and must be replaced with pilot data.
