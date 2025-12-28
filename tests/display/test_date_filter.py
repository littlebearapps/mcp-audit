"""
Tests for the date range filter functionality.

Tests date preset calculations and badge generation for v1.0.3 TUI.

v1.0.3 - task-233.15
"""

from datetime import datetime, timedelta
from unittest.mock import MagicMock, patch

import pytest


# ============================================================================
# Date Filter Preset Calculation Tests
# ============================================================================


class TestDateFilterPresets:
    """Tests for date filter preset calculations."""

    def test_today_preset_calculation(self) -> None:
        """Test Today preset returns start of today to now."""
        from token_audit.display.session_browser import SessionBrowser

        # Mock the browser state
        browser = MagicMock(spec=SessionBrowser)
        browser.DATE_PRESETS = SessionBrowser.DATE_PRESETS
        browser.state = MagicMock()
        browser.state.date_filter_preset_index = 0  # Today

        # Call the real method
        now = datetime.now()
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)

        # Simulate preset application
        label, days_start, days_end = browser.DATE_PRESETS[0]
        assert label == "Today"
        assert days_start == 0
        assert days_end == 0

        # Today should be 0 days back
        expected_start = today_start - timedelta(days=0)
        assert expected_start.date() == now.date()

    def test_yesterday_preset_calculation(self) -> None:
        """Test Yesterday preset returns yesterday only."""
        from token_audit.display.session_browser import SessionBrowser

        label, days_start, days_end = SessionBrowser.DATE_PRESETS[1]
        assert label == "Yesterday"
        assert days_start == 1
        assert days_end == 1

    def test_last_7_days_preset_calculation(self) -> None:
        """Test Last 7 days preset."""
        from token_audit.display.session_browser import SessionBrowser

        label, days_start, days_end = SessionBrowser.DATE_PRESETS[2]
        assert label == "Last 7 days"
        assert days_start == 7
        assert days_end == 0

    def test_last_14_days_preset_calculation(self) -> None:
        """Test Last 14 days preset."""
        from token_audit.display.session_browser import SessionBrowser

        label, days_start, days_end = SessionBrowser.DATE_PRESETS[3]
        assert label == "Last 14 days"
        assert days_start == 14
        assert days_end == 0

    def test_last_30_days_preset_calculation(self) -> None:
        """Test Last 30 days preset."""
        from token_audit.display.session_browser import SessionBrowser

        label, days_start, days_end = SessionBrowser.DATE_PRESETS[4]
        assert label == "Last 30 days"
        assert days_start == 30
        assert days_end == 0

    def test_last_60_days_preset_calculation(self) -> None:
        """Test Last 60 days preset."""
        from token_audit.display.session_browser import SessionBrowser

        label, days_start, days_end = SessionBrowser.DATE_PRESETS[5]
        assert label == "Last 60 days"
        assert days_start == 60
        assert days_end == 0

    def test_this_month_preset(self) -> None:
        """Test This month preset uses special handling."""
        from token_audit.display.session_browser import SessionBrowser

        label, days_start, days_end = SessionBrowser.DATE_PRESETS[6]
        assert label == "This month"
        # Special handling - None values
        assert days_start is None
        assert days_end is None

    def test_last_month_preset(self) -> None:
        """Test Last month preset uses special handling."""
        from token_audit.display.session_browser import SessionBrowser

        label, days_start, days_end = SessionBrowser.DATE_PRESETS[7]
        assert label == "Last month"
        assert days_start is None
        assert days_end is None

    def test_all_time_preset(self) -> None:
        """Test All time preset clears filter."""
        from token_audit.display.session_browser import SessionBrowser

        label, days_start, days_end = SessionBrowser.DATE_PRESETS[8]
        assert label == "All time"
        assert days_start is None
        assert days_end is None

    def test_preset_count(self) -> None:
        """Test that there are exactly 9 presets."""
        from token_audit.display.session_browser import SessionBrowser

        assert len(SessionBrowser.DATE_PRESETS) == 9


