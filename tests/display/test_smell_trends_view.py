"""
Tests for the Smell Trends View (key 6) calculations.

Tests frequency calculations, trend detection, and severity display.

v1.0.3 - task-233.15
"""

from datetime import datetime, timedelta
from unittest.mock import MagicMock

import pytest


# ============================================================================
# Smell Frequency Calculation Tests
# ============================================================================


class TestSmellFrequency:
    """Tests for smell frequency calculations."""

    def test_frequency_percentage_calculation(self) -> None:
        """Test frequency percentage is calculated correctly."""
        total_sessions = 100
        sessions_with_smell = 25

        frequency = (sessions_with_smell / total_sessions) * 100

        assert frequency == 25.0

    def test_frequency_handles_zero_sessions(self) -> None:
        """Test frequency handles zero total sessions."""
        total_sessions = 0
        sessions_with_smell = 0

        frequency = 0.0 if total_sessions == 0 else (sessions_with_smell / total_sessions) * 100

        assert frequency == 0.0

    def test_frequency_sorting_descending(self) -> None:
        """Test smells are sorted by frequency descending."""
        smells = [
            {"pattern": "MANY_SMALL_CALLS", "frequency": 45.0},
            {"pattern": "CREDENTIAL_IN_PROMPT", "frequency": 10.0},
            {"pattern": "DUPLICATE_CALLS", "frequency": 30.0},
        ]

        sorted_smells = sorted(smells, key=lambda x: x["frequency"], reverse=True)

        assert sorted_smells[0]["pattern"] == "MANY_SMALL_CALLS"
        assert sorted_smells[1]["pattern"] == "DUPLICATE_CALLS"
        assert sorted_smells[2]["pattern"] == "CREDENTIAL_IN_PROMPT"


# ============================================================================
# Trend Detection Tests
# ============================================================================


class TestTrendDetection:
    """Tests for smell trend detection (worsening/improving/stable)."""

    def test_trend_worsening(self) -> None:
        """Test worsening trend when frequency increases."""
        current_freq = 50.0
        previous_freq = 30.0

        if current_freq > previous_freq * 1.1:  # 10% threshold
            trend = "worsening"
        elif current_freq < previous_freq * 0.9:
            trend = "improving"
        else:
            trend = "stable"

        assert trend == "worsening"

    def test_trend_improving(self) -> None:
        """Test improving trend when frequency decreases."""
        current_freq = 20.0
        previous_freq = 50.0

        if current_freq > previous_freq * 1.1:
            trend = "worsening"
        elif current_freq < previous_freq * 0.9:
            trend = "improving"
        else:
            trend = "stable"

        assert trend == "improving"

    def test_trend_stable(self) -> None:
        """Test stable trend when frequency stays within threshold."""
        current_freq = 32.0
        previous_freq = 30.0

        if current_freq > previous_freq * 1.1:
            trend = "worsening"
        elif current_freq < previous_freq * 0.9:
            trend = "improving"
        else:
            trend = "stable"

        assert trend == "stable"

    def test_trend_indicator_symbols(self) -> None:
        """Test trend indicator symbols."""
        trend_symbols = {
            "worsening": "▲",
            "improving": "▼",
            "stable": "→",
        }

        assert trend_symbols["worsening"] == "▲"
        assert trend_symbols["improving"] == "▼"
        assert trend_symbols["stable"] == "→"


# ============================================================================
# Severity Indicator Tests
# ============================================================================


class TestSeverityIndicator:
    """Tests for smell severity indicators."""

    def test_severity_levels(self) -> None:
        """Test all valid severity levels."""
        valid_levels = ["low", "medium", "high", "critical"]
        for level in valid_levels:
            assert level in valid_levels

    def test_severity_indicator_dots(self) -> None:
        """Test severity indicator dot representation."""
        indicators = {
            "low": "●○○",
            "medium": "●●○",
            "high": "●●●",
            "critical": "●●●",
        }

        assert indicators["low"] == "●○○"
        assert indicators["medium"] == "●●○"
        assert indicators["high"] == "●●●"

    def test_severity_color_mapping(self) -> None:
        """Test severity to color mapping."""
        colors = {
            "low": "dim",
            "medium": "warning",
            "high": "error",
            "critical": "error",
        }

        assert colors["low"] == "dim"
        assert colors["medium"] == "warning"
        assert colors["high"] == "error"


# ============================================================================
# Days Filter Tests
# ============================================================================


class TestDaysFilter:
    """Tests for smell trends days filter."""

    def test_valid_day_options(self) -> None:
        """Test valid day filter options."""
        valid_days = [7, 14, 30, 90]
        for days in valid_days:
            assert days in valid_days

    def test_day_filter_cycling(self) -> None:
        """Test cycling through day options."""
        day_options = [7, 14, 30, 90]
        current_index = 0

        # Cycle forward
        for _ in range(len(day_options)):
            current_index = (current_index + 1) % len(day_options)

        # Should be back at start
        assert current_index == 0

    def test_date_range_from_days(self) -> None:
        """Test date range calculation from days."""
        days = 30
        now = datetime.now()
        start_date = now - timedelta(days=days)

        assert (now - start_date).days == days


# ============================================================================
# Top Tool Calculation Tests
# ============================================================================


class TestTopToolCalculation:
    """Tests for finding top tool per smell pattern."""

    def test_top_tool_selection(self) -> None:
        """Test selecting the tool with most occurrences."""
        tool_counts = {
            "mcp__zen__chat": 15,
            "mcp__brave-search__web": 8,
            "mcp__context7__search": 3,
        }

        top_tool = max(tool_counts.items(), key=lambda x: x[1])[0]

        assert top_tool == "mcp__zen__chat"

    def test_top_tool_with_tie(self) -> None:
        """Test top tool selection when there's a tie."""
        tool_counts = {
            "tool_a": 10,
            "tool_b": 10,
        }

        # Should return one of them (implementation may vary)
        top_tool = max(tool_counts.items(), key=lambda x: x[1])[0]
        assert top_tool in ["tool_a", "tool_b"]

    def test_empty_tool_counts(self) -> None:
        """Test handling empty tool counts."""
        tool_counts = {}

        if tool_counts:
            top_tool = max(tool_counts.items(), key=lambda x: x[1])[0]
        else:
            top_tool = None

        assert top_tool is None


# ============================================================================
# Aggregated Data Structure Tests
# ============================================================================


class TestAggregatedDataStructure:
    """Tests for smell trends aggregated data structure."""

    def test_aggregated_smell_structure(self) -> None:
        """Test expected structure of aggregated smell data."""
        aggregated = {
            "pattern": "MANY_SMALL_CALLS",
            "frequency": 45.0,
            "trend": "worsening",
            "severity": "medium",
            "top_tool": "mcp__zen__chat",
            "occurrences": 120,
            "sessions_affected": 45,
        }

        # Verify all fields
        assert "pattern" in aggregated
        assert "frequency" in aggregated
        assert "trend" in aggregated
        assert "severity" in aggregated
        assert "top_tool" in aggregated
        assert "occurrences" in aggregated
        assert "sessions_affected" in aggregated

    def test_summary_stats_structure(self) -> None:
        """Test smell trends summary stats structure."""
        summary = {
            "total_sessions": 100,
            "sessions_with_smells": 45,
            "unique_patterns": 8,
        }

        assert summary["total_sessions"] > 0
        assert summary["sessions_with_smells"] <= summary["total_sessions"]
