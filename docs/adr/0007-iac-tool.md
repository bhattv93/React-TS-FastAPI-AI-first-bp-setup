---
status: accepted
owner: tech-lead
last-reviewed: 2026-10-24
---

# ADR-0007: Infrastructure-as-Code: CloudFormation first, with a Terraform adaptation guide

- **Status:** Accepted
- **Date:** 2026-10-24

## Context

We need to provision ECR, ECS Fargate/ALB *or* Lambda/API Gateway, RDS (+ RDS Proxy), S3 + CloudFront,
SSM/Secrets Manager, CloudWatch, and the GitHub OIDC IAM role. AWS is the core platform. Teams that adopt this
boilerplate may standardise on Terraform instead, so the setup must not trap them.

## Decision

- The reference implementation in `infra/` uses **AWS CloudFormation** (YAML templates, deployed with the AWS CLI
  or GitHub Actions). It has no tooling to install beyond the AWS CLI, and `cfn-lint` runs as a gate.
- The docs include a **Terraform adaptation guide**
  ([terraform-adaptation.md](../06-delivery/terraform-adaptation.md)) that maps each CloudFormation stack to its
  Terraform equivalent, the state and CI differences, and the pipeline changes.
- To keep the two interchangeable, infra is split into stacks with **stable, tool-neutral names and
  parameters** (`network`, `data`, `backend-ecs`, `backend-lambda`, `frontend`, `observability`, `github-oidc`).

## Alternatives considered

| Option | Pros | Cons |
|--------|------|------|
| **CloudFormation (chosen)** | Native to AWS, no state backend to manage, change sets are reviewable | AWS-only; YAML is verbose |
| Terraform / OpenTofu | Multi-cloud, great `plan` review | State backend and a second tool to install |
| AWS CDK | Real programming language | AWS-only; another toolchain |

## Consequences

- PRs touching `infra/**` run `cfn-lint` and post a **change set** summary, as the review gate (replacing
  `terraform plan`).
- Non-AWS clouds are out of scope for the reference implementation. The application image and SPA bundle stay
  portable ([aws-backend.md](../06-delivery/aws-backend.md#other-cloud-providers)).
