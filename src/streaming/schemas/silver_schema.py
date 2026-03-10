from pyspark.sql import types as T

SILVER_SCHEMA = T.StructType([
    T.StructField("timestamp", T.StringType(), True),
    T.StructField("price", T.DoubleType(), True),
    T.StructField("volume", T.DoubleType(), True),
    T.StructField("event_time", T.TimestampType(), True),
    T.StructField("ingest_ts", T.TimestampType(), True),
])
