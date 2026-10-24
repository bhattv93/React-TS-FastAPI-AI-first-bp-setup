# .claude

Shared Claude Code configuration for this repository. GitHub Copilot in VS Code reads the same files.

| Path | Purpose | Status |
|------|---------|--------|
| `settings.json` | Enabled plugins and permission rules shared by the team | Present |
| `settings.local.json` | Your personal overrides | Gitignored; never commit |
| `rules/` | Path-scoped conventions | Planned (milestone M4) |
| `skills/` | Reusable workflows | Planned (milestone M4) |
| `agents/` | Specialist subagents | Planned (milestone M4) |
| `hooks/` | Deterministic guards (protected files, formatting) | Planned (milestone M4) |

Rules for what goes where and how big each file may be: `docs/03-ai-first/md-governance.md`.
The repository-wide instructions are in `CLAUDE.md` at the repository root.
