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
A production-ready Azure architecture (AKS, ACR, ADLS, Event Hubs) will be finalized later (Phase 3).
A CI workflow file (`ci.yml`) is already included to prepare for automated testing and image builds.
Full CI/CD integration will be implemented in the production phase when deploying to Azure.

Environment files follow a production-ready pattern.
`.env.dev` is excluded from version control and replaced with `.env.example` to document required variables without exposing real values.
This avoids conflicts with future CI/CD and Terraform-managed production variables.

---

## Architecture (DEV Environment)

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

## Prerequisites

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

## Local Development Environment (DEV)

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
        `-- ci.yml                      # CI: lint, test, build Docker images
```
