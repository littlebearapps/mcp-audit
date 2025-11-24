#!/usr/bin/env python3
"""
Test suite for session_manager module

Tests session lifecycle, persistence, and recovery.
"""

import pytest
import json
from pathlib import Path
from datetime import datetime
from session_manager import SessionManager, save_session, load_session
from base_tracker import (
    Session,
    ServerSession,
    ToolStats,
    Call,
    TokenUsage,
    MCPToolCalls,
    SCHEMA_VERSION,
)


@pytest.fixture
def temp_session_dir(tmp_path):
    """Create temporary session directory for tests"""
    return tmp_path / "test_sessions"


@pytest.fixture
def sample_session():
    """Create sample session for testing"""
    session = Session(
        project="test-project",
        platform="test-platform",
        timestamp=datetime(2025, 11, 24, 10, 30, 0),
        session_id="test-project-2025-11-24T10-30-00",
        token_usage=TokenUsage(
            input_tokens=1000,
            output_tokens=500,
            cache_created_tokens=200,
            cache_read_tokens=5000,
            total_tokens=6700,
            cache_efficiency=0.75,
        ),
        cost_estimate=0.05,
        mcp_tool_calls=MCPToolCalls(
            total_calls=10, unique_tools=3, most_called="mcp__zen__chat (5 calls)"
        ),
    )

    # Add server session
    server_session = ServerSession(server="zen", total_calls=10, total_tokens=6700)

    # Add tool stats
    tool_stats = ToolStats(
        calls=5,
        total_tokens=3000,
        avg_tokens=600.0,
        call_history=[
            Call(
                tool_name="mcp__zen__chat",
                input_tokens=100,
                output_tokens=50,
                total_tokens=150,
                timestamp=datetime(2025, 11, 24, 10, 31, 0),
            )
        ],
    )

    server_session.tools["mcp__zen__chat"] = tool_stats
    session.server_sessions["zen"] = server_session

    return session


class TestSessionManager:
    """Tests for SessionManager class"""

    def test_initialization(self, temp_session_dir):
        """Test SessionManager initialization"""
        manager = SessionManager(base_dir=temp_session_dir)
        assert manager.base_dir == temp_session_dir
        assert temp_session_dir.exists()

    def test_default_base_dir(self):
        """Test default base directory creation"""
        manager = SessionManager()
        assert manager.base_dir == Path("logs/sessions")

    def test_create_session_directory(self, temp_session_dir):
        """Test session directory creation"""
        manager = SessionManager(base_dir=temp_session_dir)
        session_id = "test-session-001"

        session_dir = manager.create_session_directory(session_id)

        assert session_dir == temp_session_dir / session_id
        assert session_dir.exists()
        assert session_dir.is_dir()


class TestSessionPersistence:
    """Tests for session save/load functionality"""

    def test_save_session(self, temp_session_dir, sample_session):
        """Test saving session to disk"""
        manager = SessionManager(base_dir=temp_session_dir)
        session_dir = manager.create_session_directory(sample_session.session_id)

        saved_files = manager.save_session(sample_session, session_dir)

        # Check files were created
        assert "summary" in saved_files
        assert "mcp-zen" in saved_files
        assert saved_files["summary"].exists()
        assert saved_files["mcp-zen"].exists()

        # Verify summary.json content
        with open(saved_files["summary"], "r") as f:
            data = json.load(f)

        assert data["project"] == "test-project"
        assert data["platform"] == "test-platform"
        assert data["session_id"] == "test-project-2025-11-24T10-30-00"
        assert data["token_usage"]["total_tokens"] == 6700

    def test_load_session(self, temp_session_dir, sample_session):
        """Test loading session from disk"""
        manager = SessionManager(base_dir=temp_session_dir)
        session_dir = manager.create_session_directory(sample_session.session_id)

        # Save then load
        manager.save_session(sample_session, session_dir)
        loaded_session = manager.load_session(session_dir)

        assert loaded_session is not None
        assert loaded_session.project == sample_session.project
        assert loaded_session.platform == sample_session.platform
        assert loaded_session.session_id == sample_session.session_id
        assert loaded_session.token_usage.total_tokens == 6700

    def test_load_nonexistent_session(self, temp_session_dir):
        """Test loading session that doesn't exist"""
        manager = SessionManager(base_dir=temp_session_dir)
        nonexistent_dir = temp_session_dir / "nonexistent"

        loaded_session = manager.load_session(nonexistent_dir)

        assert loaded_session is None

    def test_load_session_with_server_sessions(self, temp_session_dir, sample_session):
        """Test loading session with server session data"""
        manager = SessionManager(base_dir=temp_session_dir)
        session_dir = manager.create_session_directory(sample_session.session_id)

        # Save then load
        manager.save_session(sample_session, session_dir)
        loaded_session = manager.load_session(session_dir)

        assert "zen" in loaded_session.server_sessions
        zen_session = loaded_session.server_sessions["zen"]
        assert zen_session.server == "zen"
        assert zen_session.total_calls == 10
        assert "mcp__zen__chat" in zen_session.tools


