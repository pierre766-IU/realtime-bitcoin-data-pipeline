from src.streaming.utils.delta_utils import build_path
from src.streaming.utils.kafka_utils import (
    apply_kafka_options,
    build_kafka_read_options,
    build_sasl_jaas_config,
)


class DummyReader:
    def __init__(self, options=None):
        self.options = {} if options is None else dict(options)

    def option(self, key, value):
        updated = dict(self.options)
        updated[key] = value
        return DummyReader(updated)


def test_build_path_normalizes_separators():
    assert build_path("/data/delta/", "/bronze/", "events") == "/data/delta/bronze/events"


def test_build_sasl_jaas_config_prefers_explicit_value():
    config = build_sasl_jaas_config({"KAFKA_SASL_JAAS_CONFIG": "custom config"})

    assert config == "custom config"


def test_build_sasl_jaas_config_from_username_and_password():
    config = build_sasl_jaas_config(
        {
            "KAFKA_SASL_USERNAME": '$Connection"String',
            "KAFKA_SASL_PASSWORD": 'Endpoint=sb://namespace/;SharedAccessKeyName="Root"',
        }
    )

    assert 'username="$Connection\\"String"' in config
    assert 'password="Endpoint=sb://namespace/;SharedAccessKeyName=\\"Root\\""' in config


def test_build_kafka_read_options_supports_plaintext_defaults():
    options = build_kafka_read_options("bitcoin-stream", "kafka:9092", {})

    assert options == {
        "kafka.bootstrap.servers": "kafka:9092",
        "subscribe": "bitcoin-stream",
        "startingOffsets": "earliest",
        "failOnDataLoss": "false",
    }


def test_build_kafka_read_options_supports_event_hubs_settings():
    options = build_kafka_read_options(
        "bitcoin-stream",
        "namespace.servicebus.windows.net:9093",
        {
            "KAFKA_SECURITY_PROTOCOL": "SASL_SSL",
            "KAFKA_SASL_MECHANISM": "PLAIN",
            "KAFKA_SASL_USERNAME": "$ConnectionString",
            "KAFKA_SASL_PASSWORD": "Endpoint=sb://namespace/;SharedAccessKey=secret",
            "KAFKA_SSL_ENDPOINT_IDENTIFICATION_ALGORITHM": "https",
            "KAFKA_STARTING_OFFSETS": "latest",
            "KAFKA_FAIL_ON_DATA_LOSS": "true",
            "KAFKA_MAX_OFFSETS_PER_TRIGGER": "500",
        },
    )

    assert options["kafka.security.protocol"] == "SASL_SSL"
    assert options["kafka.sasl.mechanism"] == "PLAIN"
    assert options["kafka.ssl.endpoint.identification.algorithm"] == "https"
    assert options["startingOffsets"] == "latest"
    assert options["failOnDataLoss"] == "true"
    assert options["maxOffsetsPerTrigger"] == "500"
    assert options["kafka.sasl.jaas.config"].startswith(
        "org.apache.kafka.common.security.plain.PlainLoginModule required"
    )


def test_apply_kafka_options_returns_reader_with_all_options():
    reader = DummyReader()
    options = {
        "subscribe": "bitcoin-stream",
        "startingOffsets": "latest",
    }

    configured = apply_kafka_options(reader, options)

    assert configured.options == options
