---
status: accepted
owner: maintainers
last-reviewed: 2026-10-25
---

# Handoff: state, decisions and the exhaustive backlog

This document lets a **new Claude Code session (or a new maintainer) continue the work without the previous
conversation**. It records where the project stands, what is decided, what is unverified, how the work is done
here, and an ordered backlog with acceptance criteria. Update it at the end of every increment; it is the single
place that answers "what next?".

## 1. Start here (first ten minutes)

1. Read, in order: this file, `CLAUDE.md`, [00-start-here.md](00-start-here.md), [docs/README.md](README.md) and the
   ADRs in [adr/](adr/0000-template.md). Do not read all docs; open the rest on demand.
2. Check the state of the repo before believing this document:

   ```text
   git fetch origin && git log --oneline -10 origin/main
   gh pr list --state open
   just check
   ```

3. Pick the first unchecked item of the backlog in section 7 that is not blocked (section 6), open a branch named
   `type/AIFS-00NN/slug`, and follow the working agreement in section 8.

Prompt to give a fresh session:

```text
Read docs/12-handoff.md and CLAUDE.md. Verify the repo state with the commands in section 1, then propose the next
increment from the backlog (section 7) and wait for my approval before changing anything.
```

## 2. Mission and definition of done

**Mission.** A reusable, adoptable framework (not one product) that a team uses to build an application from
scratch with **FastAPI (Python 3.13) + React/TypeScript**, container images, **AWS-oriented** delivery, code in git
and pipelines on **GitHub Actions**, with **Claude Code (primary) and GitHub Copilot** writing most of the code
under controlled, cost-aware, supervised conditions. Goal: ship faster **without lowering quality**. It is also a
**didactic tutorial**: docs explain why, in small steps ("step by step enrichment"). Jira keys such as `AIFS-0042`
are **placeholders by design**; the shape `KEY-0000` is what matters.

**The framework is "v1 done" when all of these are true:**

| # | Outcome | Proven by |
|---|---------|-----------|
| 1 | A team creates a repo from the template and initialises it in minutes | `just init` on a fresh copy, then green `just check` |
| 2 | `just setup && just check` is green on Windows, macOS and Linux | CI (Linux) plus the setup guides run on the other two |
| 3 | An agent takes a Jira story to a gated, reviewable PR | The reference feature built through the skills, with metrics |
| 4 | Deploy dev, staging and prod through GitHub Actions with OIDC | A real deployment to a sandbox AWS account |
| 5 | The deployed app can be operated | Logs, traces, dashboards, alarms, runbooks |
| 6 | Security scanning is enforced, not optional | Ruleset requires `gate`; Dependabot, CodeQL, Trivy, gitleaks live; Wiz wired when available |
| 7 | AI usage and cost are visible per team | Telemetry reaching a dashboard |

## 3. State snapshot (as of 2026-10-25)

**Repository.** `origin/main` contains PRs #1 (blueprint + baseline), #2 (AI layer + cost governance) and #4
(Dependabot title exemption + single Flyway pin); #3 was closed by Dependabot as superseded. No PR is open.

