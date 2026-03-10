#!/usr/bin/env bash
set -euo pipefail
TOPIC="${1:-bitcoin-stream}"
BOOTSTRAP="${2:-localhost:9092}"
echo "Creating topic '${TOPIC}' on ${BOOTSTRAP} (if not exists)..."
docker compose exec kafka kafka-topics --create --if-not-exists --bootstrap-server "$BOOTSTRAP" --topic "$TOPIC" --partitions 1 --replication-factor 1

