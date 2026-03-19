from src.producer.utils import build_producer_config


def serializer(value):
    return str(value).encode("utf-8")


def test_build_producer_config_uses_local_defaults():
    config = build_producer_config(
        bootstrap_servers="kafka:9092",
        value_serializer=serializer,
        env={},
    )

    assert config["bootstrap_servers"] == "kafka:9092"
    assert config["value_serializer"] is serializer
    assert "security_protocol" not in config


def test_build_producer_config_supports_sasl_ssl():
    config = build_producer_config(
        bootstrap_servers="namespace.servicebus.windows.net:9093",
        value_serializer=serializer,
        env={
            "KAFKA_SECURITY_PROTOCOL": "SASL_SSL",
            "KAFKA_SASL_MECHANISM": "PLAIN",
            "KAFKA_SASL_USERNAME": "$ConnectionString",
            "KAFKA_SASL_PASSWORD": "Endpoint=sb://namespace/;SharedAccessKey=secret",
            "KAFKA_SSL_CHECK_HOSTNAME": "true",
        },
        linger_ms=50,
    )

    assert config["security_protocol"] == "SASL_SSL"
    assert config["sasl_mechanism"] == "PLAIN"
    assert config["sasl_plain_username"] == "$ConnectionString"
    assert config["sasl_plain_password"] == "Endpoint=sb://namespace/;SharedAccessKey=secret"
    assert config["ssl_check_hostname"] is True
    assert config["linger_ms"] == 50


def test_build_producer_config_defaults_event_hubs_username_when_missing():
    config = build_producer_config(
        bootstrap_servers="namespace.servicebus.windows.net:9093",
        value_serializer=serializer,
        env={
            "KAFKA_SECURITY_PROTOCOL": "SASL_SSL",
            "KAFKA_SASL_MECHANISM": "PLAIN",
            "KAFKA_SASL_PASSWORD": "Endpoint=sb://namespace/;SharedAccessKey=secret",
        },
    )

    assert config["sasl_plain_username"] == "$ConnectionString"
    assert config["sasl_plain_password"] == "Endpoint=sb://namespace/;SharedAccessKey=secret"
