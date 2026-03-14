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

This setup is **for local development only**.
A production‑ready cloud baseline is included, targeting a Databricks‑first deployment on Azure using GHCR, ADLS, Event Hubs, Key Vault, Azure Monitor, and a Databricks Workspace.
CI workflows are included for separate IaC and application lanes (`iac.yml` and `app-databricks.yml`) to support automated validation and deployment.
Full CI/CD integration will be implemented in the production phase when deploying to Azure.

Environment files follow a production-ready pattern.
`.env.dev` is excluded from version control and replaced with `.env.example` to document required variables without exposing real values.
This avoids conflicts with future CI/CD and Terraform-managed production variables.

---

## Environment Naming Model

- `local`: on-prem Docker Compose development and debugging on your machine
- `dev` (cloud): first Azure environment for integration deployment and validation
- `stage` (cloud): pre-production validation and release checks
- `prod` (cloud): production workload

Note: `local` is not deployed through Terraform/GitHub cloud deployment workflows.

---
## Architecture (Local / On-Prem)

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

## Prerequisites (Local/On-prem)

- Docker Desktop / Engine + Compose v2
- Approximately 6-8 GB RAM available to Docker recommended (project may fail on systems with only 8 GB total RAM)
- Optional: `lsof`, `nc` for quick troubleshooting

---

## Getting Started

To run the project locally, follow these steps in order.

### 1. Environment Setup

Create a `.env` file from the example:

```bash
# Using Make
make .env

# Or manually
cp .env.example .env
```

Optional: edit `.env` to adjust memory limits or replay speed.

### 2. Infrastructure Startup

Start Zookeeper, Kafka, Spark cluster, and the dashboard:

```bash
# Using Make
make up

# Or manually
docker compose --env-file .env -f docker-compose.yml -f docker-compose.dev.yml up -d
```

### 3. Run Streaming Jobs

Start the Bronze, Silver, and Gold Spark jobs:

```bash
# Using Make
make jobs

# Or manually
docker compose --env-file .env -f docker-compose.yml -f docker-compose.dev.yml up -d spark-bronze spark-silver spark-gold
```

### 4. Feed Data (Producer)

By default, `make up` starts `producer-random`.
You can also manually trigger `producer-replay` to ingest historical CSV data:

```bash
docker compose --env-file .env -f docker-compose.yml -f docker-compose.dev.yml up -d producer-replay
```

### 5. Access the Dashboard

Once the jobs are running, view real-time analytics at:

