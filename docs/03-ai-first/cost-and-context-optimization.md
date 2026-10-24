---
status: draft
owner: tech-lead
last-reviewed: 2026-10-24
---

# Cost and Context Optimization

How to get the most out of Claude Code and Copilot **per dollar and per token**, without lowering quality.
Decision record: [ADR-0011](../adr/0011-tiered-ai-operating-model.md). Sources: Anthropic's
[cost guide](https://code.claude.com/docs/en/costs), [prompt caching](https://code.claude.com/docs/en/prompt-caching)
and [model configuration](https://code.claude.com/docs/en/model-config) pages.

## The principle: the cheapest technique that works

Cost scales with **context size × number of turns × model price**. Climb the ladder only when the level below
cannot do the job. Each level is a deliberate choice, not a default.

| Level | Technique | Reach for it when | Where it lives in this repo |
|-------|-----------|-------------------|-----------------------------|
| 0 | **Hygiene**: small `CLAUDE.md`, path-scoped rules, lazy skills, deferred MCP tools, `/clear` per story, specific prompts | Always | `CLAUDE.md`, `.claude/rules/`, [md-governance](md-governance.md), lint in `scripts/check_ai_config.py` |
| 1 | **Model and effort routing** | Every session | [Routing table](#model-and-effort-routing) below |
| 2 | **Deterministic offloading**: hooks and scripts do mechanical work | Formatting, protected files, story context | `.claude/hooks/` |
| 3 | **Subagents**: isolate noisy work, return a summary | Test runs, log triage, broad searches, reviews | `.claude/agents/` |
| 4 | **Advisor**: a cheaper main model consults a stronger one at decision points | Long, multi-step work where plan quality matters | [agents-and-supervision](agents-and-supervision.md#advisor-pilot) |
| 5 | **Agent teams / workflows**: parallel agents | Parallel review, competing-hypothesis debugging, audits, migrations | [agents-and-supervision](agents-and-supervision.md#agent-teams-playbook) |
| 6 | **Supervision**: spec approval, plan mode, hooks, gates, human merge | Always, on top of the above | [self-improving-loop](self-improving-loop.md) |

## Model and effort routing

Choose at the **start of a session**. Switching models or (on most models) effort mid-task discards the prompt
cache and re-reads the whole conversation at full price.

| Task | Model | Effort | Why |
|------|-------|--------|-----|
| Routine implementation, tests, refactors | Sonnet (project default) | default | Best cost/quality for most coding |
| Searching, summarising logs and test output, AC-to-test mapping | Haiku (subagent) | low | Read-heavy work needs no deep reasoning |
| Architecture decisions, ambiguous bugs, security review | Opus | high | Pay for reasoning only where it changes the outcome |
| Long refactor with hard decision points | Sonnet + Opus advisor | default | Strong guidance at key moments, cheap turns in between |
| Trivial edits, renames | Sonnet | low | Thinking tokens are billed as output |

Subagent models are pinned in their definition (`model:`), and the AI-config lint rejects an agent without
one, so nothing silently inherits the most expensive model.

## Protect the prompt cache

The cache matches the **start** of each request, so anything that changes early invalidates everything after.

| Do | Avoid |
|----|-------|
| Pick model and effort once, at session start | Switching models mid-task (Claude Code asks while the cache is warm) |
| Run `/compact` at natural breaks, or `/clear` between unrelated stories | Letting a 6-hour session grow, then asking one-line questions |
| Keep MCP servers few and deferred (tool search is the default) | Connecting or removing servers mid-session when tools load up-front |
| Use skills, which append instructions without touching the prefix | Editing `CLAUDE.md` and expecting it to apply mid-session (it applies after `/clear`, `/compact` or restart) |
| Use `/rewind` to abandon a bad path | Re-prompting from scratch after a wrong turn |

**Cache lifetime depends on how you are billed.** On a Claude subscription the main conversation gets a
one-hour cache within plan usage; with an API key or a cloud provider it defaults to five minutes. For API-key
users who work in bursts with breaks, setting `promptCacheTtl` to `1h` can pay for itself (cache writes cost more).
Verify with `/usage`, whose `Prompt cache (main)` line shows the hit rate and why the last miss happened.
Subagents, workflows and agent-team teammates use the five-minute bucket unless `subagentPromptCacheTtl` is set.

## Keep context small by design

- **Instructions:** root `CLAUDE.md` is 150 lines or fewer, folder files 100 or fewer, rules 60 or fewer and
  scoped with `paths:`. Procedures live in skills, which cost nothing until invoked.
- **Never `@import` docs** into `CLAUDE.md`; imports load in full every session.
- **Code intelligence:** the `pyright-lsp` plugin gives symbol navigation instead of grep-and-read.
- **Delegate noise:** ask the `test-triage` subagent to run `just check` and report a 25-line summary
  instead of streaming raw output into the main conversation.
- **Be specific:** "add a `status` filter to `GET /api/v1/items`" beats "improve the API".
- **Verify with targets:** tests and acceptance criteria let the model check its own work and avoid re-work.
- **Hooks over reading:** a hook that trims or filters output before the model sees it can turn tens of
  thousands of tokens into hundreds. Anthropic's cost guide has a ready test-output filter to adapt.

## Budgets and alerts (starting points)

Anthropic reports about **$13 per developer per active day** on average, $150 to $250 per developer per month,
and under $30 per active day for 90% of users. Use these as the **initial** baseline for a pilot, then replace
them with your own measured numbers. See [usage-telemetry-and-chargeback](usage-telemetry-and-chargeback.md)
for the dashboards and alarms.

| Signal | Starting alert | Likely cause |
|--------|----------------|--------------|
| Developer daily cost | Above the 90th percentile of the pilot | Long uncleared session, Opus as default, agent teams |
| Cache hit ratio | Below 80% | Mid-task model switches, MCP churn, short TTL |
| Agent-team or workflow cost | Any run above an agreed cap | Too many teammates; no small-slice trial |
| Cost per merged PR | Rising week over week | Rework, vague prompts, weak specs |

## Measure, then adjust

Run `/usage` for the session breakdown and recommendations (it attributes usage to skills, subagents, plugins
and MCP servers and suggests changes such as trimming a bloated `CLAUDE.md`). Review the weekly dashboard and the
monthly `/insights` reports in the [self-improving loop](self-improving-loop.md), and change one thing at a time.
