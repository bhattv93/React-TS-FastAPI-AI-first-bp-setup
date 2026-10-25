"""Fail when a Markdown file links to a file or heading that does not exist.

Documentation rots first at its links: a renamed file or a reworded heading silently breaks every page
that points at it. This check is deliberately local and deterministic, so it needs no network and no
third-party tool and can gate every pull request:

* relative links (``[x](other.md)``, ``[x](../dir/)``) must resolve to a file or directory
* root-relative links (``[x](/README.md)``) resolve from the repository root
* ``#fragment`` links must match a heading in the target Markdown file, using GitHub's slug rules
* reference definitions (``[x]: target``) are checked like inline links
* links inside code fences and inline code are ignored; external URLs (``https:``, ``mailto:``) are not
  checked, because a third-party outage must not fail an unrelated pull request

Usage::

    python3 scripts/check_links.py [repo_root]
"""

import re
import sys
from collections import Counter
from pathlib import Path
from urllib.parse import unquote

SKIPPED_DIRS = {
    ".git",
    ".venv",
    "venv",
    "node_modules",
    "__pycache__",
    "dist",
    "build",
    "htmlcov",
    "coverage",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
}
# The original brief is kept verbatim and is excluded from the linters too.
SKIPPED_FILES = {"docs/project-context.md"}

INLINE_LINK = re.compile(r"\]\(\s*(<[^>]*>|[^)\s]+)(?:\s+[\"'][^\"']*[\"'])?\s*\)")
REFERENCE_DEFINITION = re.compile(r"^\s{0,3}\[[^\]]+\]:\s*(<[^>]*>|\S+)")
HEADING = re.compile(r"^\s{0,3}#{1,6}\s+(.*?)\s*#*\s*$")
FENCE = re.compile(r"^\s{0,3}(```|~~~)")
INLINE_CODE = re.compile(r"`[^`]*`")
EXTERNAL = re.compile(r"^[A-Za-z][A-Za-z0-9+.-]*:")


def slugify(heading: str) -> str:
    """Turn heading text into the anchor GitHub generates for it.

    Parameters
    ----------
    heading : str
        Heading text without the leading ``#`` marks.

    Returns
    -------
    str
        Lower-case anchor with punctuation removed and spaces replaced by hyphens.
    """
    text = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", heading)
    text = text.replace("`", "").lower()
    text = re.sub(r"[^\w\- ]", "", text)
    return text.replace(" ", "-")


def _content_lines(text: str, blank_code: bool = True) -> list[tuple[int, str]]:
    """Return the numbered lines that are prose, with fenced code dropped.

    Parameters
    ----------
    text : str
        Markdown source.
    blank_code : bool
        Remove inline code spans. Headings keep them, because they count toward the anchor.

    Returns
    -------
    list[tuple[int, str]]
        ``(line_number, line)`` pairs, one-based, excluding fenced code.
    """
    lines: list[tuple[int, str]] = []
    in_fence = False
    for number, line in enumerate(text.splitlines(), start=1):
        if FENCE.match(line):
            in_fence = not in_fence
            continue
        if not in_fence:
            lines.append((number, INLINE_CODE.sub("", line) if blank_code else line))
    return lines


def anchors(path: Path, cache: dict[Path, set[str]]) -> set[str]:
    """Collect the heading anchors a Markdown file defines.

    Parameters
    ----------
    path : Path
        Markdown file.
    cache : dict[Path, set[str]]
        Memo of anchors per file, filled in by this function.

    Returns
    -------
    set[str]
        Anchors, with ``-1``, ``-2`` suffixes for repeated headings as GitHub does.
    """
    if path not in cache:
        seen: Counter[str] = Counter()
        found: set[str] = set()
        text = path.read_text(encoding="utf-8")
        for _, line in _content_lines(text, blank_code=False):
            match = HEADING.match(line)
            if match:
                slug = slugify(match.group(1))
                found.add(slug if seen[slug] == 0 else f"{slug}-{seen[slug]}")
                seen[slug] += 1
        cache[path] = found
    return cache[path]


def _targets(line: str) -> list[str]:
    """Extract link targets from one prose line.

    Parameters
    ----------
    line : str
        A line with inline code already removed.

    Returns
    -------
    list[str]
        Inline link targets and, for a reference definition, its target.
    """
    found = [m.group(1) for m in INLINE_LINK.finditer(line)]
    definition = REFERENCE_DEFINITION.match(line)
    if definition:
        found.append(definition.group(1))
    return [t[1:-1] if t.startswith("<") and t.endswith(">") else t for t in found]


def _problem(
    source: Path, target: str, root: Path, cache: dict[Path, set[str]]
) -> str | None:
    """Explain why a link target is broken, or return ``None`` when it is fine.

    Parameters
    ----------
    source : Path
        File containing the link.
    target : str
        Raw link target.
    root : Path
        Repository root, used for root-relative links.
    cache : dict[Path, set[str]]
        Anchor memo shared across calls.

    Returns
    -------
    str | None
        A short description of the problem, or ``None``.
    """
    if EXTERNAL.match(target):
        return None
    path_part, _, fragment = target.partition("#")
    path_part = unquote(path_part.partition("?")[0])
    if not path_part:
        resolved = source
    elif path_part.startswith("/"):
        resolved = root / path_part.lstrip("/")
    else:
        resolved = source.parent / path_part
    if not resolved.exists():
        return f"file not found: {target}"
    if fragment and resolved.is_file() and resolved.suffix == ".md":
        if unquote(fragment).lower() not in anchors(resolved, cache):
            return f"no heading for anchor: {target}"
    return None


def _markdown_files(root: Path) -> list[Path]:
    """List the Markdown files to check, in a stable order.

    Parameters
    ----------
    root : Path
        Repository root.

    Returns
    -------
    list[Path]
        Markdown files outside the skipped folders and files.
    """
    files = []
    for path in sorted(root.rglob("*.md")):
        relative = path.relative_to(root)
        if SKIPPED_DIRS.intersection(relative.parts):
            continue
        if relative.as_posix() in SKIPPED_FILES:
            continue
        files.append(path)
    return files


def check(root: Path) -> list[str]:
    """Check every internal Markdown link under ``root``.

    Parameters
    ----------
    root : Path
        Repository root.

    Returns
    -------
    list[str]
        One ``file:line: problem`` message per broken link; empty when all links resolve.
    """
    errors: list[str] = []
    cache: dict[Path, set[str]] = {}
    for path in _markdown_files(root):
        label = path.relative_to(root).as_posix()
        for number, line in _content_lines(path.read_text(encoding="utf-8")):
            for target in _targets(line):
                problem = _problem(path, target, root, cache)
                if problem:
                    errors.append(f"{label}:{number}: {problem}")
    return errors


def main(argv: list[str]) -> int:
    """Run the check and print the result.

    Parameters
    ----------
    argv : list[str]
        Optional repository root as the first item; defaults to the parent of ``scripts/``.

    Returns
    -------
    int
        ``0`` when all links resolve, ``1`` otherwise.
    """
    root = Path(argv[0]) if argv else Path(__file__).resolve().parents[1]
    errors = check(root)
    for error in errors:
        print(error)
    if errors:
        print(f"{len(errors)} broken internal link(s).")
        return 1
    print("Internal Markdown links OK.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
