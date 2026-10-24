"""PostToolUse hook: format the file the agent just edited.

Formatting is mechanical, so it should never cost the model a turn or tokens. The hook runs
the project's own formatter on the single changed file; the full gates still run in
``just check`` and CI.

* ``.py`` under ``backend/``: isort then black (config from ``backend/pyproject.toml``)
* ``.ts .tsx .js .json .css .md`` under ``frontend/``: prettier

It never blocks: a formatter failure is reported on stderr and the edit stands.
"""

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

FRONTEND_SUFFIXES = {".ts", ".tsx", ".js", ".json", ".css", ".md"}


def build_commands(relative: str) -> list[list[str]]:
    """Return the formatter commands for a file.

    Parameters
    ----------
    relative : str
        POSIX-style path of the changed file, relative to the repository root.

    Returns
    -------
    list[list[str]]
        Commands to run in order; empty when the file needs no formatting.
    """
    suffix = Path(relative).suffix
    if relative.startswith("backend/") and suffix == ".py":
        return [
            ["uv", "run", "--project", "backend", "isort", "--quiet", relative],
            ["uv", "run", "--project", "backend", "black", "--quiet", relative],
        ]
    if (
        relative.startswith("frontend/")
        and suffix in FRONTEND_SUFFIXES
        and not relative.startswith("frontend/src/api/")
    ):
        inner = relative.removeprefix("frontend/")
        return [
            [
                "pnpm",
                "--dir",
                "frontend",
                "exec",
                "prettier",
                "--write",
                "--log-level",
                "silent",
                inner,
            ]
        ]
    return []


def main() -> int:
    """Format the changed file reported in the hook payload.

    Returns
    -------
    int
        Always ``0``: formatting problems never block an edit.
    """
    payload = json.load(sys.stdin)
    file_path = payload.get("tool_input", {}).get("file_path")
    if not file_path:
        return 0
    root = Path(
        os.environ.get("CLAUDE_PROJECT_DIR") or payload.get("cwd") or "."
    ).resolve()
    try:
        relative = Path(file_path).resolve().relative_to(root).as_posix()
    except ValueError:
        return 0
    for command in build_commands(relative):
        program = shutil.which(command[0])
        if program is None:
            print(f"format hook: {command[0]} not found; skipped", file=sys.stderr)
            return 0
        result = subprocess.run(
            [program, *command[1:]],
            cwd=root,
            capture_output=True,
            text=True,
            check=False,
        )
        if result.returncode != 0:
            print(
                f"format hook: {' '.join(command)} failed:\n{result.stderr}",
                file=sys.stderr,
            )
            return 0
    return 0


if __name__ == "__main__":
    sys.exit(main())
