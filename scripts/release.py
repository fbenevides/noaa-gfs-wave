from datetime import date


def bump_version(current: str, bump: str) -> str:
    raise NotImplementedError


def parse_commits(log: str) -> dict[str, list[str]]:
    raise NotImplementedError


def format_changelog_section(
    version: str, on: date, commits: dict[str, list[str]]
) -> str:
    raise NotImplementedError
