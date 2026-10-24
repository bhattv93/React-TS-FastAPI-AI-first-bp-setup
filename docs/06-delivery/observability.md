---
status: draft
owner: devops-lead
last-reviewed: 2026-10-24
---

# Observability: Logging, Metrics, Tracing, Alerting

## Logging (backend)

- **structlog** writes **JSON to stdout**. CloudWatch collects it (the ECS `awslogs` driver, or Lambda
  natively).
- Configured in `app/core/logging.py`; the same format locally, with optional pretty console output when
  `APP_ENV=local`.
- Standard fields: `timestamp`, `level`, `event`, `logger`, `request_id`, `method`, `path`, `status`,
  `duration_ms`, `env`, `version` (git SHA).
- **Request ID middleware** (`app/core/middleware.py`) reads `X-Request-ID` or generates a UUID, stores it in
  a `contextvar` and echoes it on the response. The error envelope includes it, so users can quote it in bug
  reports.
- **No PII or secrets in logs.** A structlog processor redacts known keys (`password`, `token`,
  `authorization`, `email`).
- Retention: 30 days in dev and staging, 90+ in prod (set in IaC). Save CloudWatch **Logs Insights** queries
  (errors by path, slowest requests, by request_id) as IaC.

## Metrics

| Source | Metrics |
|--------|---------|
| ALB / API Gateway | Request count, 4xx/5xx, latency p50/p95/p99 |
| ECS / Lambda | CPU, memory / duration, errors, throttles, concurrent executions |
| RDS | CPU, connections, free storage, read/write latency |
| App (custom) | Business counters via CloudWatch Embedded Metric Format (EMF) log lines, with no agent needed |
| CloudFront | Error rate, cache hit ratio |

## Tracing

- **OpenTelemetry** SDK with `opentelemetry-instrumentation-fastapi`, `-sqlalchemy` and `-httpx`.
- Export through **AWS Distro for OpenTelemetry (ADOT)**: a sidecar collector on ECS, or the ADOT Lambda
  layer. View traces in **AWS X-Ray / CloudWatch Application Signals**.
- The trace ID is added to log records, which links logs and traces.

## Frontend

- **CloudWatch RUM** (app monitor ID from `config.json`) captures JS errors, performance (Core Web Vitals) and
  page views.
- The root `ErrorBoundary` reports render errors. API errors are logged with the backend `request_id`.

## Health and readiness

| Endpoint | Checks | Used by |
|----------|--------|---------|
| `GET /health` | Process is up (no dependencies) | Liveness, Lambda Web Adapter readiness |
| `GET /ready` | DB reachable (`SELECT 1`), migrations at expected version | ALB target health, deploy smoke test |

## Alerting

CloudWatch alarms send to SNS, which goes to email or Slack (via AWS Chatbot). Defined in IaC per environment;
prod thresholds are stricter.

| Alarm | Example threshold (prod) |
|-------|--------------------------|
| API 5xx rate | > 1% for 5 min |
| API p95 latency | > 1 s for 10 min |
| ECS CPU / memory, or Lambda errors / throttles | > 80% / any throttles for 5 min |
| RDS connections / free storage | > 80% of max / < 10 GB |
| RUM JS error rate | > 2% of sessions |

Each alarm links to a runbook in `docs/runbooks/` (created in M6).
