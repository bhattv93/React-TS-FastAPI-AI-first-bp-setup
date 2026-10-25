"""PreToolUse hook: block edits to files that must never be changed by hand.

Why a hook and not just an instruction? CLAUDE.md is advisory; the model can still make the
mistake. A hook is deterministic: exit code 2 blocks the tool call and sends stderr back to
the model as the reason (see docs/03-ai-first/subagents-hooks-mcp.md).

Protected:

* ``.env`` files (``.env.example`` is allowed)
* the generated API client (``schema.d.ts`` and ``openapi.json`` in ``frontend/src/api``;
  run ``just api-gen``)
* lockfiles (use ``uv add`` / ``pnpm add``)
* Flyway migrations that are already committed (add a new migration instead)

Standard library only, so it runs under ``uv run --no-project python``.
"""

import json
import os
import subprocess
import sys
from pathlib import Path, PurePosixPath

LOCKFILES = {"backend/uv.lock", "frontend/pnpm-lock.yaml"}
GENERATED = {"frontend/src/api/schema.d.ts", "frontend/src/api/openapi.json"}


def is_tracked(root: Path, relative: str) -> bool:
    """Return whether ``relative`` is tracked by git in ``root``.

    Parameters
    ----------
    root : Path
        Repository root.
    relative : str
        POSIX-style path relative to ``root``.

    Returns
    -------
    bool
        ``True`` when git already tracks the file.
    """
    result = subprocess.run(
        ["git", "ls-files", "--error-unmatch", "--", relative],
        cwd=root,
        capture_output=True,
        check=False,
    )
    return result.returncode == 0


def evaluate(relative: str, tracked: bool) -> str | None:
    """Decide whether an edit is allowed.

    Parameters
    ----------
    relative : str
        POSIX-style path of the file, relative to the repository root.
    tracked : bool
        Whether git already tracks the file (only matters for migrations).

    Returns
    -------
    str or None
        The reason to block the edit, or ``None`` when it is allowed.
    """
    path = PurePosixPath(relative)
    name = path.name
    if (name == ".env" or name.startswith(".env.")) and name != ".env.example":
        return "Environment files hold secrets and are never edited by the agent. Edit .env.example instead."
    if relative in GENERATED:
        return "This file is generated from the backend OpenAPI schema. Run `just api-gen` instead."
    if relative in LOCKFILES:
        return "Lockfiles are managed by the package manager. Use `uv add` / `pnpm add` instead."
    in_migrations = relative.startswith("backend/db/migrations/")
    if in_migrations and name.startswith("V") and name.endswith(".sql") and tracked:
        return (
            "Applied Flyway migrations are immutable. Create a new migration with "
            "`just db-new <name>` instead."
        )
    return None


def main() -> int:
    """Read the hook payload from stdin and block protected edits.

    Returns
    -------
    int
        ``2`` to block the tool call, ``0`` to allow it.
    """
    payload = json.load(sys.stdin)
    file_path = payload.get("tool_input", {}).get("file_path") or payload.get(
        "tool_input", {}
    ).get("notebook_path")
    if not file_path:
        return 0
    root = Path(
        os.environ.get("CLAUDE_PROJECT_DIR") or payload.get("cwd") or "."
    ).resolve()
    try:
        relative = Path(file_path).resolve().relative_to(root).as_posix()
    except ValueError:
        return 0  # outside the repository: not our concern
    reason = evaluate(relative, is_tracked(root, relative))
    if reason:
        print(f"Blocked by repository policy: {reason}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
