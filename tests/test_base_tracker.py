#!/usr/bin/env python3
"""
Test suite for base_tracker module

Tests BaseTracker abstract class and shared functionality.
"""

import pytest
from datetime import datetime
from pathlib import Path
from mcp_audit.base_tracker import (
    BaseTracker,
    Session,
    ServerSession,
    ToolStats,
    Call,
    TokenUsage,
    MCPToolCalls,
    SCHEMA_VERSION,
)


# ============================================================================
# Concrete Test Implementation of BaseTracker
# ============================================================================


class ConcreteTestTracker(BaseTracker):
    """Concrete implementation of BaseTracker for testing"""

    def __init__(self, project: str = "test-project", platform: str = "test-platform"):
        super().__init__(project, platform)
        self.events = []

    def start_tracking(self) -> None:
        """Test implementation - does nothing"""
        pass

    def parse_event(self, event_data):
        """Test implementation - returns None"""
        return None

    def get_platform_metadata(self):
        """Test implementation - returns test metadata"""
        return {"test_key": "test_value"}


# ============================================================================
# Data Structure Tests
# ============================================================================


class TestDataStructures:
    """Tests for core data structures"""

    def test_call_creation(self):
        """Test Call dataclass creation"""
        call = Call(
            tool_name="mcp__zen__chat", input_tokens=100, output_tokens=50, total_tokens=150
        )

        assert call.tool_name == "mcp__zen__chat"
        assert call.input_tokens == 100
        assert call.output_tokens == 50
        assert call.total_tokens == 150
        assert call.schema_version == SCHEMA_VERSION

    def test_call_to_dict(self):
        """Test Call to_dict conversion"""
        timestamp = datetime(2025, 11, 24, 10, 30, 0)
        call = Call(
            tool_name="mcp__zen__chat",
            timestamp=timestamp,
            input_tokens=100,
            output_tokens=50,
            total_tokens=150,
        )

        data = call.to_dict()

        assert data["tool_name"] == "mcp__zen__chat"
        assert data["input_tokens"] == 100
        assert data["timestamp"] == "2025-11-24T10:30:00"

    def test_tool_stats_creation(self):
        """Test ToolStats dataclass creation"""
        stats = ToolStats(calls=5, total_tokens=1000, avg_tokens=200.0)

        assert stats.calls == 5
        assert stats.total_tokens == 1000
        assert stats.avg_tokens == 200.0

    def test_tool_stats_to_dict(self):
        """Test ToolStats to_dict with call history"""
        call = Call(tool_name="test", total_tokens=100)
        stats = ToolStats(calls=1, call_history=[call])

        data = stats.to_dict()

        assert data["calls"] == 1
        assert len(data["call_history"]) == 1
        assert data["call_history"][0]["tool_name"] == "test"

    def test_server_session_creation(self):
        """Test ServerSession dataclass creation"""
        session = ServerSession(server="zen", total_calls=10, total_tokens=5000)

        assert session.server == "zen"
        assert session.total_calls == 10
        assert session.total_tokens == 5000

    def test_session_creation(self):
        """Test Session dataclass creation"""
        session = Session(project="test-project", platform="test-platform", session_id="test-123")

        assert session.project == "test-project"
        assert session.platform == "test-platform"
        assert session.session_id == "test-123"
        assert session.schema_version == SCHEMA_VERSION


# ============================================================================
# BaseTracker Initialization Tests
# ============================================================================


class TestBaseTrackerInitialization:
    """Tests for BaseTracker initialization"""

    def test_initialization(self):
        """Test BaseTracker initialization"""
        tracker = ConcreteTestTracker(project="my-project", platform="my-platform")

        assert tracker.project == "my-project"
        assert tracker.platform == "my-platform"
        assert tracker.session.project == "my-project"
        assert tracker.session.platform == "my-platform"

    def test_session_id_generation(self):
        """Test session ID generation"""
        tracker = ConcreteTestTracker()

        session_id = tracker.session_id

        # Should be in format: project-YYYY-MM-DDTHH-MM-SS
        assert session_id.startswith("test-project-")
        assert "T" in session_id

    def test_server_sessions_initialized(self):
        """Test server sessions dictionary initialized"""
        tracker = ConcreteTestTracker()

        assert isinstance(tracker.server_sessions, dict)
        assert len(tracker.server_sessions) == 0

    def test_content_hashes_initialized(self):
        """Test content hashes dictionary initialized"""
        tracker = ConcreteTestTracker()

        assert isinstance(tracker.content_hashes, dict)


