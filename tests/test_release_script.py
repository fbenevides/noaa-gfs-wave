from datetime import date

import pytest

from scripts.release import (
    Commit,
    bump_version,
    format_changelog_section,
    parse_commits,
)

REPO_URL = "https://github.com/fbenevides/noaa-gfs-wave"


class TestBumpVersion:
    def test_patch_increments_patch(self):
        assert bump_version("0.1.0", "patch") == "0.1.1"

    def test_minor_increments_minor_and_resets_patch(self):
        assert bump_version("0.1.5", "minor") == "0.2.0"

    def test_major_increments_major_and_resets_others(self):
        assert bump_version("1.5.7", "major") == "2.0.0"

    def test_unknown_kind_raises(self):
        with pytest.raises(ValueError):
            bump_version("0.1.0", "weird")


class TestParseCommits:
    def test_groups_by_type_with_sha_and_author(self):
        log = "abc1234\tfbenevides\tfeat: add foo\ndef5678\talice\tfix: bar"
        assert parse_commits(log) == {
            "feat": [Commit(sha="abc1234", author="fbenevides", subject="add foo")],
            "fix": [Commit(sha="def5678", author="alice", subject="bar")],
        }

    def test_ignores_non_conventional_subject(self):
        log = "abc1234\tfbenevides\tfeat: add foo\n1111111\tbob\tsomething weird"
        assert parse_commits(log) == {
            "feat": [Commit(sha="abc1234", author="fbenevides", subject="add foo")],
        }

    def test_ignores_lines_without_three_fields(self):
        log = "abc1234\tfbenevides\tfeat: ok\nmalformed line"
        assert parse_commits(log) == {
            "feat": [Commit(sha="abc1234", author="fbenevides", subject="ok")],
        }

    def test_empty_log_returns_empty_dict(self):
        assert parse_commits("") == {}

    def test_groups_multiple_entries_of_same_type(self):
        log = "abc1234\tfbenevides\tfeat: one\ndef5678\tfbenevides\tfeat: two"
        assert parse_commits(log) == {
            "feat": [
                Commit(sha="abc1234", author="fbenevides", subject="one"),
                Commit(sha="def5678", author="fbenevides", subject="two"),
            ],
        }


class TestFormatChangelogSection:
    ON = date(2026, 4, 19)

    def _commits(self, ctype: str, *commits: Commit) -> dict[str, list[Commit]]:
        return {ctype: list(commits)}

    def test_header_format(self):
        commits = self._commits(
            "feat", Commit(sha="abc1234", author="fbenevides", subject="add thing")
        )
        output = format_changelog_section("0.1.1", self.ON, commits, repo_url=REPO_URL)
        assert output.startswith("## [0.1.1] - 2026-04-19")

    def test_feat_goes_under_added(self):
        commits = self._commits(
            "feat", Commit(sha="abc1234", author="fbenevides", subject="add thing")
        )
        output = format_changelog_section("0.1.1", self.ON, commits, repo_url=REPO_URL)
        assert "### Added" in output
        assert "add thing" in output

    def test_fix_goes_under_fixed(self):
        commits = self._commits(
            "fix", Commit(sha="def5678", author="fbenevides", subject="correct bug")
        )
        output = format_changelog_section("0.1.1", self.ON, commits, repo_url=REPO_URL)
        assert "### Fixed" in output
        assert "correct bug" in output

    def test_chore_goes_under_changed(self):
        commits = self._commits(
            "chore", Commit(sha="1234abc", author="fbenevides", subject="bump deps")
        )
        output = format_changelog_section("0.1.1", self.ON, commits, repo_url=REPO_URL)
        assert "### Changed" in output
        assert "bump deps" in output

    def test_test_commits_are_skipped(self):
        commits = self._commits(
            "test", Commit(sha="abc1234", author="fbenevides", subject="add tests")
        )
        output = format_changelog_section("0.1.1", self.ON, commits, repo_url=REPO_URL)
        assert "add tests" not in output

    def test_empty_types_are_omitted(self):
        commits = self._commits("feat", Commit(sha="abc1234", author="fbenevides", subject="x"))
        output = format_changelog_section("0.1.1", self.ON, commits, repo_url=REPO_URL)
        assert "### Fixed" not in output
        assert "### Changed" not in output

    def test_entry_renders_sha_link_subject_and_author(self):
        commits = self._commits(
            "feat", Commit(sha="abc1234", author="fbenevides", subject="add foo")
        )
        output = format_changelog_section("0.1.1", self.ON, commits, repo_url=REPO_URL)
        expected_line = (
            "- ([abc1234](https://github.com/fbenevides/noaa-gfs-wave/commit/abc1234)) "
            "add foo by @fbenevides"
        )
        assert expected_line in output

    def test_trailing_slash_on_repo_url_does_not_double_up(self):
        commits = self._commits(
            "feat", Commit(sha="abc1234", author="fbenevides", subject="add foo")
        )
        output = format_changelog_section("0.1.1", self.ON, commits, repo_url=REPO_URL + "/")
        assert "commit//abc1234" not in output
        assert "/commit/abc1234" in output
