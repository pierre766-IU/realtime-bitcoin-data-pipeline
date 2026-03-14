# Terraform Infrastructure (Cloud: Dev/Stage/Prod)

This folder contains the cloud production IaC baseline for the Databricks-first architecture.

## Scope Note

- `local` (on-prem Docker Compose) is outside this Terraform scope.
- This `infra/` directory manages only cloud environments: `dev`, `stage`, and `prod`.

## Structure

- `modules/`: reusable Azure modules (Event Hubs, ADLS Gen2, Key Vault, Monitoring, Databricks Workspace)
- `envs/dev`, `envs/stage`, `envs/prod`: cloud environment roots with separate state and variables

## Quick Start (Local Terraform CLI)

1. Copy env templates if needed (already committed in this repo):
   - `terraform.tfvars.example -> terraform.tfvars`
   - `backend.hcl.example -> backend.hcl`
2. Initialize and validate from the target env folder:

```bash
cd infra/envs/dev
terraform init -backend-config=backend.hcl
terraform validate
terraform plan -var-file=terraform.tfvars
```

## GitHub Environments and Secrets

Create GitHub environments: `dev`, `stage`, `prod`.

Set these environment-scoped secrets for each environment:

- `AZURE_CLIENT_ID`
- `AZURE_TENANT_ID`
- `AZURE_SUBSCRIPTION_ID`
- `TFSTATE_RESOURCE_GROUP`
- `TFSTATE_STORAGE_ACCOUNT`
- `TFSTATE_CONTAINER`
- `DATABRICKS_HOST`
- `DATABRICKS_TOKEN`
- `KEYVAULT_SECRETS_JSON` (optional JSON object of extra Key Vault secrets, for example `{"coinapi-key":"...","slack-webhook":"..."}`)

Set these environment-scoped variables for each environment:

- `TFSTATE_KEY` (example: `bitcoin-streaming-pipeline/dev.tfstate`)
- `KEYVAULT_DATABRICKS_HOST_SECRET_NAME` (optional, defaults to `databricks-host`)
- `KEYVAULT_DATABRICKS_TOKEN_SECRET_NAME` (optional, defaults to `databricks-token`)

## Secret Population Model

- Terraform creates the Key Vault and grants the deployment principal `Key Vault Secrets Officer` on that vault.
- After each successful cloud apply, `.github/workflows/iac.yml` reads the `key_vault_name` Terraform output and writes GitHub environment secrets into Key Vault with Azure CLI.
- This avoids storing runtime secret values in Terraform state.
- Secrets in `KEYVAULT_SECRETS_JSON` must use valid Azure Key Vault secret names.

## Image Publication Model

- `.github/workflows/app-databricks.yml` logs in to GitHub Container Registry with the workflow `GITHUB_TOKEN` and pushes the Spark, producer, and dashboard images to `ghcr.io/<owner>/bitcoin-streaming-pipeline/...`.
- Published images receive both an immutable `${GITHUB_SHA}` tag and an environment tag such as `dev-latest` or `prod-latest`.
- GHCR publishing is independent from Terraform state, so the app lane does not need a prior registry bootstrap step.

## Promotion Model

- Push to `main` with infra changes auto-applies `dev`.
- Push to `main` with app changes auto-publishes images to GHCR and deploys the Databricks bundle to `dev`.
- `stage` and `prod` applies are manual via workflow dispatch and should be guarded by required approvals in GitHub Environments.

## Naming Defaults and Guardrails

Environment variable defaults are preconfigured per cloud environment:

- `dev`: `resource_group_name = rg-btcpipeline-dev`
- `stage`: `resource_group_name = rg-btcpipeline-stage`
- `prod`: `resource_group_name = rg-btcpipeline-prod`

Terraform validation enforces naming conventions:

- `dev`: `^rg-[a-z0-9-]+-dev$`
- `stage`: `^rg-[a-z0-9-]+-stage$`
- `prod`: `^rg-[a-z0-9-]+-prod$`
