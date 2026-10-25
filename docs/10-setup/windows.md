---
status: draft
owner: tech-lead
last-reviewed: 2026-10-24
---

# Windows Setup Guide

From a clean Windows 10/11 machine to a green `just check`. Work through the steps in order; every step ends
with a **Check** that proves it worked.

## Conventions

- Commands are for **PowerShell**. Run them from the **repository root** unless a step says otherwise.
- `<repo-url>` is your organisation's clone URL for this repository.
- After each `winget install`, **close and reopen the terminal** so the new tools are on `PATH`.
- No step needs administrator rights, except where marked **(admin)**.

> **Verification status** (Windows 11). Run and confirmed: steps 3, 4, 5 (installs and checks), 10, 11, 12 and 13
> (including the commit-message hook, the native API, the Vite proxy and the Docker database). Docker Desktop (6)
> and `gh` (7) were installed but not signed in to or freshly installed from scratch. Not run: the fresh clone in
> step 9, the Git, Node and VS Code installers (1, 2, 8: standard vendor installers), the VS Code wiring in step
> 14, and the account sign-ins in step 15, which depend on your organisation.

## Overview

| # | Step | Tool |
|---|------|------|
| 1 | Git | Git for Windows |
| 2 | Node.js 22 or newer | Node LTS |
| 3 | Python tooling | uv (installs Python 3.13 for you) |
| 4 | pnpm | pnpm |
| 5 | Task runner | just |
| 6 | Containers **(admin)** | Docker Desktop |
| 7 | GitHub CLI | gh |
| 8 | Editor | VS Code + extensions |
| 9 | Get the code | git clone |
| 10 | Install project dependencies | `just setup` |
| 11 | Local configuration | `backend/.env` |
| 12 | Run the stack | `just db-up`, `just dev-*` |
| 13 | Run every gate | `just check` |
| 14 | Editor wiring | interpreter, extensions |
| 15 | AI tools | Claude Code, Copilot |

## 1. Git

```powershell
winget install --id Git.Git -e
git config --global core.longpaths true
git config --global user.name "Your Name"
git config --global user.email "you@your-company.com"
```

**Check:** `git --version` prints a version. Line endings are handled by the repository's `.gitattributes`;
you do not need to change `core.autocrlf`.

## 2. Node.js 22 or newer

```powershell
winget install --id OpenJS.NodeJS.LTS -e
```

**Check:** `node --version` prints `v22.x` or newer (the repository requires `>=22`; `.nvmrc` says 22).

## 3. uv and Python 3.13

uv manages Python versions, virtual environments and the lockfile. You do not install Python separately.

```powershell
winget install --id astral-sh.uv -e --scope user
```

Reopen the terminal, then:

```powershell
uv python install 3.13
```

**Check:** `uv --version` prints a version and `uv python list --only-installed` lists `cpython-3.13`.

## 4. pnpm

```powershell
npm install -g pnpm
```

> Why not `corepack enable`? With Node installed under Program Files it needs administrator rights and fails
> with `EPERM`. The repository pins the pnpm version in `frontend/package.json` (`packageManager`), and pnpm
> honours it.

If PowerShell refuses to run `pnpm.ps1` ("running scripts is disabled"):

```powershell
Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned
```

**Check:** `pnpm --version` prints a version.

## 5. just

```powershell
winget install --id Casey.Just -e --scope user
```

**Check:** `just --version` prints a version. After step 9, `just` in the repository root lists the recipes.

## 6. Docker Desktop (admin)

Docker runs Postgres and Flyway locally and powers the integration tests.

```powershell
winget install --id Docker.DockerDesktop -e
```

Docker Desktop needs virtualisation enabled and may ask for a restart. Start it from the Start menu and wait
until it reports that the engine is running.

**Check:** `docker info` prints server details (no "cannot find the file specified" error).

## 7. GitHub CLI

```powershell
winget install --id GitHub.cli -e --scope user
gh auth login
```

Choose **GitHub.com**, **HTTPS**, and sign in through the browser with your company-managed account.

**Check:** `gh auth status` shows you as logged in.

## 8. VS Code

```powershell
winget install --id Microsoft.VisualStudioCode -e --scope user
```

You install the project's extensions in step 14, after you have opened the repository.

**Check:** `code --version` prints a version.

## 9. Get the code

Clone **outside any cloud-synced folder** (OneDrive, Dropbox). The repository creates tens of thousands of
small files in `node_modules/` and `.venv/`, which sync clients slow down, lock or conflict on. Pick a plain
local folder such as `$HOME\dev`.

```powershell
mkdir $HOME\dev -Force
cd $HOME\dev
git clone <repo-url>
cd <repository-folder>
```

**Check:** `just --list` shows the recipes (`setup`, `dev-backend`, `check`, ...) and `git status` is clean.

## 10. Install project dependencies

```powershell
just setup
```

This runs `uv sync` in `backend/`, `pnpm install` in `frontend/`, and installs the git hooks (pre-commit).

**Check:** `backend/.venv` and `frontend/node_modules` exist, and `git commit --allow-empty -m "bad message"`
is **rejected** by the commit-msg hook (then use `chore: test hook (AIFS-0001)` or skip the commit).

