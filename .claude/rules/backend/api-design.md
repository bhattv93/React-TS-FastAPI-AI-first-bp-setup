---
paths:
  - "backend/src/app/api/**"
  - "backend/src/app/schemas/**"
---

# API design (routers and schemas)

- One router module per domain in `api/router/<domain>.py`, registered in `api/routes.py`. All routes live
  under `/api/v1`.
- Routers do HTTP only: parse, call one service function, return a schema. No SQL, no business rules.
- Declare `response_model` and the success `status_code` on every route. Use `SessionDep` and `SettingsDep`
  from `api/deps.py`.
- Schemas are Pydantic v2: `XCreate`, `XUpdate`, `XRead`. Read models set
  `model_config = ConfigDict(from_attributes=True)`. Schemas never import ORM models.
- Errors use the standard envelope through the domain exceptions; do not invent new error shapes.
- A change to a schema changes the OpenAPI contract: run `just api-gen` in the same change and commit the
  regenerated client.
- Tag a test with `@pytest.mark.ac("AIFS-0001", "AC-1")` for each acceptance criterion the route serves.
