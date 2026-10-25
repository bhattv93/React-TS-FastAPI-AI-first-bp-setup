---
status: draft
owner: tech-lead
last-reviewed: 2026-10-24
---

# Skill Authoring Guide

Standards for every skill in `.claude/skills/`. Based on the Claude Code skills docs and the Agent Skills open
standard (agentskills.io), which VS Code Copilot also implements.

## 1. Is it actually a skill?

| If the content is… | Put it in |
|--------------------|-----------|
| A repeatable multi-step procedure with a clear "done" | **Skill** |
| A convention for a file type | `.claude/rules/` |
| A fact needed in every session | `CLAUDE.md` |
| Something that must never or always happen | Hook or CI |

## 2. Anatomy

```text
<name>/
├── SKILL.md        # required. Frontmatter + concise instructions
├── reference.md    # optional, detailed material, read only when SKILL.md says so
├── examples.md     # optional, worked examples
├── templates/      # optional, files to copy and fill
└── scripts/        # optional, deterministic helpers. Executed, not loaded into context
```

## 3. Frontmatter rules

```yaml
---
name: new-api-endpoint            # kebab-case, equals the folder name, verb-first
description: >-
  Scaffold a FastAPI endpoint (router, Pydantic schemas, service, pytest tests) following this repo's
  layering and error envelope. Use when adding or changing a REST endpoint under backend/src/app/api.
argument-hint: "[resource] [method]"
# disable-model-invocation: true  # ← required for side effects (deploy, Jira writes, git push)
---
```

- **Description = what it does + when to use it**, with the main use case first and the concrete nouns the
  user will say ("endpoint", "route", "FastAPI"). This text is all the model sees until the skill loads, so
  it decides triggering. The listing truncates at 1,536 characters; aim for under 400.
- Use only cross-tool fields by default (see the [compatibility table](tool-parity.md#skill-and-agent-frontmatter-compatibility)).
  Any Claude-only field must be listed in the catalog row.
- Set `disable-model-invocation: true` on anything that deploys, pushes, writes to Jira, or deletes.

## 4. Body rules

1. **≤500 lines (hard), ≤200 (target).** Move depth into `reference.md` and say exactly when to read it:
   "Before writing the service, read `reference.md#error-envelope`."
2. **Structure:** Purpose (2 lines), Inputs, Steps (numbered and imperative), Done criteria (verifiable),
   Pitfalls.
3. **Verifiable steps.** "Run `uv run pytest tests/integration -k orders` and confirm it passes", not "make
   sure it works".
4. **Scripts for deterministic work** (filename timestamps, coverage parsing, template rendering). Reference
   them with `${CLAUDE_SKILL_DIR}/scripts/...` and write them in Python or Node so they run on Windows, macOS
   and Linux.
5. **Link, don't copy.** Conventions come from `.claude/rules/` and docs. A skill that restates a rule will
   drift from it.
6. **No secrets, no environment-specific URLs.** Read them from env or config.
7. **End with a self-check:** the skill's last step re-runs the gates and reports AC → test mapping where
   relevant.

## 5. Testing a skill (before merge)

Use the `skill-creator` plugin's eval loop:

1. **Trigger evals:** about 5 prompts that *should* trigger the skill and about 5 near-misses that should not
   (for example, "add a page" should not trigger `new-api-endpoint`). Target ≥90% correct.
2. **Output evals:** run the skill on 2–3 realistic tasks in a scratch branch. Every result must pass
   `just check` without manual fixes.
3. Record the eval prompts in `<skill>/evals/` so they can be re-run when the skill changes.
4. Smoke-test in **Copilot** too: invoke it as `/name` in VS Code agent mode and confirm it behaves the same.

## 6. Lifecycle

- **Owner:** each catalog row names one.
- **Change:** PR with a CODEOWNERS review. Re-run the evals when the description or steps change.
- **Deprecate:** set `disable-model-invocation: true` and add a "Deprecated, use X" line at the top. Delete it
  one sprint later.
- **Promote:** a skill that is useful across many repos moves to an internal Claude Code plugin.

## 7. Review checklist (copy into the PR)

- [ ] Not a duplicate of an existing skill or plugin skill
- [ ] Name is kebab-case, verb-first, and matches the folder
- [ ] Description states what + when, ≤400 chars
- [ ] Side effects → `disable-model-invocation: true`
- [ ] SKILL.md ≤200 lines (≤500 hard); depth lives in supporting files that are linked with "read when…"
- [ ] Deterministic steps are scripts and run cross-platform
- [ ] Trigger and output evals pass; checked in Copilot
- [ ] Catalog row added
