#!/usr/bin/env python3
"""
BaseTracker - Abstract base class for platform-specific MCP trackers

Provides a stable adapter interface for Claude Code, Codex CLI, Gemini CLI, and future platforms.
"""

import hashlib
import json
import warnings
from abc import ABC, abstractmethod
from collections import defaultdict
from dataclasses import asdict, dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# Schema version (LOCKED - see docs/CORE-SCHEMA-SPEC.md)
SCHEMA_VERSION = "1.0.0"


# ============================================================================
# Core Data Structures (Schema v1.0.0)
# ============================================================================


@dataclass
class Call:
    """Single MCP tool call record"""

    schema_version: str = SCHEMA_VERSION
    timestamp: datetime = field(default_factory=datetime.now)
    tool_name: str = ""
    input_tokens: int = 0
    output_tokens: int = 0
    cache_created_tokens: int = 0
    cache_read_tokens: int = 0
    total_tokens: int = 0
    duration_ms: int = 0  # 0 if not available
    content_hash: Optional[str] = None
    platform_data: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to JSON-serializable dict"""
        data = asdict(self)
        data["timestamp"] = self.timestamp.isoformat()
        return data


@dataclass
class ToolStats:
    """Statistics for a single MCP tool"""

    schema_version: str = SCHEMA_VERSION
    calls: int = 0
    total_tokens: int = 0
    avg_tokens: float = 0.0
    call_history: List[Call] = field(default_factory=list)
    total_duration_ms: Optional[int] = None
    avg_duration_ms: Optional[float] = None
    max_duration_ms: Optional[int] = None
    min_duration_ms: Optional[int] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to JSON-serializable dict"""
        data = asdict(self)
        data["call_history"] = [call.to_dict() for call in self.call_history]
        return data


@dataclass
class ServerSession:
    """Statistics for a single MCP server"""

    schema_version: str = SCHEMA_VERSION
    server: str = ""
    tools: Dict[str, ToolStats] = field(default_factory=dict)
    total_calls: int = 0
    total_tokens: int = 0
    metadata: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to JSON-serializable dict"""
        data = asdict(self)
        data["tools"] = {name: stats.to_dict() for name, stats in self.tools.items()}
        return data


@dataclass
class TokenUsage:
    """Token usage statistics"""

    input_tokens: int = 0
    output_tokens: int = 0
    cache_created_tokens: int = 0
    cache_read_tokens: int = 0
    total_tokens: int = 0
    cache_efficiency: float = 0.0


@dataclass
class MCPToolCalls:
    """MCP tool call summary"""

    total_calls: int = 0
    unique_tools: int = 0
    most_called: str = ""


@dataclass
class Session:
    """Complete session data"""

    schema_version: str = SCHEMA_VERSION
    project: str = ""
    platform: str = ""  # "claude-code", "codex-cli", "gemini-cli"
    timestamp: datetime = field(default_factory=datetime.now)
    session_id: str = ""
    token_usage: TokenUsage = field(default_factory=TokenUsage)
    cost_estimate: float = 0.0
    mcp_tool_calls: MCPToolCalls = field(default_factory=MCPToolCalls)
    server_sessions: Dict[str, ServerSession] = field(default_factory=dict)
    redundancy_analysis: Optional[Dict[str, Any]] = None
    anomalies: List[Dict[str, Any]] = field(default_factory=list)
    end_timestamp: Optional[datetime] = None
    duration_seconds: Optional[float] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to JSON-serializable dict"""
        data = asdict(self)
        data["timestamp"] = self.timestamp.isoformat()
        if self.end_timestamp:
            data["end_timestamp"] = self.end_timestamp.isoformat()
        data["token_usage"] = asdict(self.token_usage)
        data["mcp_tool_calls"] = asdict(self.mcp_tool_calls)
        data["server_sessions"] = {
            name: sess.to_dict() for name, sess in self.server_sessions.items()
        }
        return data


