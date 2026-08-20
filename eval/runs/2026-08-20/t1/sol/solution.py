import re


_VERSION_RE = re.compile(
    r"""
    (?P<major>0|[1-9][0-9]*)
    \.
    (?P<minor>0|[1-9][0-9]*)
    \.
    (?P<patch>0|[1-9][0-9]*)
    (?:-
        (?P<prerelease>
            (?:0|[1-9][0-9]*|[0-9A-Za-z-]*[A-Za-z-][0-9A-Za-z-]*)
            (?:\.(?:0|[1-9][0-9]*|[0-9A-Za-z-]*[A-Za-z-][0-9A-Za-z-]*))*
        )
    )?
    (?:\+
        (?P<build>[0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*)
    )?
    """,
    re.VERBOSE,
)


def _parse(version: str):
    if not isinstance(version, str):
        raise ValueError("version must be a string")

    match = _VERSION_RE.fullmatch(version)
    if match is None:
        raise ValueError(f"invalid semantic version: {version!r}")

    core = (
        int(match.group("major")),
        int(match.group("minor")),
        int(match.group("patch")),
    )
    prerelease_text = match.group("prerelease")
    prerelease = None if prerelease_text is None else tuple(prerelease_text.split("."))
    return core, prerelease


def _compare_prerelease(a, b):
    for left, right in zip(a, b):
        if left == right:
            continue

        left_is_numeric = left.isdigit()
        right_is_numeric = right.isdigit()
        if left_is_numeric and right_is_numeric:
            return -1 if int(left) < int(right) else 1
        if left_is_numeric:
            return -1
        if right_is_numeric:
            return 1
        return -1 if left < right else 1

    if len(a) == len(b):
        return 0
    return -1 if len(a) < len(b) else 1


def compare(a: str, b: str) -> int:
    """SemVer 2.0.0 버전 문자열 두 개를 비교한다.

    a < b 이면 -1, a == b 이면 0, a > b 이면 1을 반환한다.
    유효하지 않은 버전 문자열이면 ValueError를 발생시킨다.
    """
    a_core, a_prerelease = _parse(a)
    b_core, b_prerelease = _parse(b)

    if a_core != b_core:
        return -1 if a_core < b_core else 1

    if a_prerelease is None:
        return 0 if b_prerelease is None else 1
    if b_prerelease is None:
        return -1
    return _compare_prerelease(a_prerelease, b_prerelease)
