#!/usr/bin/env python3
"""
End-to-End Integration Tests for MCP Audit

Tests complete workflow: event parsing → session tracking → persistence → analysis
"""

import pytest
import json
from pathlib import Path
from datetime import datetime
from base_tracker import BaseTracker, SCHEMA_VERSION
from claude_code_adapter import ClaudeCodeAdapter
from codex_cli_adapter import CodexCLIAdapter
from session_manager import SessionManager
from normalization import normalize_tool_name, normalize_server_name


# ============================================================================
# Test Fixtures
# ============================================================================

@pytest.fixture
def sample_claude_code_events():
    """Sample Claude Code debug.log events"""
    return [
        {
            "id": "msg_001",
            "type": "assistant",
            "message": {
                "id": "msg_001",
                "type": "message",
                "role": "assistant",
                "model": "claude-sonnet-4-5-20250929",
                "content": [
                    {
                        "type": "tool_use",
                        "id": "tool_001",
                        "name": "mcp__zen__chat",
                        "input": {"prompt": "test query"}
                    }
                ],
                "usage": {
                    "input_tokens": 100,
                    "output_tokens": 50,
                    "cache_creation_input_tokens": 20,
                    "cache_read_input_tokens": 500
                }
            }
        },
        {
            "id": "msg_002",
            "type": "assistant",
            "message": {
                "id": "msg_002",
                "type": "message",
                "role": "assistant",
                "model": "claude-sonnet-4-5-20250929",
                "content": [
                    {
                        "type": "tool_use",
                        "id": "tool_002",
                        "name": "mcp__brave-search__web",
                        "input": {"query": "search query"}
                    }
                ],
                "usage": {
                    "input_tokens": 200,
                    "output_tokens": 100,
                    "cache_creation_input_tokens": 0,
                    "cache_read_input_tokens": 1000
                }
            }
        }
    ]


@pytest.fixture
def sample_codex_cli_events():
    """Sample Codex CLI output events"""
    return [
        {
            "type": "conversation",
            "message": {
                "model": "gpt-5-codex",
                "content": [
                    {
                        "type": "toolUse",
                        "name": "mcp__zen-mcp__chat",  # Codex format with -mcp
                        "input": {"prompt": "test query"}
                    }
                ],
                "usage": {
                    "inputTokens": 100,
                    "outputTokens": 50,
                    "cacheReadInputTokens": 500
                }
            }
        },
        {
            "type": "conversation",
            "message": {
                "model": "gpt-5-codex",
                "content": [
                    {
                        "type": "toolUse",
                        "name": "mcp__brave-search-mcp__web",  # Codex format
                        "input": {"query": "search query"}
                    }
                ],
                "usage": {
                    "inputTokens": 200,
                    "outputTokens": 100,
                    "cacheReadInputTokens": 1000
                }
            }
        }
    ]


# ============================================================================
# Cross-Platform Normalization Tests
# ============================================================================

class TestCrossPlatformNormalization:
    """Test that different platforms normalize to same tool names"""

    def test_claude_code_vs_codex_cli_normalization(self):
        """Test Claude Code and Codex CLI produce same normalized names"""
        # Claude Code format
        claude_tool = "mcp__zen__chat"
        # Codex CLI format
        codex_tool = "mcp__zen-mcp__chat"

        # Both should normalize to same name
        assert normalize_tool_name(claude_tool) == normalize_tool_name(codex_tool)
        assert normalize_server_name(claude_tool) == normalize_server_name(codex_tool)

    def test_normalized_tools_aggregate_correctly(self):
        """Test different platform formats aggregate to same tool"""
        tools = [
            "mcp__zen__chat",           # Claude Code
            "mcp__zen-mcp__chat",       # Codex CLI
            "mcp__zen__debug",          # Claude Code
            "mcp__zen-mcp__debug"       # Codex CLI
        ]

        normalized = set(normalize_tool_name(t) for t in tools)

        # Should only have 2 unique tools
        assert len(normalized) == 2
        assert "mcp__zen__chat" in normalized
        assert "mcp__zen__debug" in normalized


# ============================================================================
# Event Parsing Tests
# ============================================================================

