"""The Claude Code hooks that enforce repository policy (docs/03-ai-first/subagents-hooks-mcp.md)."""

import importlib.util
import io
import json
import subprocess
from pathlib import Path
from types import ModuleType

import pytest

HOOKS = Path(__file__).parents[3] / ".claude" / "hooks"


def _load(name: str) -> ModuleType:
    spec = importlib.util.spec_from_file_location(name, HOOKS / f"{name}.py")
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture(name="guard")
def guard_fixture() -> ModuleType:
    return _load("guard_protected_files")


@pytest.fixture(name="fmt")
def fmt_fixture() -> ModuleType:
    return _load("format_changed_file")


@pytest.fixture(name="session")
def session_fixture() -> ModuleType:
    return _load("session_context")


def _stdin(monkeypatch: pytest.MonkeyPatch, payload: dict[str, object]) -> None:
    monkeypatch.setattr("sys.stdin", io.StringIO(json.dumps(payload)))


# ---------------------------------------------------------------- guard_protected_files


@pytest.mark.parametrize(
    ("relative", "tracked", "blocked"),
    [
        ("backend/.env", False, True),
        (".env.local", False, True),
        ("backend/.env.example", False, False),
        ("frontend/src/api/schema.d.ts", False, True),
        ("frontend/src/api/openapi.json", False, True),
        ("backend/uv.lock", False, True),
        ("frontend/pnpm-lock.yaml", False, True),
        ("backend/db/migrations/V202610240001__create_app_meta.sql", True, True),
        ("backend/db/migrations/V202699990001__new_table.sql", False, False),
        ("backend/src/app/main.py", True, False),
    ],
)
def test_guard_decisions(
    guard: ModuleType, relative: str, tracked: bool, blocked: bool
) -> None:
    assert (guard.evaluate(relative, tracked) is not None) is blocked


