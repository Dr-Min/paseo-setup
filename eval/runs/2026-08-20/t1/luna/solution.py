"""Semantic Versioning 2.0.0 comparison."""


def _is_ascii_digit_string(value: str) -> bool:
    return bool(value) and all("0" <= char <= "9" for char in value)


def _is_identifier(value: str) -> bool:
    return bool(value) and all(
        ("0" <= char <= "9")
        or ("A" <= char <= "Z")
        or ("a" <= char <= "z")
        or char == "-"
        for char in value
    )


def _parse(version: str) -> tuple[tuple[str, str, str], list[str] | None]:
    if not isinstance(version, str) or version.count("+") > 1:
        raise ValueError("invalid semantic version")

    core_and_pre, separator, build = version.partition("+")
    if separator:
        build_identifiers = build.split(".")
        if not all(_is_identifier(identifier) for identifier in build_identifiers):
            raise ValueError("invalid semantic version")

    core, separator, pre_release = core_and_pre.partition("-")
    core_parts = core.split(".")
    if len(core_parts) != 3:
        raise ValueError("invalid semantic version")
    if not all(
        _is_ascii_digit_string(part) and (len(part) == 1 or part[0] != "0")
        for part in core_parts
    ):
        raise ValueError("invalid semantic version")

    if not separator:
        return (core_parts[0], core_parts[1], core_parts[2]), None

    pre_identifiers = pre_release.split(".")
    if not all(_is_identifier(identifier) for identifier in pre_identifiers):
        raise ValueError("invalid semantic version")
    if any(
        _is_ascii_digit_string(identifier)
        and len(identifier) > 1
        and identifier[0] == "0"
        for identifier in pre_identifiers
    ):
        raise ValueError("invalid semantic version")

    return (core_parts[0], core_parts[1], core_parts[2]), pre_identifiers


def _compare_decimal_strings(a: str, b: str) -> int:
    if len(a) != len(b):
        return -1 if len(a) < len(b) else 1
    if a == b:
        return 0
    return -1 if a < b else 1


def _compare_pre_release(a: list[str], b: list[str]) -> int:
    for left, right in zip(a, b):
        left_is_numeric = _is_ascii_digit_string(left)
        right_is_numeric = _is_ascii_digit_string(right)

        if left_is_numeric and right_is_numeric:
            result = _compare_decimal_strings(left, right)
        elif left_is_numeric != right_is_numeric:
            result = -1 if left_is_numeric else 1
        elif left == right:
            result = 0
        else:
            result = -1 if left < right else 1

        if result:
            return result

    if len(a) == len(b):
        return 0
    return -1 if len(a) < len(b) else 1


def compare(a: str, b: str) -> int:
    """Compare two Semantic Versioning 2.0.0 version strings."""
    a_core, a_pre_release = _parse(a)
    b_core, b_pre_release = _parse(b)

    for left, right in zip(a_core, b_core):
        result = _compare_decimal_strings(left, right)
        if result:
            return result

    if a_pre_release is None and b_pre_release is None:
        return 0
    if a_pre_release is None:
        return 1
    if b_pre_release is None:
        return -1
    return _compare_pre_release(a_pre_release, b_pre_release)