# ============================================================================
# Normalization Tests
# ============================================================================


class TestNormalization:
    """Tests for tool name normalization"""

    def test_normalize_server_name_claude_code(self):
        """Test server name extraction (Claude Code format)"""
        tracker = ConcreteTestTracker()

        server = tracker.normalize_server_name("mcp__zen__chat")

        assert server == "zen"

    def test_normalize_server_name_codex_cli(self):
        """Test server name extraction (Codex CLI format with -mcp)"""
        tracker = ConcreteTestTracker()

        server = tracker.normalize_server_name("mcp__zen-mcp__chat")

        assert server == "zen"

    def test_normalize_server_name_hyphenated(self):
        """Test server name with hyphens"""
        tracker = ConcreteTestTracker()

        server = tracker.normalize_server_name("mcp__brave-search__web")

        assert server == "brave-search"

    def test_normalize_tool_name_passthrough(self):
        """Test tool name normalization (Claude Code format)"""
        tracker = ConcreteTestTracker()

        normalized = tracker.normalize_tool_name("mcp__zen__chat")

        assert normalized == "mcp__zen__chat"

    def test_normalize_tool_name_codex_cli(self):
        """Test tool name normalization (Codex CLI -mcp suffix)"""
        tracker = ConcreteTestTracker()

        normalized = tracker.normalize_tool_name("mcp__zen-mcp__chat")

        assert normalized == "mcp__zen__chat"

    def test_normalize_invalid_tool_name(self):
        """Test normalization warns on invalid tool name"""
        tracker = ConcreteTestTracker()

        with pytest.warns(UserWarning):
            server = tracker.normalize_server_name("Read")

        assert server == "unknown"


# ============================================================================
# Tool Call Recording Tests
# ============================================================================


class TestToolCallRecording:
    """Tests for recording tool calls"""

    def test_record_tool_call_basic(self):
        """Test recording a basic tool call"""
        tracker = ConcreteTestTracker()

        tracker.record_tool_call(
            tool_name="mcp__zen__chat",
            input_tokens=100,
            output_tokens=50,
            cache_created_tokens=20,
            cache_read_tokens=500,
        )

        # Check session token usage
        assert tracker.session.token_usage.input_tokens == 100
        assert tracker.session.token_usage.output_tokens == 50
        assert tracker.session.token_usage.cache_created_tokens == 20
        assert tracker.session.token_usage.cache_read_tokens == 500
        assert tracker.session.token_usage.total_tokens == 670

    def test_record_tool_call_creates_server_session(self):
        """Test tool call creates server session"""
        tracker = ConcreteTestTracker()

        tracker.record_tool_call(tool_name="mcp__zen__chat", input_tokens=100, output_tokens=50)

        assert "zen" in tracker.server_sessions
        assert tracker.server_sessions["zen"].server == "zen"

    def test_record_tool_call_creates_tool_stats(self):
        """Test tool call creates tool stats"""
        tracker = ConcreteTestTracker()

        tracker.record_tool_call(tool_name="mcp__zen__chat", input_tokens=100, output_tokens=50)

        zen_session = tracker.server_sessions["zen"]
        assert "mcp__zen__chat" in zen_session.tools
        tool_stats = zen_session.tools["mcp__zen__chat"]
        assert tool_stats.calls == 1
        assert tool_stats.total_tokens == 150

    def test_record_multiple_tool_calls(self):
        """Test recording multiple tool calls"""
        tracker = ConcreteTestTracker()

        # First call
        tracker.record_tool_call(tool_name="mcp__zen__chat", input_tokens=100, output_tokens=50)

        # Second call
        tracker.record_tool_call(tool_name="mcp__zen__chat", input_tokens=200, output_tokens=100)

        tool_stats = tracker.server_sessions["zen"].tools["mcp__zen__chat"]
        assert tool_stats.calls == 2
        assert tool_stats.total_tokens == 450  # 150 + 300
        assert tool_stats.avg_tokens == 225.0  # 450 / 2

    def test_record_tool_call_normalizes_codex_name(self):
        """Test Codex CLI tool names are normalized"""
        tracker = ConcreteTestTracker()

        tracker.record_tool_call(
            tool_name="mcp__zen-mcp__chat", input_tokens=100, output_tokens=50  # Codex format
        )

        # Should be normalized to Claude Code format
        zen_session = tracker.server_sessions["zen"]
        assert "mcp__zen__chat" in zen_session.tools

    def test_record_tool_call_with_duration(self):
        """Test recording tool call with duration"""
        tracker = ConcreteTestTracker()

        tracker.record_tool_call(
            tool_name="mcp__zen__chat", input_tokens=100, output_tokens=50, duration_ms=1500
        )

        tool_stats = tracker.server_sessions["zen"].tools["mcp__zen__chat"]
        assert tool_stats.total_duration_ms == 1500
        assert tool_stats.avg_duration_ms == 1500.0
        assert tool_stats.max_duration_ms == 1500
        assert tool_stats.min_duration_ms == 1500

    def test_record_tool_call_duration_stats(self):
        """Test duration statistics across multiple calls"""
        tracker = ConcreteTestTracker()

        # Three calls with different durations
        tracker.record_tool_call(
            tool_name="mcp__zen__chat", input_tokens=100, output_tokens=50, duration_ms=1000
        )
        tracker.record_tool_call(
            tool_name="mcp__zen__chat", input_tokens=100, output_tokens=50, duration_ms=2000
        )
        tracker.record_tool_call(
            tool_name="mcp__zen__chat", input_tokens=100, output_tokens=50, duration_ms=1500
        )

        tool_stats = tracker.server_sessions["zen"].tools["mcp__zen__chat"]
        assert tool_stats.total_duration_ms == 4500
        assert tool_stats.avg_duration_ms == 1500.0
        assert tool_stats.max_duration_ms == 2000
        assert tool_stats.min_duration_ms == 1000

    def test_record_tool_call_with_content_hash(self):
        """Test recording tool call with content hash (duplicate detection)"""
        tracker = ConcreteTestTracker()

        tracker.record_tool_call(
            tool_name="mcp__zen__chat", input_tokens=100, output_tokens=50, content_hash="abc123"
        )

        assert "abc123" in tracker.content_hashes
        assert len(tracker.content_hashes["abc123"]) == 1

    def test_cache_efficiency_calculation(self):
        """Test cache efficiency calculation"""
        tracker = ConcreteTestTracker()

        tracker.record_tool_call(
            tool_name="mcp__zen__chat",
            input_tokens=100,
            output_tokens=50,
            cache_created_tokens=20,
            cache_read_tokens=500,
        )

        # cache_efficiency = cache_read / total_tokens
        # 500 / 670 = 0.746...
        assert tracker.session.token_usage.cache_efficiency > 0.74
        assert tracker.session.token_usage.cache_efficiency < 0.75


