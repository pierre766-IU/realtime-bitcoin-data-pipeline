# Terraform Infrastructure (Cloud: Dev/Stage/Prod)

This folder contains the cloud production IaC baseline for the Databricks-first architecture.
The recommended operating model is GitHub validation plus manual Terraform apply and manual Databricks bundle deploy from an operator machine.

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

GitHub Environments are optional for a manual-deploy setup.
Create `dev`, `stage`, and `prod` only if you want protected approvals, GitHub-hosted deployment, or GitHub-managed secret storage later.

Set these environment-scoped secrets only if you want GitHub-hosted Databricks bundle deployment:

- `DATABRICKS_HOST`
- `DATABRICKS_TOKEN`
- `KAFKA_SASL_PASSWORD` (Event Hubs Kafka connection string or SASL password for the bronze stream)
- `KEYVAULT_SECRETS_JSON` (optional JSON object of extra Key Vault secrets, for example `{"coinapi-key":"...","slack-webhook":"..."}`)

Set the following only if you want GitHub-hosted Terraform apply:

- `AZURE_CLIENT_ID`
- `AZURE_TENANT_ID`
- `AZURE_SUBSCRIPTION_ID`
- `TFSTATE_RESOURCE_GROUP`
- `TFSTATE_STORAGE_ACCOUNT`
- `TFSTATE_CONTAINER`

Set these environment-scoped variables only if you want GitHub-hosted Databricks bundle deployment or Key Vault secret-name overrides:

- `KEYVAULT_DATABRICKS_HOST_SECRET_NAME` (optional, defaults to `databricks-host`)
- `KEYVAULT_DATABRICKS_TOKEN_SECRET_NAME` (optional, defaults to `databricks-token`)
- `EVENT_HUBS_BOOTSTRAP`
- `EVENT_HUBS_TOPIC` (optional, defaults to `bitcoin-stream`)
- `DELTA_BASE_PATH`
- `CHECKPOINT_BASE_PATH`
- `KAFKA_SECURITY_PROTOCOL` (optional, defaults to `SASL_SSL`)
- `KAFKA_SASL_MECHANISM` (optional, defaults to `PLAIN`)
- `KAFKA_SASL_USERNAME` (optional, defaults to `$ConnectionString`)
- `KAFKA_SSL_ENDPOINT_IDENTIFICATION_ALGORITHM` (optional, defaults to `https`)
- `KAFKA_STARTING_OFFSETS` (optional, defaults to `latest`)
- `KAFKA_FAIL_ON_DATA_LOSS` (optional, defaults to `false`)

Set `TFSTATE_KEY` (example: `bitcoin-streaming-pipeline/dev.tfstate`) only if you want GitHub-hosted Terraform apply.

## Secret Population Model

- Terraform creates the Key Vault and grants the deployment principal `Key Vault Secrets Officer` on that vault.
- If you use GitHub-hosted Terraform apply, `.github/workflows/iac.yml` reads the `key_vault_name` Terraform output and writes GitHub environment secrets into Key Vault with Azure CLI after apply.
- This avoids storing runtime secret values in Terraform state.
- Secrets in `KEYVAULT_SECRETS_JSON` must use valid Azure Key Vault secret names.

## GitHub Validate + Local Apply

- `.github/workflows/iac.yml` always provides a validation lane for formatting and Terraform validation.
- If GitHub has the Azure workload credentials and backend settings listed above, the same workflow can also run `terraform init`, `plan`, and `apply` on GitHub-hosted runners.
- If those settings are not present, `.github/workflows/iac.yml` still runs Terraform formatting and validation, then skips GitHub-hosted apply instead of failing.
- The recommended default is to use local Azure CLI authentication for apply:

```bash
az login
cd infra/envs/dev
cp backend.hcl.example backend.hcl
terraform init -backend-config=backend.hcl
terraform plan -var-file=terraform.tfvars
terraform apply -var-file=terraform.tfvars
```

## Databricks Runtime Configuration Model

- Terraform outputs expose the values needed by the Databricks bundle: `event_hubs_bootstrap`, `delta_base_path`, and `checkpoint_base_path`.
- For manual deployment, pass those values directly to `databricks bundle validate/deploy` from your local machine.
- Copy those outputs into GitHub Environment variables and store `KAFKA_SASL_PASSWORD` in a GitHub Environment secret only if you later enable GitHub-hosted app deployment.

## Promotion Model

- Push to `main` with infra changes or app changes to run GitHub validation workflows.
- Promote `dev`, `stage`, and `prod` manually with local Terraform apply and local `databricks bundle deploy -t <env>`.
- GitHub-hosted apply/deploy remains an optional future automation path when credentials are available.

## Naming Defaults and Guardrails

Environment variable defaults are preconfigured per cloud environment:

- `dev`: `resource_group_name = rg-btcpipeline-dev`
- `stage`: `resource_group_name = rg-btcpipeline-stage`
- `prod`: `resource_group_name = rg-btcpipeline-prod`

Terraform validation enforces naming conventions:

- `dev`: `^rg-[a-z0-9-]+-dev$`
- `stage`: `^rg-[a-z0-9-]+-stage$`
- `prod`: `^rg-[a-z0-9-]+-prod$`
