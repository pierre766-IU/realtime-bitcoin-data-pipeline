# Bitcoin Streaming Pipeline (Kafka + Spark + Delta)

This project implements a complete **real-time Bitcoin data pipeline** using:

- **Kafka** (for ingestion)
- **Spark Structured Streaming** (for compute)
- **Delta Lake** (for storage)
- **Docker Compose** (local development environment)

The dataset is hardcoded using:

```python
DEFAULT_URL = (
    "https://github.com/pierre766-IU/btc_1min/releases/download/"
    "btc-binance-2017-2025/BTCUSD_1m_Binance.csv"
)
```

It processes Bitcoin price/volume ticks through three medallion layers:

- **Bronze** -> Raw ingestion from Kafka -> Delta
- **Silver** -> Cleaning, enrichment, validation
- **Gold** -> Aggregations and analytics for downstream consumption

The local development environment includes:

- Spark Master / Worker
- Spark History Server
- Kafka + Zookeeper
- Two producers (random + replay)
- Three Spark jobs (bronze, silver, gold)
- Delta Lake storage mounted locally

This repository supports two operating modes:
- a local Docker Compose stack for development and demonstration
- an Azure/Databricks deployment baseline for cloud validation and promotion

The local environment is intended for development only. The cloud baseline is Databricks-first and uses ADLS, Event Hubs, Key Vault, Azure Monitor, Databricks Asset Bundles, and GitHub Actions workflows for separate IaC and application delivery lanes.

Environment files follow a production-ready pattern.
`.env.dev` is excluded from version control and replaced with `.env.example` to document required variables without exposing real values.
This avoids conflicts with future CI/CD and Terraform-managed production variables.

## Table of Contents

