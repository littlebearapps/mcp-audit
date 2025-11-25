"""
DisplaySnapshot - Immutable snapshot of session state for display.

This dataclass captures all the information needed to render a display,
allowing the display layer to be completely decoupled from tracking logic.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Tuple


@dataclass(frozen=True)
class DisplaySnapshot:
    """Immutable snapshot of session state for display rendering."""

    # Session metadata
    project: str
    platform: str
    start_time: datetime
    duration_seconds: float

    # Token metrics
    input_tokens: int
    output_tokens: int
    cache_tokens: int  # cache_read + cache_created
    total_tokens: int
    cache_efficiency: float  # 0.0 to 1.0
    cost_estimate: float

    # Tool metrics
    total_tool_calls: int
    unique_tools: int
    top_tools: Tuple[Tuple[str, int, int, int], ...] = field(default_factory=tuple)
    # Each tuple is (name, calls, tokens, avg_per_call)

    # Recent activity (newest first)
    recent_events: Tuple[Tuple[datetime, str, int], ...] = field(default_factory=tuple)
    # Each tuple is (timestamp, tool_name, tokens)

    @classmethod
    def create(
        cls,
        project: str,
        platform: str,
        start_time: datetime,
        duration_seconds: float,
        input_tokens: int = 0,
        output_tokens: int = 0,
        cache_tokens: int = 0,
        total_tokens: int = 0,
        cache_efficiency: float = 0.0,
        cost_estimate: float = 0.0,
        total_tool_calls: int = 0,
        unique_tools: int = 0,
        top_tools: List[Tuple[str, int, int, int]] | None = None,
        recent_events: List[Tuple[datetime, str, int]] | None = None,
    ) -> "DisplaySnapshot":
        """Factory method to create a DisplaySnapshot with proper tuple conversion."""
        return cls(
            project=project,
            platform=platform,
            start_time=start_time,
            duration_seconds=duration_seconds,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            cache_tokens=cache_tokens,
            total_tokens=total_tokens,
            cache_efficiency=cache_efficiency,
            cost_estimate=cost_estimate,
            total_tool_calls=total_tool_calls,
            unique_tools=unique_tools,
            top_tools=tuple(top_tools) if top_tools else (),
            recent_events=tuple(recent_events) if recent_events else (),
        )
