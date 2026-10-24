---
name: implement-from-spec
description: Implement an approved spec test-first, one acceptance criterion at a time, until every criterion has a passing test and the quality gates are green. Use after the spec status is approved.
argument-hint: "[AIFS-0001]"
disable-model-invocation: true
---

# Implement from an approved spec

**Why this exists.** Test-first work gives the model a verifiable target, so it can check its own work and
you review behaviour instead of guessing. Doing it criterion by criterion keeps each step small and cheap.

## Preconditions (stop if any fails)

- `docs/specs/<KEY>.md` exists and has `status: approved`.
- The branch is `type/<KEY>/slug`, not `main`.

## Steps

1. **Plan.** Read the spec and list the files to change. For more than ~3 files, show the plan first.
2. **For each `AC-n`, in order:**
   1. Write a failing test that asserts the criterion (`@pytest.mark.ac("<KEY>", "AC-n")` in the backend;
      `it('AC-n: ...')` in the frontend). Run it and confirm it fails for the right reason.
   2. Write the smallest code that makes it pass, following the path-scoped rules that load for those files.
   3. Run only the affected tests, then continue.
3. **Contracts.** If a schema changed, run `just api-gen`. If a model changed, add a Flyway migration
   (`just db-new <name>`) in the same change.
4. **Gates.** Run `just check`. For noisy output delegate to the `test-triage` subagent. Fix failures at
   the cause; never weaken a gate, lower a threshold or edit a generated file.
5. **Verify traceability.** Delegate to the `spec-verifier` subagent; close any gap it reports.
6. Hand off to `/pr-ready`.

## Long stories: use a goal with a cap

For a multi-criterion story, suggest the user run (the turn cap is mandatory):

```text
/goal every AC in docs/specs/<KEY>.md has a passing test and `just check` exits 0, or stop after 15 turns
```

A separate small model judges completion after each turn, so the worker does not grade its own work.

## Done when

Every AC has a passing test, `just check` is green, `spec-verifier` reports no gaps, and the spec's
`status` can move to `implemented`.
