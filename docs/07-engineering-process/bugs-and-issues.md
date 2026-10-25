---
status: draft
owner: delivery-lead
last-reviewed: 2026-10-24
---

# Bugs and Issue Handling

Jira is the single intake. GitHub Issues is disabled for the team, or redirected to Jira through
`.github/ISSUE_TEMPLATE/config.yml` contact links.

## Severity and response targets

| Severity | Definition | Response | Fix target |
|----------|------------|----------|------------|
| S1 | Prod down, data loss, or security breach | Immediate (on-call) | Hotfix same day |
| S2 | Major feature broken, no workaround | Same business day | Within the sprint, or a hotfix |
| S3 | Workaround exists | Triage within 2 days | Prioritised in the backlog |
| S4 | Cosmetic | Weekly triage | Backlog |

## Flow

1. **Report** using the [bug template](../04-spec-driven-development/templates/bug.md). Include the
   `request_id` from the error UI or the `X-Request-ID` header.
2. **Triage** (weekly, or immediately for S1/S2): confirm, set severity, link to the epic or component, assign.
3. **Fix** with `/bugfix-from-jira KEY`:
   - Reproduce with a **failing test** first. That test is the bug's AC-1.
   - Fix the root cause, then run `just check`.
   - A PR with `fix(scope): … (KEY)`.
4. **Verify** in dev or staging. The Jira issue transitions when the PR is merged and deployed.
5. **Close the loop:** the regression test stays forever. For S1/S2, write a blameless post-incident review
   (template in `docs/runbooks/` from M6) with action items as Jira tasks.

## Hotfix path (S1)

- Branch from `main` → PR → `gate` green → **1** CODEOWNER approval (an emergency override is allowed for
  the on-call lead and logged) → merge → `cd.yml` with expedited prod approval.
- No skipping tests. If a test is flaky, quarantine it in a separate PR with a Jira ticket.

## Flaky tests and tech debt

- A flaky test gets a `flaky` Jira label and a fix-or-delete decision within the sprint.
- Tech debt goes into Jira with the `tech-debt` label. Reserve about 15% of sprint capacity for it.
- An AI-friction item from the retro becomes a Jira task against the rule, skill or hook that needs changing
  ([md-governance](../03-ai-first/md-governance.md#review-cadence)).
