#!/usr/bin/env python3
"""Release helper: bump pyproject.toml version and write a CHANGELOG entry from git log.

Usage:
    uv run python scripts/release.py patch
    uv run python scripts/release.py minor
    uv run python scripts/release.py major
    uv run python scripts/release.py 0.2.0
    uv run python scripts/release.py patch --dry-run

After running, manually:
    git add pyproject.toml CHANGELOG.md
    git commit -m "chore: bump version to X.Y.Z"
    git tag vX.Y.Z
    git push origin main --tags
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from dataclasses import dataclass
from datetime import date
from pathlib import Path


@dataclass(frozen=True)
class Commit:
    sha: str
    author: str
    subject: str


REPO_ROOT = Path(__file__).resolve().parent.parent
PYPROJECT = REPO_ROOT / "pyproject.toml"
CHANGELOG = REPO_ROOT / "CHANGELOG.md"

_VERSION_RE = re.compile(r'^version = "(\d+\.\d+\.\d+)"', re.MULTILINE)
_REPO_URL_RE = re.compile(r'^Repository = "([^"]+)"', re.MULTILINE)
_COMMIT_RE = re.compile(r"^([a-z]+): (.+)$")
_SEMVER_RE = re.compile(r"^\d+\.\d+\.\d+$")

_TYPE_TO_SECTION = {"feat": "Added", "fix": "Fixed", "chore": "Changed"}

_BUMP_CHOICES = ("patch", "minor", "major")


def bump_version(current: str, bump: str) -> str:
    major, minor, patch = (int(p) for p in current.split("."))
    if bump == "patch":
        return f"{major}.{minor}.{patch + 1}"
    if bump == "minor":
        return f"{major}.{minor + 1}.0"
    if bump == "major":
        return f"{major + 1}.0.0"
    raise ValueError(f"unknown bump kind: {bump!r}")


def parse_commits(log: str) -> dict[str, list[Commit]]:
    grouped: dict[str, list[Commit]] = {}
    for line in log.splitlines():
        commit = _parse_line(line)
        if commit is None:
            continue
        ctype, parsed = commit
        grouped.setdefault(ctype, []).append(parsed)
    return grouped


def _parse_line(line: str) -> tuple[str, Commit] | None:
    parts = line.split("\t", 2)
    if len(parts) != 3:
        return None
    sha, author, subject = parts
    match = _COMMIT_RE.match(subject)
    if match is None:
        return None
    return match.group(1), Commit(sha=sha, author=author, subject=match.group(2))


def format_changelog_section(
    version: str,
    on: date,
    commits: dict[str, list[Commit]],
    *,
    repo_url: str,
) -> str:
    parts = [_format_type_section(t, commits, repo_url=repo_url) for t in _TYPE_TO_SECTION]
    body = "".join(p for p in parts if p)
    return f"## [{version}] - {on.isoformat()}\n\n{body}"


def _format_type_section(ctype: str, commits: dict[str, list[Commit]], *, repo_url: str) -> str:
    entries = commits.get(ctype, [])
    if not entries:
        return ""
    header = [f"### {_TYPE_TO_SECTION[ctype]}", ""]
    body = [_format_entry(e, repo_url=repo_url) for e in entries]
    return "\n".join(header + body + ["", ""])


def _format_entry(commit: Commit, *, repo_url: str) -> str:
    link = f"{repo_url.rstrip('/')}/commit/{commit.sha}"
    return f"- ([{commit.sha}]({link})) {commit.subject} by @{commit.author}"


def _read_current_version() -> str:
    match = _VERSION_RE.search(PYPROJECT.read_text())
    if match is None:
        raise RuntimeError(f"no version found in {PYPROJECT}")
    return match.group(1)


def _rewrite_version(new_version: str) -> None:
    original = PYPROJECT.read_text()
    updated = _VERSION_RE.sub(f'version = "{new_version}"', original, count=1)
    PYPROJECT.write_text(updated)


def _latest_tag() -> str | None:
    try:
        out = subprocess.check_output(
            ["git", "describe", "--tags", "--abbrev=0"],
            cwd=REPO_ROOT,
            stderr=subprocess.DEVNULL,
        )
    except subprocess.CalledProcessError:
        return None
    return out.decode().strip()


def _git_log_since(tag: str | None) -> str:
    cmd = ["git", "log", "--pretty=format:%h%x09%an%x09%s"]
    if tag is not None:
        cmd.append(f"{tag}..HEAD")
    return subprocess.check_output(cmd, cwd=REPO_ROOT).decode()


def _read_repo_url() -> str:
    match = _REPO_URL_RE.search(PYPROJECT.read_text())
    if match is None:
        raise RuntimeError(f"no Repository URL in {PYPROJECT}")
    return match.group(1)


def _insert_changelog_section(new_section: str) -> None:
    marker = "## [Unreleased]\n"
    original = CHANGELOG.read_text()
    idx = original.find(marker)
    if idx < 0:
        raise RuntimeError("no ## [Unreleased] header in CHANGELOG.md")
    end = idx + len(marker)
    CHANGELOG.write_text(original[:end] + "\n" + new_section + original[end:])


def _resolve_new_version(current: str, arg: str) -> str:
    if arg in _BUMP_CHOICES:
        return bump_version(current, arg)
    if _SEMVER_RE.match(arg):
        return arg
    raise SystemExit(f"invalid argument: {arg!r} (use patch|minor|major or X.Y.Z)")


def _print_summary(current: str, new: str, tag: str | None, section: str, count: int) -> None:
    print(f"current: {current}")
    print(f"new:     {new}")
    print(f"since:   {tag or '(no previous tag — including all commits)'}")
    print(f"entries: {count} commits")
    print()
    print(section)


def _print_next_steps(new_version: str) -> None:
    print("next steps:")
    print("  git add pyproject.toml CHANGELOG.md")
    print(f"  git commit -m 'chore: bump version to {new_version}'")
    print(f"  git tag v{new_version}")
    print("  git push origin main --tags")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Bump version and update CHANGELOG from git log.")
    parser.add_argument("bump", help="patch, minor, major, or an explicit semver like 0.2.0")
    parser.add_argument("--dry-run", action="store_true", help="preview without writing files")
    args = parser.parse_args(argv)

    current = _read_current_version()
    new_version = _resolve_new_version(current, args.bump)
    repo_url = _read_repo_url()
    tag = _latest_tag()
    commits = parse_commits(_git_log_since(tag))
    section = format_changelog_section(new_version, date.today(), commits, repo_url=repo_url)
    count = sum(len(v) for v in commits.values())

    _print_summary(current, new_version, tag, section, count)

    if args.dry_run:
        print("[dry-run] no files written")
        return 0

    _rewrite_version(new_version)
    _insert_changelog_section(section)
    print(f"updated: {PYPROJECT.relative_to(REPO_ROOT)}")
    print(f"updated: {CHANGELOG.relative_to(REPO_ROOT)}")
    print()
    _print_next_steps(new_version)
    return 0


if __name__ == "__main__":
    sys.exit(main())
