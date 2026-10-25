"""SessionStart hook: tell the model which Jira story the branch is for.

Branch names look like ``type/AIFS-0001/short-slug``. When the branch matches, the hook adds
one short line of context (story key, spec path and the spec's status) so every session
starts oriented, without the model spending tokens to discover it.
"""

import json
import os
import re
import subprocess
import sys
from pathlib import Path

BRANCH_PATTERN = re.compile(r"^[a-z]+/([A-Z]{4}-\d{4})/")
STATUS_PATTERN = re.compile(r"^status:\s*(\S+)", re.MULTILINE)


def story_key(branch: str) -> str | None:
    """Extract the Jira key from a branch name.

    Parameters
    ----------
    branch : str
        Current git branch.

    Returns
    -------
    str or None
        The key such as ``AIFS-0001``, or ``None`` when the branch does not follow the convention.
    """
    match = BRANCH_PATTERN.match(branch)
    return match.group(1) if match else None


def describe(root: Path, key: str) -> str:
    """Build the one-line context message for a story.

    Parameters
    ----------
    root : Path
        Repository root.
    key : str
        Jira key.

    Returns
    -------
    str
        The context line.
    """
    spec = root / "docs" / "specs" / f"{key}.md"
    if not spec.exists():
        return (
            f"Current story: {key}. No spec yet at docs/specs/{key}.md; "
            "run /jira-story-to-spec before implementing."
        )
    match = STATUS_PATTERN.search(spec.read_text(encoding="utf-8"))
    status = match.group(1) if match else "unknown"
    note = (
        "" if status == "approved" else " Do not implement until the spec is approved."
    )
    return f"Current story: {key}. Spec: docs/specs/{key}.md (status: {status}).{note}"


def main() -> int:
    """Emit SessionStart context for the current branch.

    Returns
    -------
    int
        Always ``0``.
    """
    json.load(sys.stdin)  # payload is not needed, but must be consumed
    root = Path(os.environ.get("CLAUDE_PROJECT_DIR") or ".").resolve()
    result = subprocess.run(
        ["git", "branch", "--show-current"],
        cwd=root,
        capture_output=True,
        text=True,
        check=False,
    )
    key = story_key(result.stdout.strip())
    if key:
        output = {
            "hookSpecificOutput": {
                "hookEventName": "SessionStart",
                "additionalContext": describe(root, key),
            }
        }
        print(json.dumps(output))
    return 0


if __name__ == "__main__":
    sys.exit(main())
