"""The AI-configuration linter that enforces the context budgets."""

import importlib.util
from pathlib import Path
from types import ModuleType

import pytest

REPO_ROOT = Path(__file__).parents[3]
SCRIPT = REPO_ROOT / "scripts" / "check_ai_config.py"


@pytest.fixture(name="lint")
def lint_fixture() -> ModuleType:
    spec = importlib.util.spec_from_file_location("check_ai_config", SCRIPT)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _write(root: Path, relative: str, text: str) -> None:
    path = root / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _compliant(root: Path) -> None:
    _write(root, "CLAUDE.md", "# Root\n")
    _write(
        root,
        ".claude/rules/backend/style.md",
        '---\npaths:\n  - "backend/**"\n---\n# Style\n',
    )
    _write(
        root,
        ".claude/skills/new-thing/SKILL.md",
        "---\nname: new-thing\ndescription: Scaffold a thing.\n---\n# New thing\n",
    )
    _write(
        root,
        ".claude/agents/reviewer.md",
        "---\nname: reviewer\ndescription: Reviews.\ntools: Read\nmodel: haiku\n---\nBody\n",
    )


def test_the_real_repository_complies(lint: ModuleType) -> None:
    assert lint.check(REPO_ROOT) == []


def test_frontmatter_parser_handles_missing_and_unterminated_blocks(
    lint: ModuleType,
) -> None:
    assert lint.parse_frontmatter("no frontmatter") == {}
    assert lint.parse_frontmatter("---\nname: a\n") == {}
    assert lint.parse_frontmatter('---\nname: a\npaths:\n  - "x"\n---\n') == {
        "name": "a",
        "paths": "",
    }


def test_compliant_tree_passes(lint: ModuleType, tmp_path: Path) -> None:
    _compliant(tmp_path)
    assert lint.check(tmp_path) == []
    assert lint.main(["check", str(tmp_path)]) == 0


def test_size_budgets_and_docs_imports_are_enforced(
    lint: ModuleType, tmp_path: Path
) -> None:
    _compliant(tmp_path)
    _write(tmp_path, "CLAUDE.md", "line\n" * 151 + "@docs/big.md\n")
    _write(tmp_path, "backend/CLAUDE.md", "line\n" * 101)
    _write(tmp_path, ".github/copilot-instructions.md", "line\n" * 31)
    problems = "\n".join(lint.check(tmp_path))
    assert "CLAUDE.md: 152 lines exceeds the budget of 150" in problems
    assert "backend/CLAUDE.md: 101 lines" in problems
    assert "copilot-instructions.md: 31 lines" in problems
    assert "do not @-import docs" in problems


def test_rules_must_be_scoped_and_small(lint: ModuleType, tmp_path: Path) -> None:
    _compliant(tmp_path)
    _write(tmp_path, ".claude/rules/global.md", "# No paths\n")
    _write(tmp_path, ".claude/rules/long.md", "---\npaths:\n---\n" + "x\n" * 61)
    problems = "\n".join(lint.check(tmp_path))
    assert "global.md: rules must declare `paths:`" in problems
    assert "long.md" in problems and "exceeds the budget of 60" in problems


def test_skills_need_matching_name_description_and_safe_invocation(
    lint: ModuleType, tmp_path: Path
) -> None:
    _compliant(tmp_path)
    _write(tmp_path, ".claude/skills/wrong/SKILL.md", "---\nname: other\n---\n")
    _write(
        tmp_path,
        ".claude/skills/deploy-backend/SKILL.md",
        "---\nname: deploy-backend\ndescription: Deploys.\n---\n",
    )
    _write(
        tmp_path,
        ".claude/skills/wordy/SKILL.md",
        "---\nname: wordy\ndescription: " + "d" * 1025 + "\n---\n",
    )
    problems = "\n".join(lint.check(tmp_path))
    assert "`name` must equal the folder name 'wrong'" in problems
    assert "missing `description`" in problems
    assert "side-effect skills must set `disable-model-invocation: true`" in problems
    assert "description is 1025 chars" in problems


def test_agents_must_pin_a_model_and_least_privilege_tools(
    lint: ModuleType, tmp_path: Path
) -> None:
    _compliant(tmp_path)
    _write(
        tmp_path, ".claude/agents/loose.md", "---\nname: loose\ndescription: x\n---\n"
    )
    _write(
        tmp_path,
        ".claude/agents/mismatch.md",
        "---\nname: nope\ndescription: x\ntools: Read\nmodel: haiku\n---\n",
    )
    problems = "\n".join(lint.check(tmp_path))
    assert "loose.md: missing `tools`" in problems
    assert "loose.md: missing `model` (pin a model" in problems
    assert "`name` must equal the file name 'mismatch'" in problems
    assert lint.main(["check", str(tmp_path)]) == 1
