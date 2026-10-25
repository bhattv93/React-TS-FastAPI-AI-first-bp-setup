---
paths:
  - ".github/workflows/**"
---

# GitHub Actions workflows

- Pin every third-party action by full commit SHA with the version in a trailing comment.
- Default to `permissions: contents: read`; widen per job only where needed.
- Run project commands through `just` so CI and local use the same gates.
- Never expose secrets to pull requests from forks. Automation that uses an AI key must be gated by a
  repository variable, scoped to an environment, and capped with `--max-turns` and a job timeout.
- Only the `gate` job is a required status check; new jobs must be added to its `needs` list.
- Validate changes with `actionlint` before committing.
