---
status: draft
owner: tech-lead
last-reviewed: 2026-10-24
---

# Subagents, Hooks, Permissions and MCP

## Subagents (`.claude/agents/*.md`)

> **Built:** `code-reviewer` (Sonnet), `spec-verifier` (Haiku), `test-triage` (Haiku). The other rows are planned. Every agent pins a model; the lint enforces it. See [agents-and-supervision.md](agents-and-supervision.md).

Subagents run in their own context window. Use them for specialist work whose intermediate output shouldn't
pollute the main session. VS Code Copilot also reads this folder (Claude agent format).

| Agent | Tools | Purpose | Typical caller |
|-------|-------|---------|----------------|
| `code-reviewer` | `Read, Grep, Glob, Bash(git diff *)` | Reviews the diff against layering, rules, security basics and test quality. Returns ranked findings | `pr-ready` skill, or a human before pushing |
| `spec-verifier` | Read, Grep, Glob | Checks that every `AC-n` in `docs/specs/<KEY>.md` has at least one test marked with it, and that it asserts the behaviour | `implement-from-spec`, `pr-ready` |
| `test-gap-finder` | `Read, Grep, Glob, Bash(uv run pytest --cov *), Bash(pnpm test *)` | Finds untested branches and proposes test cases (doesn't write them) | `generate-tests` |
| `security-reviewer` | Read, Grep, Glob | OWASP-style pass: injection, authz gaps, secrets, unsafe deserialization, CORS | `pr-ready` for PRs labelled `security` |

Rules:

- Use read-only tools by default. An agent that writes code should be a skill instead.
- Keep each file ≤100 lines, with the description written as *when to delegate*.
- Don't duplicate the built-in Explore and Plan agents.

## Hooks (`.claude/settings.json`) are the enforcement layer

> **Built:** `guard_protected_files.py` (PreToolUse), `format_changed_file.py` (PostToolUse), `session_context.py` (SessionStart), all covered by unit tests and run with `uv run --no-project python`. The other rows are planned.

Instruction files are advisory. Hooks are deterministic. Hook scripts live in `.claude/hooks/` as Python run
through `uv run --no-project python …`, so they work on Windows and Unix. They receive the tool call as JSON
on stdin, and exit code `2` blocks the call, with the reason on stderr sent back to Claude.

| Event | Matcher | Script | Behaviour |
|-------|---------|--------|-----------|
| `PreToolUse` | `Edit\|Write\|MultiEdit` | `guard_protected_files.py` | **Blocks** edits to `.env*` (except `.env.example`), **already committed** `backend/db/migrations/V*.sql`, generated `frontend/src/api/schema.d.ts`, and lockfiles |
| `PreToolUse` | `Bash` | `guard_bash.py` | Blocks `git push --force`, `aws cloudformation deploy`/`delete-stack`, `terraform apply`/`destroy`, `flyway clean`, and `rm -rf` outside the repo |
| `PostToolUse` | `Edit\|Write\|MultiEdit` | `format_changed_file.py` | Formats the edited file by extension: `.py` → isort + black; `.ts/.tsx/.json/.md` → prettier. Fast and per-file |
| `SessionStart` | — | `session_context.py` | Reads the branch (`type/AIFS-0001/…`) and injects "Current story AIFS-0001; spec: docs/specs/AIFS-0001.md (status: …)" |
| `Stop` | — | (optional, off by default) | Runs a quick lint on changed files and returns the failures, so the agent fixes them before handing back |

The full gates (mypy, pytest, coverage) are **not** hooks, because they are too slow per edit. They run in
`just check`, pre-commit and CI.

## Permissions (`.claude/settings.json`)

```jsonc
{
  "permissions": {
    "allow": [
      "Bash(uv run *)", "Bash(uv sync*)", "Bash(pnpm *)", "Bash(just *)",
      "Bash(git status*)", "Bash(git diff*)", "Bash(git log*)", "Bash(gh pr view*)", "Bash(docker compose *)"
    ],
    "deny": [
      "Read(./.env)", "Read(./**/.env)", "Bash(git push --force*)",
      "Bash(aws cloudformation deploy*)", "Bash(aws cloudformation delete-stack*)",
      "Bash(terraform apply*)", "Bash(terraform destroy*)", "Bash(flyway clean*)"
    ]
  }
}
```

Personal additions go in `.claude/settings.local.json`, which is gitignored.

## MCP servers

Access is controlled: only servers on the allowlist in `.github/ai-policy.json` may be committed, CI enforces it,
and adding one needs a maintainer-approved PR. See [ai-access-governance.md](ai-access-governance.md).

Keep the set small. Every server's tool definitions cost context.

| Server | Purpose | Claude config | Copilot config |
|--------|---------|---------------|----------------|
| **Atlassian (Rovo MCP, official remote)** | Read Jira issues/ACs, comment, transition (Confluence too) | `.mcp.json`: `{"mcpServers":{"atlassian":{"type":"http","url":"https://mcp.atlassian.com/v1/mcp"}}}`, with OAuth per user | `.vscode/mcp.json`: `{"servers":{"atlassian":{"type":"http","url":"https://mcp.atlassian.com/v1/mcp"}}}` |
| Playwright | Drive the running SPA to verify UI changes | Plugin already enabled | `.vscode/mcp.json` (optional) |
| GitHub | PRs/issues | Not needed; use the `gh` CLI | Built in |
| AWS docs (`awslabs.aws-documentation-mcp-server`) | Optional, for infra work | Personal `~/.claude.json` | Personal |

- Check the endpoint URL against Atlassian's current docs when you implement this. No credentials are stored
  in the repo; each developer authenticates through OAuth.
- Jira **writes** (comments, transitions) only happen inside skills marked `disable-model-invocation: true`.
