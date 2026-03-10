DEV := --env-file .env -f docker-compose.yml -f docker-compose.dev.yml

.PHONY: up down clean build jobs logs smoke scale

# Automatically create .env from .env.example if missing
.env:
	cp .env.example .env

# Start full environment
up: .env
	docker compose $(DEV) up -d --remove-orphans

# Stop environment
down:
	docker compose $(DEV) down --remove-orphans

# Stop + remove volumes + clean generated data
clean:
	docker compose $(DEV) down -v --remove-orphans
	rm -rf delta spark-events

# Build all images
build:
	docker compose $(DEV) build

# Start only Spark jobs
jobs:
	docker compose $(DEV) up -d spark-bronze spark-silver spark-gold

# Follow logs for key services
logs:
	docker compose $(DEV) logs -f spark-master kafka

# Kafka smoke test
smoke:
	@echo "Kafka smoke test..."
	-docker compose $(DEV) exec kafka kafka-topics --create --if-not-exists --bootstrap-server localhost:9092 --topic smoke-test --partitions 1 --replication-factor 1
	-docker compose $(DEV) exec -T kafka bash -lc 'printf "a\nb\nc\n" | kafka-console-producer --bootstrap-server localhost:9092 --topic smoke-test; echo'
	-docker compose $(DEV) exec -T kafka timeout 3s kafka-console-consumer --bootstrap-server localhost:9092 --topic smoke-test --from-beginning || true

# Scale Spark workers dynamically
scale:
	@if [ -z "$(n)" ]; then echo "Usage: make scale n=2"; exit 1; fi
	docker compose $(DEV) up -d --scale spark-worker=$(n) --remove-orphans