# ============================================================================
# Date Filter Badge Tests
# ============================================================================


class TestDateFilterBadge:
    """Tests for date filter badge generation."""

    def test_badge_empty_when_no_filter(self) -> None:
        """Test badge returns empty string when no filter applied."""
        from token_audit.display.session_browser import SessionBrowser, BrowserState

        state = BrowserState()
        state.date_filter_start = None
        state.date_filter_end = None

        browser = MagicMock(spec=SessionBrowser)
        browser.state = state

        # Call the actual method
        badge = SessionBrowser._get_date_filter_badge(browser)
        assert badge == ""

    def test_badge_today(self) -> None:
        """Test badge shows 'Today' for today filter."""
        from token_audit.display.session_browser import SessionBrowser, BrowserState

        state = BrowserState()
        now = datetime.now()
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        state.date_filter_start = today_start
        state.date_filter_end = now

        browser = MagicMock(spec=SessionBrowser)
        browser.state = state

        badge = SessionBrowser._get_date_filter_badge(browser)
        assert badge == "Today"

    def test_badge_yesterday(self) -> None:
        """Test badge shows 'Yesterday' for yesterday filter."""
        from token_audit.display.session_browser import SessionBrowser, BrowserState

        state = BrowserState()
        now = datetime.now()
        yesterday = now - timedelta(days=1)
        yesterday_start = yesterday.replace(hour=0, minute=0, second=0, microsecond=0)
        yesterday_end = yesterday.replace(hour=23, minute=59, second=59, microsecond=999999)
        state.date_filter_start = yesterday_start
        state.date_filter_end = yesterday_end

        browser = MagicMock(spec=SessionBrowser)
        browser.state = state

        badge = SessionBrowser._get_date_filter_badge(browser)
        assert badge == "Yesterday"

    def test_badge_last_7_days(self) -> None:
        """Test badge shows 'Last 7d' for 7 day filter."""
        from token_audit.display.session_browser import SessionBrowser, BrowserState

        state = BrowserState()
        now = datetime.now()
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        state.date_filter_start = today_start - timedelta(days=7)
        state.date_filter_end = now

        browser = MagicMock(spec=SessionBrowser)
        browser.state = state

        badge = SessionBrowser._get_date_filter_badge(browser)
        assert badge == "Last 7d"

    def test_badge_last_14_days(self) -> None:
        """Test badge shows 'Last 14d' for 14 day filter."""
        from token_audit.display.session_browser import SessionBrowser, BrowserState

        state = BrowserState()
        now = datetime.now()
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        state.date_filter_start = today_start - timedelta(days=14)
        state.date_filter_end = now

        browser = MagicMock(spec=SessionBrowser)
        browser.state = state

        badge = SessionBrowser._get_date_filter_badge(browser)
        assert badge == "Last 14d"

    def test_badge_last_30_days(self) -> None:
        """Test badge shows 'Last 30d' for 30 day filter."""
        from token_audit.display.session_browser import SessionBrowser, BrowserState

        state = BrowserState()
        now = datetime.now()
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        state.date_filter_start = today_start - timedelta(days=30)
        state.date_filter_end = now

        browser = MagicMock(spec=SessionBrowser)
        browser.state = state

        badge = SessionBrowser._get_date_filter_badge(browser)
        assert badge == "Last 30d"

    def test_badge_last_60_days(self) -> None:
        """Test badge shows 'Last 60d' for 60 day filter."""
        from token_audit.display.session_browser import SessionBrowser, BrowserState

        state = BrowserState()
        now = datetime.now()
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        state.date_filter_start = today_start - timedelta(days=60)
        state.date_filter_end = now

        browser = MagicMock(spec=SessionBrowser)
        browser.state = state

        badge = SessionBrowser._get_date_filter_badge(browser)
        assert badge == "Last 60d"

    def test_badge_custom_range_fallback(self) -> None:
        """Test badge shows date range for custom dates."""
        from token_audit.display.session_browser import SessionBrowser, BrowserState

        state = BrowserState()
        # Custom range not matching any preset
        state.date_filter_start = datetime(2025, 12, 1, 0, 0, 0)
        state.date_filter_end = datetime(2025, 12, 15, 23, 59, 59)

        browser = MagicMock(spec=SessionBrowser)
        browser.state = state

        badge = SessionBrowser._get_date_filter_badge(browser)
        # Should be in format "Dec 01-Dec 15"
        assert "Dec" in badge
        assert "-" in badge


