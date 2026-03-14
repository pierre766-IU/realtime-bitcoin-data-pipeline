# Promotion Runbook (local -> dev -> stage -> prod)

This runbook documents the exact operational flow for demo evaluation.

## Scope

- `local`: on-prem Docker Compose validation on developer machine.
- `dev`, `stage`, `prod`: cloud environments deployed by GitHub workflows.

## Preconditions

- GitHub Environments exist: `dev`, `stage`, `prod`.
- Environment secrets/variables are configured as documented in `infra/README.md`.
- Databricks bundle target placeholders are replaced in `databricks.yml`.

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
2. GitHub Actions auto-runs:
- `.github/workflows/iac.yml` -> `apply-cloud-dev` (infra)
- `.github/workflows/app-databricks.yml` -> `deploy-cloud-dev` (images + app)

3. Validate in cloud `dev`:
- Terraform apply succeeded.
- Post-apply Key Vault secret sync succeeded.
- Container images were pushed to GHCR.
- Databricks bundle deployed.
- Bronze/Silver/Gold jobs running.
- Event Hubs ingest and ADLS checkpoint/data paths updating.

## Step 3: Promote to Cloud Stage (manual)

1. Trigger workflow dispatch for IaC:
- Workflow: `iac-terraform-cloud`
- Input: `target_env = stage`

2. Trigger workflow dispatch for app:
- Workflow: `app-databricks-cloud`
- Input: `target_env = stage`

3. Approve required GitHub Environment gate for `stage`.
4. Run stage validation checks:
- Job health and lag
- Post-apply Key Vault secret sync succeeded.
- Container images were pushed to GHCR with the `stage-latest` tag.
- Data quality checks (sample windows)
- Dashboard/consumer smoke checks

## Step 4: Promote to Cloud Prod (manual)

1. Trigger workflow dispatch for IaC:
- Workflow: `iac-terraform-cloud`
- Input: `target_env = prod`

2. Trigger workflow dispatch for app:
- Workflow: `app-databricks-cloud`
- Input: `target_env = prod`

3. Approve required GitHub Environment gate for `prod`.
4. Run production acceptance checks:
- Streaming jobs stable over agreed observation period.
- Post-apply Key Vault secret sync succeeded.
- Container images were pushed to GHCR with the `prod-latest` tag.
- Event Hubs throughput and consumer lag within target.
- ADLS Delta/checkpoint paths healthy.
- Monitoring/alerts active.

## Demo Evidence Checklist

- PR merged to `main`.
- Green workflow run links for:
  - `iac-terraform-cloud` (dev/stage/prod)
  - `app-databricks-cloud` (dev/stage/prod)
- Screenshots or links:
  - Databricks Jobs runs
  - GHCR package tags
  - ADLS containers/paths
  - Event Hubs metrics
  - Dashboard output

## Rollback Guidance (short)

- App rollback: redeploy previous bundle revision to target environment and republish the matching GHCR image tags if needed.
- Infra rollback: apply previous Terraform revision from git tag/commit.
- If prod is impacted, stop producer ingress first, then roll back app, then infra if required.
