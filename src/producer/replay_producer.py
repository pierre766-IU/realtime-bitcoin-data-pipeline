#!/usr/bin/env python3
import os
import csv
import json
import time
import gzip
import logging
from io import TextIOWrapper
from typing import Iterator

import requests
from kafka import KafkaProducer

# ========= DATASET URL =========
# Default to the Release asset; can be overridden via env DATASET_URL
DEFAULT_URL = (
    "https://github.com/pierre766-IU/btc_1min/releases/download/"
    "btc-binance-2017-2025/BTCUSD_1m_Binance.csv"
)
DATASET_URL = os.getenv("DATASET_URL", DEFAULT_URL)

# ========= Kafka + Producer settings =========
# Internal Kafka listener for Docker containers
BOOTSTRAP = os.getenv("BOOTSTRAP", "kafka:9092")
TOPIC = os.getenv("TOPIC", "bitcoin-stream")
SPEED = float(os.getenv("REPLAY_SPEED", "50"))  # rows per second

# CSV column names (can override by env)
TIMESTAMP_COL = os.getenv("TIMESTAMP_COL", "timestamp")
PRICE_COL = os.getenv("PRICE_COL", "price")
VOLUME_COL = os.getenv("VOLUME_COL", "volume")

REQUEST_TIMEOUT = 60
RETRY_COUNT = 5
RETRY_BACKOFF = 2.0

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")


def pick_column(columns, preferred, aliases):
    """Pick a column by exact match first, then case-insensitive alias match."""
    if preferred in columns:
        return preferred

    lower_to_actual = {c.lower(): c for c in columns}
    for candidate in aliases:
        actual = lower_to_actual.get(candidate.lower())
        if actual:
            return actual
    return preferred


def open_csv_stream(url: str):
    """Open a streaming HTTP response and return a text stream for CSV parsing."""
    headers = {"Accept": "application/octet-stream"}

    for attempt in range(1, RETRY_COUNT + 1):
        resp = None
        try:
            logging.info("Opening dataset stream from %s (attempt %d/%d)...", url, attempt, RETRY_COUNT)
            resp = requests.get(url, timeout=REQUEST_TIMEOUT, allow_redirects=True, headers=headers, stream=True)
            if resp.status_code != 200:
                logging.warning("HTTP %s when opening %s", resp.status_code, url)
                resp.close()
                time.sleep(RETRY_BACKOFF * attempt)
                continue

            # Let urllib3 decode transfer encodings, then handle .gz payloads ourselves.
            resp.raw.decode_content = True

            content_type = resp.headers.get("Content-Type", "").lower()
            content_encoding = resp.headers.get("Content-Encoding", "").lower()
            is_gz = url.lower().endswith(".gz") or ("gzip" in content_type) or ("gzip" in content_encoding)

            binary_stream = gzip.GzipFile(fileobj=resp.raw) if is_gz else resp.raw
            text_stream = TextIOWrapper(binary_stream, encoding="utf-8", errors="replace", newline="")
            logging.info("Dataset stream opened (gzip=%s)", is_gz)
            return resp, text_stream

        except requests.RequestException as e:
            logging.warning("Request error: %s", e)
            if resp is not None:
                resp.close()
            time.sleep(RETRY_BACKOFF * attempt)

    raise RuntimeError(f"Failed to open dataset stream after {RETRY_COUNT} attempts: {url}")


# -----------------------------------------------------------
# CSV reader that streams rows from HTTP (no full file in memory)
# -----------------------------------------------------------
def iter_csv_rows(url: str) -> Iterator[dict]:
    response, text_stream = open_csv_stream(url)

    with response:
        with text_stream as f:
            reader = csv.DictReader(f)
            cols = reader.fieldnames or []
            logging.info("CSV columns detected: %s", cols)

            ts_col = pick_column(
                cols,
                TIMESTAMP_COL,
                ["Open time", "open_time", "timestamp", "time"],
            )
            price_col = pick_column(
                cols,
                PRICE_COL,
                ["Close", "close", "price"],
            )
            vol_col = pick_column(
                cols,
                VOLUME_COL,
                ["Volume", "volume", "BaseVolume", "base_volume", "taker_buy_base_asset_volume"],
            )

            logging.info(
                "Using column mapping: timestamp='%s', price='%s', volume='%s'",
                ts_col,
                price_col,
                vol_col,
            )

            required = {ts_col, price_col, vol_col}
            missing = required - set(cols)
            if missing:
                raise ValueError(f"Missing required columns: {missing}. Found: {cols}")

            for row in reader:
                try:
                    yield {
                        "timestamp": row[ts_col],
                        "price": float(row[price_col]),
                        "volume": float(row[vol_col]),
                    }
                except Exception as e:
                    logging.warning("Skipping row due to error: %s -- row=%s", e, row)


# -----------------------------------------------------------
# MAIN
# -----------------------------------------------------------
def main():
    logging.info("Using dataset: %s", DATASET_URL)

    producer = KafkaProducer(
        bootstrap_servers=BOOTSTRAP,
        value_serializer=lambda v: json.dumps(v).encode("utf-8"),
        linger_ms=50,
        retries=3,
        acks=1,
    )
    logging.info("Kafka producer connected -> %s; topic=%s; speed=%.2f rows/s", BOOTSTRAP, TOPIC, SPEED)

    delay = 1.0 / SPEED if SPEED > 0 else 0.0
    sent = 0
    start = time.time()

    for msg in iter_csv_rows(DATASET_URL):
        producer.send(TOPIC, msg)
        sent += 1
        if delay:
            time.sleep(delay)
        if sent % max(1, int(SPEED * 2)) == 0:
            elapsed = max(1e-6, time.time() - start)
            logging.info("Sent %d msgs (%.1f msg/s)", sent, sent / elapsed)

    producer.flush()
    logging.info("Finished. Total messages sent: %d", sent)


if __name__ == "__main__":
    main()
