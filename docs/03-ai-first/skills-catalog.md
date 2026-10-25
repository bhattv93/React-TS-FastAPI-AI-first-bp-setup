---
status: draft
owner: tech-lead
last-reviewed: 2026-10-24
---

# Skills Catalog

Project skills live in `.claude/skills/<name>/SKILL.md`. Claude Code and Copilot both discover them there
([tool-parity](tool-parity.md)). Authoring standards: [skill-authoring-guide.md](skill-authoring-guide.md).

## Invocation modes

- **User** = `disable-model-invocation: true`. Only a human runs it, as `/name`. Use it for workflow entry
  points and anything with side effects.
- **Auto** = the default. The model may load it when the request matches the description, and a human can
  also run it.
- **Background** = `user-invocable: false`. Reference knowledge that the model loads.

## Catalog (v1)

**Built (milestone M4):** `jira-story-to-spec`, `implement-from-spec`, `new-api-endpoint`, `new-db-migration`, `new-react-page`, `pr-ready`. **Planned:** the rows below that are not in that list. Each built skill points at real code in the repo as its canonical example, so it cannot drift.

| Skill | Mode | What it does | Key supporting files | Claude-only fields |
|-------|------|--------------|----------------------|--------------------|
| `jira-story-to-spec` | User | Pulls a Jira issue (Atlassian MCP) and writes `docs/specs/<KEY>.md` from the template. Flags missing or ambiguous ACs as open questions; it never invents them | `templates/spec.md` (link), `checklist-dor.md` | — |
| `implement-from-spec` | User | Implements an **approved** spec with TDD: plan, then a failing test per AC, then code, then `just check`, then a summary mapping AC to tests | `workflow.md`, `tdd-loop.md` | — |
| `new-api-endpoint` | Auto | Scaffolds the router, schemas, service and tests for one endpoint, following the layering and error envelope | `templates/router.py.tmpl`, `service.py.tmpl`, `test_route.py.tmpl`, `reference.md` | `paths: backend/**` |
| `new-db-migration` | Auto | Writes a Flyway `V<ts>__*.sql`, updates the ORM model, runs the drift test, and applies the migration safety checklist | `scripts/new_migration.py` (timestamped filename), `safety-checklist.md` | — |
| `new-react-page` | Auto | Scaffolds a page, route entry, data hook, service call, MSW handler and RTL test | `templates/*.tsx.tmpl`, `reference.md` | `paths: frontend/**` |
| `new-react-component` | Auto | Scaffolds a component folder (`.tsx`, `.test.tsx`, `index.ts`) with accessible defaults | `templates/` | `paths: frontend/**` |
| `generate-tests` | Auto | Finds uncovered lines from the coverage report and writes meaningful tests, not assertion-free padding | `scripts/coverage_gaps.py`, `good-tests.md` | — |
| `quality-gate` | Auto | Runs `just check` (or one side), parses failures, fixes them, and repeats until the run is green or a limit is hit | `scripts/run_gates.py` | `allowed-tools: Bash(just *)` |
| `pr-ready` | User | Final checklist: gates, AC→test map, docs/rules updated. Writes a conventional PR title with the key (`feat(scope): … (AIFS-0001)`) and a body from the template | `pr-body.md.tmpl` | — |
| `bugfix-from-jira` | User | Bug issue → reproduce with a failing test → fix → regression note on the Jira issue | `workflow.md` | — |
| `adr-new` | User | Creates the next-numbered ADR from `docs/adr/0000-template.md` | — | — |
| `deploy-backend` | User | Triggers the GHA deploy workflow (`gh workflow run`) for an env and watches it. Never runs IaC apply locally | `envs.md` | `allowed-tools: Bash(gh workflow *)` |
| `deploy-frontend` | User | Same as above, for the SPA | `envs.md` | same |

**Not skills:** conventions such as Python style or React patterns belong in `.claude/rules/` (they load by
path, automatically). Hard rules belong in hooks and CI.

## Relationship to installed Claude plugins

The repo's `.claude/settings.json` enables `superpowers`, `code-review`, `skill-creator`,
`claude-md-management`, `code-simplifier`, `playwright`, `pyright-lsp` and `frontend-design`. Project skills
**complement** these and don't re-implement them:

| Need | Use |
|------|-----|
| Brainstorm or plan a feature | `superpowers:brainstorming`, `superpowers:writing-plans` (Claude), or plan mode |
| Strict TDD discipline | `implement-from-spec` (works in both tools). Claude users may also invoke `superpowers:test-driven-development` |
| Local code review | `/code-review`, or the `code-reviewer` subagent |
| Create or eval a skill | `skill-creator` plugin |
| Maintain CLAUDE.md | `claude-md-management:revise-claude-md`, `claude-md-improver` |

## Example layout

```text
.claude/skills/new-api-endpoint/
├── SKILL.md            # ≤200 lines: when to use, inputs, steps, done-criteria, links below
├── reference.md        # layering rules, error envelope, naming (loaded when needed)
├── examples.md         # one complete worked endpoint
└── templates/
    ├── router.py.tmpl
    ├── schema.py.tmpl
    ├── service.py.tmpl
    └── test_route.py.tmpl
```

## Adding a skill

1. Check this catalog and the plugin table first, so you don't create a duplicate.
2. Follow [skill-authoring-guide.md](skill-authoring-guide.md), including the eval step.
3. Add a row here in the same PR. CODEOWNERS on `.claude/` requires tech-lead review.
