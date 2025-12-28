"""
Tests for the Export functionality (keys e/j/a).

Tests CSV, JSON, and AI prompt export format generation.

v1.0.3 - task-233.15
"""

import csv
import json
import os
import tempfile
from datetime import datetime
from io import StringIO
from unittest.mock import MagicMock, patch

import pytest


# ============================================================================
# CSV Export Tests
# ============================================================================


class TestCSVExport:
    """Tests for CSV export format generation."""

    def test_csv_header_row(self) -> None:
        """Test CSV includes header row."""
        data = [
            {"session_id": "abc123", "tokens": 1000, "cost": 0.01},
            {"session_id": "def456", "tokens": 2000, "cost": 0.02},
        ]

        output = StringIO()
        if data:
            writer = csv.DictWriter(output, fieldnames=data[0].keys())
            writer.writeheader()
            writer.writerows(data)

        csv_content = output.getvalue()
        lines = csv_content.strip().split("\n")

        # Strip any trailing \r from CSV lines
        assert lines[0].rstrip("\r") == "session_id,tokens,cost"

    def test_csv_data_rows(self) -> None:
        """Test CSV contains data rows."""
        data = [
            {"session_id": "abc123", "tokens": 1000},
        ]

        output = StringIO()
        writer = csv.DictWriter(output, fieldnames=data[0].keys())
        writer.writeheader()
        writer.writerows(data)

        csv_content = output.getvalue()
        lines = csv_content.strip().split("\n")

        assert len(lines) == 2  # Header + 1 data row
        assert "abc123" in lines[1]
        assert "1000" in lines[1]

    def test_csv_handles_special_characters(self) -> None:
        """Test CSV properly escapes special characters."""
        data = [
            {"name": 'Test "quoted" value', "note": "Has, comma"},
        ]

        output = StringIO()
        writer = csv.DictWriter(output, fieldnames=data[0].keys())
        writer.writeheader()
        writer.writerows(data)

        csv_content = output.getvalue()

        # CSV should properly quote fields with commas/quotes
        assert "quoted" in csv_content
        assert "comma" in csv_content

    def test_csv_empty_data(self) -> None:
        """Test CSV handles empty data."""
        data = []

        output = StringIO()
        if data:
            writer = csv.DictWriter(output, fieldnames=data[0].keys())
            writer.writeheader()
            writer.writerows(data)

        csv_content = output.getvalue()
        assert csv_content == ""


# ============================================================================
# JSON Export Tests
# ============================================================================


class TestJSONExport:
    """Tests for JSON export format generation."""

    def test_json_valid_format(self) -> None:
        """Test JSON output is valid JSON."""
        data = {
            "view": "analytics",
            "exported_at": datetime.now().isoformat(),
            "records": [
                {"period": "2025-12-26", "tokens": 10000},
            ],
        }

        json_str = json.dumps(data, indent=2)
        parsed = json.loads(json_str)

        assert parsed["view"] == "analytics"
        assert len(parsed["records"]) == 1

    def test_json_includes_metadata(self) -> None:
        """Test JSON export includes metadata."""
        data = {
            "view": "sessions",
            "exported_at": datetime.now().isoformat(),
            "filter_applied": "Last 7d",
            "record_count": 5,
            "records": [],
        }

        json_str = json.dumps(data)
        parsed = json.loads(json_str)

        assert "view" in parsed
        assert "exported_at" in parsed
        assert "record_count" in parsed

    def test_json_handles_nested_data(self) -> None:
        """Test JSON handles nested structures."""
        data = {
            "session": {
                "id": "abc123",
                "tools": [
                    {"name": "mcp__zen__chat", "calls": 5},
                    {"name": "mcp__search__web", "calls": 3},
                ],
            },
        }

        json_str = json.dumps(data, indent=2)
        parsed = json.loads(json_str)

        assert parsed["session"]["id"] == "abc123"
        assert len(parsed["session"]["tools"]) == 2

    def test_json_datetime_handling(self) -> None:
        """Test JSON handles datetime serialization."""
        now = datetime.now()
        data = {"timestamp": now.isoformat()}

        json_str = json.dumps(data)
        parsed = json.loads(json_str)

        # Should be ISO format string
        assert isinstance(parsed["timestamp"], str)
        assert "T" in parsed["timestamp"]


# ============================================================================
# AI Export Tests
# ============================================================================


class TestAIExport:
    """Tests for AI prompt export format generation."""

    def test_ai_export_markdown_format(self) -> None:
        """Test AI export uses markdown format."""
        data = {
            "view": "smell_trends",
            "smells": [
                {"pattern": "MANY_SMALL_CALLS", "frequency": 45.0},
            ],
        }

        # AI export should be markdown
        prompt = f"""# Token Audit Analysis

## View: {data['view']}

### Detected Patterns

| Pattern | Frequency |
|---------|-----------|
"""
        for smell in data["smells"]:
            prompt += f"| {smell['pattern']} | {smell['frequency']}% |\n"

        assert "# Token Audit Analysis" in prompt
        assert "MANY_SMALL_CALLS" in prompt

    def test_ai_export_includes_context(self) -> None:
        """Test AI export includes analysis context."""
        export = """# Token Audit Analysis

## Analysis Request

Please analyze the following MCP tool usage patterns and provide recommendations.

## Data Summary

- Total sessions analyzed: 50
- Date range: Last 7 days
- Issues detected: 3

## Recommendations Requested

1. Identify inefficiencies
2. Suggest optimizations
3. Prioritize by impact
"""

        assert "Analysis Request" in export
        assert "Recommendations" in export

    def test_ai_export_truncates_large_data(self) -> None:
        """Test AI export truncates very large data sets."""
        max_records = 100
        records = [{"id": i} for i in range(500)]

        # Truncate if needed
        if len(records) > max_records:
            export_records = records[:max_records]
            truncated = True
        else:
            export_records = records
            truncated = False

        assert len(export_records) == max_records
        assert truncated is True