# ============================================================================
# Session Finalization Tests
# ============================================================================


class TestSessionFinalization:
    """Tests for session finalization"""

    def test_finalize_session_basic(self):
        """Test basic session finalization"""
        tracker = ConcreteTestTracker()

        # Record some calls
        tracker.record_tool_call(tool_name="mcp__zen__chat", input_tokens=100, output_tokens=50)

        session = tracker.finalize_session()

        assert session.end_timestamp is not None
        assert session.duration_seconds is not None
        assert session.duration_seconds >= 0

    def test_finalize_session_mcp_summary(self):
        """Test MCP tool calls summary"""
        tracker = ConcreteTestTracker()

        # Record multiple calls
        tracker.record_tool_call(tool_name="mcp__zen__chat", input_tokens=100, output_tokens=50)
        tracker.record_tool_call(tool_name="mcp__zen__chat", input_tokens=100, output_tokens=50)
        tracker.record_tool_call(tool_name="mcp__zen__debug", input_tokens=200, output_tokens=100)

        session = tracker.finalize_session()

        assert session.mcp_tool_calls.total_calls == 3
        assert session.mcp_tool_calls.unique_tools == 2
        assert "mcp__zen__chat (2 calls)" in session.mcp_tool_calls.most_called

    def test_finalize_session_server_sessions(self):
        """Test server sessions added to session"""
        tracker = ConcreteTestTracker()

        tracker.record_tool_call(tool_name="mcp__zen__chat", input_tokens=100, output_tokens=50)

        session = tracker.finalize_session()

        assert "zen" in session.server_sessions
        assert session.server_sessions["zen"].server == "zen"

    def test_analyze_redundancy(self):
        """Test redundancy analysis (duplicate detection)"""
        tracker = ConcreteTestTracker()

        # Same content hash = duplicate
        tracker.record_tool_call(
            tool_name="mcp__zen__chat", input_tokens=100, output_tokens=50, content_hash="abc123"
        )
        tracker.record_tool_call(
            tool_name="mcp__zen__chat",
            input_tokens=100,
            output_tokens=50,
            content_hash="abc123",  # Duplicate
        )
        tracker.record_tool_call(
            tool_name="mcp__zen__chat",
            input_tokens=100,
            output_tokens=50,
            content_hash="def456",  # Different
        )

        session = tracker.finalize_session()

        assert session.redundancy_analysis is not None
        assert session.redundancy_analysis["duplicate_calls"] == 1
        assert session.redundancy_analysis["potential_savings"] == 150

    def test_detect_anomalies_high_frequency(self):
        """Test anomaly detection for high frequency"""
        tracker = ConcreteTestTracker()

        # 15 calls (threshold is 10)
        for _ in range(15):
            tracker.record_tool_call(tool_name="mcp__zen__chat", input_tokens=100, output_tokens=50)

        session = tracker.finalize_session()

        # Should detect high frequency anomaly
        assert len(session.anomalies) > 0
        anomaly = session.anomalies[0]
        assert anomaly["type"] == "high_frequency"
        assert anomaly["tool"] == "mcp__zen__chat"
        assert anomaly["calls"] == 15

    def test_detect_anomalies_high_avg_tokens(self):
        """Test anomaly detection for high average tokens"""
        tracker = ConcreteTestTracker()

        # 150K tokens (threshold is 100K)
        tracker.record_tool_call(
            tool_name="mcp__zen__thinkdeep", input_tokens=100000, output_tokens=50000
        )

        session = tracker.finalize_session()

        # Should detect high avg tokens anomaly
        assert len(session.anomalies) > 0
        anomaly = session.anomalies[0]
        assert anomaly["type"] == "high_avg_tokens"
        assert anomaly["tool"] == "mcp__zen__thinkdeep"
        assert anomaly["avg_tokens"] == 150000


