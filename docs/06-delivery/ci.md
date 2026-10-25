---
status: draft
owner: devops-lead
last-reviewed: 2026-10-24
---

# Continuous Integration (GitHub Actions)

Every PR to `main` runs the gates from [05-quality-gates.md](../05-quality-gates.md). A single required check,
**`gate`**, summarises them all.

## Workflow layout

```text
.github/workflows/
  ci.yml                    # entry point on pull_request + push to main; path filters; final `gate` job
  _backend.yml              # reusable (workflow_call): lint, type, test, build image
  _frontend.yml             # reusable: lint, type, test, build
  _repo.yml                 # reusable: markdown/AI-config lint, gitleaks, actionlint, PR title
  cd.yml                    # deploys (see cd-and-environments.md)
  claude-review.yml         # optional AI review (see below)
```

### Why one entry workflow with a `gate` job

With path-filtered *separate* workflows, a required check that never ran stays "pending" and blocks the
merge. Instead, `ci.yml` uses `dorny/paths-filter` to decide which reusable workflows to call. A final job
(`gate`, `if: always()`) fails if any called job failed or was cancelled **and** passes when jobs were
skipped. It also waits for `changes`, so a broken change-detection job fails the gate instead of silently
skipping the backend and frontend jobs. Only `gate` is a required status check. The backend job also runs when `scripts/**`, `.claude/**` or `.github/ai-policy.json` change, because the unit
tests for those files live in the backend suite. The repo-hygiene job fails a pull request that modifies,
renames or deletes a file in `backend/db/migrations` (an applied migration is immutable). The workflow also
runs on `edited` pull requests, so fixing a wrong PR title re-runs the title check without a new push.

## Jobs

| Workflow | Job | Steps |
|----------|-----|-------|
| `_backend` | `lint` | `astral-sh/setup-uv` (cache), `uv sync --locked`, `black --check`, `isort --check-only`, `pylint src`, `mypy src` |
| | `test` | Postgres service container, then `docker run flyway/flyway … migrate`, then `pytest` (coverage XML), then `diff-cover --fail-under=80`, then the coverage summary in the job summary |
| | `contract` | Export `openapi.json` from the app and fail if it differs from the committed `frontend/src/api/openapi.json` |
| | `image` | `docker build` (no push on PRs); Trivy scan for HIGH/CRITICAL |
| `_frontend` | `lint` | `pnpm install --frozen-lockfile`, `prettier --check`, `eslint`, `tsc --noEmit` |
| | `test` | `vitest run --coverage`, then `diff-cover` |
| | `client` | `pnpm api:gen`, then `git diff --exit-code src/api` |
| | `build` | `pnpm build` (upload `dist/` artifact on `main`) |
| `_security` | `backend-deps` / `frontend-deps` | `scripts/check_deps.py`: lock consistency, package compatibility, `pip-audit`, `pnpm audit`, strict peers from scratch. Also runs weekly via `security.yml` |
| | `wiz` | Optional Wiz CLI scan (skipped until `WIZ_ENABLED=true`); see [vulnerability-management.md](../07-engineering-process/vulnerability-management.md#wiz) |
| `_repo` | `docs` | `markdownlint-cli2`, AI-config size and name lint ([md-governance](../03-ai-first/md-governance.md#change-control)) |
| | `security` | `gitleaks`, `pip-audit`, `pnpm audit --prod` |
| | `meta` | `actionlint`; PR title regex: conventional commit + `(AIFS-0001)` |

Standards for all workflows:

- `permissions: contents: read` by default; widen only where needed.
- `concurrency: { group: ci-${{ github.ref }}, cancel-in-progress: true }`.
- Third-party actions **pinned by commit SHA**; Dependabot keeps them updated.
- Container images are **pinned by digest** everywhere: the `Dockerfile`, `docker-compose.yml`, the Postgres
  and Flyway images in `_backend.yml`, and the gitleaks and actionlint images in `_repo.yml`. Dependabot
  bumps the Dockerfile and compose digests; images referenced only inside workflow scripts are bumped by
  hand, so review them when a scanner release matters.
- No long-lived AWS keys. CI never deploys from PRs.

## Branch protection (repository ruleset on `main`)

- Require a PR. Require the **`gate`** status check. Require branches to be up to date.
- At least one approval from **CODEOWNERS**, and two for `infra/**`, `.github/workflows/**`, `.claude/**` and
  `backend/db/migrations/**` (via CODEOWNERS teams).
- Dismiss stale approvals on new commits. Require conversation resolution.
- Squash merge only, with the PR title as the commit message (feeds release-please). No force pushes.

## AI review jobs

| Reviewer | Setup | Role |
|----------|-------|------|
| **Copilot code review** | Ruleset option "automatically request Copilot review". Reads `.github/copilot-instructions.md` | First-pass comments on every PR |
| **Claude** (optional) | `claude-review.yml` using `anthropics/claude-code-action`, triggered on `pull_request` and `@claude` comments. Auth uses the `ANTHROPIC_API_KEY` GitHub Actions secret (environment-scoped; rotate it regularly) | Deeper review against `CLAUDE.md` and rules; can apply fixes when asked with `@claude` |

AI reviews are **advisory**. The author must address or answer every comment, and human CODEOWNER approval
is always required.