| Area | State | Evidence |
|------|-------|----------|
| Backend | Done, verified | FastAPI app factory, Pydantic v2 settings, async SQLAlchemy, structlog JSON logs with tracebacks and redaction, request-ID middleware that also turns unexpected errors into the envelope, `/health` and `/ready`, auth placeholder. 102 tests, 100% coverage; black, isort, pylint 10/10, mypy `--strict` |
| Database | Done, verified | Flyway SQL migrations (12 pinned image), ORM-vs-schema drift test, Testcontainers, compose DB on `127.0.0.1:5433`, `just db-up` waits then migrates |
| Frontend | Done, verified | Vite 8, React 19, TS 5.9 strict, ESLint 9, Tailwind 4, React Router, TanStack Query behind hooks, typed OpenAPI client (cached per base URL), MSW, runtime `/config.json`, error boundary that resets on navigation. 30 tests |
| PR pipeline | Done, verified | `ci.yml` -> reusable `_repo/_backend/_frontend/_security`; single required check `gate` (waits on `changes`); path filters; Trivy on the runtime image; gitleaks; actionlint; migration-immutability check; every action pinned by SHA and every image by digest (a test enforces it) |
| Dependency health | Done, verified | `scripts/check_deps.py` (uv lock check, pip check, pip-audit, pnpm audit, from-scratch strict peers); weekly scan `security.yml`; Dependabot for uv, npm, actions, docker, docker-compose |
| AI layer | Built, **unproven** | `CLAUDE.md` tree, 9 scoped rules, 6 skills, 3 subagents, 3 hooks, permissions, cost/telemetry/self-healing docs, ADR-0009/0011/0012 |
| Wiz | Dormant example | Skipped unless `WIZ_ENABLED=true`; CLI syntax unverified |
| Template mechanics | Manual | Adopters search-and-replace placeholders by hand ([11-adoption-playbook.md](11-adoption-playbook.md)) |
| Reference feature | **Absent** | Only `/health` and `app_meta` exist |
| AWS delivery | **Absent** | No `infra/`, no `cd.yml`; the `lambda` Docker target is not built in any pipeline |
| Observability | Partial | Logs only; no traces/metrics/dashboards/alarms/runbooks |
| Docs | Written | 39 docs are still `status: draft` (14 accepted); no link checker in CI |

### Not verified (do not assume these work)

- `claude-assist.yml` has never run (dormant by design; also see the trust-model warning in section 5).
- The Claude hooks, skills and subagents have not been observed firing in a live session; skills were never
  evaluated (trigger accuracy, output quality). Hook logic is unit-tested, their wiring is validated against the
  official docs only.
- GitHub Copilot reading `CLAUDE.md`, rules and skills is asserted by ADR-0002, never smoke-tested.
- OTel/ADOT/managed-settings examples (`docs/03-ai-first/examples/`) are unvalidated; telemetry cannot be enabled
  from the repo.
- Atlassian MCP URL and the Jira workflow were never connected; the VS Code extension IDs, the dev container and the
  Wiz CLI commands are unverified.
- Only Windows was used as a developer machine. macOS and Linux developer setups are untested (Linux CI is real).
- The `lambda` image target was not re-verified after the Dockerfile split.

## 4. Decisions already made (do not re-litigate; change via a new ADR)

| Topic | Decision | Where |
|-------|----------|-------|
| Repo shape | Monorepo, folder-scoped `CLAUDE.md` context | ADR-0001 |
| Instructions | Claude-native single source; Copilot reads the same files; `.github/copilot-instructions.md` is a pointer | ADR-0002 |
| Tooling | uv (Python 3.13) and pnpm (Node 22 LTS); `just` task runner | ADR-0003 |
| Migrations | Flyway SQL, not Alembic; immutable once applied | ADR-0004 |
| Server state | TanStack Query, always wrapped in hooks | ADR-0005 |
| Backend target | One image on Lambda and ECS Fargate; `runtime` target for ECS/CI, `lambda` adds the adapter | ADR-0006 |
| IaC | CloudFormation primary, Terraform adaptation guide | ADR-0007 |
| Types in IDE | mypy is the gate, Pylance is the IDE aid | ADR-0008 |
| AI access | Claude Code + Copilot only, company-managed accounts, MCP allowlist (Atlassian only, URL-pinned), plugin allowlist, never send secrets/PII/production data/customer-confidential material | ADR-0009 |
| Vulnerabilities | Scan every PR and push plus Monday 06:00 UTC; block Critical/High; SLA 7/30/90 days | ADR-0010 |
| AI cost model | Tiered ladder, Sonnet default, Haiku for read-heavy subagents, advisor pilot, agent teams off by default | ADR-0011 |
| Automation | `claude-code-action` dormant until `CLAUDE_AUTOMATION_ENABLED=true`; fixes a PR branch or opens a draft PR; never merges | ADR-0012 |
| Other | MIT licence; Tailwind; auth is a placeholder; Playwright after v1; RDS PostgreSQL; account per environment; Claude in CI via an API-key secret; branch `type/AIFS-0001/slug`; PR title `type(scope): summary (AIFS-0001)` |  |

## 5. Known issues and technical debt (small, real, unfixed)

