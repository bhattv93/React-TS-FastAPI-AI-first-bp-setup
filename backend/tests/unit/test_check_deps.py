"""The dependency-health script shared by `just deps-check` and CI."""

import importlib.util
from pathlib import Path
from types import ModuleType

import pytest

SCRIPT = Path(__file__).parents[3] / "scripts" / "check_deps.py"


@pytest.fixture(name="deps")
def deps_fixture() -> ModuleType:
    spec = importlib.util.spec_from_file_location("check_deps", SCRIPT)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_backend_checks_cover_lock_compatibility_and_audit(deps: ModuleType) -> None:
    names = [check.name for check in deps.build_checks("backend")]
    assert names == [
        "backend: lockfile matches pyproject.toml",
        "backend: installed packages are compatible",
        "backend: pip-audit (known vulnerabilities)",
    ]


def test_frontend_checks_cover_audit_and_fresh_peer_resolution(
    deps: ModuleType,
) -> None:
    names = [check.name for check in deps.build_checks("frontend")]
    assert names == [
        "frontend: pnpm audit (high and critical)",
        "frontend: peer dependencies resolve from scratch",
    ]
    assert len(deps.build_checks("all")) == 5


def test_every_failing_check_is_reported_and_none_are_skipped(deps: ModuleType) -> None:
    seen: list[list[str]] = []

    def runner(command: list[str], cwd: Path) -> int:
        seen.append(command)
        return 1 if command[:2] == ["uv", "lock"] else 0

    failed = deps.run_checks(deps.build_checks("backend"), runner)
    assert failed == ["backend: lockfile matches pyproject.toml"]
    assert len(seen) == 3


def test_fresh_peer_resolution_uses_a_temp_copy_with_strict_peers(
    deps: ModuleType,
) -> None:
    captured: dict[str, object] = {}

    def runner(command: list[str], cwd: Path) -> int:
        captured["command"] = command
        captured["files"] = sorted(p.name for p in cwd.iterdir())
        captured["cwd"] = cwd
        return 0

    check = deps.build_checks("frontend")[1]
    assert check.run(runner) == 0
    assert captured["command"] == [
        "pnpm",
        "install",
        "--lockfile-only",
        "--strict-peer-dependencies",
    ]
    assert "package.json" in captured["files"]  # type: ignore[operator]
    assert "pnpm-lock.yaml" not in captured["files"]  # type: ignore[operator]
    assert not Path(str(captured["cwd"])).exists()


def test_run_command_reports_missing_programs(
    deps: ModuleType, tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    assert deps.run_command(["definitely-not-a-real-program"], tmp_path) == 127
    assert "command not found" in capsys.readouterr().err


def test_main_rejects_unknown_targets_and_aggregates_results(
    deps: ModuleType, monkeypatch: pytest.MonkeyPatch
) -> None:
    assert deps.main(["check_deps", "nope"]) == 2
    monkeypatch.setattr(deps, "run_checks", lambda _checks: [])
    assert deps.main(["check_deps", "backend"]) == 0
    monkeypatch.setattr(deps, "run_checks", lambda _checks: ["something"])
    assert deps.main(["check_deps", "frontend"]) == 1