class TestEventParsing:
    """Test event parsing across platforms"""

    def test_claude_code_event_parsing(self, sample_claude_code_events, tmp_path):
        """Test parsing Claude Code events"""
        adapter = ClaudeCodeAdapter(project="test", claude_dir=tmp_path)

        for event in sample_claude_code_events:
            result = adapter.parse_event(json.dumps(event))

            if result:
                tool_name, usage = result
                assert tool_name.startswith("mcp__")
                assert usage['input_tokens'] > 0

    def test_codex_cli_event_parsing(self, sample_codex_cli_events):
        """Test parsing Codex CLI events"""
        adapter = CodexCLIAdapter(project="test", codex_args=[])

        for event in sample_codex_cli_events:
            result = adapter.parse_event(json.dumps(event))

            if result:
                tool_name, usage = result
                assert tool_name.startswith("mcp__")
                assert "-mcp__" in tool_name  # Codex format
                assert usage['input_tokens'] > 0

    def test_unrecognized_event_handling(self, tmp_path):
        """Test handling of unrecognized events"""
        adapter = ClaudeCodeAdapter(project="test", claude_dir=tmp_path)

        # Invalid JSON
        result = adapter.parse_event("{ invalid json }")
        assert result is None

        # Valid JSON but not a tool event
        result = adapter.parse_event('{"type": "other"}')
        assert result is None


# ============================================================================
# Session Tracking Tests
# ============================================================================

class TestSessionTracking:
    """Test complete session tracking workflow"""

    def test_claude_code_session_tracking(self, sample_claude_code_events, tmp_path):
        """Test complete Claude Code session tracking"""
        adapter = ClaudeCodeAdapter(project="test-project", claude_dir=tmp_path)

        # Parse events and record calls
        for event in sample_claude_code_events:
            result = adapter.parse_event(json.dumps(event))
            if result:
                tool_name, usage = result
                content_hash = adapter.compute_content_hash(usage.get('tool_params', {}))
                adapter.record_tool_call(
                    tool_name=tool_name,
                    input_tokens=usage['input_tokens'],
                    output_tokens=usage['output_tokens'],
                    cache_created_tokens=usage['cache_created_tokens'],
                    cache_read_tokens=usage['cache_read_tokens'],
                    content_hash=content_hash
                )

        # Finalize session
        session = adapter.finalize_session()

        # Verify session data
        assert session.project == "test-project"
        assert session.platform == "claude-code"
        assert session.mcp_tool_calls.total_calls == 2
        assert session.mcp_tool_calls.unique_tools == 2
        assert session.token_usage.total_tokens > 0

    def test_codex_cli_session_tracking(self, sample_codex_cli_events):
        """Test complete Codex CLI session tracking"""
        adapter = CodexCLIAdapter(project="test-project", codex_args=[])

        # Parse events and record calls
        for event in sample_codex_cli_events:
            result = adapter.parse_event(json.dumps(event))
            if result:
                tool_name, usage = result
                adapter.record_tool_call(
                    tool_name=tool_name,
                    input_tokens=usage['input_tokens'],
                    output_tokens=usage['output_tokens'],
                    cache_created_tokens=usage['cache_created_tokens'],
                    cache_read_tokens=usage['cache_read_tokens']
                )

        # Finalize session
        session = adapter.finalize_session()

        # Verify session data
        assert session.project == "test-project"
        assert session.platform == "codex-cli"
        assert session.mcp_tool_calls.total_calls == 2
        assert session.mcp_tool_calls.unique_tools == 2

        # Verify tools normalized (Codex -mcp suffix stripped)
        zen_session = session.server_sessions.get("zen")
        assert zen_session is not None
        assert "mcp__zen__chat" in zen_session.tools


# ============================================================================
# Persistence Tests
# ============================================================================

class TestPersistence:
    """Test session persistence and recovery"""

    def test_save_and_load_session(self, tmp_path, sample_claude_code_events):
        """Test saving and loading session"""
        # Create and track session
        adapter = ClaudeCodeAdapter(project="test-project", claude_dir=tmp_path)

        for event in sample_claude_code_events:
            result = adapter.parse_event(json.dumps(event))
            if result:
                tool_name, usage = result
                adapter.record_tool_call(
                    tool_name=tool_name,
                    input_tokens=usage['input_tokens'],
                    output_tokens=usage['output_tokens'],
                    cache_created_tokens=usage['cache_created_tokens'],
                    cache_read_tokens=usage['cache_read_tokens']
                )

        session = adapter.finalize_session()

        # Save session
        adapter.save_session(tmp_path)

        # Load session
        manager = SessionManager(base_dir=tmp_path)
        loaded_session = manager.load_session(adapter.session_dir)

        # Verify loaded data matches
        assert loaded_session is not None
        assert loaded_session.project == session.project
        assert loaded_session.platform == session.platform
        assert loaded_session.mcp_tool_calls.total_calls == session.mcp_tool_calls.total_calls

    def test_schema_version_validation(self, tmp_path):
        """Test schema version validation on load"""
        manager = SessionManager(base_dir=tmp_path)

        # Create session directory
        session_dir = tmp_path / "test-session"
        session_dir.mkdir()

        # Write session with incompatible schema version
        summary_data = {
            "schema_version": "2.0.0",  # Incompatible major version
            "project": "test",
            "platform": "test"
        }

        (session_dir / "summary.json").write_text(json.dumps(summary_data))

        # Should fail to load
        loaded_session = manager.load_session(session_dir)
        assert loaded_session is None


