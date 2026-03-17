import os
from collections.abc import Callable, Mapping
from typing import Any

TRUE_VALUES = {"1", "true", "yes", "on"}


def _resolve_env(env: Mapping[str, str] | None = None) -> Mapping[str, str]:
    return os.environ if env is None else env


def _parse_bool(value: str, default: bool) -> bool:
    if value is None:
        return default
    return value.strip().lower() in TRUE_VALUES


def build_producer_config(
    *,
    bootstrap_servers: str,
    value_serializer: Callable[[Any], bytes],
    env: Mapping[str, str] | None = None,
    **overrides: Any,
) -> dict[str, Any]:
    env_map = _resolve_env(env)
    config: dict[str, Any] = {
        "bootstrap_servers": bootstrap_servers,
        "value_serializer": value_serializer,
    }

    option_map = {
        "security_protocol": "KAFKA_SECURITY_PROTOCOL",
        "sasl_mechanism": "KAFKA_SASL_MECHANISM",
        "sasl_plain_username": "KAFKA_SASL_USERNAME",
        "sasl_plain_password": "KAFKA_SASL_PASSWORD",
    }

    for option_name, env_name in option_map.items():
        value = env_map.get(env_name)
        if value:
            config[option_name] = value

    ssl_check_hostname = env_map.get("KAFKA_SSL_CHECK_HOSTNAME")
    if ssl_check_hostname is not None:
        config["ssl_check_hostname"] = _parse_bool(ssl_check_hostname, default=True)

    config.update(overrides)
    return config
