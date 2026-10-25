---
status: draft
owner: devops-lead
last-reviewed: 2026-10-24
---

# Terraform Adaptation Guide

The reference infrastructure in `infra/` is **CloudFormation** ([ADR-0007](../adr/0007-iac-tool.md)). This guide
shows a team how to swap it for Terraform (or OpenTofu) without touching the application, the CI gates, or the
AI layer.

## What stays the same

| Area | Why it does not change |
|------|------------------------|
| Application code, Dockerfile, ECR image flow | The image is built once and promoted by digest ([cd-and-environments.md](cd-and-environments.md#build-once-promote-everywhere)) |
| Quality gates and PR checks | `gate` job in [ci.md](ci.md) is IaC-agnostic |
| GitHub OIDC authentication | Same IAM roles, only created by a different tool |
| `.claude/` rules and skills | Only `infra/CLAUDE.md` and `.claude/rules/infra/iac.md` mention the tool |

## Stack-to-module mapping

The CloudFormation stacks use tool-neutral names so each one maps to a Terraform module:

| CloudFormation stack (`infra/cloudformation/`) | Terraform module (`infra/terraform/modules/`) | Notes |
|---|---|---|
| `network.yaml` | `network` | VPC, subnets, security groups |
| `github-oidc.yaml` | `github_oidc` | OIDC provider and per-environment deploy roles |
| `data.yaml` | `data` | RDS PostgreSQL, RDS Proxy, secrets |
| `backend-ecs.yaml` | `backend_ecs` | ECR, ECS cluster/service, ALB |
| `backend-lambda.yaml` | `backend_lambda` | Lambda container image, HTTP API |
| `frontend.yaml` | `frontend` | S3 (private), CloudFront with OAC, response headers policy |
| `observability.yaml` | `observability` | Log groups, alarms, dashboards, SNS |

Stack **parameters** become module **variables** with the same names (`environment`, `image_digest`,
`backend_target` = `ecs` or `lambda`, and so on).

## Behavioural differences to plan for

| Concern | CloudFormation | Terraform |
|---------|----------------|-----------|
| State | AWS-managed, per stack | You manage it: S3 bucket with versioning and native locking, one state file per environment |
| Review gate | `cfn-lint` + change set summary on the PR | `terraform fmt -check`, `tflint`, `terraform validate`, `terraform plan` posted on the PR |
| Apply | `aws cloudformation deploy` with environment approval | `terraform apply` of the saved plan with environment approval |
| Drift | `detect-stack-drift` | `terraform plan` shows drift |
| Cross-stack values | `Outputs` + `Fn::ImportValue` | Module outputs, or `terraform_remote_state` |
| Rollback | Automatic stack rollback | Re-apply the previous commit; no automatic rollback |

## Migration steps

1. Create `infra/terraform/` with `modules/` and `envs/{dev,staging,prod}/` (a root module per environment).
2. Create the state bucket (one-time bootstrap, kept outside the modules).
3. Port one stack at a time, in order: `network` → `github-oidc` → `data` → backend → `frontend` →
   `observability`.
4. For resources that already exist, use `terraform import` (or `import` blocks) rather than recreating them.
   Never delete a CloudFormation stack that still owns a resource before the import has been verified with
   an empty `terraform plan`. Use `DeletionPolicy: Retain` on the stack first.
5. Replace the CI jobs:
   - IaC lint job: `cfn-lint` → `terraform fmt`, `tflint`, `terraform validate`
   - PR comment: change set summary → `terraform plan`
   - CD deploy step: `aws cloudformation deploy` → `terraform apply`
6. Update the docs and guardrails:
   - `infra/CLAUDE.md` and `.claude/rules/infra/iac.md`
   - the deny rules in `.claude/settings.json` already include `terraform apply` and `terraform destroy`
   - add `hashicorp.terraform` to `.vscode/extensions.json`
   - add the `terraform` ecosystem to `.github/dependabot.yml`
7. Mark ADR-0007 `Superseded` and add the new ADR.

## Checklist

- [ ] Every stack has a module with the same inputs and outputs
- [ ] `terraform plan` is empty for each environment after import
- [ ] CI uses the OIDC role to read state; no static AWS keys
- [ ] The state bucket has versioning, encryption and restricted access
- [ ] Docs and AI instruction files no longer mention CloudFormation as current
