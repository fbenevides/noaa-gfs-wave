from datetime import date

import pytest

from scripts.release import (
    bump_version,
    format_changelog_section,
    parse_commits,
)


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
    def test_groups_by_type(self):
        log = "feat: add foo\nfix: bar\nchore: baz"
        assert parse_commits(log) == {
            "feat": ["add foo"],
            "fix": ["bar"],
            "chore": ["baz"],
        }

    def test_ignores_non_conventional_lines(self):
        log = "feat: add foo\nsomething weird\nfix: bar"
        assert parse_commits(log) == {"feat": ["add foo"], "fix": ["bar"]}

    def test_empty_log_returns_empty_dict(self):
        assert parse_commits("") == {}

    def test_groups_multiple_entries_of_same_type(self):
        log = "feat: one\nfeat: two"
        assert parse_commits(log) == {"feat": ["one", "two"]}


class TestFormatChangelogSection:
    ON = date(2026, 4, 19)

    def test_header_format(self):
        output = format_changelog_section("0.1.1", self.ON, {"feat": ["add thing"]})
        assert output.startswith("## [0.1.1] - 2026-04-19")

    def test_feat_goes_under_added(self):
        output = format_changelog_section("0.1.1", self.ON, {"feat": ["add thing"]})
        assert "### Added\n\n- add thing" in output

    def test_fix_goes_under_fixed(self):
        output = format_changelog_section("0.1.1", self.ON, {"fix": ["correct bug"]})
        assert "### Fixed\n\n- correct bug" in output

    def test_chore_goes_under_changed(self):
        output = format_changelog_section("0.1.1", self.ON, {"chore": ["bump deps"]})
        assert "### Changed\n\n- bump deps" in output

    def test_test_commits_are_skipped(self):
        output = format_changelog_section("0.1.1", self.ON, {"test": ["add tests"]})
        assert "add tests" not in output

    def test_empty_types_are_omitted(self):
        output = format_changelog_section("0.1.1", self.ON, {"feat": ["x"]})
        assert "### Fixed" not in output
        assert "### Changed" not in output
