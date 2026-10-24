---
status: accepted
owner: tech-lead
last-reviewed: 2026-10-24
---

# ADR-0009: Controlled access to GenAI tools

- **Status:** Accepted
- **Date:** 2026-10-24

## Context

The team relies on AI agents to write most of the code. Agents can read the repository, run commands and call
external tools (MCP servers), so access to them is a security and data-protection concern, not only a
productivity choice. We needed rules for which tools are allowed, how people sign in, how external tools are
added, and what data may never reach an AI service.

## Decision

1. **Approved tools:** Claude Code and GitHub Copilot only. Other GenAI tools are out of policy for this
   repository's content. Adding one requires a new ADR.
2. **Accounts:** company-managed accounts and seats only. No personal subscriptions or personal API keys for
   work on this repository.
3. **MCP servers:**
   - The repo-committed set is an **allowlist** (currently `atlassian` only) in `.github/ai-policy.json`.
     Adding one needs a maintainer-approved PR, and CI fails if `.mcp.json` or `.vscode/mcp.json` list a server
     that is not on it.
   - Developers may add **personal** servers in their own user configuration for non-repository tasks. No
     personal server may receive repository code, specs, logs or secrets unless the maintainers approved it.
4. **Plugins** enabled in `.claude/settings.json` are an allowlist in the same file, with the same PR rule.
5. **Data that must never reach an AI tool:** secrets and credentials, personal data (PII), production data, and
   customer-confidential code or contracts.
6. **Defence in depth:** policy text, committed Claude Code permission rules, a CI policy check, secret
   scanning, and (recommended) organisation-managed settings that developers cannot override.

Details and the enforcement matrix: [ai-access-governance.md](../03-ai-first/ai-access-governance.md).

## Alternatives considered

| Option | Pros | Cons |
|--------|------|------|
| Documented guidance only | Zero friction | Nothing is enforced; drift is invisible |
| **Policy + committed controls + CI check (chosen)** | Reviewable, automated where possible | Some controls (personal MCP, account type) cannot be enforced from the repo |
| Organisation-managed settings only | Strongest for Claude Code | Needs admin-console access; does not cover Copilot or CI |

## Consequences

- Repo-level controls are advisory for a developer who edits their own user settings. Real enforcement of
  account type and personal MCP servers needs the organisation-managed layer (see the governance doc).
- The allowlist file and AI configuration are CODEOWNERS-protected.
- Reviewers check PRs for new MCP servers, plugins and any prompt or fixture containing sensitive data.
