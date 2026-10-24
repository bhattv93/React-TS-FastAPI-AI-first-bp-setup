"""Create an empty Flyway migration named with the current UTC timestamp.

Usage (via ``just db-new create_items``)::

    uv run --project backend python backend/scripts/new_migration.py create_items
"""

import re
import sys
from datetime import UTC, datetime
from pathlib import Path

MIGRATIONS_DIR = Path(__file__).resolve().parents[1] / "db" / "migrations"
NAME_PATTERN = re.compile(r"^[a-z][a-z0-9_]*$")


def main(argv: list[str]) -> int:
    """Create the migration file.

    Parameters
    ----------
    argv : list[str]
        Command-line arguments; the first argument is the snake_case description.

    Returns
    -------
    int
        Process exit code (``2`` for a missing or invalid name).
    """
    if len(argv) != 2 or not NAME_PATTERN.match(argv[1]):
        print("usage: new_migration.py <snake_case_description>", file=sys.stderr)
        return 2
    version = datetime.now(UTC).strftime("%Y%m%d%H%M")
    path = MIGRATIONS_DIR / f"V{version}__{argv[1]}.sql"
    path.write_text(
        "-- Applied migrations are immutable. Fix mistakes with a NEW migration.\n\n",
        encoding="utf-8",
        newline="\n",
    )
    print(path.relative_to(MIGRATIONS_DIR.parents[1]).as_posix())
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
