#!/usr/bin/env python3
import os
from pyspark.sql import SparkSession, functions as F

from utils.delta_utils import build_path, configure_abfs_shared_key

DELTA_BASE_PATH = os.getenv("DELTA_BASE_PATH", "/data/delta")
CHECKPOINT_BASE_PATH = os.getenv("CHECKPOINT_BASE_PATH", f"{DELTA_BASE_PATH}/_checkpoints")


if __name__ == "__main__":
    silver_path = build_path(DELTA_BASE_PATH, "silver")
    gold_path = build_path(DELTA_BASE_PATH, "gold")
    checkpoint_path = build_path(CHECKPOINT_BASE_PATH, "gold")

    spark = SparkSession.builder.appName("gold_agg").getOrCreate()
    configure_abfs_shared_key(spark)

    silver = spark.readStream.format("delta").load(silver_path)

    gold = (
        silver.withWatermark("event_time", "10 minutes")
        .groupBy(F.window(F.col("event_time"), "1 minute"))
        .agg(F.avg("price").alias("avg_price"), F.sum("volume").alias("total_volume"))
    )

    def write_gold_batch(batch_df, _batch_id):
        (
            batch_df.write.format("delta")
            .mode("overwrite")
            .option("overwriteSchema", "true")
            .save(gold_path)
        )

    query = (
        gold.writeStream.outputMode("complete")
        .foreachBatch(write_gold_batch)
        .option("checkpointLocation", checkpoint_path)
        .trigger(processingTime="10 seconds")
        .start()
    )

    query.awaitTermination()
