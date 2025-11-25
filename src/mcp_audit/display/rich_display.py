"""
RichDisplay - Rich-based TUI with in-place updating.

Uses Rich's Live display for a beautiful, real-time updating dashboard
that shows session metrics without scrolling.
"""

import contextlib
from collections import deque
from datetime import datetime
from typing import Deque, Optional, Tuple

from rich.console import Console
from rich.layout import Layout
from rich.live import Live
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from .base import DisplayAdapter
from .snapshot import DisplaySnapshot


class RichDisplay(DisplayAdapter):
    """Rich-based TUI with in-place updating dashboard.

    Provides a beautiful terminal UI that updates in place,
    showing real-time token usage, tool calls, and activity.
    """

    def __init__(self, refresh_rate: float = 0.5) -> None:
        """Initialize Rich display.

        Args:
            refresh_rate: Display refresh rate in seconds (default 0.5 = 2Hz)
        """
        self.console = Console()
        self.refresh_rate = refresh_rate
        self.live: Optional[Live] = None
        self.recent_events: Deque[Tuple[datetime, str, int]] = deque(maxlen=5)
        self._current_snapshot: Optional[DisplaySnapshot] = None
        self._fallback_warned = False

    def start(self, snapshot: DisplaySnapshot) -> None:
        """Start the live display."""
        self._current_snapshot = snapshot
        self.live = Live(
            self._build_layout(snapshot),
            console=self.console,
            refresh_per_second=1 / self.refresh_rate,
            transient=False,
        )
        self.live.start()

    def update(self, snapshot: DisplaySnapshot) -> None:
        """Update display with new snapshot."""
        self._current_snapshot = snapshot
        if self.live:
            try:
                self.live.update(self._build_layout(snapshot))
            except Exception as e:
                # Graceful fallback if rendering fails
                if not self._fallback_warned:
                    import sys

                    print(
                        f"Warning: TUI rendering failed ({e}), continuing without updates",
                        file=sys.stderr,
                    )
                    self._fallback_warned = True

    def on_event(self, tool_name: str, tokens: int, timestamp: datetime) -> None:
        """Add event to recent activity feed."""
        self.recent_events.append((timestamp, tool_name, tokens))

    def stop(self, snapshot: DisplaySnapshot) -> None:
        """Stop live display and show final summary."""
        if self.live:
            with contextlib.suppress(Exception):
                self.live.stop()
            self.live = None
        self._print_final_summary(snapshot)

    def _build_layout(self, snapshot: DisplaySnapshot) -> Layout:
        """Build the dashboard layout."""
        layout = Layout()

        layout.split_column(
            Layout(self._build_header(snapshot), name="header", size=5),
            Layout(self._build_tokens(snapshot), name="tokens", size=5),
            Layout(self._build_tools(snapshot), name="tools", size=10),
            Layout(self._build_activity(), name="activity", size=8),
            Layout(self._build_footer(), name="footer", size=1),
        )

        return layout

    def _build_header(self, snapshot: DisplaySnapshot) -> Panel:
        """Build header panel with project info."""
        duration = self._format_duration(snapshot.duration_seconds)

        header_text = Text()
        header_text.append("MCP Audit - Live Session", style="bold cyan")
        header_text.append(f"  [{snapshot.platform}]", style="dim")
        header_text.append(f"\nProject: {snapshot.project}", style="white")
        header_text.append(f"  Duration: {duration}", style="dim")

        return Panel(header_text, border_style="cyan")

    def _build_tokens(self, snapshot: DisplaySnapshot) -> Panel:
        """Build token usage panel."""
        table = Table(show_header=False, box=None, padding=(0, 2))
        table.add_column("Label", style="dim")
        table.add_column("Value", justify="right")
        table.add_column("Label2", style="dim")
        table.add_column("Value2", justify="right")
        table.add_column("Label3", style="dim")
        table.add_column("Value3", justify="right")

        table.add_row(
            "Input:",
            f"{snapshot.input_tokens:,}",
            "Output:",
            f"{snapshot.output_tokens:,}",
            "Cache:",
            f"{snapshot.cache_tokens:,}",
        )
        table.add_row(
            "Total:",
            f"{snapshot.total_tokens:,}",
            "Efficiency:",
            f"{snapshot.cache_efficiency:.0%}",
            "Cost:",
            f"${snapshot.cost_estimate:.4f}",
        )

        return Panel(table, title="Token Usage", border_style="green")

    def _build_tools(self, snapshot: DisplaySnapshot) -> Panel:
        """Build MCP tools table."""
        table = Table(box=None)
        table.add_column("Tool", style="cyan", no_wrap=True)
        table.add_column("Calls", justify="right")
        table.add_column("Tokens", justify="right")
        table.add_column("Avg/Call", justify="right", style="dim")

        for tool_data in snapshot.top_tools[:5]:
            name, calls, tokens, avg = tool_data
            # Truncate long tool names
            display_name = name if len(name) <= 35 else name[:32] + "..."
            table.add_row(display_name, str(calls), f"{tokens:,}", f"{avg:,}")

        if not snapshot.top_tools:
            table.add_row("No MCP tools called yet", "", "", "")

        return Panel(
            table,
            title=f"MCP Tools ({snapshot.total_tool_calls} calls)",
            border_style="yellow",
        )

    def _build_activity(self) -> Panel:
        """Build recent activity panel."""
        if not self.recent_events:
            content = Text("Waiting for events...", style="dim italic")
        else:
            content = Text()
            for timestamp, tool_name, tokens in self.recent_events:
                time_str = timestamp.strftime("%H:%M:%S")
                short_name = tool_name if len(tool_name) <= 40 else tool_name[:37] + "..."
                content.append(f"[{time_str}] ", style="dim")
                content.append(f"{short_name}", style="cyan")
                content.append(f" ({tokens:,} tokens)\n", style="dim")

        return Panel(content, title="Recent Activity", border_style="blue")

    def _build_footer(self) -> Text:
        """Build footer with instructions."""
        return Text(
            "Press Ctrl+C to stop and save session",
            style="dim italic",
            justify="center",
        )

    def _format_duration(self, seconds: float) -> str:
        """Format duration as HH:MM:SS."""
        hours, remainder = divmod(int(seconds), 3600)
        minutes, secs = divmod(remainder, 60)
        return f"{hours:02d}:{minutes:02d}:{secs:02d}"

    def _print_final_summary(self, snapshot: DisplaySnapshot) -> None:
        """Print final summary after stopping."""
        self.console.print()
        self.console.print(
            Panel(
                f"[bold green]Session Complete![/bold green]\n\n"
                f"Total tokens: {snapshot.total_tokens:,}\n"
                f"Cost estimate: ${snapshot.cost_estimate:.4f}\n"
                f"MCP tool calls: {snapshot.total_tool_calls}\n"
                f"Cache efficiency: {snapshot.cache_efficiency:.0%}",
                title="Session Summary",
                border_style="green",
            )
        )
