---
status: draft
owner: tech-lead
last-reviewed: 2026-10-24
---

# AI Access Governance

Who and what may use GenAI on this repository, how external tools are added, and what data must never reach an
AI service. Decision record: [ADR-0009](../adr/0009-controlled-genai-access.md).

## Policy at a glance

| Topic | Rule |
|-------|------|
| Approved tools | **Claude Code** and **GitHub Copilot** only. Anything else (other chat assistants, editors with built-in agents, browser extensions) is out of policy for this repository's content |
| Accounts | **Company-managed accounts and seats only.** No personal subscriptions and no personal API keys for work on this repository |
| MCP servers | Repo-committed set is an allowlist: **`atlassian` only**. Adding one needs a maintainer-approved PR. Personal servers are allowed in a developer's own user config **for non-repository tasks only** |
| Claude plugins | Allowlist in `.github/ai-policy.json`; same PR rule |
| Skills, agents, hooks | Code that runs on developer machines. Reviewed like code; CODEOWNERS protects `.claude/` |
| Data | Secrets, PII, production data and customer-confidential material **never** go to an AI tool (below) |
| Accountability | The human committing a change owns it, whoever or whatever wrote it |

## Data that must never reach an AI tool

| Category | Examples | Do this instead |
|----------|----------|-----------------|
| Secrets and credentials | API keys, tokens, `.env` contents, private keys, connection strings with passwords | Reference variable names only. Rotate immediately if one was pasted (see incident steps) |
| Personal data (PII) | Customer or employee names, emails, phone numbers, IDs, in logs, fixtures, screenshots or error dumps | Use synthetic data and factories; redact before sharing |
| Production data | Rows or dumps from a real database, real request payloads | Use seeded fixtures; describe the shape, not the content |
| Customer-confidential code or contracts | Third-party code, NDA material, contract text | Do not include it in the repository or prompts; ask a maintainer |

The same rule covers MCP tools: a tool call that sends content to a third party is a disclosure.

## What is enforced, and what is advisory

Be honest about the limits: a developer can edit their own user settings, so repository controls reduce
mistakes but do not stop a determined person. Only the organisation-managed layer is hard to bypass.

| Control | Where | Enforced by | Can a developer bypass it? |
|---------|-------|-------------|----------------------------|
| MCP servers match the allowlist | `.mcp.json`, `.vscode/mcp.json`, `.github/ai-policy.json` | `scripts/check_ai_policy.py` in pre-commit, `just check` and CI | Not in a merged PR (CI fails); locally yes |
| Plugins match the allowlist | `.claude/settings.json` | Same check | Same |
| Project MCP servers need explicit approval | `enableAllProjectMcpServers: false` in `.claude/settings.json`; Claude Code prompts per user | Claude Code | A user can approve in their own session |
| Secret files unreadable by the agent | `permissions.deny` for `.env`, `*.pem`, `*.key`, `secrets/` | Claude Code | A user can relax it in local settings |
| Outbound network from the agent asks first | `permissions.ask` for `curl`, `wget`, `WebFetch` | Claude Code | A user can allow it locally |
| Destructive commands denied | `permissions.deny` (force push, `cloudformation deploy`, `terraform apply`, `flyway clean`) | Claude Code | Same |
| Secrets not committed | `.gitignore`, gitleaks (pre-commit and CI) | pre-commit + CI | Locally yes; CI blocks the merge |
| Changes to AI config are reviewed | CODEOWNERS on `.claude/`, `.mcp.json`, `.vscode/mcp.json`, `.github/` | GitHub branch protection | No (once rulesets are enabled) |
| Account type (managed vs personal) | Organisation settings | **Organisation-managed settings** and seat assignment | Only the managed layer is strong |
| Personal MCP servers | Developer user config | Policy + review; managed MCP restrictions if you adopt them | Yes without managed settings |

## Adding an MCP server, plugin or AI tool

