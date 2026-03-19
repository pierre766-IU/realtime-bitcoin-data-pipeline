import os
from collections.abc import Mapping


def build_path(base: str, *parts: str) -> str:
    return "/".join([base.rstrip("/")] + [part.strip("/") for part in parts if part])


def configure_abfs_shared_key(spark, env: Mapping[str, str] | None = None) -> None:
    env_map = os.environ if env is None else env
    account_name = env_map.get("STORAGE_ACCOUNT_NAME", "").strip()
    account_key = env_map.get("STORAGE_ACCOUNT_KEY", "").strip()

    if not account_name or not account_key:
        return

    spark.conf.set(
        f"fs.azure.account.auth.type.{account_name}.dfs.core.windows.net",
        "SharedKey",
    )
    spark.conf.set(
        f"fs.azure.account.key.{account_name}.dfs.core.windows.net",
        account_key,
    )
