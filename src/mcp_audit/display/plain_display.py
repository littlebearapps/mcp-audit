"""
PlainDisplay - Simple print-based display for CI/logging environments.

This adapter outputs plain text that works in any terminal, including
non-TTY environments like CI pipelines or log files.
"""

import time
from datetime import datetime

from .base import DisplayAdapter
from .snapshot import DisplaySnapshot


class PlainDisplay(DisplayAdapter):
    """Simple print-based display for CI/logging.

    Rate-limits update output to avoid log spam while still
    providing periodic progress information.
    """

    def __init__(self, print_interval: float = 5.0) -> None:
        """Initialize plain display.

        Args:
            print_interval: Minimum seconds between progress updates
        """
        self._last_print_time: float = 0
        self._print_interval = print_interval

    def start(self, snapshot: DisplaySnapshot) -> None:
        """Print header and initial state."""
        print("=" * 70)
        print(f"MCP Audit - {snapshot.platform}")
        print(f"Project: {snapshot.project}")
        print("=" * 70)
        print("Tracking started. Press Ctrl+C to stop.")
        print()

    def update(self, snapshot: DisplaySnapshot) -> None:
        """Print progress update (rate-limited)."""
        now = time.time()
        if now - self._last_print_time >= self._print_interval:
            self._last_print_time = now
            print(
                f"[{snapshot.duration_seconds:.0f}s] "
                f"Tokens: {snapshot.total_tokens:,} | "
                f"MCP calls: {snapshot.total_tool_calls} | "
                f"Cost: ${snapshot.cost_estimate:.4f}"
            )

    def on_event(self, tool_name: str, tokens: int, timestamp: datetime) -> None:
        """Print each tool call."""
        time_str = timestamp.strftime("%H:%M:%S")
        print(f"  [{time_str}] {tool_name} ({tokens:,} tokens)")

    def stop(self, snapshot: DisplaySnapshot) -> None:
        """Print final summary."""
        print()
        print("=" * 70)
        print("Session Complete")
        print("=" * 70)
        print(f"Total tokens: {snapshot.total_tokens:,}")
        print(f"Cost estimate: ${snapshot.cost_estimate:.4f}")
        print(f"MCP tool calls: {snapshot.total_tool_calls}")
        print(f"Cache efficiency: {snapshot.cache_efficiency:.0%}")