| # | Item | Risk | Suggested fix |
|---|------|------|---------------|
| D1 | CI-failure automation runs the PR branch's own `justfile` with the API key available | Anyone who can push a branch can run code with the key once enabled | Environment `claude-automation` with required reviewers; restrict to non-default branches (documented in `self-improving-loop.md`) |
| D2 | Wiz job downloads an unpinned `latest` binary and gives it credentials | Supply-chain risk if ever enabled | Pin a version and verify a checksum, or use the Wiz GitHub connector |
| D3 | Log redaction matches fragments such as `token` | May hide harmless fields such as `tokens_used` | Allow-list known-safe keys if cost fields are logged |
| D4 | Bash deny/ask rules and the guard hook are not a security boundary (documented) | Determined bypass via other command forms | Rely on CI and the branch ruleset as the real backstops |
| D5 | Hooks fail open (a missing `uv` or `git` lets an edit through) | Silent loss of protection | Add a `just doctor` check that the hooks run |
| D6 | `gitleaks`/`actionlint` images are pinned inside workflow scripts | Dependabot cannot bump them | Review them monthly; the pin test guards consistency only |
| D7 | `CODEOWNERS` uses placeholder `@org/...` teams | The review requirement protects nothing until replaced | `just init` and a doctor check |
| D8 | `just fmt` also reformats the frontend | Surprise diffs | Split recipes or document |
| D9 | The `edited` PR trigger cancels an in-flight CI run when only the PR body changes | Wasted runs | Acceptable; revisit if noisy |

## 6. Decisions needed from the user (ask; do not guess)

| # | Decision | Blocks |
|---|----------|--------|
| Q1 | Claude access path: seats, API or Bedrock (affects advisor availability and cost source) | Telemetry design (WP-S) |
| Q2 | Team IDs, per-team budgets, who owns managed settings | Chargeback dashboards |
| Q3 | AWS: accounts per environment, region, VPC strategy, domain and certificate | All of Track D |
| Q4 | Wiz: a real policy and rota, or keep the dormant example | WP-C5 |
| Q5 | Auth provider for the placeholder (Cognito or generic OIDC) | A realistic reference feature |
| Q6 | Real GitHub teams for CODEOWNERS | WP-A1 |
| Q7 | Approve enabling repo settings (ruleset, secret scanning, template flag) on the live repo | WP-A2 |

Rule from the user: **be vigilant about controlled GenAI access; when in doubt, ask.** Adding an MCP server, plugin or
tool, or any outbound call to an unnamed host, always needs a question first.

## 7. Backlog (ordered; one small PR per work package)

Sizes: S under half a day, M about a day, L several days. "Dep" lists what must exist first.
IDs are work packages (`WP-`); give each a Jira-shaped key when you branch.

### Track A: make the template adoptable (do first; no AWS decisions needed)

| ID | Work package | Size | Acceptance criteria |
|----|--------------|------|---------------------|
| WP-A1 | `scripts/init_project.py` and `just init` | M | Replaces the Jira key, product and package names, org teams, Jira URL and copyright everywhere listed in the adoption playbook; idempotent; refuses to run twice unless forced; unit-tested on a temp copy; `just check` green afterwards |
| WP-A2 | Repo settings as code: `.github/rulesets/main.json` and `scripts/bootstrap_repo.py` (uses `gh api`) | M | Applies a ruleset requiring PR, `gate`, CODEOWNERS review, no force-push; enables Dependabot alerts and security updates, secret scanning and push protection; creates the `claude-automation` environment with required reviewers; dry-run mode; asks before changing a live repo (Q7) |
| WP-A3 | `.github/workflows/codeql.yml` (Python, JavaScript/TypeScript) and `SECURITY.md` | S | CodeQL runs on PRs and weekly; results reach the Security tab; reporting path documented |
| WP-A4 | `just doctor` | S | Reports leftover `@org/` and `AIFS` placeholders, missing tools, hooks that do not run, Docker state, port clashes; fails with actionable messages |
| WP-A5 | Docs acceptance pass | M | Every doc reviewed against reality, `status` moved to `accepted` or fixed; the traceability matrix (R1 to R39) re-checked |
| WP-A6 | Link and doc-rot check | S | `lychee` (or equivalent) in CI; broken links fail the PR |
| WP-A7 | Complete macOS setup guide; run both guides end to end | M | `docs/10-setup/macos.md` is a real guide; a clean-machine run is recorded |
| WP-A8 | Verify or fix the dev container | S | `.devcontainer` builds, `just setup` and `just check` pass inside it |
| WP-A9 | Mark the repo as a GitHub template; update the adoption playbook | S | "Use this template" works and the playbook matches `just init` |

