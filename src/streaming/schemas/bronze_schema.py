from pyspark.sql import types as T

BRONZE_SCHEMA = T.StructType([
    T.StructField("timestamp", T.StringType(), True),
    T.StructField("price", T.DoubleType(), True),
    T.StructField("volume", T.DoubleType(), True),
])
