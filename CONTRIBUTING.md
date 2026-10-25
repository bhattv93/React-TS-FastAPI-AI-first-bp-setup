# Contributing

Thanks for helping. This project is built spec-first: requirements and acceptance criteria live in Jira, and
AI tools (Claude Code, GitHub Copilot) write much of the code. The gates below are what keep that safe.

## 1. Set up

Follow the setup guide for your OS: [docs/10-setup/windows.md](docs/10-setup/windows.md). Then run
`just setup` once from the repository root.

## 2. Pick up a story

1. Take a Jira story whose acceptance criteria (`AC-1`...) are clear. Questions go back to the story owner.
2. Make sure `docs/specs/AIFS-0001.md` exists and is approved (see
   [docs/04-spec-driven-development/jira-workflow.md](docs/04-spec-driven-development/jira-workflow.md)).
3. Create a branch named `type/AIFS-0001/short-slug`, for example `feature/AIFS-0042/order-status-filter`.
   Types: `feature`, `fix`, `refactor`, `chore`, `docs`, `test`, `ci`, `hotfix`.

## 3. Write the change

- Write a failing test for each acceptance criterion first, then the code.
- Follow the layering and style rules in [`CLAUDE.md`](CLAUDE.md), `backend/CLAUDE.md` and
  `frontend/CLAUDE.md`. They apply to humans and AI alike.
- Backend: numpy-style docstrings, full type hints, black + isort, pylint and mypy clean.
- Frontend: strict TypeScript, prettier and eslint clean, accessible components.
- Schema changes are new Flyway migrations. Never edit one that has been applied.
- Never edit generated files (`frontend/src/api/schema.d.ts`). Run `just api-gen` instead.

## 4. Check locally

```text
just check
```

This runs every gate CI runs, including the **80% coverage** threshold for both sides. Pre-commit hooks run
the fast gates on every commit.

## 5. Open the pull request

- Commit messages and the PR title use Conventional Commits and end with the Jira key:
  `feat(orders): add status filter (AIFS-0042)`.
- Fill in the PR template, including which test covers which acceptance criterion.
- CI must pass (`gate` is the required check). Copilot may leave a first-pass review; address or answer
  every comment.
- A code owner (see [.github/CODEOWNERS](.github/CODEOWNERS)) must approve. Changes to `infra/`,
  `.github/workflows/`, `.claude/`, `CLAUDE.md` and migrations need maintainer review.

## 6. Using AI tools

You are accountable for every line you commit, whoever or whatever wrote it. Read the tests first when
reviewing AI-written code: would they fail if the behaviour were wrong? Details:
[docs/03-ai-first/ai-workflows-playbook.md](docs/03-ai-first/ai-workflows-playbook.md).

## Reporting bugs

Use Jira with the bug template ([docs/04-spec-driven-development/templates/bug.md](docs/04-spec-driven-development/templates/bug.md)).
Include the `X-Request-ID` from the failing response.