class TestSchemaVersionValidation:
    """Tests for schema version validation"""

    def test_validate_schema_version_valid(self, temp_session_dir):
        """Test validation of compatible schema version"""
        manager = SessionManager(base_dir=temp_session_dir)

        data = {"schema_version": SCHEMA_VERSION}
        assert manager._validate_schema_version(data) == True

    def test_validate_schema_version_missing(self, temp_session_dir):
        """Test validation fails when schema_version missing"""
        manager = SessionManager(base_dir=temp_session_dir)

        data = {}
        assert manager._validate_schema_version(data) == False

    def test_validate_schema_version_incompatible_major(self, temp_session_dir):
        """Test validation fails for incompatible major version"""
        manager = SessionManager(base_dir=temp_session_dir)

        data = {"schema_version": "2.0.0"}  # Different major version
        assert manager._validate_schema_version(data) == False

    def test_validate_schema_version_older_minor(self, temp_session_dir):
        """Test validation succeeds for older minor version (forward compatible)"""
        manager = SessionManager(base_dir=temp_session_dir)

        # Assuming current version is 1.0.0, test with 1.0.0 (same)
        data = {"schema_version": "1.0.0"}
        assert manager._validate_schema_version(data) == True

    def test_parse_version(self, temp_session_dir):
        """Test version string parsing"""
        manager = SessionManager(base_dir=temp_session_dir)

        major, minor, patch = manager._parse_version("1.2.3")
        assert major == 1
        assert minor == 2
        assert patch == 3


class TestSessionListing:
    """Tests for session listing and discovery"""

    def test_list_sessions_empty(self, temp_session_dir):
        """Test listing sessions in empty directory"""
        manager = SessionManager(base_dir=temp_session_dir)

        sessions = manager.list_sessions()

        assert sessions == []

    def test_list_sessions(self, temp_session_dir, sample_session):
        """Test listing multiple sessions"""
        manager = SessionManager(base_dir=temp_session_dir)

        # Create 3 sessions
        for i in range(3):
            session_id = f"test-session-{i:03d}"
            session_dir = manager.create_session_directory(session_id)
            sample_session.session_id = session_id
            manager.save_session(sample_session, session_dir)

        sessions = manager.list_sessions()

        assert len(sessions) == 3

    def test_list_sessions_sorted(self, temp_session_dir, sample_session):
        """Test sessions are sorted by timestamp (newest first)"""
        manager = SessionManager(base_dir=temp_session_dir)

        # Create sessions with different timestamps
        session_ids = [
            "test-2025-11-20T10-00-00",
            "test-2025-11-24T10-00-00",
            "test-2025-11-22T10-00-00",
        ]

        for session_id in session_ids:
            session_dir = manager.create_session_directory(session_id)
            sample_session.session_id = session_id
            manager.save_session(sample_session, session_dir)

        sessions = manager.list_sessions()

        # Should be sorted newest first
        assert sessions[0].name == "test-2025-11-24T10-00-00"
        assert sessions[1].name == "test-2025-11-22T10-00-00"
        assert sessions[2].name == "test-2025-11-20T10-00-00"

    def test_list_sessions_with_limit(self, temp_session_dir, sample_session):
        """Test listing sessions with limit"""
        manager = SessionManager(base_dir=temp_session_dir)

        # Create 5 sessions
        for i in range(5):
            session_id = f"test-session-{i:03d}"
            session_dir = manager.create_session_directory(session_id)
            sample_session.session_id = session_id
            manager.save_session(sample_session, session_dir)

        sessions = manager.list_sessions(limit=3)

        assert len(sessions) == 3


class TestIncompleteSessionDetection:
    """Tests for incomplete session detection and recovery"""

    def test_find_incomplete_sessions(self, temp_session_dir):
        """Test finding sessions missing required files"""
        manager = SessionManager(base_dir=temp_session_dir)

        # Create complete session
        complete_dir = manager.create_session_directory("complete-session")
        (complete_dir / "summary.json").write_text("{}")

        # Create incomplete session (no summary.json)
        incomplete_dir = manager.create_session_directory("incomplete-session")

        incomplete = manager.find_incomplete_sessions()

        assert len(incomplete) == 1
        assert incomplete[0].name == "incomplete-session"

    def test_recover_from_events_no_file(self, temp_session_dir):
        """Test recovery when events.jsonl doesn't exist"""
        manager = SessionManager(base_dir=temp_session_dir)
        session_dir = manager.create_session_directory("test-session")

        recovered = manager.recover_from_events(session_dir)

        assert recovered is None


