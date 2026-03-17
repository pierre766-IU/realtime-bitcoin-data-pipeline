import os
from collections.abc import Mapping

DEFAULT_STARTING_OFFSETS = "earliest"
DEFAULT_FAIL_ON_DATA_LOSS = "false"


def _resolve_env(env: Mapping[str, str] | None = None) -> Mapping[str, str]:
    return os.environ if env is None else env


def escape_jaas_value(value: str) -> str:
    return value.replace("\\", "\\\\").replace('"', '\\"')


def build_sasl_jaas_config(env: Mapping[str, str] | None = None) -> str | None:
    env_map = _resolve_env(env)
    explicit = env_map.get("KAFKA_SASL_JAAS_CONFIG", "").strip()
    if explicit:
        return explicit

    username = env_map.get("KAFKA_SASL_USERNAME")
    password = env_map.get("KAFKA_SASL_PASSWORD")
    if not username or not password:
        return None

    return (
        "org.apache.kafka.common.security.plain.PlainLoginModule required "
        f'username="{escape_jaas_value(username)}" '
        f'password="{escape_jaas_value(password)}";'
    )


def build_kafka_read_options(
    topic: str,
    bootstrap_servers: str,
    env: Mapping[str, str] | None = None,
) -> dict[str, str]:
    env_map = _resolve_env(env)
    options = {
        "kafka.bootstrap.servers": bootstrap_servers,
        "subscribe": topic,
        "startingOffsets": env_map.get("KAFKA_STARTING_OFFSETS", DEFAULT_STARTING_OFFSETS),
        "failOnDataLoss": env_map.get("KAFKA_FAIL_ON_DATA_LOSS", DEFAULT_FAIL_ON_DATA_LOSS),
    }

    option_map = {
        "kafka.security.protocol": "KAFKA_SECURITY_PROTOCOL",
        "kafka.sasl.mechanism": "KAFKA_SASL_MECHANISM",
        "kafka.ssl.endpoint.identification.algorithm": "KAFKA_SSL_ENDPOINT_IDENTIFICATION_ALGORITHM",
        "maxOffsetsPerTrigger": "KAFKA_MAX_OFFSETS_PER_TRIGGER",
    }

    for option_name, env_name in option_map.items():
        value = env_map.get(env_name)
        if value:
            options[option_name] = value

    sasl_jaas_config = build_sasl_jaas_config(env_map)
    if sasl_jaas_config:
        options["kafka.sasl.jaas.config"] = sasl_jaas_config

    return options


def apply_kafka_options(reader, options: Mapping[str, str]):
    configured_reader = reader
    for option_name, value in options.items():
        configured_reader = configured_reader.option(option_name, value)
    return configured_reader