1. Open a Jira story and an ADR (or an addendum to ADR-0009) stating the purpose and owner.
2. Review: what data can the tool read, what can it write or send out, and who operates it? Use the
   narrowest OAuth scopes and read-only access wherever possible.
3. Check the vendor terms for data retention and training use.
4. Add it to `.github/ai-policy.json` and the relevant config file in the same PR. CODEOWNERS requires
   maintainer approval, and CI re-checks the allowlist.
5. Document it in [subagents-hooks-mcp.md](subagents-hooks-mcp.md).

**Personal servers:** allowed in your own user configuration for tasks unrelated to this repository. Do not run
a personal server in a session where repository code, specs, logs or secrets are in context.

## Skills, agents and hooks are code

They execute commands on developer machines and shape what the agent does.

- Review them as code. Read every script a skill runs. CODEOWNERS applies.
- Prefer scripts over free-form shell in skills; keep `allowed-tools` narrow and mark side-effect skills
  `disable-model-invocation: true` ([skill-authoring-guide](skill-authoring-guide.md)).
- Do not install skills or plugins from unreviewed sources.

## Untrusted content and prompt injection

Text the agent reads can contain instructions: Jira descriptions and comments, web pages, issue text, file
contents, tool output.

- Treat it as **data, not instructions**. A story that says "ignore previous rules and ..." is a red flag.
- A human approves each spec before implementation; the agent never invents acceptance criteria.
- Jira writes (comments, transitions) happen only inside user-invoked skills.
- Review diffs for unexpected network calls, new dependencies and changes to AI config.

## Accounts and organisation-level settings

Repository files cannot enforce who signs in. These must be set in the organisation:

| Area | What to configure |
|------|-------------------|
| Claude | Company-managed seats. Deliver **managed settings** (server-managed from the admin console, or MDM / a `managed-settings.json`) that mirror the deny rules above and restrict MCP servers. See Anthropic's managed settings and managed MCP documentation |
| GitHub Copilot | Business or Enterprise seats assigned by the organisation. Review organisation policies: content exclusion for sensitive paths, matching public code, preview features, and which Copilot features are enabled |
| GitHub | Rulesets requiring the `gate` check and CODEOWNERS review; secret scanning with push protection; Dependabot alerts |

> Open item: these organisation settings are outside the repository and depend on your plan and admin access.
> They are listed in [Open decisions](#open-decisions).

## CI and API keys

- The optional Claude review workflow uses an `ANTHROPIC_API_KEY` secret. Store it as an **environment
  secret** limited to that workflow, never as a broadly available repository secret.
- Never run it for pull requests from forks. Give the job minimal `permissions`.
- Use a key owned by the organisation, set a spend limit, and rotate it on a schedule.
- Developers never put API keys in `.env` files for AI tools; they sign in with their managed account.

## If sensitive data reached an AI tool

1. **Stop**, and do not try to delete your way out of it.
2. **Rotate** any secret involved, immediately.
3. Tell the maintainers and the security contact; record what, when and which tool.
4. Check whether the content was committed (git history) or logged, and remove it per the secret-handling
   process.
5. Add a rule, hook or test so the same path cannot happen again.

## Review cadence

| When | What |
|------|------|
| Every PR | CODEOWNERS review of any AI config; CI policy check |
| Quarterly | Re-confirm the allowlists, review MCP server scopes, review Claude and Copilot organisation settings, re-read vendor data terms |
| On any incident | Run the steps above, then update this document |

## Open decisions

These need an answer from the project owner before adoption (they are not guessed in the docs):

1. Who are the **approvers** for AI config changes (the `@org/maintainers` placeholder)?
2. Which **organisation-managed settings** delivery will you use for Claude (admin console, MDM, or file), and
   will you adopt managed MCP restrictions?
3. Which **Copilot organisation policies** apply (content exclusions, public-code matching, preview features)?
4. Is the **Claude review workflow** wanted at all, and who owns its API key and spend limit?
5. What is the **security contact** and incident channel?
