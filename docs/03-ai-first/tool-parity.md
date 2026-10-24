---
status: draft
owner: tech-lead
last-reviewed: 2026-10-24
---

# Claude Code ↔ GitHub Copilot Parity

Claude Code is the **primary** tool. Copilot (VS Code chat/agent mode, Copilot code review, the Copilot coding
agent) is **secondary**. Decision: [ADR-0002](../adr/0002-claude-native-instructions-copilot-reads.md). There is
one copy of every instruction, in Claude-native locations, and Copilot reads it.

## What each tool reads

| Artifact | Path | Claude Code | Copilot in VS Code | Copilot code review on GitHub.com |
|----------|------|:-----------:|:------------------:|:-------------------------------------------------:|
| Repo instructions | `CLAUDE.md`, `backend/CLAUDE.md`, … | ✅ native | ✅ with `chat.useClaudeMdFile` | Coding agent: reads `CLAUDE.md` (verify per release) |
| Copilot pointer | `.github/copilot-instructions.md` | — | ✅ | ✅ (code review) |
| Path-scoped rules | `.claude/rules/**.md` (`paths:`) | ✅ | ✅ (reads `paths`) | ❌ → covered by the pointer + CI gates |
| Skills | `.claude/skills/<name>/SKILL.md` | ✅ | ✅ (Agent Skills standard) | Coding agent: verify per release |
| Subagents / custom agents | `.claude/agents/*.md` | ✅ | ✅ (Claude agent format) | ❌ |
| Hooks | `.claude/settings.json` | ✅ | Partial / verify | ❌ → CI is the backstop |
| MCP servers | `.mcp.json` (Claude), `.vscode/mcp.json` (VS Code) | ✅ | ✅ | Coding agent: configured in repo settings on GitHub |
| Plugins (superpowers, code-review, …) | `.claude/settings.json` `enabledPlugins` | ✅ | ❌ | ❌ |

**Consequence:** project skills must be **self-sufficient**. They may *suggest* Claude plugins (for example
`superpowers:test-driven-development`) as accelerators, but must not depend on them, because Copilot users
don't have plugins.

## Skill and agent frontmatter compatibility

| Field | Claude Code | VS Code Copilot | Agent Skills spec | Use it? |
|-------|:-:|:-:|:-:|---|
| `name`, `description` | ✅ | ✅ | ✅ | Always |
| `argument-hint` | ✅ | ✅ | — | Yes |
| `disable-model-invocation` | ✅ | ✅ | — | Yes, for side-effect skills |
| `user-invocable` | ✅ | ✅ | — | Yes, for background-only skills |
| `context: fork` | ✅ | ✅ (experimental) | — | Sparingly |
| `allowed-tools`, `paths`, `model`, `effort`, `hooks` | ✅ | ignored | `allowed-tools` only | Allowed, and the catalog flags them **Claude-only** |

## `.github/copilot-instructions.md` (≤30 lines)

Contents, in order:

1. One paragraph: the stack and the monorepo layout.
2. "Project conventions live in `CLAUDE.md`, `backend/CLAUDE.md`, `frontend/CLAUDE.md` and `.claude/rules/`.
   Follow them."
3. The non-negotiables, which Copilot code review needs because it can't see rules:
   - layering (router → service → model; page → hook → service)
   - numpy docstrings
   - mypy strict and TS strict
   - tests for every change, coverage ≥80%
   - never edit generated client or applied migrations
4. "Every PR references a Jira key; acceptance criteria are in `docs/specs/<KEY>.md`."

## VS Code settings that enable parity (`.vscode/settings.json`)

```jsonc
{
  "chat.useClaudeMdFile": true,                                   // read CLAUDE.md files
  "github.copilot.chat.codeGeneration.useInstructionFiles": true, // read .github/copilot-instructions.md
  "chat.includeApplyingInstructions": true,                       // path-scoped instructions/rules
  "chat.useCustomizationsInParentRepositories": true              // when a dev opens backend/ or frontend/ as the workspace
}
```

> These features are new and move fast. Re-verify each quarter against the
> [VS Code customization docs](https://code.visualstudio.com/docs/copilot/customization/overview) (see the
> review cadence in [md-governance.md](md-governance.md#review-cadence)).

## Access control

Both tools follow the same approved-tool, account and data rules: see
[ai-access-governance.md](ai-access-governance.md).

## Where Copilot-only files are allowed

Only when Copilot cannot read the Claude-native equivalent:

- `.github/prompts/*.prompt.md`: none planned. Skills cover these, since both tools invoke them as `/name`.
- `.github/instructions/*.instructions.md`: none planned. Add one only if Copilot code review on GitHub.com
  needs path-specific rules, and then link to the rule rather than copying it.

## Claude on GitHub

Optional: [`anthropics/claude-code-action`](https://github.com/anthropics/claude-code-action) for `@claude`
mentions on issues and PRs, plus an automated review job. It reads the same `CLAUDE.md` and `.claude/` files.
See [ci.md](../06-delivery/ci.md#ai-review-jobs).
