#!/usr/bin/env python3
from pyspark.sql import SparkSession, functions as F

if __name__ == "__main__":
    spark = (SparkSession.builder.appName("gold_agg")
             .getOrCreate())

    silver = (spark.readStream
              .format("delta")
              .load("/data/delta/silver"))

    # Aggregate: tumbling 1-minute window
    gold = (silver
            .withWatermark("event_time", "10 minutes")
            .groupBy(F.window(F.col("event_time"), "1 minute"))
            .agg(
                F.avg("price").alias("avg_price"),
                F.sum("volume").alias("total_volume")
            ))

    query = (gold.writeStream
             .format("delta")
             .outputMode("append")
             .option("checkpointLocation", "/data/delta/_checkpoints/gold")
             .trigger(processingTime="10 seconds")
             .start("/data/delta/gold"))

    query.awaitTermination()