---
status: accepted
owner: tech-lead
last-reviewed: 2026-10-24
---

# ADR-0008: mypy is the type-check gate; Pylance/Pyright is the IDE experience

- **Status:** Accepted
- **Date:** 2026-10-24

## Context

The requirement mandates mypy. VS Code's Pylance (and the Claude Code `pyright-lsp` plugin enabled in
`.claude/settings.json`) use Pyright, which sometimes disagrees with mypy.

## Decision

- **mypy `--strict`** with the `pydantic.mypy` plugin is the **only** blocking type gate, in pre-commit and CI.
- Pylance runs in `basic` type-checking mode for in-editor feedback only. Pyright's opinions never block a PR.
- When the two disagree, mypy wins. Fix the code for mypy; suppress the Pyright warning locally if needed.
- The VS Code `ms-python.mypy-type-checker` extension shows mypy results in the editor, so devs see the gate's
  real verdict.

## Consequences

- AI agents run `uv run mypy src` to verify types, never rely on LSP diagnostics alone.
- `# type: ignore[code]` requires a specific error code (enforced by `warn_unused_ignores` + review).