- [1. Limitations](#1-limitations)
- [2. Environment Naming Model](#2-environment-naming-model)
- [3. Architecture (Local / On-Prem)](#3-architecture-local--on-prem)
- [4. Prerequisites (Local/On-prem)](#4-prerequisites-localon-prem)
- [5. Getting Started](#5-getting-started)
- [5.1 Environment Setup](#51-environment-setup)
- [5.2 Infrastructure Startup](#52-infrastructure-startup)
- [5.3 Run Streaming Jobs](#53-run-streaming-jobs)
- [5.4 Feed Data (Producer)](#54-feed-data-producer)
- [5.5 Access the Dashboard](#55-access-the-dashboard)
- [6. Local Development Environment (local / on-prem)](#6-local-development-environment-local--on-prem)
- [6.1 Example `.env.dev`](#61-example-envdev)
- [6.2 Directory Layout](#62-directory-layout)
- [7. Production Baseline (Azure + Databricks)](#7-production-baseline-azure--databricks)
- [7.1 Added Structure](#71-added-structure)
- [7.2 Environment Promotion Model](#72-environment-promotion-model)
- [7.3 Required GitHub Environment Configuration](#73-required-github-environment-configuration)
- [7.4 Running in Cloud (Azure + Databricks)](#74-running-in-cloud-azure--databricks)
- [7.5 Security and Compliance (Cloud)](#75-security-and-compliance-cloud)
- [7.6 Availability](#76-availability)
- [7.7 Scalability](#77-scalability)
- [7.8 Maintainability](#78-maintainability)
- [7.9 Data Governance](#79-data-governance)
- [7.10 Technology Choices](#710-technology-choices)
- [7.11 Notes](#711-notes)

---


## 1. Limitations

- The local stack is designed for development and demonstration, not high-availability production use.
- Local Kafka runs in single-broker mode, so there is no replication or fault tolerance in the on-prem setup.
- The replay producer depends on a fixed historical dataset URL and does not ingest from a live exchange feed.
- Cloud deployment depends on user-managed Azure credentials, GitHub Environment secrets, and Databricks access, so it is not zero-touch for external evaluators.
- The Databricks cloud path is functional as a deployment baseline, but it still requires environment-specific configuration and cost control in Azure.
- Running the full cloud stack on a personal Azure account may consume free credits quickly if Databricks and related resources are left running.

---

## 2. Environment Naming Model

- `local`: on-prem Docker Compose development and debugging on your machine
- `dev` (cloud): first Azure environment for integration deployment and validation
- `stage` (cloud): pre-production validation and release checks
- `prod` (cloud): production workload

Note: `local` is not deployed through Terraform/GitHub cloud deployment workflows.

---
## 3. Architecture (Local / On-Prem)

- **Zookeeper** -> Kafka metadata (single-broker dev mode)
- **Kafka** -> topic: `bitcoin-stream`
- **Spark Master + Worker** -> cluster execution
- **Spark History Server** -> job history (event logs)
- **Producers**
  - `producer-random`: generates synthetic ticks to Kafka
  - `producer-replay`: replays dataset rows to Kafka
- **Spark Jobs**
  - `spark-bronze`: stream from Kafka into Delta `./delta`
  - `spark-silver`: transform bronze data
  - `spark-gold`: compute aggregations

UIs and endpoints:

- Spark Master -> <http://localhost:8082>
- Spark History -> <http://localhost:18080>
- Kafka from host -> `localhost:9393`
- Kafka from containers -> `kafka:9092`

---

## 4. Prerequisites (Local/On-prem)

- Docker Desktop / Engine + Compose v2
- Approximately 6-8 GB RAM available to Docker recommended (project may fail on systems with only 8 GB total RAM)
- Optional: `lsof`, `nc` for quick troubleshooting

---

## 5. Getting Started

To run the project locally, follow these steps in order.

### 5.1 Environment Setup

Create a `.env` file from the example:

```bash
# Using Make
make .env

# Or manually
cp .env.example .env
```

Optional: edit `.env` to adjust memory limits or replay speed.

### 5.2 Infrastructure Startup

Start Zookeeper, Kafka, Spark cluster, and the dashboard:

```bash
# Using Make
make up

# Or manually
docker compose --env-file .env -f docker-compose.yml -f docker-compose.dev.yml up -d
```

### 5.3 Run Streaming Jobs

Start the Bronze, Silver, and Gold Spark jobs:

```bash
# Using Make
make jobs

# Or manually
docker compose --env-file .env -f docker-compose.yml -f docker-compose.dev.yml up -d spark-bronze spark-silver spark-gold
```

### 5.4 Feed Data (Producer)

By default, `make up` starts `producer-random`.
You can also manually trigger `producer-replay` to ingest historical CSV data:

```bash
docker compose --env-file .env -f docker-compose.yml -f docker-compose.dev.yml up -d producer-replay
```

### 5.5 Access the Dashboard

Once the jobs are running, view real-time analytics at:

**Streamlit Dashboard:** [http://localhost:8501](http://localhost:8501)

---

## 6. Local Development Environment (local / on-prem)

This project uses a two-file Docker Compose setup:

- `docker-compose.yml` -> base services
- `docker-compose.dev.yml` -> local-only overrides (ports, volumes, relaxed health checks)

And a local environment file:

- `.env.dev`

### 6.1 Example `.env.dev`

```dotenv
HOST_ADVERTISED=localhost
HOST_KAFKA_PORT=9393
TOPIC=bitcoin-stream
REPLAY_SPEED=50
SPARK_WORKER_MEMORY=4G
SPARK_WORKER_CORES=3
KAFKA_AUTO_CREATE_TOPICS_ENABLE=true
```

### 6.2 Directory Layout

```text
bitcoin-streaming-pipeline/
|-- README.md                            # project overview and operating guide
|-- architecture-v2.md                   # target cloud architecture notes
|-- databricks.yml                       # Databricks Asset Bundle definition
|-- docker-compose.yml                   # base compose services
|-- docker-compose.dev.yml               # local/on-prem overrides
|-- makefile                             # local helper commands
|-- requirements-ci.txt                  # CI lint/test dependencies
|-- .env.example                         # documented environment variables
|
|-- src/                                 # application code shared across local/cloud paths
|   |-- producer/                        # random and replay producers
|   |-- streaming/                       # bronze, silver, gold Spark jobs
|   `-- dashboard/                       # Streamlit dashboard
|
|-- data/                                # local replay input data
|-- delta/                               # local Delta Lake runtime storage
|-- spark-events/                        # local Spark History Server logs
|-- notebooks/                           # exploration and validation notebooks
|-- scripts/                             # local smoke/bootstrap scripts
|
|-- infra/                               # Terraform-based cloud infrastructure
|   |-- envs/
|   |   |-- dev/                         # dev root module and tfvars
|   |   |-- stage/                       # stage root module and tfvars
|   |   `-- prod/                        # prod root module and tfvars
|   |-- modules/                         # reusable Azure modules
|   `-- README.md                        # cloud/IaC usage notes
|
|-- docs/                                # operational and promotion runbooks
|
`-- .github/
    |-- actions/
    |   `-- sync-keyvault-secrets/       # composite action for post-deploy secret sync
    `-- workflows/
        |-- iac.yml                      # Terraform validate/deploy workflow
        `-- app-databricks.yml           # app lint/build/deploy workflow
```

---

## 7. Production Baseline (Azure + Databricks)

This repository now includes a cloud production IaC and deployment scaffold aligned to `architecture-v2.md`.

### 7.1 Added Structure

- `infra/modules/*`: reusable Terraform modules (`eventhub`, `adls`, `keyvault`, `monitoring`, `databricks_workspace`)
- `infra/envs/dev|stage|prod`: separate cloud Terraform roots for explicit environment promotion
- `databricks.yml`: Databricks Asset Bundle for Bronze/Silver/Gold streaming jobs
- `.github/workflows/iac.yml`: IaC lane (validate + deploy)
- `.github/workflows/app-databricks.yml`: app lane (lint/build + Databricks bundle deploy)

### 7.2 Environment Promotion Model

- `dev` (cloud): auto-apply for infra on push to `main` when `infra/**` changes; auto app deploy on push to `main` when `src/**` changes
- `stage` and `prod` (cloud): manual deploy via workflow dispatch with GitHub Environment approvals

### 7.3 Required GitHub Environment Configuration

Create cloud environments: `dev`, `stage`, `prod`.

For each environment, add secrets:

- `DATABRICKS_HOST`
- `DATABRICKS_TOKEN`
- `KAFKA_SASL_PASSWORD` (Event Hubs Kafka connection string or SASL password for bronze ingest)
- `KEYVAULT_SECRETS_JSON` (optional JSON object of extra Key Vault secrets)

Add the following only if you want GitHub-hosted Terraform apply for that environment:

- `AZURE_CLIENT_ID`
- `AZURE_TENANT_ID`
- `AZURE_SUBSCRIPTION_ID`
- `TFSTATE_RESOURCE_GROUP`
- `TFSTATE_STORAGE_ACCOUNT`
- `TFSTATE_CONTAINER`

For each environment, add variables:

- `KEYVAULT_DATABRICKS_HOST_SECRET_NAME` (optional, defaults to `databricks-host`)
- `KEYVAULT_DATABRICKS_TOKEN_SECRET_NAME` (optional, defaults to `databricks-token`)
- `EVENT_HUBS_BOOTSTRAP` (for example `<namespace>.servicebus.windows.net:9093`)
- `EVENT_HUBS_TOPIC` (optional, defaults to `bitcoin-stream`)
- `DELTA_BASE_PATH` (for example `abfss://delta@<storage>.dfs.core.windows.net/bitcoin`)
- `CHECKPOINT_BASE_PATH` (for example `abfss://checkpoints@<storage>.dfs.core.windows.net/bitcoin`)
- `KAFKA_SECURITY_PROTOCOL` (optional, defaults to `SASL_SSL`)
- `KAFKA_SASL_MECHANISM` (optional, defaults to `PLAIN`)
- `KAFKA_SASL_USERNAME` (optional, defaults to `$ConnectionString`)
- `KAFKA_SSL_ENDPOINT_IDENTIFICATION_ALGORITHM` (optional, defaults to `https`)
- `KAFKA_STARTING_OFFSETS` (optional, defaults to `latest`)
- `KAFKA_FAIL_ON_DATA_LOSS` (optional, defaults to `false`)

Add `TFSTATE_KEY` (example: `bitcoin-streaming-pipeline/dev.tfstate`) only if you want GitHub-hosted Terraform apply for that environment.

### 7.4 Running in Cloud (Azure + Databricks)

Use this flow when you want to run the project through GitHub Actions in a real cloud environment.

1. Prepare the target cloud environment.
- Create or choose an Azure subscription.
- Create the Terraform backend resource group, storage account, and blob container.
- Create the GitHub Environment (`dev`, `stage`, or `prod`) and add the required secrets/variables listed above.

2. Review environment-specific configuration.
- Confirm the target Terraform values in `infra/envs/<env>/terraform.tfvars`.
- Set the GitHub Environment runtime values used by `app-databricks.yml`.
- Keep `backend.hcl` local only if you run Terraform manually outside GitHub Actions.

3. Deploy infrastructure first.
- If GitHub has Azure workload credentials for the target environment, push infra changes to `main` for `dev` or use `workflow_dispatch` for `stage` and `prod`.
- If GitHub does not have Azure workload credentials, the IaC workflow will still run `fmt` and `validate`, then skip GitHub-hosted apply with a message instead of failing.
- In that case, apply Terraform manually from your machine using Azure CLI authentication:

```bash
az login
cd infra/envs/dev
cp backend.hcl.example backend.hcl
terraform init -backend-config=backend.hcl
terraform plan -var-file=terraform.tfvars
terraform apply -var-file=terraform.tfvars
```

4. Capture and verify Terraform outputs.
- Record `databricks_workspace_url`.
- Record `event_hubs_bootstrap`.
- Record `delta_base_path` and `checkpoint_base_path`.
- Copy these values into the matching GitHub Environment variables for the target environment.

5. Deploy the application lane.
- Trigger `app-databricks-cloud` for the same target environment.
- The workflow lints and tests the repo, validates the bundle, and deploys the Databricks jobs for the target environment.
- The bronze job reads its Kafka/Event Hubs security settings from GitHub Environment variables and the `KAFKA_SASL_PASSWORD` secret.

6. Validate the cloud deployment.
- Check that the IaC workflow either succeeded with apply or completed validation and reported that GitHub-hosted apply was skipped.
- Verify that Databricks jobs for bronze, silver, and gold are present and healthy.
- Verify that Event Hubs ingest is active and ADLS Delta/checkpoint paths are updating.
- Confirm that Key Vault secret sync succeeded after infra apply.

7. Promote to the next environment only after validation.
- `dev` is the first integration environment.
- `stage` and `prod` should be promoted manually with environment approvals and smoke checks.

### 7.5 Security and Compliance (Cloud)

- Secrets are not committed to the repository; sensitive values are expected to be stored in GitHub Environment secrets and synchronized into Azure Key Vault after infrastructure deployment.
- The repository uses a no-credentials-in-source approach, with `.env.example` documenting required variables while real tokens, client IDs, and runtime secrets remain outside version control.
- Access control is intended to follow least-privilege role assignments, including scoped GitHub Environment permissions and Azure RBAC assignments such as the Key Vault secret management role used by the deployment identity.
- Environment separation is enforced through dedicated `dev`, `stage`, and `prod` configurations, isolated Terraform state keys, and environment-specific variables to reduce cross-environment drift and accidental credential reuse.

### 7.6 Availability

- Cloud environments are separated into `dev`, `stage`, and `prod`, which reduces blast radius and allows validation before promotion.
- The design relies on managed services such as Event Hubs, ADLS Gen2, Key Vault, Azure Monitor, and Databricks rather than self-managed infrastructure components.
- GitHub Actions and Terraform provide a repeatable redeployment path, which improves operational recovery compared with manual environment rebuilds.
- Full production-grade high availability is still a future hardening step and depends on final Azure sizing, networking, and Databricks runtime configuration.

### 7.7 Scalability

- Event Hubs capacity, partitions, and retention are configured per environment, allowing throughput to be increased as ingestion demand grows.
- Databricks job cluster sizing is environment-specific, so compute capacity can be increased independently from local development defaults.
- ADLS Gen2 provides a scalable storage layer for Delta data and checkpoints as historical volume increases.
- Databricks bundle variables and environment-specific cluster sizing support repeatable promotion across environments without editing source code per stage.

### 7.8 Maintainability

- Terraform is organized into reusable modules and separate environment roots, which keeps infrastructure changes structured and easier to review.
- The repository separates the IaC lane and the application lane into different GitHub workflows, reducing coupling between infrastructure and app delivery changes.
- Environment-specific variables in Terraform and `databricks.yml` make configuration differences explicit instead of hiding them in ad hoc manual changes.
- The numbered README flow and promotion guidance improve handover, onboarding, and evaluation reproducibility.

### 7.9 Data Governance

- The medallion layout supports governance by separating raw, cleaned, and aggregated data into bronze, silver, and gold processing stages.
- Environment-specific storage paths and isolated cloud environments reduce the risk of mixing test and production-like datasets during deployment and validation.

### 7.10 Technology Choices

- **Why Event Hubs instead of IoT Hub?** This pipeline ingests stream events from application producers rather than device-managed IoT fleets. Event Hubs fits the requirement better because it provides Kafka-compatible event ingestion for high-throughput streaming without the device registry, device twins, and protocol-management features that are more specific to IoT Hub.
- **Why Databricks instead of self-managed Spark?** The cloud design uses Databricks as the managed Spark runtime to reduce operational overhead, simplify environment promotion, and align streaming compute with Delta-oriented lakehouse patterns on Azure. In other words, the project still uses Spark as the processing engine, but Databricks is the managed platform chosen to run Spark in the cloud.

### 7.11 Notes

- Populate the Databricks runtime GitHub Environment variables and secrets before deployment.
- Keep `infra/envs/*/backend.hcl` local only (ignored by `.gitignore`).
- Infra deploys now sync GitHub environment secrets into the provisioned Key Vault after Terraform apply, so runtime secret values stay out of Terraform state.
- App deploys validate and deploy the Databricks bundle using the environment-specific Event Hubs and ADLS runtime settings.
- Use private networking, managed identities, and RBAC policies as part of environment hardening before go-live.

