#!/usr/bin/env python3
"""
Session Manager Module - Session lifecycle and persistence

Handles session creation, lifecycle management, and persistence to disk.
"""

import json
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any, List
from dataclasses import asdict

from base_tracker import Session, ServerSession, SCHEMA_VERSION


class SessionManager:
    """
    Manages session lifecycle and persistence.

    Responsibilities:
    - Session directory creation
    - Writing session data to disk
    - Loading sessions from disk
    - Session validation
    - Recovery from incomplete sessions
    """

    def __init__(self, base_dir: Path = None):
        """
        Initialize session manager.

        Args:
            base_dir: Base directory for session storage (default: logs/sessions)
        """
        self.base_dir = base_dir or Path("logs/sessions")
        self.base_dir.mkdir(parents=True, exist_ok=True)

    def create_session_directory(self, session_id: str) -> Path:
        """
        Create directory for session data.

        Args:
            session_id: Unique session identifier

        Returns:
            Path to created session directory
        """
        session_dir = self.base_dir / session_id
        session_dir.mkdir(parents=True, exist_ok=True)
        return session_dir

    def save_session(self, session: Session, session_dir: Path) -> Dict[str, Path]:
        """
        Save complete session data to disk.

        Creates:
        - summary.json: Complete session object
        - mcp-{server}.json: Per-server statistics
        - events.jsonl: Event stream (if available)

        Args:
            session: Session object to save
            session_dir: Directory to save session files

        Returns:
            Dictionary mapping file type to file path
        """
        saved_files = {}

        # Ensure directory exists
        session_dir.mkdir(parents=True, exist_ok=True)

        # Save session summary
        summary_path = session_dir / "summary.json"
        with open(summary_path, "w") as f:
            json.dump(session.to_dict(), f, indent=2, default=str)
        saved_files["summary"] = summary_path

        # Save per-server sessions
        for server_name, server_session in session.server_sessions.items():
            server_path = session_dir / f"mcp-{server_name}.json"
            with open(server_path, "w") as f:
                json.dump(server_session.to_dict(), f, indent=2, default=str)
            saved_files[f"mcp-{server_name}"] = server_path

        return saved_files

    def load_session(self, session_dir: Path) -> Optional[Session]:
        """
        Load session from disk.

        Args:
            session_dir: Directory containing session files

        Returns:
            Session object if successful, None otherwise
        """
        summary_path = session_dir / "summary.json"
        if not summary_path.exists():
            return None

        try:
            with open(summary_path, "r") as f:
                data = json.load(f)

            # Validate schema version
            if not self._validate_schema_version(data):
                return None

            # Reconstruct Session object
            session = self._reconstruct_session(data)

            # Load server sessions
            for server_file in session_dir.glob("mcp-*.json"):
                server_name = server_file.stem[4:]  # Remove 'mcp-' prefix
                server_session = self._load_server_session(server_file)
                if server_session:
                    session.server_sessions[server_name] = server_session

            return session

        except (json.JSONDecodeError, KeyError, ValueError) as e:
            print(f"Error loading session from {session_dir}: {e}")
            return None

    def _validate_schema_version(self, data: dict) -> bool:
        """
        Validate schema version compatibility.

        Args:
            data: Session data dictionary

        Returns:
            True if compatible, False otherwise
        """
        if "schema_version" not in data:
            print("Warning: Session data missing schema_version field")
            return False

        session_version = data["schema_version"]
        major, minor, patch = self._parse_version(session_version)
        current_major, current_minor, _ = self._parse_version(SCHEMA_VERSION)

        # Major version must match
        if major != current_major:
            print(f"Error: Incompatible major version: {major} != {current_major}")
            return False

        # Minor version can be older (forward compatible)
        if minor > current_minor:
            print(f"Warning: Future minor version detected: {minor} > {current_minor}")

        return True

    def _parse_version(self, version_str: str) -> tuple:
        """Parse version string into (major, minor, patch) tuple"""
        parts = version_str.split(".")
        return (int(parts[0]), int(parts[1]), int(parts[2]))

    def _reconstruct_session(self, data: dict) -> Session:
        """
        Reconstruct Session object from dictionary.

        Args:
            data: Session data dictionary

        Returns:
            Session object
        """
        # Import needed for type reconstruction
        from base_tracker import TokenUsage, MCPToolCalls

        # Reconstruct timestamp
        timestamp = datetime.fromisoformat(data["timestamp"])
        end_timestamp = None
        if data.get("end_timestamp"):
            end_timestamp = datetime.fromisoformat(data["end_timestamp"])

        # Reconstruct TokenUsage
        token_usage = TokenUsage(**data["token_usage"])

        # Reconstruct MCPToolCalls
        mcp_tool_calls = MCPToolCalls(**data["mcp_tool_calls"])

        # Create Session object
        session = Session(
            schema_version=data["schema_version"],
            project=data["project"],
            platform=data["platform"],
            timestamp=timestamp,
            session_id=data["session_id"],
            token_usage=token_usage,
            cost_estimate=data["cost_estimate"],
            mcp_tool_calls=mcp_tool_calls,
            server_sessions={},  # Will be loaded separately
            redundancy_analysis=data.get("redundancy_analysis"),
            anomalies=data.get("anomalies", []),
            end_timestamp=end_timestamp,
            duration_seconds=data.get("duration_seconds"),
        )

        return session

    def _load_server_session(self, server_file: Path) -> Optional[ServerSession]:
        """
        Load ServerSession from file.

        Args:
            server_file: Path to mcp-{server}.json file

        Returns:
            ServerSession object if successful, None otherwise
        """
        try:
            with open(server_file, "r") as f:
                data = json.load(f)

            # Import needed for type reconstruction
            from base_tracker import ToolStats, Call

            # Reconstruct ToolStats for each tool
            tools = {}
            for tool_name, tool_data in data.get("tools", {}).items():
                # Reconstruct Call objects
                call_history = []
                for call_data in tool_data.get("call_history", []):
                    call = Call(
                        schema_version=call_data["schema_version"],
                        timestamp=datetime.fromisoformat(call_data["timestamp"]),
                        tool_name=call_data["tool_name"],
                        input_tokens=call_data["input_tokens"],
                        output_tokens=call_data["output_tokens"],
                        cache_created_tokens=call_data["cache_created_tokens"],
                        cache_read_tokens=call_data["cache_read_tokens"],
                        total_tokens=call_data["total_tokens"],
                        duration_ms=call_data["duration_ms"],
                        content_hash=call_data.get("content_hash"),
                        platform_data=call_data.get("platform_data"),
                    )
                    call_history.append(call)

                # Create ToolStats object
                tool_stats = ToolStats(
                    schema_version=tool_data["schema_version"],
                    calls=tool_data["calls"],
                    total_tokens=tool_data["total_tokens"],
                    avg_tokens=tool_data["avg_tokens"],
                    call_history=call_history,
                    total_duration_ms=tool_data.get("total_duration_ms"),
                    avg_duration_ms=tool_data.get("avg_duration_ms"),
                    max_duration_ms=tool_data.get("max_duration_ms"),
                    min_duration_ms=tool_data.get("min_duration_ms"),
                )
                tools[tool_name] = tool_stats

            # Create ServerSession object
            server_session = ServerSession(
                schema_version=data["schema_version"],
                server=data["server"],
                tools=tools,
                total_calls=data["total_calls"],
                total_tokens=data["total_tokens"],
                metadata=data.get("metadata"),
            )

            return server_session

        except (json.JSONDecodeError, KeyError, ValueError) as e:
            print(f"Error loading server session from {server_file}: {e}")
            return None

    def list_sessions(self, limit: Optional[int] = None) -> List[Path]:
        """
        List all session directories.

        Args:
            limit: Maximum number of sessions to return (most recent first)

        Returns:
            List of session directory paths, sorted by timestamp (newest first)
        """
        if not self.base_dir.exists():
            return []

        # Get all directories
        session_dirs = [d for d in self.base_dir.iterdir() if d.is_dir()]

        # Sort by name (which includes timestamp)
        session_dirs.sort(reverse=True)

        # Apply limit if specified
        if limit:
            session_dirs = session_dirs[:limit]

        return session_dirs

    def find_incomplete_sessions(self) -> List[Path]:
        """
        Find sessions that are missing required files.

        Returns:
            List of incomplete session directory paths
        """
        incomplete = []

        for session_dir in self.list_sessions():
            summary_path = session_dir / "summary.json"
            if not summary_path.exists():
                incomplete.append(session_dir)

        return incomplete

    def recover_from_events(self, session_dir: Path) -> Optional[Session]:
        """
        Recover session data from events.jsonl file.

        Used when session was interrupted and summary.json is missing.

        Args:
            session_dir: Directory containing events.jsonl

        Returns:
            Recovered Session object if successful, None otherwise
        """
        events_file = session_dir / "events.jsonl"
        if not events_file.exists():
            return None

        print(f"Attempting recovery from {events_file}")

        # TODO: Implement event stream parsing and session reconstruction
        # This would parse events.jsonl line by line and rebuild the session
        # For now, return None (will be implemented in future)

        return None

    def cleanup_old_sessions(self, max_age_days: int = 30) -> int:
        """
        Remove sessions older than specified age.

        Args:
            max_age_days: Maximum age in days

        Returns:
            Number of sessions deleted
        """
        import shutil
        from datetime import timedelta

        cutoff_date = datetime.now() - timedelta(days=max_age_days)
        deleted_count = 0

        for session_dir in self.list_sessions():
            # Extract timestamp from directory name
            # Format: {project}-{YYYY-MM-DD-HHMMSS}
            try:
                parts = session_dir.name.rsplit("-", 4)
                if len(parts) >= 4:
                    date_str = "-".join(parts[-4:])  # YYYY-MM-DD-HHMMSS
                    session_date = datetime.strptime(date_str, "%Y-%m-%d-%H%M%S")

                    if session_date < cutoff_date:
                        shutil.rmtree(session_dir)
                        deleted_count += 1
            except (ValueError, IndexError):
                # Skip if can't parse timestamp
                continue

        return deleted_count


# ============================================================================
# Convenience Functions
# ============================================================================


def save_session(session: Session, session_dir: Path) -> Dict[str, Path]:
    """
    Convenience function to save a session.

    Args:
        session: Session object to save
        session_dir: Directory to save session files

    Returns:
        Dictionary mapping file type to file path
    """
    manager = SessionManager()
    return manager.save_session(session, session_dir)


def load_session(session_dir: Path) -> Optional[Session]:
    """
    Convenience function to load a session.

    Args:
        session_dir: Directory containing session files

    Returns:
        Session object if successful, None otherwise
    """
    manager = SessionManager()
    return manager.load_session(session_dir)


# ============================================================================
# Testing
# ============================================================================

if __name__ == "__main__":
    # Manual test
    print("Session Manager Module Tests")
    print("=" * 60)

    manager = SessionManager(base_dir=Path("test_sessions"))

    # Test session directory creation
    session_dir = manager.create_session_directory("test-session-001")
    print(f"Created session directory: {session_dir}")

    # Test listing sessions
    sessions = manager.list_sessions()
    print(f"\nFound {len(sessions)} sessions")

    # Test cleanup
    print("\nSession manager initialized successfully")