## 11. Local configuration

```powershell
Copy-Item backend/.env.example backend/.env
```

The defaults work with the local Docker database. `backend/.env` is **gitignored**; never commit it.

**Check:** `git status` does not list `backend/.env`.

## 12. Run the stack

```powershell
just db-up
```

Then, in two separate terminals:

```powershell
just dev-backend
just dev-frontend
```

**Check:**

- `http://localhost:8000/health` returns `{"status":"ok",...}`
- `http://localhost:8000/api/v1/ready` returns `{"status":"ok","database":"ok"}`
- `http://localhost:8000/docs` shows the API documentation
- `http://localhost:5173` shows the app with **API is healthy**

Stop the database with `just db-down`.

## 13. Run every gate

```powershell
just check
```

This is exactly what CI runs: black, isort, pylint, mypy, pytest (80% coverage), prettier, eslint, tsc, vitest
(80% coverage), the API-client freshness check, and the AI-policy check. Integration tests start their own
Postgres with Docker and skip themselves if Docker is not running.

**Check:** the command ends without errors. Use `just fmt` to auto-fix formatting problems.

## 14. Editor wiring

1. Open the repository folder in VS Code (`code .`).
2. Accept **Install Recommended Extensions** (from `.vscode/extensions.json`).
3. Command Palette > **Python: Select Interpreter** > choose the one under `backend/.venv`.
4. Open the Testing view; pytest (backend) and Vitest (frontend) tests should appear.

**Check:** saving a Python or TypeScript file formats it, and the Problems panel shows mypy/pylint/eslint
results.

## 15. AI tools

Only **Claude Code** and **GitHub Copilot** are approved, with **company-managed accounts**. Read
[AI access governance](../03-ai-first/ai-access-governance.md) before you start, especially which data must
never be sent to an AI tool.

1. **GitHub Copilot:** sign in to VS Code with your company GitHub account. The shared settings in
   `.vscode/settings.json` already enable reading `CLAUDE.md` and instruction files.
2. **Claude Code:** install it from the official instructions at `https://code.claude.com/docs`, then run
   `claude` in the repository root and sign in with your company account. Do not use a personal account or a
   personal API key.
3. **Jira (MCP):** the first time a tool uses the Atlassian server, approve it and sign in through your browser.
   You only grant the access you have in Jira.

**Check:** in Claude Code, `/status` shows your company account and the project settings
(`.claude/settings.json`). Ask it to summarise `CLAUDE.md`.

## Local files that are never committed

These exist only on your machine and are covered by `.gitignore`:

| File or folder | What it is |
|----------------|-----------|
| `backend/.env` | Your local backend configuration |
| `CLAUDE.local.md` | Your personal Claude Code instructions for this project |
| `.claude/settings.local.json` | Your personal Claude Code permission overrides |
| `backend/.venv/`, `frontend/node_modules/` | Installed dependencies |
| `frontend/dist/`, `coverage/`, `htmlcov/` | Build and test output |
| `.vscode/` files other than the shared ones | Your personal editor state |

## Troubleshooting

| Symptom | Cause and fix |
|---------|---------------|
| `just`, `uv` or `gh` "is not recognized" | The terminal predates the install. Close and reopen it |
| `pnpm` "running scripts is disabled" | `Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned` |
| `corepack enable` fails with `EPERM` | Use `npm install -g pnpm` (step 4) |
| `docker: error during connect ... dockerDesktopLinuxEngine` | Docker Desktop is not running. Start it and wait for the engine |
| Integration tests are skipped | Docker is not running; start it and re-run `just test-backend` |
| Testcontainers "port mapping ... 8080 is not available" | Already handled: the test setup disables the Ryuk sidecar. Update the repository if you still see it |
| `/ready` says "Database is not reachable", or `password authentication failed for user "app"` | Another PostgreSQL is answering on the port. The project database is published on `127.0.0.1:5433` precisely to avoid a locally installed PostgreSQL on 5432; make sure `APP_DATABASE_URL` in `backend/.env` uses port **5433** (re-copy `backend/.env.example` if it says 5432) |
| Port 5433, 8000 or 5173 already in use | Stop the other service, or change the published port in `docker-compose.yml` (and `APP_DATABASE_URL`) |
| `uv python install` is blocked or slow | A proxy or firewall is blocking downloads. Ask IT to allow `github.com` and `astral.sh` |
| `pnpm install` fails with `ERR_PNPM_PEER_DEP_ISSUES` | Strict peer dependencies are on. Do not override: pick versions that satisfy the peer ranges (see the known-constraints table in the vulnerability-management doc) |
| Slow installs, file-lock errors | The repository is inside OneDrive or another synced folder. Move it (step 9) |
| Pre-commit hook fails on first run | It is downloading hook environments (needs network access to GitHub). Re-run the commit |

## Next

- Read the [contributing guide](../../CONTRIBUTING.md) and the
  [Jira workflow](../04-spec-driven-development/jira-workflow.md).
- macOS users: see the [macOS guide](macos.md) (planned).
