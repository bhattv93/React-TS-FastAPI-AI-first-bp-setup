---
name: pr-ready
description: Final pre-pull-request checklist: run the gates, review the diff, verify acceptance-criterion coverage, then draft the PR title and body with the Jira key. Use when implementation is finished and you are about to open a pull request.
disable-model-invocation: true
---

# Pull request ready

**Why this exists.** AI speeds up writing code, so the checks before a human reviews it have to be
systematic. This skill runs them in the cheapest order and stops at the first real problem.

## Steps

1. **Branch and key.** The branch must be `type/AIFS-0001/slug`; take the key from it.
2. **Gates.** Delegate `just check` to the `test-triage` subagent. Stop and fix on any failure.
3. **Traceability.** Delegate to `spec-verifier` for `docs/specs/<KEY>.md`. Every AC must be covered.
4. **Review.** Delegate to `code-reviewer`. Address every blocking finding; report suggestions.
5. **Docs.** If a convention changed, the matching rule, `CLAUDE.md`, skill or doc is updated.
6. **AI hygiene.** Confirm no secrets, PII, production data or customer-confidential material is in the
   diff, fixtures, logs or screenshots, and no MCP server, plugin or AI tool was added without approval.
7. **Draft the PR** (do not push or open it unless the user asks):
   - title: `type(scope): summary (AIFS-0001)`
   - body: use `.github/pull_request_template.md`, with the AC-to-test table filled from step 3
8. Show the user the title, body and any open findings, and wait.

## Never

Open, push or merge without the user's go-ahead. Never weaken a gate to get a green check.
