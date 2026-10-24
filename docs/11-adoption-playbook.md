---
status: draft
owner: tech-lead
last-reviewed: 2026-10-24
---

# Adoption Playbook

How another team turns this repository into its own project and rolls out AI-first development safely.

## 1. Create your copy

1. Use **Use this template** on GitHub (enable *Template repository* in the source repo's settings), or copy the
   repository without its history.
2. Search and replace the placeholders:

| Placeholder | Where | Replace with |
|-------------|-------|--------------|
| `AIFS` / `AIFS-0001` | Docs, skills, hooks, CI PR-title check, `CLAUDE.md` | Your Jira project key (keep the `KEY-0000` shape) |
| `@org/maintainers`, `@org/backend`, ... | `.github/CODEOWNERS` | Your GitHub teams |
| `https://your-company.atlassian.net/...` | `.github/ISSUE_TEMPLATE/config.yml` | Your Jira URL |
| `The AI-First Boilerplate Authors` | `LICENSE` | Your copyright holder, or change the licence |
| `ai-first`, `ai-first-backend`, `ai-first-frontend` | `docker-compose.yml`, `pyproject.toml`, `package.json` | Your product name |
| Ports 5433, 8000, 5173 | `docker-compose.yml`, `backend/.env.example` | Only if they clash |

Then run `just setup` and `just check`. Everything should be green before you change anything else.

## 2. Make the open decisions

These are deliberately left to you. Record each as an ADR.

| Decision | Options | Document |
|----------|---------|----------|
| Claude access path | Team/Enterprise seats, Anthropic API, Bedrock | [telemetry](03-ai-first/usage-telemetry-and-chargeback.md#which-view-you-get-depends-on-the-access-path) |
| Who approves AI-tool, MCP and plugin changes | Named maintainers | [AI access governance](03-ai-first/ai-access-governance.md#open-decisions) |
| Managed settings owner and telemetry sink | Admin console, MDM, file; CloudWatch, Grafana, vendor | [telemetry](03-ai-first/usage-telemetry-and-chargeback.md#open-decisions) |
| Wiz / vulnerability tooling and rota | Connector or CLI | [vulnerability management](07-engineering-process/vulnerability-management.md#open-decisions) |
| Infrastructure as code | CloudFormation (default) or Terraform | [ADR-0007](adr/0007-iac-tool.md), [Terraform guide](06-delivery/terraform-adaptation.md) |
| Whether to enable the Claude automation | Variable + environment secret | [self-improving loop](03-ai-first/self-improving-loop.md) |

## 3. Roll out in phases

| Phase | Weeks | What | Exit criteria |
|-------|-------|------|---------------|
| **0. Baseline** | 1 to 4 | Measure the [scorecard](00-start-here.md#the-scorecard) on your current process. Change nothing | Four weeks of baseline numbers |
| **1. Pilot** | 5 to 8 | One team: labs 1 to 7, Sonnet default, hooks and gates on, telemetry on | Scorecard flat or better on quality; cost per PR known |
| **2. Tune** | 9 to 12 | Add the advisor pilot, monthly `/insights`, the weekly scan; change **one thing at a time** | Written keep/revert decision for each change |
| **3. Scale** | 13+ | More teams, per-team budgets and alarms, agent teams only for approved cases | Each team has a baseline and a budget |

Do not skip phase 0. Without a baseline you cannot tell a real gain from a feeling.

## 4. Protect quality while you speed up

- Never relax a gate to land AI-written code. If a gate blocks you, fix the cause or change the gate through a
  reviewed ADR.
- Review **tests first** for AI-written changes: would they fail if the behaviour were wrong?
- Watch review rework and escaped defects as closely as lead time.
- Keep a human on every merge. Keep the 80% coverage floor.

## 5. Common failure modes

| Symptom | Likely cause | Fix |
|---------|--------------|-----|
| Costs climb, quality flat | Long sessions, Opus default, unused agent teams | Cost guide: clear, route models, review `/usage` |
| AI-written bugs reach review | Weak specs or tests that cannot fail | Tighten acceptance criteria; mutation spot-check |
| Instruction files keep growing | Procedures stuffed into `CLAUDE.md` | Move them to skills and rules; the lint will fail |
| The same review comment repeats | Convention lives only in people's heads | Turn it into a rule or a lint |
| Nobody reads the dashboards | No owner or cadence | Weekly review by the tech lead |

## 6. Keep the framework healthy

Review quarterly: model routing, budgets, allowlists, skill evals, and the known-constraint table. Re-check the
vendor documentation, because Claude Code and Copilot change quickly; the docs in this repo cite their sources
so you can verify.

## 7. Extending

- **A new service:** give it its own `CLAUDE.md`, rules folder and (optionally) nested skills; see
  [context strategy](03-ai-first/context-strategy.md#scaling-path).
- **A new skill:** follow the [authoring guide](03-ai-first/skill-authoring-guide.md); the lint enforces the size
  and metadata rules.
- **Sharing across repositories:** package skills, rules and agents as an internal Claude Code plugin.
