# Architecture v2 (Databricks-First)

This page defines the exact final diagram text and labels for the production architecture.

## 1. Explicit Environments

Add a box labeled:

`Environment Promotion`

Inside that box, use these labels:

- `Local (on-prem) -> Dev (cloud) -> Stage (cloud) -> Prod (cloud)`
- `Separate per env: Resource Group, Event Hubs namespace, ADLS Gen2 account, Key Vault, Databricks workspace (recommended)`
- `GitHub Environments with approval gates:`
- `1. Promote from local validation to dev (cloud) deployment`
- `2. Manual approval to stage (cloud)`
- `3. Manual approval to prod (cloud)`

## 2. Security Controls

Replace the current security box text with exactly:

`Security: Managed Identity + RBAC, Key Vault references, Private Endpoints (ADLS/Event Hubs/Key Vault), VNet injection for Databricks, encryption at rest + TLS in transit, audit logs + Defender policies`

## 3. Reliability Controls

Add a new reliability box with exactly:

`Reliability: ADLS checkpoints per stream, consumer groups per job, retries with backoff, idempotent writes/merge logic, bad-record quarantine (bronze_deadletter), autoscaling job clusters, alerting on lag/failures/checkpoint growth`

## 4. CI/CD Lanes (Databricks Jobs Path)

Use these two lanes and labels:

- `IaC lane: GitHub Actions -> Terraform plan/apply -> Azure infra`
- `App lane: GitHub Actions -> build/test package -> Databricks Asset Bundles deploy -> Databricks Jobs run`

## 5. Databricks-Only Main Flow

For the main production flow, use exactly:

`Event Hubs -> Databricks Structured Streaming -> ADLS Bronze/Silver/Gold -> Power BI/Dashboard`

And remove from main flow:

- `AKS/Flux path`

---

## Suggested One-Page Layout (for the visual diagram)

- Top-left: `IaC lane`
- Top-right: `App lane`
- Center: `Event Hubs -> Databricks Structured Streaming -> ADLS Bronze/Silver/Gold -> Power BI/Dashboard`
- Bottom-left: `Reliability` box
- Bottom-right: `Security` box
- Top-center or side strip: `Environment Promotion (Local -> Dev -> Stage -> Prod)`

