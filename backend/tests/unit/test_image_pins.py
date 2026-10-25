"""Container images are pinned by digest, and one image has one pin across the repository.

Why: a floating tag changes under you, and two different pins for the same image mean CI tests
something other than what developers and production run (for example Flyway 11 in CI but 12 in
``docker-compose.yml``). Dependabot bumps the Dockerfile and compose digests; images that only
appear inside workflow scripts are bumped by hand, which is exactly what this test keeps honest.

The scan covers ``image:`` keys, Dockerfile ``FROM`` / ``COPY --from`` and ``owner/name:tag``
tokens in workflow scripts. It does not try to parse shell, so a bare ``name:tag`` with no owner
inside a script is out of scope.
"""

import re
from pathlib import Path

import pytest

ROOT = Path(__file__).parents[3]
DIGEST = re.compile(r"@sha256:[0-9a-f]{64}$")
IMAGE_KEY = re.compile(r"^[ \t]*(?:-[ \t]*)?image:[ \t]*(?P<ref>[^\s#]+)", re.MULTILINE)
SCRIPT_TOKEN = re.compile(
    r"^[a-z0-9][\w.-]*(?:/[\w.-]+)+:[\w.-]+(?:@sha256:[0-9a-f]{64})?$"
)
FROM_LINE = re.compile(
    r"^FROM[ \t]+(?P<ref>\S+)(?:[ \t]+AS[ \t]+(?P<alias>\S+))?",
    re.IGNORECASE | re.MULTILINE,
)
COPY_FROM = re.compile(r"^COPY[ \t]+--from=(?P<ref>\S+)", re.MULTILINE)


def _dockerfile_references(text: str) -> list[str]:
    """Return external image references in a Dockerfile (stage aliases excluded)."""
    aliases = {m["alias"].lower() for m in FROM_LINE.finditer(text) if m["alias"]}
    refs = [m["ref"] for m in FROM_LINE.finditer(text)]
    refs += [m["ref"] for m in COPY_FROM.finditer(text)]
    return [ref for ref in refs if ref.lower() not in aliases]


def _image_references() -> list[tuple[str, str]]:
    """Return ``(source file, image reference)`` for every image the repository uses."""
    found: list[tuple[str, str]] = []
    dockerfile = ROOT / "backend" / "Dockerfile"
    found += [
        (dockerfile.relative_to(ROOT).as_posix(), ref)
        for ref in _dockerfile_references(dockerfile.read_text(encoding="utf-8"))
    ]
    yaml_files = [
        ROOT / "docker-compose.yml",
        *sorted((ROOT / ".github" / "workflows").glob("*.yml")),
    ]
    for path in yaml_files:
        text = path.read_text(encoding="utf-8")
        source = path.relative_to(ROOT).as_posix()
        found += [(source, m["ref"]) for m in IMAGE_KEY.finditer(text)]
        if path.parent.name == "workflows":
            tokens = (token.strip("\"'\\") for token in text.split())
            found += [(source, token) for token in tokens if SCRIPT_TOKEN.match(token)]
    return sorted(set(found))


def _repository(ref: str) -> str:
    """Return the image name without its tag or digest."""
    base = ref.split("@", maxsplit=1)[0]
    name, _, tag = base.rpartition(":")
    return name if name and "/" not in tag else base


REFERENCES = _image_references()


def test_the_scan_finds_the_images_we_know_about() -> None:
    repositories = {_repository(ref) for _, ref in REFERENCES}
    assert {
        "postgres",
        "flyway/flyway",
        "python",
        "ghcr.io/astral-sh/uv",
        "zricethezav/gitleaks",
        "rhysd/actionlint",
    } <= repositories


@pytest.mark.parametrize(
    ("source", "ref"), REFERENCES, ids=[f"{s}::{r}" for s, r in REFERENCES]
)
def test_image_is_pinned_by_digest(source: str, ref: str) -> None:
    assert DIGEST.search(ref), f"{source} uses {ref} without an @sha256 digest"


def test_each_image_has_a_single_pin_across_the_repository() -> None:
    pins: dict[str, set[str]] = {}
    for _, ref in REFERENCES:
        pins.setdefault(_repository(ref), set()).add(ref)
    drifted = {name: sorted(refs) for name, refs in pins.items() if len(refs) > 1}
    assert (
        not drifted
    ), f"the same image is pinned differently in different files: {drifted}"
