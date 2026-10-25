---
status: draft
owner: tech-lead
last-reviewed: 2026-10-24
---

# Quality Gates

Because most code is AI-written, the gates are what make it safe to merge. Every gate is **automated**, and
each one runs at the earliest layer where it is fast enough.

## Where each gate runs

| Gate | IDE (save) | Claude hook (per edit) | pre-commit | `just check` | CI (PR) |
|------|:-:|:-:|:-:|:-:|:-:|
| black + isort | ✅ | ✅ | ✅ | ✅ | ✅ |
| pylint (incl. numpy docstrings) | ✅ (extension) | — | ✅ (changed files) | ✅ | ✅ |
| mypy `--strict` | ✅ (extension) | — | ✅ | ✅ | ✅ |
| pytest + coverage ≥80% | Test explorer | — | — | ✅ | ✅ |
| Flyway validate + drift test | — | — | — | ✅ | ✅ |
| prettier | ✅ | ✅ | ✅ | ✅ | ✅ |
| eslint | ✅ | — | ✅ (changed files) | ✅ | ✅ |
| `tsc --noEmit` | ✅ | — | — | ✅ | ✅ |
| vitest + RTL + coverage ≥80% | Vitest extension | — | — | ✅ | ✅ |
| API client up to date | — | — | — | ✅ | ✅ |
| Secret scan (gitleaks) | — | Hook blocks `.env` | ✅ | — | ✅ |
| Conventional commit / PR title with Jira key | — | — | ✅ (commit-msg) | — | ✅ |
| markdownlint + AI-config size lint | ✅ | — | ✅ | ✅ | ✅ |
| Dependency health and audit (`just deps-check`: `uv lock --check`, `uv pip check`, `pip-audit`, `pnpm audit`, strict peers) | — | — | — | Manual (needs network) | ✅ every PR + weekly |

`just check` is the single local command that mirrors CI. Agents run it before declaring work done.

## Backend

All configuration lives in `backend/pyproject.toml`:

```toml
[tool.black]
line-length = 88
target-version = ["py313"]

[tool.isort]
profile = "black"
known_first_party = ["app"]

[tool.pylint.main]
py-version = "3.13"
load-plugins = ["pylint.extensions.docparams", "pylint.extensions.docstyle"]

[tool.pylint.format]
max-line-length = 88

[tool.pylint.parameter_documentation]
default-docstring-type = "numpy"
accept-no-param-doc = false
accept-no-raise-doc = false
accept-no-return-doc = false
accept-no-yields-doc = false

[tool.pylint."messages control"]
disable = ["too-few-public-methods"]   # Pydantic/SQLAlchemy models

[tool.mypy]
python_version = "3.13"
strict = true
plugins = ["pydantic.mypy"]
warn_unused_ignores = true

[tool.pytest.ini_options]
testpaths = ["tests"]
asyncio_mode = "auto"
addopts = "--cov=app --cov-branch --cov-report=term-missing --cov-report=xml --cov-fail-under=80"
markers = ["ac(key, id): links a test to a Jira acceptance criterion"]
```

Docstrings follow **numpy style** for every public module, class, function and method:

```python
def list_orders(session: AsyncSession, status: OrderStatus | None = None) -> list[Order]:
    """List orders, newest first.

    Parameters
    ----------
    session : AsyncSession
        Active database session.
    status : OrderStatus or None, optional
        Filter by status. ``None`` returns all orders.

    Returns
    -------
    list[Order]
        Matching orders ordered by ``created_at`` descending.
    """
```

Pylint `docparams` checks that parameters, returns and raises are documented. It does not fully validate the
numpy section format. If that becomes a problem, add the `numpydoc` pre-commit hook (`numpydoc-validation`).

## Frontend

- `tsconfig.json`: `"strict": true`, `"noUncheckedIndexedAccess": true`, `"noImplicitOverride": true`.
- `eslint.config.js` (flat config):
  - `typescript-eslint` (`strictTypeChecked`), `eslint-plugin-react-hooks`, `eslint-plugin-react-refresh`,
    `eslint-plugin-jsx-a11y`, `eslint-config-prettier` (last)
  - `no-restricted-imports` for layering ([frontend.md](02-architecture/frontend.md))
- `.prettierrc`: defaults, plus `"singleQuote": true` and `"trailingComma": "all"`. `.prettierignore` excludes
  `src/api/`.
- `vitest.config.ts`: `environment: "jsdom"`, `setupFiles: ["src/tests/setup.ts"]`, coverage as below.

## Coverage

| Rule | Backend | Frontend |
|------|---------|----------|
| Overall threshold | `--cov-fail-under=80` (lines + branches) | `coverage.thresholds: { lines: 80, branches: 80, functions: 80, statements: 80 }`, provider `v8` |
| New / changed lines | `diff-cover coverage.xml --compare-branch=origin/main --fail-under=80` | `diff-cover coverage/cobertura-coverage.xml …` (vitest `reporter: ["text", "cobertura"]`) |
| Allowed exclusions | `# pragma: no cover` only with a reason comment; never on business logic | `src/api/**` (generated), `src/main.tsx`, `**/*.d.ts` |

Coverage is a floor, not a goal. Reviewers reject tests that execute code without asserting behaviour. The
`generate-tests` skill is told to write behavioural assertions.

## pre-commit (`.pre-commit-config.yaml`)

Hooks: `black`, `isort`, local `pylint` and `mypy` (through `uv run`), `prettier`, local `eslint` (through
`pnpm`), `gitleaks`, `markdownlint-cli2`, `check-yaml`, `end-of-file-fixer`, `trailing-whitespace`, and a
conventional commit message check (`commit-msg` stage). It is installed by `just setup`.
