def build_path(base: str, *parts: str) -> str:
    return "/".join([base.rstrip("/")] + [part.strip("/") for part in parts if part])