class TestSessionCleanup:
    """Tests for old session cleanup"""

    def test_cleanup_old_sessions(self, temp_session_dir, sample_session):
        """Test cleaning up old sessions"""
        manager = SessionManager(base_dir=temp_session_dir)

        # Create old session (2 months ago)
        old_session_id = "test-2025-09-20-100000"
        old_dir = manager.create_session_directory(old_session_id)
        sample_session.session_id = old_session_id
        manager.save_session(sample_session, old_dir)

        # Create recent session
        recent_session_id = "test-2025-11-24-100000"
        recent_dir = manager.create_session_directory(recent_session_id)
        sample_session.session_id = recent_session_id
        manager.save_session(sample_session, recent_dir)

        # Cleanup sessions older than 30 days
        deleted_count = manager.cleanup_old_sessions(max_age_days=30)

        assert deleted_count == 1
        assert not old_dir.exists()
        assert recent_dir.exists()


class TestConvenienceFunctions:
    """Tests for convenience functions"""

    def test_save_session_function(self, temp_session_dir, sample_session):
        """Test save_session convenience function"""
        session_dir = temp_session_dir / sample_session.session_id
        session_dir.mkdir(parents=True)

        saved_files = save_session(sample_session, session_dir)

        assert "summary" in saved_files
        assert saved_files["summary"].exists()

    def test_load_session_function(self, temp_session_dir, sample_session):
        """Test load_session convenience function"""
        session_dir = temp_session_dir / sample_session.session_id
        session_dir.mkdir(parents=True)

        # Save then load
        save_session(sample_session, session_dir)
        loaded_session = load_session(session_dir)

        assert loaded_session is not None
        assert loaded_session.project == sample_session.project


class TestEdgeCases:
    """Tests for edge cases and error handling"""

    def test_load_corrupt_json(self, temp_session_dir):
        """Test loading session with corrupt JSON"""
        manager = SessionManager(base_dir=temp_session_dir)
        session_dir = manager.create_session_directory("corrupt-session")

        # Write corrupt JSON
        (session_dir / "summary.json").write_text("{ invalid json }")

        loaded_session = manager.load_session(session_dir)

        assert loaded_session is None

    def test_load_missing_fields(self, temp_session_dir):
        """Test loading session with missing required fields"""
        manager = SessionManager(base_dir=temp_session_dir)
        session_dir = manager.create_session_directory("missing-fields")

        # Write JSON missing required fields
        (session_dir / "summary.json").write_text('{"schema_version": "1.0.0"}')

        loaded_session = manager.load_session(session_dir)

        assert loaded_session is None


# ============================================================================
# Integration Tests
# ============================================================================


class TestSessionManagerIntegration:
    """Integration tests for complete session lifecycle"""

    def test_complete_session_lifecycle(self, temp_session_dir, sample_session):
        """Test complete save/load/list/cleanup lifecycle"""
        manager = SessionManager(base_dir=temp_session_dir)

        # 1. Create and save session
        session_dir = manager.create_session_directory(sample_session.session_id)
        saved_files = manager.save_session(sample_session, session_dir)
        assert len(saved_files) == 2  # summary + mcp-zen

        # 2. Load session
        loaded_session = manager.load_session(session_dir)
        assert loaded_session.project == sample_session.project

        # 3. List sessions
        sessions = manager.list_sessions()
        assert len(sessions) == 1

        # 4. Verify incomplete session detection works
        incomplete = manager.find_incomplete_sessions()
        assert len(incomplete) == 0  # Session is complete

    def test_multiple_server_sessions(self, temp_session_dir, sample_session):
        """Test saving/loading session with multiple servers"""
        manager = SessionManager(base_dir=temp_session_dir)

        # Add second server session
        brave_session = ServerSession(server="brave-search", total_calls=5, total_tokens=2000)
        sample_session.server_sessions["brave-search"] = brave_session

        # Save and load
        session_dir = manager.create_session_directory(sample_session.session_id)
        saved_files = manager.save_session(sample_session, session_dir)
        loaded_session = manager.load_session(session_dir)

        # Verify both servers loaded
        assert "zen" in loaded_session.server_sessions
        assert "brave-search" in loaded_session.server_sessions
        assert len(saved_files) == 3  # summary + mcp-zen + mcp-brave-search


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
