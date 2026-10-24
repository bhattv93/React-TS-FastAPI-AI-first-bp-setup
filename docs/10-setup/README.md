---
status: draft
owner: tech-lead
last-reviewed: 2026-10-24
---

# Developer Setup Guides

Step-by-step environment setup, one guide per operating system. Each guide goes from a clean machine to a
green `just check`, and builds up in small, verifiable steps.

| Guide | Status |
|-------|--------|
| [Windows 10/11](windows.md) | Written and verified on Windows 11 |
| [macOS](macos.md) | Planned; outline only |

## Rules these guides follow

- **No machine-specific paths.** Every path is relative to the repository root (`backend/.env`,
  `frontend/src`) or uses a standard placeholder such as `<repo-url>`. Nothing refers to a user name, a drive
  letter or a particular checkout location.
- **Run from the repository root** unless a step says otherwise.
- **User-scope installs where possible**, so no administrator rights are needed (Docker Desktop and Git are
  the exceptions).
- **Each step has a check** that tells you it worked before you move on.
- Anything personal or local is **gitignored** and never committed: `backend/.env`, `CLAUDE.local.md`,
  `.claude/settings.local.json`, `.venv/`, `node_modules/`. See the table at the end of each guide.