# ============================================================================
# BaseTracker Abstract Class
# ============================================================================


class BaseTracker(ABC):
    """
    Abstract base class for platform-specific MCP trackers.

    Provides common functionality and defines the adapter interface
    that all platform trackers must implement.
    """

    def __init__(self, project: str, platform: str):
        """
        Initialize base tracker.

        Args:
            project: Project name (e.g., "mcp-audit")
            platform: Platform identifier (e.g., "claude-code", "codex-cli", "gemini-cli")
        """
        self.project = project
        self.platform = platform
        self.timestamp = datetime.now()
        self.session_id = self._generate_session_id()

        # Session data
        self.session = Session(
            project=project, platform=platform, timestamp=self.timestamp, session_id=self.session_id
        )

        # Server sessions (key: server name)
        self.server_sessions: Dict[str, ServerSession] = {}

        # Duplicate detection (key: content_hash)
        self.content_hashes: Dict[str, List[Call]] = defaultdict(list)

        # Session directory
        self.session_dir: Optional[Path] = None

    def _generate_session_id(self) -> str:
        """Generate unique session ID"""
        timestamp_str = self.timestamp.strftime("%Y-%m-%dT%H-%M-%S")
        return f"{self.project}-{timestamp_str}"

    # ========================================================================
    # Abstract Methods (Platform-specific implementation required)
    # ========================================================================

    @abstractmethod
    def start_tracking(self) -> None:
        """
        Start tracking session.

        Platform-specific implementation:
        - Claude Code: Start tailing debug.log
        - Codex CLI: Start process wrapper
        - Gemini CLI: Start process wrapper with --debug
        """
        pass

    @abstractmethod
    def parse_event(self, event_data: Any) -> Optional[Tuple[str, Dict[str, Any]]]:
        """
        Parse platform-specific event into normalized format.

        Args:
            event_data: Raw event data (line, JSON object, etc.)

        Returns:
            Tuple of (tool_name, usage_dict) if MCP tool call, None otherwise

        Platform-specific parsing:
        - Claude Code: Parse debug.log JSON event
        - Codex CLI: Parse stdout/stderr text
        - Gemini CLI: Parse debug output or checkpoint
        """
        pass

    @abstractmethod
    def get_platform_metadata(self) -> Dict[str, Any]:
        """
        Get platform-specific metadata.

        Returns:
            Dictionary with platform-specific data
            (e.g., model, debug_log_path, checkpoint_path)
        """
        pass

    # ========================================================================
    # Normalization (Shared implementation)
    # ========================================================================

    def normalize_server_name(self, tool_name: str) -> str:
        """
        Extract and normalize server name from tool name.

        Examples:
            "mcp__zen__chat" → "zen"
            "mcp__zen-mcp__chat" → "zen" (Codex CLI format)
            "mcp__brave-search__web" → "brave-search"

        Args:
            tool_name: Full MCP tool name

        Returns:
            Normalized server name
        """
        if not tool_name.startswith("mcp__"):
            warnings.warn(f"Tool name doesn't start with 'mcp__': {tool_name}", stacklevel=2)
            return "unknown"

        # Remove mcp__ prefix
        name_parts = tool_name[5:].split("__")

        # Handle Codex CLI format: mcp__zen-mcp__chat
        server_name = name_parts[0]
        if server_name.endswith("-mcp"):
            server_name = server_name[:-4]

        return server_name

    def normalize_tool_name(self, tool_name: str) -> str:
        """
        Normalize tool name to consistent format.

        Examples:
            "mcp__zen-mcp__chat" → "mcp__zen__chat" (Codex CLI)
            "mcp__zen__chat" → "mcp__zen__chat" (Claude Code)

        Args:
            tool_name: Raw tool name from platform

        Returns:
            Normalized tool name (Claude Code format)
        """
        # Strip -mcp suffix from server name (Codex CLI compatibility)
        if "-mcp__" in tool_name:
            parts = tool_name.split("__")
            if len(parts) >= 2 and parts[0] == "mcp":
                server_name = parts[1].replace("-mcp", "")
                tool_suffix = "__".join(parts[2:])
                return f"mcp__{server_name}__{tool_suffix}"

        return tool_name

    # ========================================================================
    # Session Management (Shared implementation)
    # ========================================================================

    def record_tool_call(
        self,
        tool_name: str,
        input_tokens: int,
        output_tokens: int,
        cache_created_tokens: int = 0,
        cache_read_tokens: int = 0,
        duration_ms: int = 0,
        content_hash: Optional[str] = None,
        platform_data: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Record a single MCP tool call.

        Args:
            tool_name: Normalized tool name
            input_tokens: Input token count
            output_tokens: Output token count
            cache_created_tokens: Cache creation tokens
            cache_read_tokens: Cache read tokens
            duration_ms: Call duration in milliseconds (0 if not available)
            content_hash: SHA256 hash of input (for duplicate detection)
            platform_data: Platform-specific metadata
        """
        # Normalize tool name
        normalized_tool = self.normalize_tool_name(tool_name)
        server_name = self.normalize_server_name(normalized_tool)

        # Create Call object
        total_tokens = input_tokens + output_tokens + cache_created_tokens + cache_read_tokens
        call = Call(
            timestamp=datetime.now(),
            tool_name=normalized_tool,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            cache_created_tokens=cache_created_tokens,
            cache_read_tokens=cache_read_tokens,
            total_tokens=total_tokens,
            duration_ms=duration_ms,
            content_hash=content_hash,
            platform_data=platform_data,
        )

        # Track duplicate calls
        if content_hash:
            self.content_hashes[content_hash].append(call)

        # Get or create server session
        if server_name not in self.server_sessions:
            self.server_sessions[server_name] = ServerSession(server=server_name)

        server_session = self.server_sessions[server_name]

        # Get or create tool stats
        if normalized_tool not in server_session.tools:
            server_session.tools[normalized_tool] = ToolStats()

        tool_stats = server_session.tools[normalized_tool]

        # Update tool stats
        tool_stats.calls += 1
        tool_stats.total_tokens += total_tokens
        tool_stats.avg_tokens = tool_stats.total_tokens / tool_stats.calls
        tool_stats.call_history.append(call)

        # Update duration stats (if available)
        if duration_ms > 0:
            if tool_stats.total_duration_ms is None:
                tool_stats.total_duration_ms = 0
            tool_stats.total_duration_ms += duration_ms
            tool_stats.avg_duration_ms = tool_stats.total_duration_ms / tool_stats.calls

            if tool_stats.max_duration_ms is None or duration_ms > tool_stats.max_duration_ms:
                tool_stats.max_duration_ms = duration_ms

            if tool_stats.min_duration_ms is None or duration_ms < tool_stats.min_duration_ms:
                tool_stats.min_duration_ms = duration_ms

        # Update server totals
        server_session.total_calls += 1
        server_session.total_tokens += total_tokens

        # Update session token usage
        self.session.token_usage.input_tokens += input_tokens
        self.session.token_usage.output_tokens += output_tokens
        self.session.token_usage.cache_created_tokens += cache_created_tokens
        self.session.token_usage.cache_read_tokens += cache_read_tokens
        self.session.token_usage.total_tokens += total_tokens

        # Recalculate cache efficiency
        if self.session.token_usage.total_tokens > 0:
            self.session.token_usage.cache_efficiency = (
                self.session.token_usage.cache_read_tokens / self.session.token_usage.total_tokens
            )

    def finalize_session(self) -> Session:
        """
        Finalize session data and calculate summary statistics.

        Returns:
            Complete Session object
        """
        # Update session end time
        self.session.end_timestamp = datetime.now()
        self.session.duration_seconds = (
            self.session.end_timestamp - self.session.timestamp
        ).total_seconds()

        # Update MCP tool calls summary
        all_tools = set()
        most_called_tool = ""
        most_called_count = 0

        for server_session in self.server_sessions.values():
            for tool_name, tool_stats in server_session.tools.items():
                all_tools.add(tool_name)
                if tool_stats.calls > most_called_count:
                    most_called_count = tool_stats.calls
                    most_called_tool = f"{tool_name} ({tool_stats.calls} calls)"

        self.session.mcp_tool_calls.total_calls = sum(
            ss.total_calls for ss in self.server_sessions.values()
        )
        self.session.mcp_tool_calls.unique_tools = len(all_tools)
        self.session.mcp_tool_calls.most_called = most_called_tool

        # Add server sessions to session
        self.session.server_sessions = self.server_sessions

        # Analyze duplicates
        self.session.redundancy_analysis = self._analyze_redundancy()

        # Detect anomalies
        self.session.anomalies = self._detect_anomalies()

        return self.session

    def _analyze_redundancy(self) -> Dict[str, Any]:
        """Analyze duplicate tool calls"""
        duplicate_calls = 0
        potential_savings = 0

        for _content_hash, calls in self.content_hashes.items():
            if len(calls) > 1:
                duplicate_calls += len(calls) - 1
                # Calculate savings (all calls after first could be cached)
                for call in calls[1:]:
                    potential_savings += call.total_tokens

        return {"duplicate_calls": duplicate_calls, "potential_savings": potential_savings}

    def _detect_anomalies(self) -> List[Dict[str, Any]]:
        """Detect anomalies in tool usage"""
        anomalies = []

        for server_session in self.server_sessions.values():
            for tool_name, tool_stats in server_session.tools.items():
                # High frequency (>10 calls)
                if tool_stats.calls > 10:
                    anomalies.append(
                        {
                            "type": "high_frequency",
                            "tool": tool_name,
                            "calls": tool_stats.calls,
                            "threshold": 10,
                        }
                    )

                # High average tokens (>100K per call)
                if tool_stats.avg_tokens > 100000:
                    anomalies.append(
                        {
                            "type": "high_avg_tokens",
                            "tool": tool_name,
                            "avg_tokens": tool_stats.avg_tokens,
                            "threshold": 100000,
                        }
                    )

        return anomalies

    # ========================================================================
    # Persistence (Shared implementation)
    # ========================================================================

    def save_session(self, output_dir: Path) -> None:
        """
        Save session data to disk.

        Args:
            output_dir: Directory to save session files
        """
        self.session_dir = output_dir / self.session_id
        self.session_dir.mkdir(parents=True, exist_ok=True)

        # Save session summary
        summary_path = self.session_dir / "summary.json"
        with open(summary_path, "w") as f:
            json.dump(self.session.to_dict(), f, indent=2, default=str)

        # Save per-server sessions
        for server_name, server_session in self.server_sessions.items():
            server_path = self.session_dir / f"mcp-{server_name}.json"
            with open(server_path, "w") as f:
                json.dump(server_session.to_dict(), f, indent=2, default=str)

    # ========================================================================
    # Unrecognized Line Handler (Shared implementation)
    # ========================================================================

    def handle_unrecognized_line(self, line: str) -> None:
        """
        Handle unrecognized event lines gracefully.

        Args:
            line: Unrecognized event line
        """
        # Log warning but don't crash
        warnings.warn(f"Unrecognized event format: {line[:100]}...", stacklevel=2)

    # ========================================================================
    # Utility Methods
    # ========================================================================

    @staticmethod
    def compute_content_hash(input_data: Any) -> str:
        """
        Compute SHA256 hash of input data for duplicate detection.

        Args:
            input_data: Tool input parameters

        Returns:
            SHA256 hash string
        """
        # Convert to stable JSON string
        json_str = json.dumps(input_data, sort_keys=True)
        return hashlib.sha256(json_str.encode()).hexdigest()