# ============================================================================
# Persistence Tests
# ============================================================================


class TestPersistence:
    """Tests for session persistence"""

    def test_save_session(self, tmp_path):
        """Test saving session to disk"""
        tracker = ConcreteTestTracker()

        tracker.record_tool_call(tool_name="mcp__zen__chat", input_tokens=100, output_tokens=50)

        tracker.finalize_session()
        tracker.save_session(tmp_path)

        # Check files created
        assert tracker.session_dir is not None
        assert tracker.session_dir.exists()
        assert (tracker.session_dir / "summary.json").exists()
        assert (tracker.session_dir / "mcp-zen.json").exists()


# ============================================================================
# Utility Methods Tests
# ============================================================================


class TestUtilityMethods:
    """Tests for utility methods"""

    def test_compute_content_hash(self):
        """Test content hash computation"""
        input_data = {"query": "test", "options": {"verbose": True}}

        hash1 = BaseTracker.compute_content_hash(input_data)
        hash2 = BaseTracker.compute_content_hash(input_data)

        # Same input = same hash
        assert hash1 == hash2

        # Different input = different hash
        input_data2 = {"query": "different"}
        hash3 = BaseTracker.compute_content_hash(input_data2)
        assert hash3 != hash1

    def test_handle_unrecognized_line(self):
        """Test unrecognized line handling"""
        tracker = ConcreteTestTracker()

        # Should not crash, just warn
        with pytest.warns(UserWarning):
            tracker.handle_unrecognized_line("invalid line format")


# ============================================================================
# Integration Tests
# ============================================================================


class TestBaseTrackerIntegration:
    """Integration tests for complete tracker workflow"""

    def test_complete_workflow(self, tmp_path):
        """Test complete tracking workflow"""
        tracker = ConcreteTestTracker()

        # Record multiple tools across multiple servers
        tracker.record_tool_call(
            tool_name="mcp__zen__chat", input_tokens=100, output_tokens=50, duration_ms=1000
        )
        tracker.record_tool_call(
            tool_name="mcp__zen__debug", input_tokens=200, output_tokens=100, duration_ms=2000
        )
        tracker.record_tool_call(
            tool_name="mcp__brave-search__web", input_tokens=150, output_tokens=75, duration_ms=500
        )

        # Finalize and save
        session = tracker.finalize_session()
        tracker.save_session(tmp_path)

        # Verify session data
        assert session.mcp_tool_calls.total_calls == 3
        assert session.mcp_tool_calls.unique_tools == 3
        assert len(tracker.server_sessions) == 2  # zen + brave-search

        # Verify files
        assert (tracker.session_dir / "summary.json").exists()
        assert (tracker.session_dir / "mcp-zen.json").exists()
        assert (tracker.session_dir / "mcp-brave-search.json").exists()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
