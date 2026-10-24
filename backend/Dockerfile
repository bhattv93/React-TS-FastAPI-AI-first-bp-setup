# One build lineage for local, ECS Fargate and AWS Lambda (see docs/06-delivery/aws-backend.md).
#
#   docker build --target runtime backend   -> ECS, local, CI gate (no third-party adapter needed)
#   docker build --target lambda  backend   -> the same layers plus the Lambda Web Adapter extension
#
# Every base image is pinned by digest for reproducible, reviewable builds. Dependabot (docker
# ecosystem) proposes digest bumps as pull requests.

# ---- builder: resolve and install locked dependencies with uv ----
FROM python:3.13-slim@sha256:d98cc29d3266e535dd9da1099688d9cb3ca4753813571e071763d17725460962 AS builder
COPY --from=ghcr.io/astral-sh/uv:0.13.5@sha256:32a7bb39b496babbd997b0a39a4d66c126bdaf5661b302bf6f06abda8deca6ff /uv /uvx /bin/
ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_PYTHON_DOWNLOADS=never
WORKDIR /app
COPY pyproject.toml uv.lock README.md ./
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --locked --no-dev --no-install-project
COPY src ./src
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --locked --no-dev

# ---- runtime: slim, non-root. Used for ECS, local runs and the CI image gate ----
FROM python:3.13-slim@sha256:d98cc29d3266e535dd9da1099688d9cb3ca4753813571e071763d17725460962 AS runtime
RUN useradd --create-home --uid 10001 app
WORKDIR /app
COPY --from=builder --chown=app:app /app /app
ENV PATH="/app/.venv/bin:$PATH" \
    PYTHONUNBUFFERED=1 \
    PORT=8000
USER app
EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=3s --start-period=10s \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/health')"
CMD ["uvicorn", "--factory", "app.main:create_app", "--host", "0.0.0.0", "--port", "8000"]

# ---- lambda: runtime + the AWS Lambda Web Adapter (one extra layer, inert outside Lambda) ----
# Built in the deploy pipeline, not in the PR gate: the adapter comes from public ECR, which
# rate-limits anonymous pulls from shared CI runners.
FROM runtime AS lambda
COPY --from=public.ecr.aws/awsguru/aws-lambda-adapter:0.9.1@sha256:46d6625e68cbbdd2efab4a20245977664513f13ffef47915b000d431adcea0b4 /lambda-adapter /opt/extensions/lambda-adapter
ENV AWS_LWA_READINESS_CHECK_PATH=/health
