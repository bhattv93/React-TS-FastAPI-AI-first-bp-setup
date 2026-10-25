"""The internal Markdown link checker that guards against documentation rot."""

import importlib.util
from pathlib import Path
from types import ModuleType

import pytest

REPO_ROOT = Path(__file__).parents[3]
SCRIPT = REPO_ROOT / "scripts" / "check_links.py"


@pytest.fixture(name="links")
def links_fixture() -> ModuleType:
    spec = importlib.util.spec_from_file_location("check_links", SCRIPT)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _write(root: Path, relative: str, text: str) -> None:
    path = root / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def test_the_real_repository_has_no_broken_internal_links(links: ModuleType) -> None:
    assert links.check(REPO_ROOT) == []


def test_a_valid_relative_link_passes(tmp_path: Path, links: ModuleType) -> None:
    _write(tmp_path, "docs/a.md", "See [b](b.md).\n")
    _write(tmp_path, "docs/b.md", "# B\n")
    assert links.check(tmp_path) == []


def test_a_link_to_a_missing_file_is_reported_with_file_and_line(
    tmp_path: Path, links: ModuleType
) -> None:
    _write(tmp_path, "docs/a.md", "ok\n\nSee [gone](gone.md).\n")
    errors = links.check(tmp_path)
    assert len(errors) == 1
    assert "docs/a.md:3" in errors[0]
    assert "gone.md" in errors[0]


def test_a_link_to_a_directory_passes(tmp_path: Path, links: ModuleType) -> None:
    _write(tmp_path, "docs/a.md", "See [adr](adr/).\n")
    (tmp_path / "docs" / "adr").mkdir()
    assert links.check(tmp_path) == []


def test_a_root_relative_link_resolves_from_the_repository_root(
    tmp_path: Path, links: ModuleType
) -> None:
    _write(tmp_path, "docs/deep/a.md", "See [top](/README.md).\n")
    _write(tmp_path, "README.md", "# Top\n")
    assert links.check(tmp_path) == []


def test_external_and_mail_links_are_not_checked(
    tmp_path: Path, links: ModuleType
) -> None:
    _write(
        tmp_path,
        "a.md",
        "[x](https://example.invalid/nope) [y](mailto:a@b.c) <https://example.invalid>\n",
    )
    assert links.check(tmp_path) == []


def test_an_anchor_must_match_a_heading_in_the_target_file(
    tmp_path: Path, links: ModuleType
) -> None:
    _write(tmp_path, "a.md", "[ok](b.md#my-section) [bad](b.md#nope)\n")
    _write(tmp_path, "b.md", "# Title\n\n## My `Section`!\n")
    errors = links.check(tmp_path)
    assert len(errors) == 1
    assert "#nope" in errors[0]


def test_a_same_file_anchor_is_checked(tmp_path: Path, links: ModuleType) -> None:
    _write(tmp_path, "a.md", "# Intro\n\n[up](#intro) [bad](#missing)\n")
    errors = links.check(tmp_path)
    assert len(errors) == 1
    assert "#missing" in errors[0]


def test_duplicate_headings_get_numbered_anchors(
    tmp_path: Path, links: ModuleType
) -> None:
    _write(tmp_path, "a.md", "# Setup\n\n# Setup\n\n[second](#setup-1)\n")
    assert links.check(tmp_path) == []


def test_links_inside_code_are_ignored(tmp_path: Path, links: ModuleType) -> None:
    _write(
        tmp_path,
        "a.md",
        "```text\n[x](missing.md)\n```\n\nInline `[y](missing.md)` too.\n",
    )
    assert links.check(tmp_path) == []


def test_reference_style_definitions_are_checked(
    tmp_path: Path, links: ModuleType
) -> None:
    _write(tmp_path, "a.md", "See [thing][t].\n\n[t]: missing.md\n")
    errors = links.check(tmp_path)
    assert len(errors) == 1
    assert "missing.md" in errors[0]


def test_a_link_with_a_title_is_parsed(tmp_path: Path, links: ModuleType) -> None:
    _write(tmp_path, "a.md", '[b](b.md "Title here")\n')
    _write(tmp_path, "b.md", "# B\n")
    assert links.check(tmp_path) == []


def test_excluded_folders_are_not_scanned(tmp_path: Path, links: ModuleType) -> None:
    _write(tmp_path, "node_modules/pkg/README.md", "[x](missing.md)\n")
    _write(tmp_path, "docs/project-context.md", "[x](missing.md)\n")
    assert links.check(tmp_path) == []


def test_main_returns_nonzero_when_links_are_broken(
    tmp_path: Path, links: ModuleType, capsys: pytest.CaptureFixture[str]
) -> None:
    _write(tmp_path, "a.md", "[x](missing.md)\n")
    assert links.main([str(tmp_path)]) == 1
    assert "missing.md" in capsys.readouterr().out


def test_main_returns_zero_for_a_clean_tree(tmp_path: Path, links: ModuleType) -> None:
    _write(tmp_path, "a.md", "# Fine\n")
    assert links.main([str(tmp_path)]) == 0
