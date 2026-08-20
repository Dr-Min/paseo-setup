import os


def safe_join(base_dir: str, user_path: str) -> str:
    """Resolve user_path beneath base_dir and return its absolute path."""
    if "\x00" in base_dir or "\x00" in user_path:
        raise ValueError("paths must not contain null bytes")

    base = os.path.realpath(os.path.abspath(base_dir))
    candidate = os.path.realpath(os.path.join(base, user_path))

    try:
        contained = os.path.commonpath((base, candidate)) == base
    except ValueError:
        contained = False

    if not contained:
        raise ValueError("path escapes base directory")

    return candidate