def test_guard_blocks_with_exit_code_2_and_a_reason(
    guard: ModuleType,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    monkeypatch.setenv("CLAUDE_PROJECT_DIR", str(tmp_path))
    monkeypatch.setattr(guard, "is_tracked", lambda _root, _relative: False)
    _stdin(
        monkeypatch, {"tool_input": {"file_path": str(tmp_path / "backend" / ".env")}}
    )
    assert guard.main() == 2
    assert "Blocked by repository policy" in capsys.readouterr().err


def test_guard_allows_normal_files_and_paths_outside_the_repo(
    guard: ModuleType, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.setenv("CLAUDE_PROJECT_DIR", str(tmp_path / "repo"))
    monkeypatch.setattr(guard, "is_tracked", lambda _root, _relative: False)
    _stdin(
        monkeypatch, {"tool_input": {"file_path": str(tmp_path / "repo" / "README.md")}}
    )
    assert guard.main() == 0
    _stdin(
        monkeypatch, {"tool_input": {"file_path": str(tmp_path / "elsewhere" / ".env")}}
    )
    assert guard.main() == 0
    _stdin(monkeypatch, {"tool_input": {}})
    assert guard.main() == 0


def test_guard_detects_committed_files_with_real_git(
    guard: ModuleType, tmp_path: Path
) -> None:
    subprocess.run(["git", "init", "-q"], cwd=tmp_path, check=True)
    (tmp_path / "tracked.txt").write_text("x", encoding="utf-8")
    subprocess.run(["git", "add", "tracked.txt"], cwd=tmp_path, check=True)
    assert guard.is_tracked(tmp_path, "tracked.txt") is True
    assert guard.is_tracked(tmp_path, "untracked.txt") is False


# ---------------------------------------------------------------- format_changed_file


def test_format_commands_are_chosen_by_area_and_suffix(fmt: ModuleType) -> None:
    py = fmt.build_commands("backend/src/app/main.py")
    assert [c[4] for c in py] == ["isort", "black"]
    ts = fmt.build_commands("frontend/src/pages/HomePage.tsx")
    assert ts == [
        [
            "pnpm",
            "--dir",
            "frontend",
            "exec",
            "prettier",
            "--write",
            "--log-level",
            "silent",
            "src/pages/HomePage.tsx",
        ]
    ]
    assert fmt.build_commands("frontend/src/api/schema.d.ts") == []
    assert fmt.build_commands("docs/README.md") == []
    assert fmt.build_commands("backend/db/migrations/V1__x.sql") == []


def test_format_runs_commands_and_never_blocks(
    fmt: ModuleType,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    monkeypatch.setenv("CLAUDE_PROJECT_DIR", str(tmp_path))
    calls: list[list[str]] = []

    def fake_run(
        command: list[str], **_kwargs: object
    ) -> subprocess.CompletedProcess[str]:
        calls.append(command)
        return subprocess.CompletedProcess(command, 1, "", "boom")

    monkeypatch.setattr(fmt.shutil, "which", lambda name: name)
    monkeypatch.setattr(fmt.subprocess, "run", fake_run)
    _stdin(
        monkeypatch, {"tool_input": {"file_path": str(tmp_path / "backend" / "x.py")}}
    )
    assert fmt.main() == 0
    assert len(calls) == 1  # stops after the first failure
    assert "failed" in capsys.readouterr().err


def test_format_skips_when_the_tool_is_missing_or_file_is_irrelevant(
    fmt: ModuleType,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    monkeypatch.setenv("CLAUDE_PROJECT_DIR", str(tmp_path))
    monkeypatch.setattr(fmt.shutil, "which", lambda _name: None)
    _stdin(
        monkeypatch, {"tool_input": {"file_path": str(tmp_path / "backend" / "x.py")}}
    )
    assert fmt.main() == 0
    assert "not found" in capsys.readouterr().err
    _stdin(monkeypatch, {"tool_input": {"file_path": str(tmp_path / "docs" / "a.md")}})
    assert fmt.main() == 0
    _stdin(
        monkeypatch, {"tool_input": {"file_path": str(tmp_path.parent / "other.py")}}
    )
    assert fmt.main() == 0
    _stdin(monkeypatch, {"tool_input": {}})
    assert fmt.main() == 0


# ---------------------------------------------------------------- session_context


def test_story_key_parses_the_branch_convention(session: ModuleType) -> None:
    assert session.story_key("feature/AIFS-0042/order-filter") == "AIFS-0042"
    assert session.story_key("main") is None
    assert session.story_key("AIFS-0042-no-type") is None


def test_describe_reports_missing_draft_and_approved_specs(
    session: ModuleType, tmp_path: Path
) -> None:
    assert "No spec yet" in session.describe(tmp_path, "AIFS-0001")
    specs = tmp_path / "docs" / "specs"
    specs.mkdir(parents=True)
    (specs / "AIFS-0001.md").write_text("---\nstatus: draft\n---\n", encoding="utf-8")
    assert "Do not implement until the spec is approved" in session.describe(
        tmp_path, "AIFS-0001"
    )
    (specs / "AIFS-0001.md").write_text(
        "---\nstatus: approved\n---\n", encoding="utf-8"
    )
    message = session.describe(tmp_path, "AIFS-0001")
    assert "status: approved" in message
    assert "Do not implement" not in message


def test_main_emits_context_only_on_a_story_branch(
    session: ModuleType,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    monkeypatch.setenv("CLAUDE_PROJECT_DIR", str(tmp_path))

    def fake_branch(branch: str):
        def run(
            command: list[str], **_kwargs: object
        ) -> subprocess.CompletedProcess[str]:
            return subprocess.CompletedProcess(command, 0, branch + "\n", "")

        return run

    monkeypatch.setattr(
        session.subprocess, "run", fake_branch("fix/AIFS-0007/null-total")
    )
    _stdin(monkeypatch, {})
    assert session.main() == 0
    out = json.loads(capsys.readouterr().out)
    assert out["hookSpecificOutput"]["hookEventName"] == "SessionStart"
    assert "AIFS-0007" in out["hookSpecificOutput"]["additionalContext"]

    monkeypatch.setattr(session.subprocess, "run", fake_branch("main"))
    _stdin(monkeypatch, {})
    assert session.main() == 0
    assert capsys.readouterr().out == ""
