"""Check that dependencies resolve consistently and carry no known vulnerabilities.

One implementation is used locally (``just deps-check``) and in CI, so the results always agree.

Usage::

    python scripts/check_deps.py [backend|frontend|all]

Backend: lockfile matches ``pyproject.toml``, installed packages are mutually compatible, and
``pip-audit`` finds no known vulnerabilities.

Frontend: ``pnpm audit`` finds no high or critical vulnerabilities, and the dependency graph resolves **from
scratch** with strict peer dependencies (a stale lockfile can hide unmet peers).

Requires ``uv`` and ``pnpm`` on ``PATH`` and the dependencies already installed.
"""

import shutil
import subprocess
import sys
import tempfile
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
Runner = Callable[[list[str], Path], int]


@dataclass(frozen=True)
class Check:
    """One named check that returns a process-style exit code."""

    name: str
    run: Callable[[Runner], int]


def run_command(command: list[str], cwd: Path) -> int:
    """Run a command, streaming its output.

    Parameters
    ----------
    command : list[str]
        Program and arguments. The program is resolved through ``PATH`` (so ``pnpm.cmd`` works on Windows).
    cwd : Path
        Working directory.

    Returns
    -------
    int
        The exit code, or ``127`` when the program cannot be found.
    """
    program = shutil.which(command[0])
    if program is None:
        print(f"  command not found: {command[0]}", file=sys.stderr)
        return 127
    return subprocess.run([program, *command[1:]], cwd=cwd, check=False).returncode


def _command_check(name: str, command: list[str], cwd: Path) -> Check:
    """Build a check that runs one command.

    Parameters
    ----------
    name : str
        Human-readable name.
    command : list[str]
        Command to run.
    cwd : Path
        Working directory.

    Returns
    -------
    Check
        The check.
    """
    return Check(name, lambda runner: runner(command, cwd))


def _fresh_peer_resolution(runner: Runner) -> int:
    """Resolve the frontend dependency graph from scratch with strict peer dependencies.

    A copy of ``package.json`` and ``pnpm-workspace.yaml`` is resolved in a temporary directory with no
    lockfile, so peers hidden by a stale lockfile are reported. Nothing in the repository is modified.

    Parameters
    ----------
    runner : Runner
        Command runner.

    Returns
    -------
    int
        Exit code of the resolution.
    """
    frontend = ROOT / "frontend"
    with tempfile.TemporaryDirectory(prefix="peercheck-") as tmp:
        for name in ("package.json", "pnpm-workspace.yaml"):
            source = frontend / name
            if source.exists():
                shutil.copy(source, Path(tmp) / name)
        return runner(
            ["pnpm", "install", "--lockfile-only", "--strict-peer-dependencies"],
            Path(tmp),
        )


def build_checks(target: str) -> list[Check]:
    """Return the checks for ``target``.

    Parameters
    ----------
    target : str
        ``backend``, ``frontend`` or ``all``.

    Returns
    -------
    list[Check]
        Checks to run, in order.
    """
    backend = ROOT / "backend"
    frontend = ROOT / "frontend"
    checks: list[Check] = []
    if target in {"backend", "all"}:
        checks += [
            _command_check("backend: lockfile matches pyproject.toml", ["uv", "lock", "--check"], backend),
            _command_check("backend: installed packages are compatible", ["uv", "pip", "check"], backend),
            _command_check("backend: pip-audit (known vulnerabilities)", ["uv", "run", "pip-audit"], backend),
        ]
    if target in {"frontend", "all"}:
        checks += [
            _command_check(
                "frontend: pnpm audit (high and critical)",
                ["pnpm", "audit", "--audit-level=high"],
                frontend,
            ),
            Check("frontend: peer dependencies resolve from scratch", _fresh_peer_resolution),
        ]
    return checks


def run_checks(checks: list[Check], runner: Runner = run_command) -> list[str]:
    """Run every check and collect the names of the ones that failed.

    Parameters
    ----------
    checks : list[Check]
        Checks to run.
    runner : Runner, optional
        Command runner; injectable for tests.

    Returns
    -------
    list[str]
        Names of failed checks; empty when everything passed.
    """
    failed: list[str] = []
    for check in checks:
        print(f"\n== {check.name}")
        if check.run(runner) != 0:
            failed.append(check.name)
    return failed


def main(argv: list[str]) -> int:
    """Run the dependency checks.

    Parameters
    ----------
    argv : list[str]
        Command-line arguments; an optional first argument selects ``backend``, ``frontend`` or ``all``.

    Returns
    -------
    int
        ``0`` when all checks pass, ``1`` when any fails, ``2`` for a bad argument.
    """
    target = argv[1] if len(argv) > 1 else "all"
    if target not in {"backend", "frontend", "all"}:
        print("usage: check_deps.py [backend|frontend|all]", file=sys.stderr)
        return 2
    failed = run_checks(build_checks(target))
    if failed:
        print("\nDependency checks FAILED:", file=sys.stderr)
        for name in failed:
            print(f"  - {name}", file=sys.stderr)
        return 1
    print("\nAll dependency checks passed")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
