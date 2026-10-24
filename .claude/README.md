# .claude

Shared Claude Code configuration for this repository. GitHub Copilot in VS Code reads the same files.

| Path | Purpose | Status |
|------|---------|--------|
| `settings.json` | Default model, enabled plugins, permissions and hooks shared by the team | Present |
| `settings.local.json` | Your personal overrides | Gitignored; never commit |
| `rules/` | Path-scoped conventions that load only when matching files are touched | Present |
| `skills/` | Reusable workflows: spec, implement, endpoint, migration, page, PR-ready | Present (more planned) |
| `agents/` | Model-routed subagents: code-reviewer, spec-verifier, test-triage | Present |
| `hooks/` | Deterministic guards: protected files, formatting, story context | Present |
| `loop.md` | Default prompt for `/loop` (babysit the current PR) | Present |

Why these exist and how big each may be: `docs/03-ai-first/md-governance.md`. The budgets are enforced by
`just check-ai-config`. The repository-wide instructions are in `CLAUDE.md` at the repository root.