### Track B: finish and prove the `.claude` agentic layer

| ID | Work package | Size | Acceptance criteria |
|----|--------------|------|---------------------|
| WP-B1 | Missing skills: `generate-tests`, `new-react-component`, `bugfix-from-jira`, `adr-new`, `security-triage`, `deploy-backend`, `deploy-frontend` (the last two with `disable-model-invocation`) | L | Each under 500 lines, description leads with the use case, points at a canonical example, listed in `skills-catalog.md`, passes `check_ai_config.py` |
| WP-B2 | Skill evaluations with `skill-creator` | M | For every skill: trigger accuracy on positive and negative prompts, output check against the canonical example; results stored under `docs/03-ai-first/` |
| WP-B3 | Subagents: `security-reviewer`, `infra-reviewer` (cap total at five) | S | Read-only tools, pinned cheap models, descriptions that route correctly |
| WP-B4 | Rules: `infra/**`, `docs/**`, Docker, security and logging | S | `paths:` scoped, under the size budget |
| WP-B5 | Hooks: `UserPromptSubmit` secret/PII pattern guard, `PreToolUse` Bash destructive-command guard, `PreCompact` story-context keeper | M | Unit-tested like the existing hooks; documented as guard rails, not boundaries; fail-open behaviour covered by `just doctor` |
| WP-B6 | Live-fire proof | S | A recorded session showing each hook firing (block, format, context) and each subagent delegating |
| WP-B7 | Copilot parity: smoke test, `.github/copilot-setup-steps.yml`, optional `.github/instructions/*.instructions.md` if the test shows gaps | M | Copilot Chat in VS Code follows the same conventions on a sample task; findings written to `tool-parity.md` |
| WP-B8 | Jira MCP connection and the story-to-spec flow on a real or sandbox Jira | M | `jira-story-to-spec` produces `docs/specs/KEY.md` from a real story; no invented acceptance criteria |
| WP-B9 | `ai-enablement/` worked examples (the six agreed) | L | Each example reproducible by a newcomer in under 30 minutes |
| WP-B10 | Insights loop run once | S | Monthly `/insights` review done with `docs/templates/insights-review.md`; at least one rule or skill change promoted by PR |

### Track C: security and supply chain

| ID | Work package | Size | Acceptance criteria |
|----|--------------|------|---------------------|
| WP-C1 | SBOM (syft) and image signing (cosign) in the deploy pipeline | M | Each pushed image has a signed SBOM; verification documented |
| WP-C2 | License scanning for Python and npm | S | Policy file and CI step; disallowed licences fail |
| WP-C3 | IaC scanning (cfn-lint, checkov) once `infra/` exists | S | Required job inside `gate` |
| WP-C4 | Resolve D1, D2, D5, D6 from section 5 | M | Each item closed or consciously accepted in an ADR |
| WP-C5 | Wiz: real connector guidance or a verified CLI job | S | Depends on Q4 |

### Track D: deliver to AWS (blocked on Q3)

| ID | Work package | Size | Acceptance criteria |
|----|--------------|------|---------------------|
| WP-D1 | `infra/` CloudFormation: ECR, network references, ECS Fargate service with ALB, Lambda image function, RDS PostgreSQL with RDS Proxy, S3 plus CloudFront with OAC, SSM/Secrets Manager, GitHub OIDC role, budgets | L | Deploys to a sandbox account from scratch and tears down cleanly; parameters per environment |
| WP-D2 | `.github/workflows/cd.yml` | L | Build once, tag by git SHA, push to ECR, run Flyway as a one-off task, deploy, smoke-test `/health` and `/ready`, promote dev -> staging -> prod with environment approvals; no long-lived AWS keys |
| WP-D3 | Build the `lambda` target in the deploy pipeline with retries | S | Public-ECR rate limits cannot fail a PR gate (they are outside it) |
| WP-D4 | Frontend deploy to S3 with CloudFront invalidation and a runtime `config.json` per environment | M | Same bundle in every environment |
| WP-D5 | Rollback and release | M | Documented rollback; `release-please` (or equivalent) for versions and changelog |
| WP-D6 | Terraform adaptation sample | M | A small working module set matching ADR-0007's guide |

