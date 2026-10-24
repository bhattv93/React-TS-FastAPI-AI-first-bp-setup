"""Lint the AI instruction files against the context budgets in docs/03-ai-first/md-governance.md.

Every token in an instruction file is paid for on every session, so the budgets are enforced, not
suggested:

* ``CLAUDE.md`` at most 150 lines; ``backend/``, ``frontend/``, ``infra/`` ``CLAUDE.md`` at most 100
* ``.github/copilot-instructions.md`` at most 30 lines
* each ``.claude/rules/**/*.md`` at most 60 lines and scoped with ``paths:``
* each ``.claude/skills/<name>/SKILL.md`` at most 500 lines, ``name`` equal to its folder, a
  ``description`` of at most 1024 characters, and ``disable-model-invocation: true`` for anything that
  deploys or releases
* each ``.claude/agents/<name>.md`` at most 100 lines with ``name``, ``description``, ``tools`` and a
  pinned ``model`` (cost routing: no agent silently inherits the most expensive model)
* no ``CLAUDE.md`` ``@``-imports of ``docs/`` (imports load in full, every session)

Usage::

    python3 scripts/check_ai_config.py [repo_root]
"""

import re
import sys
from pathlib import Path

LIMITS = {
    "CLAUDE.md": 150,
    "backend/CLAUDE.md": 100,
    "frontend/CLAUDE.md": 100,
    "infra/CLAUDE.md": 100,
    ".github/copilot-instructions.md": 30,
}
RULE_LINES = 60
SKILL_LINES = 500
AGENT_LINES = 100
DESCRIPTION_CHARS = 1024
SIDE_EFFECT_WORDS = ("deploy", "release", "publish")


def parse_frontmatter(text: str) -> dict[str, str]:
    """Parse the simple ``key: value`` frontmatter used by skills, agents and rules.

    Parameters
    ----------
    text : str
        File contents.

    Returns
    -------
    dict[str, str]
        Top-level keys mapped to their raw value (empty string for block lists such as ``paths:``).
        Empty when the file has no frontmatter.
    """
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return {}
    data: dict[str, str] = {}
    for line in lines[1:]:
        if line.strip() == "---":
            return data
        match = re.match(r"^([A-Za-z][\w-]*):\s*(.*)$", line)
        if match:
            data[match.group(1)] = match.group(2).strip().strip('"')
    return {}  # unterminated frontmatter


def _lines(path: Path) -> int:
    """Count the lines in a file.

    Parameters
    ----------
    path : Path
        File to measure.

    Returns
    -------
    int
        Number of lines.
    """
    return len(path.read_text(encoding="utf-8").splitlines())


def _check_budgets(root: Path) -> list[str]:
    """Check instruction-file size budgets and forbidden imports.

    Parameters
    ----------
    root : Path
        Repository root.

    Returns
    -------
    list[str]
        Violations.
    """
    problems: list[str] = []
    for relative, limit in LIMITS.items():
        path = root / relative
        if path.exists() and _lines(path) > limit:
            problems.append(
                f"{relative}: {_lines(path)} lines exceeds the budget of {limit}"
            )
    for path in root.rglob("CLAUDE.md"):
        if any(part in {"node_modules", ".venv"} for part in path.parts):
            continue
        for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            if re.search(r"(^|\s)@docs/", line):
                problems.append(
                    f"{path.relative_to(root).as_posix()}:{number}: do not @-import docs into CLAUDE.md "
                    "(imports load every session); link to them instead"
                )
    return problems


def _check_rules(root: Path) -> list[str]:
    """Check path-scoped rule files.

    Parameters
    ----------
    root : Path
        Repository root.

    Returns
    -------
    list[str]
        Violations.
    """
    problems: list[str] = []
    for path in sorted((root / ".claude" / "rules").rglob("*.md")):
        name = path.relative_to(root).as_posix()
        text = path.read_text(encoding="utf-8")
        if _lines(path) > RULE_LINES:
            problems.append(
                f"{name}: {_lines(path)} lines exceeds the budget of {RULE_LINES}"
            )
        if "paths" not in parse_frontmatter(text):
            problems.append(
                f"{name}: rules must declare `paths:` so they load only when relevant"
            )
    return problems


def _check_skills(root: Path) -> list[str]:
    """Check skill definitions.

    Parameters
    ----------
    root : Path
        Repository root.

    Returns
    -------
    list[str]
        Violations.
    """
    problems: list[str] = []
    for path in sorted((root / ".claude" / "skills").glob("*/SKILL.md")):
        name = path.relative_to(root).as_posix()
        meta = parse_frontmatter(path.read_text(encoding="utf-8"))
        folder = path.parent.name
        if _lines(path) > SKILL_LINES:
            problems.append(
                f"{name}: {_lines(path)} lines exceeds the hard limit of {SKILL_LINES}"
            )
        if meta.get("name") != folder:
            problems.append(f"{name}: `name` must equal the folder name '{folder}'")
        description = meta.get("description", "")
        if not description:
            problems.append(
                f"{name}: missing `description` (it decides when the skill triggers)"
            )
        elif len(description) > DESCRIPTION_CHARS:
            problems.append(
                f"{name}: description is {len(description)} chars; keep it under {DESCRIPTION_CHARS}"
            )
        if (
            any(word in folder for word in SIDE_EFFECT_WORDS)
            and meta.get("disable-model-invocation") != "true"
        ):
            problems.append(
                f"{name}: side-effect skills must set `disable-model-invocation: true`"
            )
    return problems


def _check_agents(root: Path) -> list[str]:
    """Check subagent definitions.

    Parameters
    ----------
    root : Path
        Repository root.

    Returns
    -------
    list[str]
        Violations.
    """
    problems: list[str] = []
    for path in sorted((root / ".claude" / "agents").glob("*.md")):
        name = path.relative_to(root).as_posix()
        meta = parse_frontmatter(path.read_text(encoding="utf-8"))
        if _lines(path) > AGENT_LINES:
            problems.append(
                f"{name}: {_lines(path)} lines exceeds the budget of {AGENT_LINES}"
            )
        if meta.get("name") != path.stem:
            problems.append(f"{name}: `name` must equal the file name '{path.stem}'")
        for required in ("description", "tools", "model"):
            if not meta.get(required):
                reason = (
                    " (pin a model so cost routing is explicit)"
                    if required == "model"
                    else ""
                )
                problems.append(f"{name}: missing `{required}`{reason}")
    return problems


def check(root: Path) -> list[str]:
    """Return every AI-configuration violation under ``root``.

    Parameters
    ----------
    root : Path
        Repository root.

    Returns
    -------
    list[str]
        Human-readable violations; empty when everything complies.
    """
    return (
        _check_budgets(root)
        + _check_rules(root)
        + _check_skills(root)
        + _check_agents(root)
    )


def main(argv: list[str]) -> int:
    """Run the check and print violations.

    Parameters
    ----------
    argv : list[str]
        Command-line arguments; an optional first argument is the repository root.

    Returns
    -------
    int
        ``0`` when compliant, ``1`` when there are violations.
    """
    root = Path(argv[1]) if len(argv) > 1 else Path(__file__).resolve().parents[1]
    problems = check(root)
    for problem in problems:
        print(f"AI config violation: {problem}", file=sys.stderr)
    if not problems:
        print("AI config check passed")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
