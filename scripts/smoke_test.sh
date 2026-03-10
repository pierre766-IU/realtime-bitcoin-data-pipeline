#!/usr/bin/env bash
set -euo pipefail
BOOTSTRAP="${1:-localhost:9092}"
TOPIC="${2:-smoke-test}"
echo "Smoke topic '${TOPIC}'..."
docker compose exec kafka kafka-topics --create --if-not-exists --bootstrap-server "$BOOTSTRAP" --topic "$TOPIC" --partitions 1 --replication-factor 1
echo "Producing..."
docker compose exec -T kafka bash -lc "printf 'a
b
c
' | kafka-console-producer --bootstrap-server $BOOTSTRAP --topic $TOPIC; echo"
echo "Consuming (3s)..."
docker compose exec -T kafka timeout 3s kafka-console-consumer --bootstrap-server "$BOOTSTRAP" --topic "$TOPIC" --from-beginning || true

