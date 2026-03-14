#!/usr/bin/env python3
import os
from pyspark.sql import SparkSession, functions as F

from schemas.bronze_schema import BRONZE_SCHEMA

TOPIC = os.getenv("TOPIC", "bitcoin-stream")
BOOTSTRAP = os.getenv("BOOTSTRAP", "kafka:9092")
DELTA_BASE_PATH = os.getenv("DELTA_BASE_PATH", "/data/delta")
CHECKPOINT_BASE_PATH = os.getenv("CHECKPOINT_BASE_PATH", f"{DELTA_BASE_PATH}/_checkpoints")

schema = BRONZE_SCHEMA


def build_path(base: str, *parts: str) -> str:
    return "/".join([base.rstrip("/")] + [p.strip("/") for p in parts])


def to_event_time(col):
    return F.coalesce(
        F.to_timestamp(col),
        F.to_timestamp(F.from_unixtime(col.cast("long"))),
        F.to_timestamp(F.from_unixtime((col.cast("double") / 1000.0))),
    )


if __name__ == "__main__":
    bronze_path = build_path(DELTA_BASE_PATH, "bronze")
    checkpoint_path = build_path(CHECKPOINT_BASE_PATH, "bronze")

    spark = SparkSession.builder.appName("bronze_ingest").getOrCreate()

    raw = (
        spark.readStream.format("kafka")
        .option("kafka.bootstrap.servers", BOOTSTRAP)
        .option("subscribe", TOPIC)
        .option("startingOffsets", "earliest")
        .load()
    )

    parsed = (
        raw.select(F.col("value").cast("string").alias("json_str"))
        .select(F.from_json("json_str", schema).alias("data"))
        .select("data.*")
        .withColumn("event_time", to_event_time(F.col("timestamp")))
        .withColumn("ingest_ts", F.current_timestamp())
    )

    bronze = (
        parsed.filter(F.col("price").isNotNull() & F.col("volume").isNotNull())
        .filter(F.col("event_time").isNotNull())
    )

    query = (
        bronze.writeStream.format("delta")
        .outputMode("append")
        .option("checkpointLocation", checkpoint_path)
        .trigger(processingTime="10 seconds")
        .start(bronze_path)
    )

    query.awaitTermination()
