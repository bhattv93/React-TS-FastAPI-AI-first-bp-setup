---
status: draft
owner: tech-lead
last-reviewed: 2026-10-24
---

# Dependencies and Versioning

Tooling decision: [ADR-0003](../adr/0003-uv-and-pnpm.md).

## Runtime versions (pinned)

| Tool | Pin location |
|------|--------------|
| Python 3.13 | `backend/.python-version`, `requires-python = ">=3.13,<3.14"` |
| Node 22 LTS | `.nvmrc` and `"engines"` in `frontend/package.json` |
| pnpm | `"packageManager": "pnpm@<x.y.z>"` (Corepack) |
| Postgres | `postgres:16` in compose and CI; RDS engine version in IaC |
| Docker base images | Tag + digest in `Dockerfile` |

## Declaring dependencies

- **Backend:** `uv add <pkg>` (or `uv add --dev <pkg>` for the dev group). `pyproject.toml` holds compatible
  ranges (`>=x.y,<x+1`). `uv.lock` pins exact versions and is committed. CI runs `uv sync --locked`.
- **Frontend:** `pnpm add <pkg>` (or `-D`). Use caret ranges in `package.json`. `pnpm-lock.yaml` is
  committed. CI runs `pnpm install --frozen-lockfile`.
- Agents add dependencies only through these commands, never by hand-editing the lockfiles (a hook blocks
  it). A new runtime dependency needs a one-line justification in the PR.

## Updates (`.github/dependabot.yml`)

| Ecosystem | Directory | Schedule | Grouping |
|-----------|-----------|----------|----------|
| `uv` | `/backend` | weekly | minor + patch grouped |
| `npm` (pnpm lockfile) | `/frontend` | weekly | minor + patch grouped; separate groups for `react*`, `@testing-library/*`, `eslint*` |
| `github-actions` | `/` | weekly | grouped |
| `docker` | `/backend` | weekly | — |

- Security updates are raised immediately (Dependabot alerts on).
- Patch updates of dev dependencies may auto-merge once `gate` is green. Everything else needs a normal review.
- Majors get a Jira task, and their changelogs get read.

## Dependency health and security

Compatibility checks, vulnerability scanning, the weekly schedule and the severity policy are in
[vulnerability-management.md](vulnerability-management.md).

## Security and licensing

- CI runs `pip-audit` and `pnpm audit --prod`, failing on high or critical.
- The image is scanned with Trivy in CI and with ECR scan on push.
- Optional: license allowlist check (`pip-licenses`, `license-checker`) before v1.0.

## Application versioning

- **SemVer** for the product, driven by conventional commits through **release-please**
  ([cd-and-environments.md](../06-delivery/cd-and-environments.md#releases)).
- `CHANGELOG.md` is generated, never hand-edited.
- The API version (`/api/v1`) is independent of the app version. It is bumped only on breaking API changes,
  with the old version supported for an agreed deprecation window.
- The git SHA is injected at build time (`APP_VERSION`), and it appears in logs and the `/health` response.