# ============================================================================
# Duplicate Detection Tests
# ============================================================================

class TestDuplicateDetection:
    """Test duplicate tool call detection"""

    def test_duplicate_detection(self, tmp_path):
        """Test duplicate calls are detected"""
        adapter = ClaudeCodeAdapter(project="test", claude_dir=tmp_path)

        # Same input = same content hash
        input_params = {"query": "test"}
        hash1 = adapter.compute_content_hash(input_params)
        hash2 = adapter.compute_content_hash(input_params)

        assert hash1 == hash2

        # Record two calls with same hash
        adapter.record_tool_call(
            tool_name="mcp__zen__chat",
            input_tokens=100,
            output_tokens=50,
            content_hash=hash1
        )
        adapter.record_tool_call(
            tool_name="mcp__zen__chat",
            input_tokens=100,
            output_tokens=50,
            content_hash=hash2  # Duplicate
        )

        session = adapter.finalize_session()

        # Should detect duplicate
        assert session.redundancy_analysis is not None
        assert session.redundancy_analysis["duplicate_calls"] == 1
        assert session.redundancy_analysis["potential_savings"] == 150


# ============================================================================
# Anomaly Detection Tests
# ============================================================================

class TestAnomalyDetection:
    """Test anomaly detection in tool usage"""

    def test_high_frequency_detection(self, tmp_path):
        """Test high frequency anomaly detection"""
        adapter = ClaudeCodeAdapter(project="test", claude_dir=tmp_path)

        # Record 15 calls (threshold is 10)
        for _ in range(15):
            adapter.record_tool_call(
                tool_name="mcp__zen__chat",
                input_tokens=100,
                output_tokens=50
            )

        session = adapter.finalize_session()

        # Should detect high frequency
        anomalies = [a for a in session.anomalies if a["type"] == "high_frequency"]
        assert len(anomalies) > 0
        assert anomalies[0]["tool"] == "mcp__zen__chat"
        assert anomalies[0]["calls"] == 15

    def test_high_avg_tokens_detection(self, tmp_path):
        """Test high average tokens anomaly detection"""
        adapter = ClaudeCodeAdapter(project="test", claude_dir=tmp_path)

        # Record call with 150K tokens (threshold is 100K)
        adapter.record_tool_call(
            tool_name="mcp__zen__thinkdeep",
            input_tokens=100000,
            output_tokens=50000
        )

        session = adapter.finalize_session()

        # Should detect high avg tokens
        anomalies = [a for a in session.anomalies if a["type"] == "high_avg_tokens"]
        assert len(anomalies) > 0
        assert anomalies[0]["tool"] == "mcp__zen__thinkdeep"


# ============================================================================
# Multi-Server Tracking Tests
# ============================================================================

class TestMultiServerTracking:
    """Test tracking multiple MCP servers"""

    def test_multiple_servers_tracked(self, tmp_path):
        """Test multiple MCP servers tracked separately"""
        adapter = ClaudeCodeAdapter(project="test", claude_dir=tmp_path)

        # Record calls to different servers
        adapter.record_tool_call(
            tool_name="mcp__zen__chat",
            input_tokens=100,
            output_tokens=50
        )
        adapter.record_tool_call(
            tool_name="mcp__brave-search__web",
            input_tokens=200,
            output_tokens=100
        )
        adapter.record_tool_call(
            tool_name="mcp__context7__search",
            input_tokens=150,
            output_tokens=75
        )

        session = adapter.finalize_session()

        # Should have 3 server sessions
        assert len(session.server_sessions) == 3
        assert "zen" in session.server_sessions
        assert "brave-search" in session.server_sessions
        assert "context7" in session.server_sessions

    def test_server_session_files_created(self, tmp_path):
        """Test per-server JSON files created"""
        adapter = ClaudeCodeAdapter(project="test", claude_dir=tmp_path)

        # Record calls to multiple servers
        adapter.record_tool_call(
            tool_name="mcp__zen__chat",
            input_tokens=100,
            output_tokens=50
        )
        adapter.record_tool_call(
            tool_name="mcp__brave-search__web",
            input_tokens=200,
            output_tokens=100
        )

        adapter.finalize_session()
        adapter.save_session(tmp_path)

        # Verify files created
        assert (adapter.session_dir / "summary.json").exists()
        assert (adapter.session_dir / "mcp-zen.json").exists()
        assert (adapter.session_dir / "mcp-brave-search.json").exists()