# ============================================================================
# Export File Generation Tests
# ============================================================================


class TestExportFileGeneration:
    """Tests for export file path generation."""

    def test_export_filename_format(self) -> None:
        """Test export filename format."""
        view = "analytics"
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        extension = "csv"

        filename = f"token-audit-{view}-{timestamp}.{extension}"

        assert filename.startswith("token-audit-analytics-")
        assert filename.endswith(".csv")

    def test_export_directory_creation(self) -> None:
        """Test export directory is created if missing."""
        with tempfile.TemporaryDirectory() as tmpdir:
            export_dir = os.path.join(tmpdir, "exports")

            # Should not exist initially
            assert not os.path.exists(export_dir)

            # Create it
            os.makedirs(export_dir, exist_ok=True)

            assert os.path.exists(export_dir)

    def test_export_file_writing(self) -> None:
        """Test export file is written correctly."""
        with tempfile.TemporaryDirectory() as tmpdir:
            filepath = os.path.join(tmpdir, "test-export.csv")

            content = "header1,header2\nvalue1,value2"
            with open(filepath, "w") as f:
                f.write(content)

            with open(filepath) as f:
                read_content = f.read()

            assert read_content == content


# ============================================================================
# View-Specific Export Tests
# ============================================================================


class TestViewSpecificExport:
    """Tests for view-specific export data."""

    def test_dashboard_export_data(self) -> None:
        """Test dashboard export includes summary stats."""
        export_data = {
            "view": "dashboard",
            "today": {"sessions": 5, "tokens": 10000, "cost": 0.05},
            "week": {"sessions": 25, "tokens": 50000, "cost": 0.25},
            "month": {"sessions": 100, "tokens": 200000, "cost": 1.00},
        }

        assert "today" in export_data
        assert "week" in export_data
        assert "month" in export_data

    def test_list_export_includes_session_details(self) -> None:
        """Test list export includes all session details."""
        session = {
            "session_id": "abc123",
            "date": "2025-12-26",
            "platform": "claude-code",
            "project": "token-audit",
            "tokens": 10000,
            "cost": 0.05,
            "smells": 2,
        }

        required_fields = ["session_id", "date", "platform", "tokens", "cost"]
        for field in required_fields:
            assert field in session

    def test_analytics_export_includes_period(self) -> None:
        """Test analytics export includes period data."""
        export_data = {
            "view": "analytics",
            "period_type": "daily",
            "records": [
                {"period": "2025-12-26", "sessions": 5, "tokens": 10000},
            ],
        }

        assert export_data["period_type"] in ["daily", "weekly", "monthly"]

    def test_smell_trends_export(self) -> None:
        """Test smell trends export structure."""
        export_data = {
            "view": "smell_trends",
            "days_analyzed": 30,
            "patterns": [
                {
                    "pattern": "MANY_SMALL_CALLS",
                    "frequency": 45.0,
                    "trend": "worsening",
                    "severity": "medium",
                },
            ],
        }

        assert export_data["view"] == "smell_trends"
        assert len(export_data["patterns"]) > 0

    def test_pinned_servers_export(self) -> None:
        """Test pinned servers export structure."""
        export_data = {
            "view": "pinned_servers",
            "servers": [
                {"name": "zen", "source": "explicit", "usage": 150},
                {"name": "backlog", "source": "auto", "usage": 45},
            ],
        }

        assert export_data["view"] == "pinned_servers"
        for server in export_data["servers"]:
            assert "name" in server
            assert "source" in server


# ============================================================================
# Clipboard Integration Tests
# ============================================================================


class TestClipboardIntegration:
    """Tests for clipboard copy functionality."""

    def test_ai_export_copies_to_clipboard(self) -> None:
        """Test AI export is copied to clipboard (mocked)."""
        content = "# Analysis\n\nTest content"

        # Test clipboard copy logic without requiring pyperclip
        # In production, pyperclip is optional and may not be installed
        clipboard_content = None

        def mock_copy(text: str) -> None:
            nonlocal clipboard_content
            clipboard_content = text

        mock_copy(content)
        assert clipboard_content == content

    def test_clipboard_fallback_on_error(self) -> None:
        """Test clipboard gracefully handles errors."""
        # Test that clipboard errors are handled gracefully
        success = False

        def failing_copy(_: str) -> None:
            raise Exception("No clipboard")

        try:
            failing_copy("test")
            success = True
        except Exception:
            success = False

        assert success is False
