import os
import json
import time
import random
from kafka import KafkaProducer
from utils import build_producer_config

# Internal Kafka address for Docker containers
bootstrap = os.getenv("BOOTSTRAP", "kafka:9092")
topic = os.getenv("TOPIC", "bitcoin-stream")

producer = KafkaProducer(**build_producer_config(
    bootstrap_servers=bootstrap,
    value_serializer=lambda v: json.dumps(v).encode("utf-8"),
))

while True:
    msg = {
        "timestamp": int(time.time() * 1000),
        "price": round(20000 + random.random() * 1000, 2),
        "volume": random.randint(1, 5)
    }
    producer.send(topic, msg)
    producer.flush()
    time.sleep(1)
