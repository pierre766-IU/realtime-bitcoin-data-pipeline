#!/usr/bin/env python3
import os
from pyspark.sql import SparkSession, functions as F

DELTA_BASE_PATH = os.getenv("DELTA_BASE_PATH", "/data/delta")
CHECKPOINT_BASE_PATH = os.getenv("CHECKPOINT_BASE_PATH", f"{DELTA_BASE_PATH}/_checkpoints")


def build_path(base: str, *parts: str) -> str:
    return "/".join([base.rstrip("/")] + [p.strip("/") for p in parts])


if __name__ == "__main__":
    silver_path = build_path(DELTA_BASE_PATH, "silver")
    gold_path = build_path(DELTA_BASE_PATH, "gold")
    checkpoint_path = build_path(CHECKPOINT_BASE_PATH, "gold")

    spark = SparkSession.builder.appName("gold_agg").getOrCreate()

    silver = spark.readStream.format("delta").load(silver_path)

    gold = (
        silver.withWatermark("event_time", "10 minutes")
        .groupBy(F.window(F.col("event_time"), "1 minute"))
        .agg(F.avg("price").alias("avg_price"), F.sum("volume").alias("total_volume"))
    )

    query = (
        gold.writeStream.format("delta")
        .outputMode("append")
        .option("checkpointLocation", checkpoint_path)
        .trigger(processingTime="10 seconds")
        .start(gold_path)
    )

    query.awaitTermination()
