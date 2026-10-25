---
paths:
  - "backend/tests/**"
---

# Backend tests

- `unit/` needs no database and no Docker. `integration/` uses Testcontainers Postgres and skips itself
  when Docker is unavailable.
- Use the `client` and `app` fixtures from `tests/conftest.py`; override dependencies with
  `app.dependency_overrides` and the fakes in `tests/fixtures/`.
- Write the failing test for an acceptance criterion first, then the code. Name tests after the behaviour,
  and mark them `@pytest.mark.ac("AIFS-0001", "AC-1")`.
- Assert behaviour, not implementation. A test that cannot fail when the code is wrong is worthless; if
  asked to raise coverage, write tests that assert outcomes.
- Coverage must stay at or above 80% (`--cov-fail-under` is set in `pyproject.toml`). Never lower it.
- Docstrings are not required in tests.
