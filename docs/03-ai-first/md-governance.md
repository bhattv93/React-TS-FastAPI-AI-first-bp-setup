---
status: draft
owner: tech-lead
last-reviewed: 2026-10-24
---

# Markdown File Governance

How every `.md` file that steers humans or AI is structured, owned, sized and kept accurate.

## Inventory

| Type | Location | Audience | Loaded by AI | Size budget | Owner | Update when |
|------|----------|----------|--------------|-------------|-------|-------------|
| Root instructions | `CLAUDE.md` | AI | Every session | ≤150 lines | Tech lead | Repo-wide command or workflow changes |
| Folder instructions | `backend/`, `frontend/`, `infra/` `CLAUDE.md` | AI | On demand | ≤100 lines | Area lead | Area layout or commands change |
| Rules | `.claude/rules/<area>/<topic>.md` | AI | By `paths:` | ≤60 lines, one topic | Area lead | A convention changes |
| Skills | `.claude/skills/<name>/SKILL.md` + files | AI | On invoke | ≤200 target / 500 hard | Named per skill | Procedure changes; evals fail |
| Subagents | `.claude/agents/<name>.md` | AI | On delegate | ≤100 lines | Tech lead | Review criteria change |
| Copilot pointer | `.github/copilot-instructions.md` | AI (GitHub.com) | Always (Copilot) | ≤30 lines | Tech lead | The non-negotiables change |
| Personal | `CLAUDE.local.md`, auto memory | AI | Every session (yours) | — | You | Anytime; **gitignored** |
| Blueprint docs | `docs/**` | Humans (AI via links) | Never auto | Sectioned | Per frontmatter | Design changes |
| ADRs | `docs/adr/` | Humans | Never auto | 1–2 pages | Deciders | New decision (immutable once accepted) |
| Specs | `docs/specs/<KEY>.md` | Both | Via skill | Per story | Story owner | Jira changes |
| Repo docs | `README.md`, `CONTRIBUTING.md` | Humans | Never auto | — | Tech lead | Setup or process changes |
| Examples | `ai-enablement/**` | Humans | Never auto | — | Tech lead | Workflows change |

## Rules

1. **One fact, one place.** Rules state conventions. Skills link to rules. CLAUDE.md links to skills. Docs
   explain the why. If you copy text between two of these, one copy will go stale.
2. **Never `@import` docs into CLAUDE.md.** Imports load in full every session. Use a plain link (or a
   backticked path) so the agent reads the doc only when it needs to.
3. **Write for the model:**
   - Use the imperative mood, and be specific and verifiable ("Use `uv run pytest`", not "test properly").
   - Show one short example rather than three paragraphs of prose.
   - Give the reason in half a sentence at most. The full rationale goes in an ADR.
   - Don't inflate emphasis (ALL CAPS, repeated IMPORTANT). If something truly must not happen, enforce it
     with a hook or CI.
4. **No contradictions.** Root vs folder vs rule files must agree. When a convention changes, update all
   affected files in **one PR**.
5. **Frontmatter:** docs carry `status/owner/last-reviewed`. Rules carry `paths:`. Skills carry
   `name/description`.
6. **Generated or personal files never get committed:** `CLAUDE.local.md`, `.claude/settings.local.json`.

## Change control

- `.github/CODEOWNERS` assigns `CLAUDE.md`, `**/CLAUDE.md`, `.claude/**`, `.github/copilot-instructions.md`
  and `.mcp.json` to the tech lead (plus area leads for their folders).
- A PR template checkbox asks: "Changed a convention? Updated rule + CLAUDE.md + affected skills + docs."
- `.github/ai-policy.json` (the MCP server and plugin allowlist) is CODEOWNERS-protected and checked by
  `scripts/check_ai_policy.py`. See [ai-access-governance.md](ai-access-governance.md).
- CI lint (built: `scripts/check_ai_config.py`, run by `just check`, pre-commit and CI):
  - markdownlint on all `.md`
  - a script that fails if root `CLAUDE.md` > 150 lines, a folder `CLAUDE.md` > 100, a rule > 60, or
    `SKILL.md` > 500
  - a check that each skill `name` matches its folder

## Review cadence

| When | What |
|------|------|
| Every PR | CODEOWNERS review of any AI-config change |
| Every sprint retro | Standing item, "AI friction": where did the agent go wrong? Each answer becomes a rule, skill or hook fix |
| Monthly | `/doctor prompt-audit` (contradictions, staleness) and the `claude-md-management:claude-md-improver` audit |
| Quarterly | Re-check the Claude Code and VS Code Copilot docs for discovery or format changes ([tool-parity](tool-parity.md)); re-run the skill evals; prune unused skills |

## Promoting learnings

Auto memory and `CLAUDE.local.md` are personal. When a personal note would help everyone:

1. Run `/revise-claude-md` (claude-md-management plugin) or edit the right file by hand. Use the decision
   tree in [context-strategy.md](context-strategy.md#the-five-context-mechanisms-and-what-goes-where).
2. Open a PR, get a CODEOWNERS review, and merge.
