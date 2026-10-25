"""Fail if the committed AI configuration drifts outside the policy allowlist (ADR-0009).

Checks, relative to the repository root:

* ``.mcp.json``, ``.vscode/mcp.json`` and ``.claude/settings.json`` declare only approved MCP
  servers, and each approved server still points at its pinned URL (a renamed host or a local
  command under an approved name is a violation).
* ``.claude/settings.json`` enables only approved plugins.
* ``.claude/settings.json`` does not auto-approve project MCP servers, default to bypass mode or
  skip the dangerous-mode prompt.

Usage::

    uv run --project backend python scripts/check_ai_policy.py [repo_root]
"""

import json
import sys
from pathlib import Path
from typing import Any


def _load(path: Path) -> dict[str, Any]:
    """Read a JSON file, returning an empty mapping when it does not exist.

    Parameters
    ----------
    path : Path
        File to read.

    Returns
    -------
    dict[str, Any]
        Parsed JSON object, or ``{}`` when the file is missing.
    """
    if not path.exists():
        return {}
    data: dict[str, Any] = json.loads(path.read_text(encoding="utf-8"))
    return data


def check(root: Path) -> list[str]:
    """Return the list of policy violations found under ``root``.

    Parameters
    ----------
    root : Path
        Repository root.

    Returns
    -------
    list[str]
        Human-readable violations; empty when the configuration complies.
    """
    policy = _load(root / ".github" / "ai-policy.json")
    approved_servers = set(policy.get("mcpServers", {}).get("approved", []))
    pinned_urls: dict[str, str] = policy.get("mcpServers", {}).get("urls", {})
    approved_plugins = set(policy.get("claudePlugins", {}).get("approved", []))
    problems: list[str] = []

    settings = _load(root / ".claude" / "settings.json")
    declared = (
        (".mcp.json", _load(root / ".mcp.json").get("mcpServers", {})),
        (".vscode/mcp.json", _load(root / ".vscode" / "mcp.json").get("servers", {})),
        (".claude/settings.json", settings.get("mcpServers", {})),
    )
    for relative, servers in declared:
        for name in sorted(servers):
            if name not in approved_servers:
                problems.append(
                    f"{relative}: MCP server '{name}' is not on the allowlist in "
                    ".github/ai-policy.json"
                )
                continue
            pinned = pinned_urls.get(name)
            found = servers[name].get("url")
            if pinned is not None and found != pinned:
                problems.append(
                    f"{relative}: MCP server '{name}' must use {pinned} "
                    f"(found {found or 'a local command'})"
                )

    enabled = {name for name, on in settings.get("enabledPlugins", {}).items() if on}
    problems += [
        f".claude/settings.json: plugin '{name}' is not on the allowlist in .github/ai-policy.json"
        for name in sorted(enabled - approved_plugins)
    ]
    if settings.get("enableAllProjectMcpServers") is True:
        problems.append(".claude/settings.json: enableAllProjectMcpServers must not be true")
    if settings.get("permissions", {}).get("defaultMode") in {"bypassPermissions", "auto"}:
        problems.append(".claude/settings.json: defaultMode must not bypass permission prompts")
    if settings.get("skipDangerousModePermissionPrompt") is True:
        problems.append(".claude/settings.json: skipDangerousModePermissionPrompt must not be true")
    return problems


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
        print(f"AI policy violation: {problem}", file=sys.stderr)
    if not problems:
        print("AI policy check passed")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
