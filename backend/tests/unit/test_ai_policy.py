"""The AI-policy check that guards MCP servers and plugins (ADR-0009)."""

import importlib.util
import json
from pathlib import Path
from types import ModuleType

import pytest

REPO_ROOT = Path(__file__).parents[3]
SCRIPT = REPO_ROOT / "scripts" / "check_ai_policy.py"


def _load_script() -> ModuleType:
    spec = importlib.util.spec_from_file_location("check_ai_policy", SCRIPT)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture(name="policy")
def policy_fixture() -> ModuleType:
    return _load_script()


def _write(root: Path, relative: str, data: object) -> None:
    path = root / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data), encoding="utf-8")


def _compliant_repo(root: Path) -> None:
    _write(
        root,
        ".github/ai-policy.json",
        {
            "mcpServers": {
                "approved": ["atlassian"],
                "urls": {"atlassian": "https://mcp.example.com/mcp"},
            },
            "claudePlugins": {"approved": ["a@x"]},
        },
    )
    server = {"type": "http", "url": "https://mcp.example.com/mcp"}
    _write(root, ".mcp.json", {"mcpServers": {"atlassian": server}})
    _write(root, ".vscode/mcp.json", {"servers": {"atlassian": server}})
    _write(
        root, ".claude/settings.json", {"enabledPlugins": {"a@x": True, "off@x": False}}
    )


def test_the_real_repository_complies(policy: ModuleType) -> None:
    assert policy.check(REPO_ROOT) == []


def test_compliant_configuration_passes(policy: ModuleType, tmp_path: Path) -> None:
    _compliant_repo(tmp_path)
    assert policy.check(tmp_path) == []
    assert policy.main(["check", str(tmp_path)]) == 0


def test_unapproved_mcp_server_is_reported_in_both_files(
    policy: ModuleType, tmp_path: Path
) -> None:
    _compliant_repo(tmp_path)
    _write(
        tmp_path,
        ".mcp.json",
        {
            "mcpServers": {
                "atlassian": {"url": "https://mcp.example.com/mcp"},
                "evil": {},
            }
        },
    )
    _write(tmp_path, ".vscode/mcp.json", {"servers": {"other": {}}})
    problems = policy.check(tmp_path)
    assert any(".mcp.json" in p and "evil" in p for p in problems)
    assert any(".vscode/mcp.json" in p and "other" in p for p in problems)


def test_unapproved_plugin_and_risky_settings_are_reported(
    policy: ModuleType, tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    _compliant_repo(tmp_path)
    _write(
        tmp_path,
        ".claude/settings.json",
        {
            "enabledPlugins": {"rogue@x": True},
            "enableAllProjectMcpServers": True,
            "permissions": {"defaultMode": "bypassPermissions"},
        },
    )
    assert policy.main(["check", str(tmp_path)]) == 1
    err = capsys.readouterr().err
    assert "rogue@x" in err
    assert "enableAllProjectMcpServers" in err
    assert "defaultMode" in err


def test_missing_files_mean_nothing_to_check(
    policy: ModuleType, tmp_path: Path
) -> None:
    assert policy.check(tmp_path) == []


def test_an_approved_name_pointing_at_another_host_is_reported(
    policy: ModuleType, tmp_path: Path
) -> None:
    _compliant_repo(tmp_path)
    _write(
        tmp_path,
        ".mcp.json",
        {"mcpServers": {"atlassian": {"type": "http", "url": "https://evil.test/mcp"}}},
    )
    problems = policy.check(tmp_path)
    assert any(
        "atlassian" in p and "https://mcp.example.com/mcp" in p for p in problems
    )


def test_an_approved_name_running_a_local_command_is_reported(
    policy: ModuleType, tmp_path: Path
) -> None:
    _compliant_repo(tmp_path)
    _write(
        tmp_path,
        ".mcp.json",
        {"mcpServers": {"atlassian": {"command": "npx", "args": ["evil"]}}},
    )
    assert any("atlassian" in p for p in policy.check(tmp_path))


def test_servers_declared_in_claude_settings_are_checked(
    policy: ModuleType, tmp_path: Path
) -> None:
    _compliant_repo(tmp_path)
    _write(
        tmp_path,
        ".claude/settings.json",
        {"mcpServers": {"sneaky": {"command": "npx"}}},
    )
    problems = policy.check(tmp_path)
    assert any(".claude/settings.json" in p and "sneaky" in p for p in problems)


def test_skipping_the_dangerous_mode_prompt_is_reported(
    policy: ModuleType, tmp_path: Path
) -> None:
    _compliant_repo(tmp_path)
    _write(
        tmp_path,
        ".claude/settings.json",
        {"skipDangerousModePermissionPrompt": True},
    )
    assert any("skipDangerousModePermissionPrompt" in p for p in policy.check(tmp_path))