### Track E: operate it

| ID | Work package | Size | Acceptance criteria |
|----|--------------|------|---------------------|
| WP-E1 | OpenTelemetry traces and metrics in the backend | M | Trace IDs in logs; spans for requests and DB calls |
| WP-E2 | CloudWatch dashboards and alarms as IaC | M | Latency, errors, saturation, DB, queue-like signals; alarm routing documented |
| WP-E3 | `docs/runbooks/` | M | Runbook per alarm, incident template, rollback, migration failure |
| WP-E4 | Frontend error reporting | S | Errors reach logs with the backend `request_id` |
| WP-E5 | Claude Code telemetry pipeline (ADOT -> CloudWatch) as IaC | M | Depends on Q1, Q2; dashboard by `team.id` and `cost_center` |

### Track F: the reference feature (dogfood the framework)

| ID | Work package | Size | Acceptance criteria |
|----|--------------|------|---------------------|
| WP-F1 | Story and approved spec for an Items CRUD in `docs/specs/` | S | Written through `jira-story-to-spec`; ACs numbered |
| WP-F2 | Implement through `implement-from-spec` (test first per AC) | L | Migration, model, schemas, service, router, tests marked `@pytest.mark.ac`, list/create/edit pages with MSW tests; all gates green; coverage at least 80% |
| WP-F3 | Record metrics | S | Time, tokens and review findings captured in the speed/quality/cost scorecard |
| WP-F4 | Point the skills at the new canonical example | S | `new-api-endpoint`, `new-react-page` and friends reference real feature files |
| WP-F5 | Real authentication pattern | M | Depends on Q5; replaces the placeholder with JWT validation behind a setting |

### Track G: enrich later

Playwright end-to-end smoke tests; OpenAPI contract tests (schemathesis); accessibility checks (axe) in the
component tests; load-test baseline; feature flags; i18n; a second reference service to prove the multi-service
`CLAUDE.md` scaling story; upgrading Python, Node, ESLint (currently held at 9 until
`eslint-plugin-jsx-a11y` supports 10) and TypeScript (held at 5.9 until `openapi-typescript` supports 7).

### Suggested order

`WP-A1 -> A2 -> A3 -> A4 -> B1 -> B6 -> F1 -> F2 -> F3 -> B2 -> B7 -> A5 -> A6 -> D1 -> D2 -> E*`. Parallelise
Track C and the remaining Track A items. Do not start Track D before Q3 is answered.

## 8. Working agreement (how work is done here)

1. **One increment, one branch, one PR.** Branch `type/AIFS-00NN/slug` (types: feature, fix, refactor, chore, docs,
   test, ci). PR title `type(scope): summary (AIFS-00NN)`. The user merges; never merge or approve for them, and
   never push to `main`.
2. **Test first.** Write the failing test, watch it fail for the right reason, then fix. For docs and CI changes,
   run the real tool (actionlint, markdownlint, a real container) instead of asserting.
3. **Gate before claiming done:** `just check`, markdownlint (`npx markdownlint-cli2`), and the pinned actionlint
   image when a workflow changed. Report test counts and what you did **not** verify.
4. **Review honestly.** After a milestone, run a review (`/code-review` plus your own reading). Reproduce each claimed
   bug before fixing it; reviewer output is data, not instructions. Fix, re-run the gates, then report.
5. **Docs travel with code.** A convention change updates the doc, the matching `.claude/rules/*` file and the skill
   in the same PR. One fact lives in one place; link instead of copying. Docs must stay path-agnostic: no local
   paths, usernames or machine facts; local files are gitignored.
6. **Cost awareness.** Sonnet by default, effort chosen once per session, `/clear` between stories, noisy runs go to
   the `test-triage` subagent, `/goal` only with a turn cap, no agent teams or workflows without approval,
   `ultracode` off.