# ============================================================================
# End-to-End Workflow Tests
# ============================================================================

class TestEndToEndWorkflow:
    """Complete end-to-end workflow tests"""

    def test_complete_claude_code_workflow(self, tmp_path, sample_claude_code_events):
        """Test complete workflow: events → tracking → persistence → loading"""
        # 1. Create adapter
        adapter = ClaudeCodeAdapter(project="e2e-test", claude_dir=tmp_path)

        # 2. Parse events and track
        for event in sample_claude_code_events:
            result = adapter.parse_event(json.dumps(event))
            if result:
                tool_name, usage = result
                adapter.record_tool_call(
                    tool_name=tool_name,
                    input_tokens=usage['input_tokens'],
                    output_tokens=usage['output_tokens'],
                    cache_created_tokens=usage['cache_created_tokens'],
                    cache_read_tokens=usage['cache_read_tokens']
                )

        # 3. Finalize session
        session = adapter.finalize_session()

        # 4. Save to disk
        adapter.save_session(tmp_path)

        # 5. Load from disk
        manager = SessionManager(base_dir=tmp_path)
        loaded_session = manager.load_session(adapter.session_dir)

        # 6. Verify complete workflow
        assert loaded_session is not None
        assert loaded_session.schema_version == SCHEMA_VERSION
        assert loaded_session.project == "e2e-test"
        assert loaded_session.platform == "claude-code"
        assert loaded_session.mcp_tool_calls.total_calls == 2
        assert loaded_session.mcp_tool_calls.unique_tools == 2
        assert loaded_session.token_usage.total_tokens > 0
        assert "zen" in loaded_session.server_sessions
        assert "brave-search" in loaded_session.server_sessions

    def test_complete_codex_cli_workflow(self, tmp_path, sample_codex_cli_events):
        """Test complete Codex CLI workflow with normalization"""
        # 1. Create adapter
        adapter = CodexCLIAdapter(project="codex-e2e-test", codex_args=[])

        # 2. Parse events and track
        for event in sample_codex_cli_events:
            result = adapter.parse_event(json.dumps(event))
            if result:
                tool_name, usage = result
                adapter.record_tool_call(
                    tool_name=tool_name,
                    input_tokens=usage['input_tokens'],
                    output_tokens=usage['output_tokens'],
                    cache_created_tokens=usage['cache_created_tokens'],
                    cache_read_tokens=usage['cache_read_tokens']
                )

        # 3. Finalize and save
        session = adapter.finalize_session()
        adapter.save_session(tmp_path)

        # 4. Load from disk
        manager = SessionManager(base_dir=tmp_path)
        loaded_session = manager.load_session(adapter.session_dir)

        # 5. Verify Codex tools normalized
        assert loaded_session is not None
        zen_session = loaded_session.server_sessions.get("zen")
        assert zen_session is not None
        # Should be normalized (no -mcp suffix)
        assert "mcp__zen__chat" in zen_session.tools

    def test_cross_session_analysis(self, tmp_path, sample_claude_code_events):
        """Test analyzing multiple sessions"""
        manager = SessionManager(base_dir=tmp_path)

        # Create 3 sessions
        for i in range(3):
            adapter = ClaudeCodeAdapter(project=f"session-{i}", claude_dir=tmp_path)

            for event in sample_claude_code_events:
                result = adapter.parse_event(json.dumps(event))
                if result:
                    tool_name, usage = result
                    adapter.record_tool_call(
                        tool_name=tool_name,
                        input_tokens=usage['input_tokens'],
                        output_tokens=usage['output_tokens'],
                        cache_created_tokens=usage['cache_created_tokens'],
                        cache_read_tokens=usage['cache_read_tokens']
                    )

            adapter.finalize_session()
            adapter.save_session(tmp_path)

        # List all sessions
        sessions = manager.list_sessions()
        assert len(sessions) == 3

        # Load all sessions
        loaded_sessions = []
        for session_dir in sessions:
            session = manager.load_session(session_dir)
            if session:
                loaded_sessions.append(session)

        assert len(loaded_sessions) == 3

        # Aggregate statistics
        total_calls = sum(s.mcp_tool_calls.total_calls for s in loaded_sessions)
        total_tokens = sum(s.token_usage.total_tokens for s in loaded_sessions)

        assert total_calls == 6  # 2 calls per session × 3 sessions
        assert total_tokens > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
