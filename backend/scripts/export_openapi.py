"""Write the API's OpenAPI schema to a file for client generation.

Usage (from the repository root, via ``just api-export``)::

    uv run --project backend python backend/scripts/export_openapi.py [output.json]

The default output is ``frontend/src/api/openapi.json``, which is committed so CI
can detect a stale generated client.
"""

import json
import sys
from pathlib import Path

from app.core.config import Settings
from app.main import create_app

DEFAULT_OUTPUT = (
    Path(__file__).resolve().parents[2] / "frontend" / "src" / "api" / "openapi.json"
)


def main(argv: list[str]) -> int:
    """Export the schema.

    Parameters
    ----------
    argv : list[str]
        Command-line arguments; an optional first argument overrides the output.

    Returns
    -------
    int
        Process exit code.
    """
    output = Path(argv[1]) if len(argv) > 1 else DEFAULT_OUTPUT
    settings = Settings(
        _env_file=None,
        database_url="postgresql+asyncpg://export:export@localhost:5432/export",
        secret_key="export-only",
    )
    schema = create_app(settings).openapi()
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        json.dumps(schema, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
