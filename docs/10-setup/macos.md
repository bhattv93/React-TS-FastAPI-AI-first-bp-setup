---
status: planned
owner: tech-lead
last-reviewed: 2026-10-24
---

# macOS Setup Guide (planned)

The macOS guide follows the same fifteen steps and the same rules as the
[Windows guide](windows.md): relative paths only, one **Check** per step, no administrator rights unless
marked, and the same list of never-committed local files.

> **Status:** not written or verified yet. The table below is the intended outline only; do not treat the
> commands as tested. It will be completed and verified on a Mac in a follow-up change.

| # | Step | Intended tool |
|---|------|---------------|
| 1 | Git | Xcode Command Line Tools or Homebrew `git` |
| 2 | Node.js 22 or newer | Homebrew `node` (or `fnm`, reading `.nvmrc`) |
| 3 | Python tooling | Homebrew `uv`, then `uv python install 3.13` |
| 4 | pnpm | `npm install -g pnpm` |
| 5 | Task runner | Homebrew `just` |
| 6 | Containers | Docker Desktop |
| 7 | GitHub CLI | Homebrew `gh` |
| 8 | Editor | Homebrew cask `visual-studio-code` |
| 9 - 15 | Clone, `just setup`, configuration, run, `just check`, editor, AI tools | Identical to Windows, using `cp` instead of `Copy-Item` and the default shell |

Differences to expect:

- The `justfile` already uses the default POSIX shell on macOS, so the same recipes apply.
- The shared `.vscode/settings.json` has no OS-specific paths, so it works unchanged.
- Apple Silicon: the Docker images used here publish `arm64` variants; verify when writing the guide.