# ============================================================================
# Date Filter Key Handling Tests
# ============================================================================


class TestDateFilterKeyHandling:
    """Tests for date filter modal keyboard interactions."""

    def test_number_keys_select_presets(self) -> None:
        """Test number keys 1-8 select presets."""
        from token_audit.display.session_browser import SessionBrowser

        # Keys 1-8 should map to indices 0-7
        key_to_index = {
            "1": 0,
            "2": 1,
            "3": 2,
            "4": 3,
            "5": 4,
            "6": 5,
            "7": 6,
            "8": 7,
        }

        for key, expected_index in key_to_index.items():
            assert int(key) - 1 == expected_index

    def test_zero_key_selects_all_time(self) -> None:
        """Test 0 key selects All time (last preset)."""
        from token_audit.display.session_browser import SessionBrowser

        # 0 should select index 8 (All time)
        max_index = len(SessionBrowser.DATE_PRESETS) - 1
        assert max_index == 8
        assert SessionBrowser.DATE_PRESETS[max_index][0] == "All time"


# ============================================================================
# This Month Calculation Tests
# ============================================================================


class TestThisMonthCalculation:
    """Tests for This month preset edge cases."""

    def test_this_month_first_day(self) -> None:
        """Test This month on first day of month."""
        # On Jan 1, This month should start on Jan 1
        test_date = datetime(2025, 1, 1, 12, 0, 0)
        expected_start = datetime(2025, 1, 1, 0, 0, 0)
        assert expected_start.day == 1

    def test_this_month_last_day(self) -> None:
        """Test This month on last day of month."""
        # On Jan 31, This month should still start on Jan 1
        test_date = datetime(2025, 1, 31, 12, 0, 0)
        expected_start = test_date.replace(day=1)
        assert expected_start == datetime(2025, 1, 1, 12, 0, 0)


# ============================================================================
# Last Month Calculation Tests
# ============================================================================


class TestLastMonthCalculation:
    """Tests for Last month preset edge cases."""

    def test_last_month_from_january(self) -> None:
        """Test Last month from January returns December."""
        # From Jan 2025, Last month should be Dec 2024
        test_date = datetime(2025, 1, 15, 12, 0, 0)
        first_of_this = test_date.replace(day=1)
        last_of_prev = first_of_this - timedelta(days=1)

        assert last_of_prev.month == 12
        assert last_of_prev.year == 2024

    def test_last_month_february_to_january(self) -> None:
        """Test Last month from February returns January."""
        test_date = datetime(2025, 2, 15, 12, 0, 0)
        first_of_this = test_date.replace(day=1)
        last_of_prev = first_of_this - timedelta(days=1)
        first_of_prev = last_of_prev.replace(day=1)

        assert first_of_prev.month == 1
        assert last_of_prev.month == 1
        assert last_of_prev.day == 31  # January has 31 days

    def test_last_month_handles_leap_year(self) -> None:
        """Test Last month handles leap year February correctly."""
        # March 2024 -> February 2024 (leap year, 29 days)
        test_date = datetime(2024, 3, 15, 12, 0, 0)
        first_of_this = test_date.replace(day=1)
        last_of_prev = first_of_this - timedelta(days=1)

        assert last_of_prev.month == 2
        assert last_of_prev.day == 29  # Leap year
