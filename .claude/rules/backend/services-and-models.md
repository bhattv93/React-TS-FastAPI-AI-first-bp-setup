---
paths:
  - "backend/src/app/services/**"
  - "backend/src/app/models/**"
---

# Services and models

- Services hold business logic and own the transaction (`async with session.begin():`). They take a session
  and plain arguments, and never import `fastapi`.
- Raise `NotFoundError`, `ConflictError` or `DomainValidationError`; the error handler turns them into HTTP.
- Models are SQLAlchemy 2.0 `Mapped[...]` classes on `Base`, one module per aggregate, exported from
  `models/__init__.py`. Reuse `TimestampMixin`.
- Constraint and index names follow `NAMING_CONVENTION` so they match the SQL migrations exactly.
- A model change is never complete without its Flyway migration (see the migrations rule). The schema drift
  test fails when they disagree.
- Dependencies point one way: `api -> services -> models`. Do not import upward.
