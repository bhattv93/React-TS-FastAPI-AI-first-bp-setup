---
status: draft
owner: tech-lead
last-reviewed: 2026-10-24
---

# AI Workflows Playbook

The standard ways to use AI on this repo. Each workflow also gets a worked, runnable example in
`ai-enablement/examples/` (see [09-scaffold-spec.md](../09-scaffold-spec.md#ai-enablement-examples)).

## W1. Jira story → merged PR (the main loop)

```mermaid
flowchart LR
  A[Jira story<br/>with ACs] --> B[/jira-story-to-spec AIFS-0001/]
  B --> C[docs/specs/AIFS-0001.md<br/>status: draft]
  C --> D{Human approves spec}
  D -->|changes| A
  D -->|approved| E[/implement-from-spec AIFS-0001/]
  E --> F[failing test per AC → code → just check]
  F --> G[/pr-ready/<br/>code-reviewer + spec-verifier]
  G --> H[PR: CI gates + Copilot/Claude review + CODEOWNER]
  H --> I[Merge → deploy dev]
```

1. `git switch -c feature/AIFS-0001/order-history` (the SessionStart hook picks up the key).
2. `/jira-story-to-spec AIFS-0001`, then review the spec. Fix the ACs **in Jira** if they're wrong.
3. Set `status: approved` in the spec, then `/clear`.
4. `/implement-from-spec AIFS-0001`. The agent plans, writes one failing test per AC, implements, and loops
   on `just check`.
5. `/pr-ready` runs the subagents, fills in the PR body, and opens the PR with `gh pr create`.

## W2. Generate tests and raise coverage

> "Run `/generate-tests backend/src/app/services/orders.py`. Focus on error paths. No snapshot tests."

The skill reads the coverage gaps, writes tests that assert behaviour, and re-runs coverage. A human checks
that the tests would **fail** if the code were broken. As a mutation spot-check, revert one line and see
whether a test goes red.

## W3. Bug fix

`/bugfix-from-jira AIFS-0002`: reproduce it as a failing test, then fix the root cause (not the symptom).
Verify the test passes, then post a regression note on the Jira issue.

## W4. Add an endpoint or page outside a story

Ask in plain words, for example "add a GET endpoint to list orders filtered by status". The `new-api-endpoint`
skill triggers automatically. Then run `/new-react-page` for the UI. In the frontend, run `just api-gen`
after the backend change.

## W5. Refactor safely

1. Plan mode first: "Plan a refactor of X. List the files and the behaviour that must not change."
2. Confirm that coverage of the affected code is ≥80% *before* starting. If it isn't, run W2 first.
3. Make small commits, and run `just check` after each one.
4. Optionally use the `code-simplifier` agent to polish.

## W6. Review

- Before pushing: run `/code-review` locally, or ask Claude to use the `code-reviewer` subagent.
- On the PR: Copilot code review (it reads `.github/copilot-instructions.md`) and/or the Claude review job.
  Then **human CODEOWNER approval is always required**. AI review never replaces it.

## W7. Using Copilot instead of Claude

The same skills are available as `/name` in VS Code Copilot agent mode, and the same `CLAUDE.md` and rules are
loaded. Differences:

- Claude plugins (superpowers and others) are unavailable.
- Hooks may not fire, so run `just check` yourself before committing. Pre-commit runs it anyway.

## Prompting norms

- Always name the Jira key and the spec file.
- Ask for a plan before changes that touch more than 3 files.
- Say what *done* means ("`just check` green, AC-1..3 covered").
- When the agent goes wrong twice on the same thing, stop and fix the **instruction** (rule, skill or hook),
  not just the code. Then log it for the retro.
