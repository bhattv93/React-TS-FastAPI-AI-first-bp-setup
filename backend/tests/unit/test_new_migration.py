"""The ``just db-new`` helper must never overwrite an existing migration."""

import importlib.util
from pathlib import Path
from types import ModuleType

import pytest

SCRIPT = Path(__file__).parents[2] / "scripts" / "new_migration.py"


@pytest.fixture(name="script")
def script_fixture(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> ModuleType:
    spec = importlib.util.spec_from_file_location("new_migration", SCRIPT)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    (tmp_path / "db" / "migrations").mkdir(parents=True)
    monkeypatch.setattr(module, "MIGRATIONS_DIR", tmp_path / "db" / "migrations")
    return module


def test_creates_a_versioned_empty_migration(script: ModuleType) -> None:
    assert script.main(["new_migration", "create_items"]) == 0
    created = list(script.MIGRATIONS_DIR.glob("V*__create_items.sql"))
    assert len(created) == 1
    assert "immutable" in created[0].read_text(encoding="utf-8")


def test_refuses_to_overwrite_an_existing_migration(
    script: ModuleType, capsys: pytest.CaptureFixture[str]
) -> None:
    assert script.main(["new_migration", "create_items"]) == 0
    existing = next(script.MIGRATIONS_DIR.glob("V*__create_items.sql"))
    existing.write_text("CREATE TABLE items ();\n", encoding="utf-8")
    assert script.main(["new_migration", "create_items"]) == 1
    assert existing.read_text(encoding="utf-8") == "CREATE TABLE items ();\n"
    assert "already exists" in capsys.readouterr().err


def test_rejects_an_invalid_name(script: ModuleType) -> None:
    assert script.main(["new_migration", "Bad Name"]) == 2
