#!/usr/bin/env python3
from pyspark.sql import SparkSession, functions as F

if __name__ == "__main__":
    spark = (SparkSession.builder.appName("silver_transform")
             .getOrCreate())

    bronze = (spark.readStream
              .format("delta")
              .load("/data/delta/bronze"))

    # Example cleanup: drop obvious bad values, deduplicate by keys over a watermark
    cleaned = (bronze
               .withWatermark("event_time", "10 minutes")
               .filter((F.col("price") > 0) & (F.col("volume") >= 0))
               .dropDuplicates(["timestamp", "price", "volume", "event_time"]))

    query = (cleaned.writeStream
             .format("delta")
             .outputMode("append")
             .option("checkpointLocation", "/data/delta/_checkpoints/silver")
             .trigger(processingTime="10 seconds")
             .start("/data/delta/silver"))

    query.awaitTermination()