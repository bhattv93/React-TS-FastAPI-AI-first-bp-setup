---
paths:
  - "backend/**/*.py"
---

# Python style (backend)

Loads only when a Python file under `backend/` is touched. Enforced by `just lint-backend`.

- **Docstrings:** numpy style on every public module, class, function and method, with `Parameters`,
  `Returns`, `Raises` and `Yields` where they apply. Pylint's `docparams` check fails otherwise.
- **Types:** full annotations; mypy runs `--strict`. Prefer `X | None` over `Optional[X]`. No `Any` in
  service signatures. `# type: ignore[code]` needs the specific error code.
- **Imports:** isort with the black profile; first-party package is `app`. Absolute imports only.
- **Formatting:** black, 88 columns. Do not hand-format; the formatter hook runs on save.
- **Async:** use `async def` for I/O. Never call blocking code on the event loop.
- **Logging:** `structlog.get_logger(__name__)`; never log secrets or personal data.
- **Errors:** raise the domain errors in `app/core/errors.py`, not `HTTPException`, outside routers.
- **Config:** read settings through `get_settings()`; never `os.environ` directly.
