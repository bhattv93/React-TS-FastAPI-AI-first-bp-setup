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
        Process exit code (``2`` for a missing or invalid name, ``1`` if the file exists).
    """
    if len(argv) != 2 or not NAME_PATTERN.match(argv[1]):
        print("usage: new_migration.py <snake_case_description>", file=sys.stderr)
        return 2
    version = datetime.now(UTC).strftime("%Y%m%d%H%M")
    path = MIGRATIONS_DIR / f"V{version}__{argv[1]}.sql"
    taken = sorted(MIGRATIONS_DIR.glob(f"V{version}__*.sql"))
    if taken:
        # Flyway rejects two migrations that share a version, whatever their descriptions.
        print(
            f"a migration with version V{version} already exists ({taken[0].name}); "
            "wait a minute and retry",
            file=sys.stderr,
        )
        return 1
    try:
        # Mode "x" fails instead of truncating a migration that already exists.
        with path.open("x", encoding="utf-8", newline="\n") as handle:
            handle.write(
                "-- Applied migrations are immutable. Fix mistakes with a NEW migration.\n\n"
            )
    except FileExistsError:
        print(
            f"{path.name} already exists; wait a minute or pick another name",
            file=sys.stderr,
        )
        return 1
    print(path.relative_to(MIGRATIONS_DIR.parents[1]).as_posix())
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