**Streamlit Dashboard:** [http://localhost:8501](http://localhost:8501)

---

## Local Development Environment (local / on-prem)

This project uses a two-file Docker Compose setup:

- `docker-compose.yml` -> base services
- `docker-compose.dev.yml` -> local-only overrides (ports, volumes, relaxed health checks)

And a local environment file:

- `.env.dev`

### Example `.env.dev`

```dotenv
HOST_ADVERTISED=localhost
HOST_KAFKA_PORT=9393
TOPIC=bitcoin-stream
REPLAY_SPEED=50
SPARK_WORKER_MEMORY=4G
SPARK_WORKER_CORES=3
KAFKA_AUTO_CREATE_TOPICS_ENABLE=true
```

### Directory Layout

```text
bitcoin-streaming-pipeline/
|-- docker-compose.yml                  # base compose for all services
|-- docker-compose.dev.yml              # local development overrides
|-- .env.dev                            # local environment variables
|-- makefile                            # helper commands
|-- README.md
|-- .gitignore
|
|-- data/                               # input data for replay producer
|   |-- bitcoin.csv
|   `-- .gitkeep
|
|-- delta/                              # Delta Lake storage (runtime)
|   |-- bronze/
|   |-- silver/
|   |-- gold/
|   `-- .gitkeep
|
|-- spark-events/                       # Spark History Server logs
|   `-- .gitkeep
|
|-- src/
|   |-- producer/
|   |   |-- Dockerfile
|   |   |-- random_producer.py
|   |   |-- replay_producer.py
|   |   |-- utils.py
|   |   `-- __init__.py
|   |
|   |-- dashboard/
|   |   |-- Dockerfile
|   |   `-- app.py
|   |
|   `-- streaming/
|       |-- Dockerfile                  # FROM apache/spark:3.5.7 + python3
|       |-- bronze_ingest.py
|       |-- silver_transform.py
|       |-- gold_agg.py
|       |
|       |-- utils/
|       |   |-- delta_utils.py
|       |   |-- kafka_utils.py
|       |   `-- __init__.py
|       |
|       |-- schemas/
|       |   |-- bronze_schema.py
|       |   |-- silver_schema.py
|       |   `-- __init__.py
|       |
|       |-- config/
|       |   |-- settings.yaml
|       |   `-- logging.conf
|       |
|       `-- __init__.py
|
|-- notebooks/
|   |-- exploration.ipynb
|   `-- validation.ipynb
|
|-- scripts/
|   |-- init_topics.sh                  # optional Kafka topic initialization
|   `-- smoke_test.sh                   # optional producer/consumer smoke test
|
`-- .github/
    `-- workflows/
        |-- iac.yml                     # IaC lane: terraform validate/deploy
        `-- app-databricks.yml          # App lane: lint/build + Databricks deploy
```

---

## Production Baseline (Azure + Databricks)

This repository now includes a cloud production IaC and deployment scaffold aligned to `architecture-v2.md`.

### Added Structure

- `infra/modules/*`: reusable Terraform modules (`eventhub`, `adls`, `keyvault`, `monitoring`, `databricks_workspace`)
- `infra/envs/dev|stage|prod`: separate cloud Terraform roots for explicit environment promotion
- `databricks.yml`: Databricks Asset Bundle for Bronze/Silver/Gold streaming jobs
- `.github/workflows/iac.yml`: IaC lane (validate + deploy)
- `.github/workflows/app-databricks.yml`: app lane (lint/build + Databricks bundle deploy)

### Environment Promotion Model

- `dev` (cloud): auto-apply for infra on push to `main` when `infra/**` changes; auto app deploy on push to `main` when `src/**` changes
- `stage` and `prod` (cloud): manual deploy via workflow dispatch with GitHub Environment approvals

### Required GitHub Environment Configuration

Create cloud environments: `dev`, `stage`, `prod`.

For each environment, add secrets:

- `AZURE_CLIENT_ID`
- `AZURE_TENANT_ID`
- `AZURE_SUBSCRIPTION_ID`
- `TFSTATE_RESOURCE_GROUP`
- `TFSTATE_STORAGE_ACCOUNT`
- `TFSTATE_CONTAINER`
- `DATABRICKS_HOST`
- `DATABRICKS_TOKEN`
- `KEYVAULT_SECRETS_JSON` (optional JSON object of extra Key Vault secrets)

For each environment, add variables:

- `TFSTATE_KEY` (example: `bitcoin-streaming-pipeline/dev.tfstate`)
- `KEYVAULT_DATABRICKS_HOST_SECRET_NAME` (optional, defaults to `databricks-host`)
- `KEYVAULT_DATABRICKS_TOKEN_SECRET_NAME` (optional, defaults to `databricks-token`)

### Notes

- Replace placeholder values in `databricks.yml` target variables before deployment.
- Keep `infra/envs/*/backend.hcl` local only (ignored by `.gitignore`).
- Infra deploys now sync GitHub environment secrets into the provisioned Key Vault after Terraform apply, so runtime secret values stay out of Terraform state.
- App deploys publish the Spark, producer, and dashboard container images into GitHub Container Registry before the Databricks bundle deploy runs.
- GHCR publishing is independent from Terraform state, so the app lane can publish images without a prior registry bootstrap step.
- Use private networking, managed identities, and RBAC policies as part of environment hardening before go-live.











