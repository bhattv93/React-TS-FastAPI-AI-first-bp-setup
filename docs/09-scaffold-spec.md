---
status: draft
owner: tech-lead
last-reviewed: 2026-10-24
---

# Scaffold Specification

Every file to create in milestones M1–M6, and its purpose. Folder-internal code layout is in
[02-architecture/](02-architecture/overview.md#repository-layout).

## Repository root

| File | Purpose |
|------|---------|
| `README.md` | Overview, architecture diagram, quick start (`just setup && just dev`), links to `docs/` |
| `CONTRIBUTING.md` | Workflow (Jira → spec → branch → PR), code style summary with links to the gates, testing requirements, PR process, how to use Claude/Copilot here |
| `LICENSE` | MIT |
| `CLAUDE.md` | Lean repo-wide AI context ([outline](03-ai-first/context-strategy.md#root-claudemd-outline-target-100-lines)) |
| `.editorconfig` | UTF-8, LF, final newline; 4 spaces for Python, 2 for TS/JSON/YAML/MD |
| `.gitattributes` | `* text=auto eol=lf`; the Windows team gets LF consistently; `*.sh`/hook scripts are LF |
| `.gitignore` | Python, Node, `.env`, `.venv`, `coverage/`, `dist/`, `CLAUDE.local.md`, `.claude/settings.local.json` |
| `.nvmrc` | Node 22 LTS version |
| `.pre-commit-config.yaml` | Hooks per [05-quality-gates.md](05-quality-gates.md#pre-commit-pre-commit-configyaml) |
| `.markdownlint.jsonc` | Markdown rules (line length off for tables) |
| `cspell.json` | Project dictionary (pytest, mypy, isort, Flyway, …) |
| `justfile` | Cross-platform task runner (works in PowerShell and bash); recipes below |
| `docker-compose.yml` | `db` (postgres:16), `flyway` (migrate, then exit), `api` (optional) |
| `.mcp.json` | Claude Code MCP: Atlassian (allowlisted in `.github/ai-policy.json`) |
| `scripts/check_deps.py` | Dependency health and vulnerability checks shared by `just deps-check` and CI ([ADR-0010](adr/0010-vulnerability-and-dependency-health.md)) |
| `scripts/check_ai_config.py` | Enforces context budgets: file sizes, scoped rules, skill metadata, pinned subagent models |
| `scripts/check_links.py` | Fails when a Markdown link points at a missing file or heading (internal links only, no network) |
| `.github/workflows/claude-assist.yml` | Dormant, human-merged Claude automation: `@claude`, CI-failure fixes, weekly remediation ([ADR-0012](adr/0012-self-healing-automation-boundaries.md)) |
| `.claude/loop.md` | Default prompt for `/loop`: babysit the current PR |
| `scripts/check_ai_policy.py` | CI/pre-commit check that MCP servers and plugins stay on the allowlist ([ADR-0009](adr/0009-controlled-genai-access.md)) |
| `release-please-config.json`, `.release-please-manifest.json` | Release automation |

### `justfile` recipes

`setup` (uv sync, pnpm install, pre-commit install) · `dev` (db + api + web) · `dev-backend` · `dev-frontend`
· `check` (all gates) · `check-backend` · `check-frontend` · `test` · `fmt` · `api-gen` (export openapi.json,
then generate the TS client) · `db-migrate` · `db-new name=…`

## `.github/`

| File | Purpose |
|------|---------|
| `ai-policy.json` | Allowlist of approved AI tools, MCP servers and Claude plugins |
| `copilot-instructions.md` | ≤30-line pointer ([tool-parity](03-ai-first/tool-parity.md#githubcopilot-instructionsmd-30-lines)) |
| `CODEOWNERS` | Ownership ([git-and-code-review](07-engineering-process/git-and-code-review.md#codeowners-githubcodeowners-illustrative)) |
| `pull_request_template.md` | PR checklist |
| `ISSUE_TEMPLATE/config.yml` | Disables blank issues; links to Jira |
| `dependabot.yml` | Update policy ([dependencies](07-engineering-process/dependencies-and-versioning.md#updates-githubdependabotyml)) |
| `workflows/ci.yml`, `_backend.yml`, `_frontend.yml`, `_repo.yml`, `_security.yml` | PR gates ([ci.md](06-delivery/ci.md)) |
| `workflows/security.yml` | Weekly scheduled vulnerability and dependency scan |
| `workflows/cd.yml`, `release-please.yml` | Delivery |
| `workflows/claude-review.yml` | Optional Claude review |

## `.claude/`

| Path | Purpose |
|------|---------|
| `settings.json` | `enabledPlugins` (existing), `permissions`, `hooks` ([subagents-hooks-mcp](03-ai-first/subagents-hooks-mcp.md)) |
| `rules/**` | Path-scoped conventions ([planned list](03-ai-first/context-strategy.md#planned-files)) |
| `skills/**` | [Skills catalog](03-ai-first/skills-catalog.md) |
| `agents/*.md` | Subagents |
| `hooks/*.py` | `guard_protected_files.py`, `guard_bash.py`, `format_changed_file.py`, `session_context.py` |
| `README.md` | Currently empty. Becomes a short map of this folder with a link to md-governance |

## `.vscode/`

| File | Content |
|------|---------|
| `extensions.json` | `recommendations` below |
| `settings.json` | Format on save; per-language formatters; Python interpreter `backend/.venv`; pytest `cwd` backend; `eslint.workingDirectories: ["frontend"]`; `files.eol: "\n"`; Copilot parity flags ([tool-parity](03-ai-first/tool-parity.md#vs-code-settings-that-enable-parity-vscodesettingsjson)) |
| `launch.json` | Debug FastAPI (uvicorn module, `--reload` off), debug the current pytest, debug Vitest, Chrome against Vite |
| `mcp.json` | Copilot MCP: Atlassian |

Recommended extensions (verify the IDs when you implement this):

| Area | Extension IDs |
|------|---------------|
| Python | `ms-python.python`, `ms-python.vscode-pylance`, `ms-python.mypy-type-checker`, `ms-python.black-formatter`, `ms-python.isort`, `ms-python.pylint` |
| Frontend | `dbaeumer.vscode-eslint`, `esbenp.prettier-vscode`, `vitest.explorer` |
| AI | `anthropic.claude-code`, `github.copilot-chat` |
| Infra / CI | `ms-azuretools.vscode-containers`, `github.vscode-github-actions`, `redhat.vscode-yaml`, `aws-toolkit-vscode` / `kddejong.vscode-cfn-lint` (CloudFormation) |
| Docs / hygiene | `DavidAnson.vscode-markdownlint`, `EditorConfig.EditorConfig`, `streetsidesoftware.code-spell-checker`, `bierner.markdown-mermaid` |
| Optional | `mtxr.sqltools` + `mtxr.sqltools-driver-pg` (DB browsing) |

## `backend/`, `frontend/`, `infra/`

Defined in [overview.md](02-architecture/overview.md#repository-layout), [backend.md](02-architecture/backend.md),
[frontend.md](02-architecture/frontend.md) and [aws-backend.md](06-delivery/aws-backend.md). Each top-level
folder also has its own `CLAUDE.md` and `.env.example` (backend).

## AI enablement examples

`ai-enablement/` teaches the team *how* to work AI-first. It holds worked examples, not instructions the
agent loads.

```text
ai-enablement/
├── README.md                         # what's here, how to run each example, the time each takes
├── examples/
│   ├── 01-story-to-pr/               # sample Jira story → generated spec → session notes → resulting PR diff
│   ├── 02-generate-tests/            # raising coverage on an under-tested service; good vs bad tests
│   ├── 03-bugfix-from-jira/          # failing-test-first bug fix
│   ├── 04-endpoint-and-page/         # new-api-endpoint + new-react-page end to end
│   ├── 05-review-and-refactor/       # code-reviewer subagent, plan-first refactor
│   └── 06-copilot-equivalents/       # the same flows in VS Code Copilot agent mode
├── prompts.md                        # prompt cheat-sheet (prompting norms from the playbook)
└── anti-patterns.md                  # what goes wrong (context bloat, unreviewed AI tests, skipping specs) and the fix
```

Each example has `README.md` (goal, steps, expected output), the input artefacts and the expected result. The
examples are refreshed when a skill changes (owner: tech lead).
