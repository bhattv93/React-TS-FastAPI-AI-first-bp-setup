---
name: new-api-endpoint
description: Scaffold a FastAPI endpoint with its Pydantic schemas, service function and tests, following this repo's layering and error envelope. Use when adding or changing a REST endpoint under backend/src/app/api.
argument-hint: "[resource] [method]"
---

# New API endpoint

**Canonical example to copy:** `backend/src/app/api/router/health.py` (router),
`backend/src/app/schemas/health.py` (schemas), and `backend/tests/unit/test_health.py` (tests). Read them
instead of relying on memory; they are always current.

## Steps

1. **Schemas** in `backend/src/app/schemas/<domain>.py`: `XCreate`, `XUpdate`, `XRead`
   (`ConfigDict(from_attributes=True)` on read models).
2. **Service** in `backend/src/app/services/<domain>.py`: an `async` function taking the session and plain
   arguments, owning the transaction, raising `NotFoundError` / `ConflictError`. No `fastapi` imports.
3. **Router** in `backend/src/app/api/router/<domain>.py`: declare `response_model` and `status_code`, use
   `SessionDep`, call one service function. Register it in `backend/src/app/api/routes.py`.
4. **Tests first** in `backend/tests/unit/` (service with fakes) and `backend/tests/integration/` when the
   query matters. Cover success, validation error and not-found. Tag acceptance criteria with
   `@pytest.mark.ac(...)`.
5. **Contract:** run `just api-gen` and commit the regenerated `frontend/src/api` files.
6. **Verify:** `just lint-backend` and `just test-backend`.

If the endpoint needs a new table or column, use the `new-db-migration` skill first.
Numpy docstrings with `Parameters` and `Returns` are required on public functions.
