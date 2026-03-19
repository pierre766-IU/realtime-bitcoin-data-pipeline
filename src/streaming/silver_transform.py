#!/usr/bin/env python3
import os
from pyspark.sql import SparkSession, functions as F

from utils.delta_utils import build_path, configure_abfs_shared_key

DELTA_BASE_PATH = os.getenv("DELTA_BASE_PATH", "/data/delta")
CHECKPOINT_BASE_PATH = os.getenv("CHECKPOINT_BASE_PATH", f"{DELTA_BASE_PATH}/_checkpoints")


if __name__ == "__main__":
    bronze_path = build_path(DELTA_BASE_PATH, "bronze")
    silver_path = build_path(DELTA_BASE_PATH, "silver")
    checkpoint_path = build_path(CHECKPOINT_BASE_PATH, "silver")

    spark = SparkSession.builder.appName("silver_transform").getOrCreate()
    configure_abfs_shared_key(spark)

    bronze = spark.readStream.format("delta").load(bronze_path)

    cleaned = (
        bronze.withWatermark("event_time", "10 minutes")
        .filter((F.col("price") > 0) & (F.col("volume") >= 0))
        .dropDuplicates(["timestamp", "price", "volume", "event_time"])
    )

    query = (
        cleaned.writeStream.format("delta")
        .outputMode("append")
        .option("checkpointLocation", checkpoint_path)
        .trigger(processingTime="10 seconds")
        .start(silver_path)
    )

    query.awaitTermination()
