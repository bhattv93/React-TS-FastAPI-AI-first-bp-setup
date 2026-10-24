---
jira: AIFS-0001
summary: "story summary"
status: draft            # draft | approved | implemented
spec-author: "agent or human"
approved-by:
last-synced-from-jira: YYYY-MM-DD
---

# AIFS-0001: {story summary}

## 1. Requirement (copied from Jira; Jira wins on conflict)

**Story:** As a … I want … so that …

| ID | Acceptance criterion |
|----|----------------------|
| AC-1 | Given … When … Then … |
| NFR-1 | … |

## 2. Technical approach

- **Backend:** endpoints (method, path, request/response schema names), service functions, error cases.
- **Data:** tables/columns; Flyway migration name; expand/contract notes.
- **Frontend:** pages, components, hooks, routes; loading, empty and error states.
- **Config / infra:** new env vars (and the `.env.example` update), IaC changes.

## 3. Files expected to change

| Path | Change |
|------|--------|
| `backend/src/app/api/router/{x}.py` | new route |

## 4. Test plan (one row per AC minimum)

| AC | Test level | Test location / name |
|----|-----------|----------------------|
| AC-1 | integration | `tests/integration/test_orders.py::test_ac1_filters_by_status` |

## 5. Risks and rollout

- Migration risk, feature flag, backwards compatibility.

## 6. Open questions

- {resolve before setting status: approved}
