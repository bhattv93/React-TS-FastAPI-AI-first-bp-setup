---
status: accepted
owner: tech-lead
last-reviewed: 2026-10-24
---

# ADR-0002: Claude-native instruction files as the single source; Copilot reads them

- **Status:** Accepted
- **Date:** 2026-10-24

## Context

Claude Code is the primary AI tool; GitHub Copilot in VS Code is secondary. Keeping two parallel instruction
sets (`.claude/*` and `.github/instructions/*`) means every convention is written twice and drifts.
VS Code Copilot now natively discovers Claude-format files:

- `CLAUDE.md`, `.claude/CLAUDE.md` and `CLAUDE.local.md`, when `chat.useClaudeMdFile` is enabled.
- `.claude/rules/*.md`, using `paths:` globs in place of `applyTo`.
- Skills in `.claude/skills/<name>/SKILL.md` (Agent Skills open standard).
- Custom agents in `.claude/agents/*.md` (Claude agent format).

## Decision

- `CLAUDE.md` (root and per folder), `.claude/rules/`, `.claude/skills/` and `.claude/agents/` are the **only**
  copy of AI instructions.
- `.github/copilot-instructions.md` is a short pointer (≤30 lines). It names the stack, points to `CLAUDE.md`
  and lists the non-negotiable gates. GitHub.com surfaces (Copilot code review) read
  it even where the VS Code settings don't apply.
- `.vscode/settings.json` turns on the flags (see [tool-parity.md](../03-ai-first/tool-parity.md)).
- Skill and agent frontmatter sticks to fields both tools understand. Claude-only fields are allowed where
  needed and are listed in the catalog.

## Alternatives considered

| Option | Pros | Cons |
|--------|------|------|
| AGENTS.md as source, `CLAUDE.md` = `@AGENTS.md` | Tool-neutral (Codex, Cursor) | Claude features such as rules and skills still live in `.claude/`; two systems to explain |
| Separate files per tool | Each tool fully native | Double maintenance, guaranteed drift |
| **Claude-native, Copilot reads** | One copy, Claude-first | Depends on VS Code flags; GitHub.com surfaces need the pointer file |

## Consequences

- If Copilot cannot see a file type, the fix is a VS Code setting or a pointer, never a copy.
- Re-verify the VS Code discovery rules each quarter (the features are new; see md-governance review cadence).
- MCP config is the one exception that needs two small files (`.mcp.json` for Claude, `.vscode/mcp.json` for
  Copilot), because the formats differ.
