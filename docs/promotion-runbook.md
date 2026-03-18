# Promotion Runbook (local -> dev -> stage -> prod)

This runbook documents the exact operational flow for demo evaluation.

## Scope

- `local`: on-prem Docker Compose validation on developer machine.
- `dev`, `stage`, `prod`: cloud environments validated by GitHub workflows and deployed manually from an operator machine.

## Preconditions

- Azure CLI access is available for the target subscription/tenant.
- Databricks CLI access is available for the target workspace.
- Target Terraform values are prepared in `infra/envs/<env>/terraform.tfvars`.
- Databricks bundle inputs are available from Terraform outputs or environment-specific notes.

## Step 1: Local Validation (on-prem)

1. Start local stack:

```bash
make up
make jobs
```

2. Feed stream data:

```bash
docker compose --env-file .env -f docker-compose.yml -f docker-compose.dev.yml up -d producer-replay
```

3. Validate local outputs:
- Spark jobs are healthy.
- Dashboard loads and updates.
- Bronze/Silver/Gold tables are produced in local Delta path.

4. Commit changes and push branch:

```bash
git add .
git commit -m "Prepare release candidate"
git push origin <branch>
```

5. Open PR to `main` and merge after review.

## Step 2: Promote to Cloud Dev

1. Merge to `main`.
2. GitHub Actions auto-run validation:
- `.github/workflows/iac.yml` validates Terraform formatting and configuration.
- `.github/workflows/app-databricks.yml` runs lint/tests/build validation.

3. Apply infrastructure manually:

```bash
az login
cd infra/envs/dev
cp backend.hcl.example backend.hcl
terraform init -backend-config=backend.hcl
terraform plan -var-file=terraform.tfvars
terraform apply -var-file=terraform.tfvars
```

4. Capture Terraform outputs needed by the Databricks bundle:
- `databricks_workspace_url`
- `event_hubs_bootstrap`
- `delta_base_path`
- `checkpoint_base_path`

5. Validate and deploy the Databricks bundle manually:

```bash
export DATABRICKS_TOKEN="<databricks-pat>"

databricks bundle validate -t dev \
  --var="databricks_host=<workspace-url>" \
  --var="event_hubs_bootstrap=<namespace>.servicebus.windows.net:9093" \
  --var="event_hubs_topic=bitcoin-stream" \
  --var="delta_base_path=abfss://delta@<storage>.dfs.core.windows.net/bitcoin" \
  --var="checkpoint_base_path=abfss://checkpoints@<storage>.dfs.core.windows.net/bitcoin" \
  --var="kafka_security_protocol=SASL_SSL" \
  --var="kafka_sasl_mechanism=PLAIN" \
  --var="kafka_sasl_username=\$ConnectionString" \
  --var="kafka_sasl_password=<event-hubs-connection-string>" \
  --var="kafka_ssl_endpoint_identification_algorithm=https" \
  --var="kafka_starting_offsets=latest" \
  --var="kafka_fail_on_data_loss=false"

databricks bundle deploy -t dev \
  --var="databricks_host=<workspace-url>" \
  --var="event_hubs_bootstrap=<namespace>.servicebus.windows.net:9093" \
  --var="event_hubs_topic=bitcoin-stream" \
  --var="delta_base_path=abfss://delta@<storage>.dfs.core.windows.net/bitcoin" \
  --var="checkpoint_base_path=abfss://checkpoints@<storage>.dfs.core.windows.net/bitcoin" \
  --var="kafka_security_protocol=SASL_SSL" \
  --var="kafka_sasl_mechanism=PLAIN" \
  --var="kafka_sasl_username=\$ConnectionString" \
  --var="kafka_sasl_password=<event-hubs-connection-string>" \
  --var="kafka_ssl_endpoint_identification_algorithm=https" \
  --var="kafka_starting_offsets=latest" \
  --var="kafka_fail_on_data_loss=false"
```

6. Validate in cloud `dev`:
- Local Terraform apply succeeded.
- Databricks bundle deployed successfully.
- Bronze/Silver/Gold jobs running.
- Event Hubs ingest and ADLS checkpoint/data paths updating.

## Step 3: Promote to Cloud Stage (manual)

1. Run the same local Terraform flow in `infra/envs/stage`.
2. Run `databricks bundle validate -t stage` and `databricks bundle deploy -t stage` with the stage-specific values.
3. Run stage validation checks:
- Job health and lag
- Data quality checks (sample windows)
- Dashboard/consumer smoke checks

## Step 4: Promote to Cloud Prod (manual)

1. Run the same local Terraform flow in `infra/envs/prod`.
2. Run `databricks bundle validate -t prod` and `databricks bundle deploy -t prod` with the prod-specific values.
3. Run production acceptance checks:
- Streaming jobs stable over agreed observation period.
- Event Hubs throughput and consumer lag within target.
- ADLS Delta/checkpoint paths healthy.
- Monitoring/alerts active.

## Demo Evidence Checklist

- PR merged to `main`.
- Green workflow run links for:
  - `iac-terraform-cloud` validation
  - `app-databricks-cloud` quality-build
- Screenshots or links:
  - Databricks Jobs runs
  - ADLS containers/paths
  - Event Hubs metrics
  - Dashboard output

## Rollback Guidance (short)

- App rollback: redeploy the previous bundle revision to the target environment.
- Infra rollback: apply previous Terraform revision from git tag/commit.
- If prod is impacted, stop producer ingress first, then roll back app, then infra if required.
