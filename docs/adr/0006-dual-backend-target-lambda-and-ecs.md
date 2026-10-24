---
status: accepted
owner: tech-lead
last-reviewed: 2026-10-24
---

# ADR-0006: One backend container image, deployable to AWS Lambda or ECS Fargate

- **Status:** Accepted
- **Date:** 2026-10-24

## Context

Projects built from this boilerplate differ. Some are low-traffic or spiky, which suits Lambda. Others are
steady-traffic, need long requests or WebSockets, or keep warm connection pools, which suits ECS. We don't
want two codebases or two build pipelines.

## Decision

- The app is a plain ASGI FastAPI app run by `uvicorn`, with no AWS-specific code in `app/`.
- **One Dockerfile** (multi-stage, `uv` based, non-root, base images pinned by digest) with two thin targets,
  `runtime` and `lambda`. They share every layer except one; both are pushed to **ECR** and tagged with the git
  SHA.
- **ECS Fargate:** the `runtime` target runs `uvicorn` behind an ALB. The PR gate builds and scans this target.
- **Lambda:** the `lambda` target (the same layers) runs as a Lambda container image with the
  [AWS Lambda Web Adapter](https://github.com/awslabs/aws-lambda-web-adapter) layer/extension copied in. It
  forwards Lambda events to uvicorn, behind API Gateway HTTP API or a Function URL.
- [Mangum](https://mangum.fastapiexpert.com/) (`handler = Mangum(app)`) stays a documented fallback for
  zip-based Lambda deploys.
- The target is chosen per environment through IaC variables. See
  [aws-backend.md](../06-delivery/aws-backend.md).

## Alternatives considered

| Option | Pros | Cons |
|--------|------|------|
| Lambda only (zip + Mangum) | Cheapest at low traffic | Cold starts, 15-min limit, DB connection churn |
| ECS only | Simple mental model | Always-on cost for small projects |
| **Same image, both targets** | Parity, one pipeline, choose per env | Slightly larger Lambda image; RDS Proxy advised for Lambda |

## Consequences

- Lambda deployments should use **RDS Proxy** to avoid exhausting Postgres connections.
- Health endpoints (`/health`, `/ready`) work for both ALB health checks and Lambda smoke tests.
