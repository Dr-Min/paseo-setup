import os


def safe_join(base_dir: str, user_path: str) -> str:
    """base_dir 아래에 있는 사용자 제공 경로를 절대 경로로 해석해 반환한다.
    결과가 base_dir 바깥을 가리키면 ValueError를 발생시킨다.
    """
    base = os.path.realpath(base_dir)
    candidate = os.path.realpath(os.path.join(base, user_path))

    try:
        is_within_base = os.path.commonpath((base, candidate)) == base
    except ValueError as exc:
        raise ValueError("path escapes base directory") from exc

    if not is_within_base:
        raise ValueError("path escapes base directory")

    return candidate
