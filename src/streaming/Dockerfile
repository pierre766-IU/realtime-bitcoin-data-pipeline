FROM apache/spark:3.5.7
USER root
WORKDIR /opt/spark-apps
RUN apt-get update && apt-get install -y --no-install-recommends python3 python3-pip ca-certificates && rm -rf /var/lib/apt/lists/*
ENV PYSPARK_PYTHON=/usr/bin/python3 PYSPARK_DRIVER_PYTHON=/usr/bin/python3
RUN mkdir -p /opt/spark-apps /data/delta /opt/spark/events && chown -R 185:0 /opt/spark-apps /data/delta /opt/spark/events || true
COPY --chown=185:0 . /opt/spark-apps
USER 185
