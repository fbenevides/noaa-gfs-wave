from datetime import UTC, datetime

from noaa_gfs_wave import NOAA_CYCLES, latest_available_cycle


class TestNoaaCycle:
    def test_noaa_cycles_are_six_hourly(self):
        assert NOAA_CYCLES == [0, 6, 12, 18]

    def test_returns_tuple_of_datetime_and_int(self):
        now = datetime(2026, 3, 24, 23, 0, 0, tzinfo=UTC)
        cycle_time, cycle = latest_available_cycle(now)
        assert isinstance(cycle_time, datetime)
        assert isinstance(cycle, int)

    def test_cycle_is_valid_noaa_cycle(self):
        now = datetime(2026, 3, 24, 23, 0, 0, tzinfo=UTC)
        _, cycle = latest_available_cycle(now)
        assert cycle in NOAA_CYCLES

    def test_cycle_time_aligns_with_cycle(self):
        now = datetime(2026, 3, 24, 23, 0, 0, tzinfo=UTC)
        cycle_time, cycle = latest_available_cycle(now)
        assert cycle_time.hour == cycle
        assert cycle_time.minute == 0
        assert cycle_time.second == 0

    def test_returns_cycle_far_enough_in_past(self):
        # At 23:00 UTC the 12z cycle (12+9=21 <= 23) should be available
        now = datetime(2026, 3, 24, 23, 0, 0, tzinfo=UTC)
        cycle_time, _ = latest_available_cycle(now)
        assert cycle_time <= now

    def test_publication_lag_respected(self):
        # At 20:00 UTC the 18z cycle is NOT yet published (18+9=27 > 20)
        # but the 12z cycle is (12+9=21 > 20 — also not published)
        # so the 6z cycle should be returned (6+9=15 <= 20)
        now = datetime(2026, 3, 24, 20, 0, 0, tzinfo=UTC)
        _, cycle = latest_available_cycle(now)
        assert cycle == 6

    def test_exact_publication_boundary(self):
        # At exactly 21:00 UTC the 12z cycle is just published (12+9=21 <= 21)
        now = datetime(2026, 3, 24, 21, 0, 0, tzinfo=UTC)
        _, cycle = latest_available_cycle(now)
        assert cycle == 12

    def test_raises_for_normal_time(self):
        # Should not raise for a valid datetime
        now = datetime(2026, 3, 24, 12, 0, 0, tzinfo=UTC)
        cycle_time, cycle = latest_available_cycle(now)
        assert cycle_time is not None

    def test_uses_current_time_when_none_passed(self):
        # Should work without argument (uses datetime.now(UTC))
        cycle_time, cycle = latest_available_cycle()
        assert cycle in NOAA_CYCLES
        assert isinstance(cycle_time, datetime)
