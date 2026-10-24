---
status: draft
owner: tech-lead
last-reviewed: 2026-10-24
---

# Configuration, Environment Variables and Secrets

Principle: **12-factor.** Code is identical across environments; config comes from the environment.

## Backend (`app/core/config.py`)

```python
class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(env_prefix="APP_", env_file=".env", extra="ignore")

    env: Literal["local", "test", "dev", "staging", "prod"] = "local"
    database_url: PostgresDsn
    log_level: str = "INFO"
    runtime: Literal["uvicorn", "lambda"] = "uvicorn"
    cors_origins: list[str] = []
    secret_key: SecretStr


@lru_cache
def get_settings() -> Settings:
    """Return cached settings (override in tests via dependency_overrides)."""
    return Settings()
```

- All config is typed and validated at startup. A missing or invalid variable fails fast with a clear error.
- Secrets are typed `SecretStr`, so they are never logged or included in `repr`.
- Code reads config only through `get_settings()` / `Depends(get_settings)`. Direct `os.environ` access is
  banned by a lint rule.

## Sources per environment

| Env | Non-secret config | Secrets |
|-----|-------------------|---------|
| local | `backend/.env` (copied from `.env.example`) | `.env` (gitignored) |
| test / CI | Workflow `env:` | GitHub Actions secrets (minimal; prefer OIDC) |
| AWS | **SSM Parameter Store** `/<app>/<env>/<KEY>` | **Secrets Manager** `<app>/<env>/<name>` (DB creds with rotation) |

- **ECS:** the task definition `secrets:` block injects values at container start.
- **Lambda:** non-secret values go into environment variables through IaC. Secrets are fetched at cold start
  with the **AWS Parameters and Secrets Lambda Extension** (cached), never stored as plaintext Lambda env.

## `.env.example` contract

- Every `Settings` field has an entry with a comment and a safe placeholder.
- A test (`tests/unit/test_settings_contract.py`) fails if `Settings` and `.env.example` drift apart.
- `.env` is never committed: it is in `.gitignore`, the Claude `PreToolUse` hook blocks it, the `Read` deny
  rule hides it, and gitleaks runs in pre-commit and CI.

## Frontend

- Runtime `config.json` per environment ([aws-frontend.md](../06-delivery/aws-frontend.md#environment-configuration)).
- `VITE_*` only for build-time constants. Typed in `src/vite-env.d.ts`.
- **No secrets in the frontend**; anything in the bundle or `config.json` is public.

## Feature flags

- v1: boolean settings (`APP_FEATURE_<NAME>`) exposed to the frontend through `config.json` when needed.
- Later: AWS AppConfig for runtime toggles without a redeploy.
