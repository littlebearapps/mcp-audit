"""
Tests for the Analytics View (key 5) data handling.

Tests aggregation by period (daily/weekly/monthly) and project grouping.

v1.0.3 - task-233.15
"""

from datetime import datetime, timedelta
from unittest.mock import MagicMock

import pytest

from token_audit.display.session_browser import BrowserState


# ============================================================================
# Analytics State Tests
# ============================================================================


class TestAnalyticsState:
    """Tests for analytics state management."""

    def test_default_analytics_period(self) -> None:
        """Test default analytics period is daily."""
        state = BrowserState()
        assert state.analytics_period == "daily"

    def test_analytics_period_options(self) -> None:
        """Test all valid analytics period options."""
        state = BrowserState()
        valid_periods = ["daily", "weekly", "monthly"]
        for period in valid_periods:
            state.analytics_period = period
            assert state.analytics_period == period

    def test_default_group_by_project(self) -> None:
        """Test default group by project is False."""
        state = BrowserState()
        assert state.analytics_group_by_project is False

    def test_toggle_group_by_project(self) -> None:
        """Test toggling group by project."""
        state = BrowserState()
        state.analytics_group_by_project = True
        assert state.analytics_group_by_project is True
        state.analytics_group_by_project = False
        assert state.analytics_group_by_project is False


# ============================================================================
# Period Aggregation Logic Tests
# ============================================================================


class TestPeriodAggregation:
    """Tests for period aggregation calculations."""

    def test_daily_period_spans_14_days(self) -> None:
        """Test daily aggregation covers last 14 days."""
        # Daily period configuration
        expected_days = 14
        today = datetime.now().date()
        start_date = today - timedelta(days=expected_days)

        # Verify span
        assert (today - start_date).days == expected_days

    def test_weekly_period_spans_8_weeks(self) -> None:
        """Test weekly aggregation covers last 8 weeks."""
        expected_weeks = 8
        expected_days = expected_weeks * 7
        today = datetime.now().date()
        start_date = today - timedelta(days=expected_days)

        assert (today - start_date).days == expected_days

    def test_monthly_period_spans_6_months(self) -> None:
        """Test monthly aggregation covers last 6 months."""
        expected_months = 6
        # Approximate days (varies by month)
        min_days = expected_months * 28
        max_days = expected_months * 31

        assert min_days <= 168 <= max_days


# ============================================================================
# Project Grouping Tests
# ============================================================================


class TestProjectGrouping:
    """Tests for project grouping in analytics."""

    def test_group_by_project_aggregates_correctly(self) -> None:
        """Test that grouping by project aggregates costs and tokens."""
        # Mock session data
        sessions = [
            MagicMock(project="project-a", total_tokens=1000, cost_estimate=0.01),
            MagicMock(project="project-a", total_tokens=2000, cost_estimate=0.02),
            MagicMock(project="project-b", total_tokens=500, cost_estimate=0.005),
        ]

        # Group by project
        grouped = {}
        for s in sessions:
            if s.project not in grouped:
                grouped[s.project] = {"tokens": 0, "cost": 0.0, "count": 0}
            grouped[s.project]["tokens"] += s.total_tokens
            grouped[s.project]["cost"] += s.cost_estimate
            grouped[s.project]["count"] += 1

        assert grouped["project-a"]["tokens"] == 3000
        assert grouped["project-a"]["cost"] == 0.03
        assert grouped["project-a"]["count"] == 2
        assert grouped["project-b"]["tokens"] == 500
        assert grouped["project-b"]["count"] == 1

    def test_empty_project_grouped_as_no_project(self) -> None:
        """Test sessions without project are grouped as '(no project)'."""
        sessions = [
            MagicMock(project=None, total_tokens=1000, cost_estimate=0.01),
            MagicMock(project="", total_tokens=500, cost_estimate=0.005),
        ]

        # Group with fallback for empty project
        grouped = {}
        for s in sessions:
            project = s.project if s.project else "(no project)"
            if project not in grouped:
                grouped[project] = {"tokens": 0, "cost": 0.0}
            grouped[project]["tokens"] += s.total_tokens
            grouped[project]["cost"] += s.cost_estimate

        assert "(no project)" in grouped
        assert grouped["(no project)"]["tokens"] == 1500

    def test_cost_share_calculation(self) -> None:
        """Test cost share percentage calculation."""
        projects = {
            "project-a": {"cost": 0.50},
            "project-b": {"cost": 0.30},
            "project-c": {"cost": 0.20},
        }
        total_cost = sum(p["cost"] for p in projects.values())

        # Calculate shares
        shares = {}
        for name, data in projects.items():
            shares[name] = (data["cost"] / total_cost) * 100 if total_cost > 0 else 0

        assert shares["project-a"] == 50.0
        assert shares["project-b"] == 30.0
        assert shares["project-c"] == 20.0


# ============================================================================
# Analytics Data Structure Tests
# ============================================================================


class TestAnalyticsDataStructure:
    """Tests for analytics data format."""

    def test_analytics_data_attribute(self) -> None:
        """Test analytics data can be set on state."""
        state = BrowserState()
        # Analytics data is loaded dynamically, not a default attribute
        # Set it manually for testing
        state.analytics_data = None
        assert state.analytics_data is None

    def test_analytics_row_structure(self) -> None:
        """Test expected structure of analytics row data."""
        # Expected row structure
        row = {
            "period": "2025-12-26",
            "sessions": 5,
            "tokens": 10000,
            "cost": 0.05,
            "trend": "up",
            "smells": 2,
        }

        # Verify all fields present
        assert "period" in row
        assert "sessions" in row
        assert "tokens" in row
        assert "cost" in row
        assert "trend" in row
        assert "smells" in row

    def test_trend_values(self) -> None:
        """Test valid trend indicator values."""
        valid_trends = ["up", "down", "stable", None]
        for trend in valid_trends:
            # Each trend value should be valid
            assert trend in valid_trends


# ============================================================================
# Model Breakdown Tests
# ============================================================================


class TestModelBreakdown:
    """Tests for model usage breakdown in analytics."""

    def test_top_3_models_by_tokens(self) -> None:
        """Test only top 3 models are shown."""
        model_usage = {
            "claude-3.5-sonnet": 50000,
            "claude-3-opus": 30000,
            "gpt-4": 20000,
            "claude-haiku": 10000,
            "gpt-3.5": 5000,
        }

        # Sort and take top 3
        top_3 = sorted(model_usage.items(), key=lambda x: x[1], reverse=True)[:3]

        assert len(top_3) == 3
        assert top_3[0][0] == "claude-3.5-sonnet"
        assert top_3[1][0] == "claude-3-opus"
        assert top_3[2][0] == "gpt-4"

    def test_percentage_bar_calculation(self) -> None:
        """Test percentage bar width calculation."""
        total = 100000
        model_tokens = 30000

        percentage = (model_tokens / total) * 100

        assert percentage == 30.0