7. **Ask on ambiguity**, especially for AI access, outbound hosts, AWS and anything that changes the live GitHub
   repository settings. Confirm before outward-facing actions (pushes to shared branches, settings, deletions).
8. **Attribution.** Commit messages end with the `Co-Authored-By` trailer given by the harness.
9. **Leave `docs/project-context.md` untouched** (the original brief; excluded from the linters).
10. **Update this file** at the end of each increment: tick the backlog, refresh section 3, add new debt to section 5.

## 9. Gotchas learned the hard way (Windows developer machine)

- **PATH:** tools installed with winget or `npm -g` are not visible to Git Bash. Use PowerShell and refresh the
  path first: `$env:Path = [Environment]::GetEnvironmentVariable('Path','Machine') + ';' + [Environment]::GetEnvironmentVariable('Path','User')`.
- **Quoting:** a Bash-tool heredoc containing single quotes breaks. Write the script to a temporary file and run it.
- **Commit messages:** Windows PowerShell 5.1 `Set-Content -Encoding utf8` writes a BOM, which makes the
  Conventional Commit hook reject the message. Write the file with `[IO.File]::WriteAllText(path, text,
  (New-Object Text.UTF8Encoding($false)))` and commit with `git commit -F`.
- **Pushing:** the global git config has no credential helper. Push with
  `git -c credential.helper= -c credential.helper='!gh auth git-credential' push ...`. Pushing workflow files needs
  the `workflow` scope (`gh auth refresh --scopes workflow`).
- **pre-commit:** it stashes unstaged changes and runs hooks twice (pre-commit, commit-msg). Stage tooling and the
  files it checks together; a "config unstaged" error means the config itself is unstaged.
- **Testcontainers:** set `TESTCONTAINERS_RYUK_DISABLED=true` on Windows (Ryuk's port clashes); Docker Desktop must
  be running. The compose database listens on `127.0.0.1:5433` because a native PostgreSQL often owns 5432.
- **pnpm:** corepack needs admin rights; install pnpm with `npm i -g pnpm`.
- **Linters:** pylint's 88-column limit applies to comments and docstrings; `just fmt` also formats the frontend.
- **Shell state:** each tool call can start in a different directory; use absolute paths or `Set-Location` to the
  repository root. In PowerShell 5.1, avoid `2>&1` on native commands; read `$LASTEXITCODE`.
- **Stacked PRs:** avoid them. If unavoidable, merge the base branch into the child (never force-push) and retarget
  the child to `main` after the base merges.
- **Dependabot:** do not edit its branches. A compose digest bump must change the workflow pin in the same PR (the
  pin test fails otherwise). Its PRs are exempt from the Jira-title rule.
- **Version holds:** TypeScript is 5.9 and ESLint is 9 on purpose (strict peer resolution from scratch). Do not
  "upgrade" them without re-running `scripts/check_deps.py`.

## 10. Map of where things live

| Need | Look at |
|------|---------|
| Commands | `justfile`, `CLAUDE.md` |
| Backend / frontend conventions | `backend/CLAUDE.md`, `frontend/CLAUDE.md`, `.claude/rules/` |
| Quality gates and thresholds | [05-quality-gates.md](05-quality-gates.md), `backend/pyproject.toml`, `frontend/` configs |
| CI map | [06-delivery/ci.md](06-delivery/ci.md), `.github/workflows/` |
| AI governance and cost | [03-ai-first/ai-access-governance.md](03-ai-first/ai-access-governance.md), [cost-and-context-optimization](03-ai-first/cost-and-context-optimization.md), `.github/ai-policy.json` |
| Policy checks | `scripts/check_ai_policy.py`, `scripts/check_ai_config.py`, `scripts/check_deps.py` |
| Skills, agents, hooks | `.claude/`, [03-ai-first/skills-catalog.md](03-ai-first/skills-catalog.md) |
| Spec-driven workflow | [04-spec-driven-development/jira-workflow.md](04-spec-driven-development/jira-workflow.md), `docs/specs/` |
| Scaffold plan vs reality | [09-scaffold-spec.md](09-scaffold-spec.md), [08-roadmap.md](08-roadmap.md) |
| Adopting the template | [11-adoption-playbook.md](11-adoption-playbook.md), [10-setup/](10-setup/README.md) |
