# TUI Implementation Plan - mcp-audit

**Created**: 2025-11-25
**Status**: Ready for Implementation
**Estimated Effort**: 4-6 days
**Validated By**: GPT-5.1 via zen thinkdeep

---

## Executive Summary

Replace mcp-audit's current scrolling `print()` output with a proper in-place updating terminal UI using the **Rich** library. The implementation follows a **Display Adapter Pattern** that separates rendering from tracking logic, enabling:

- Beautiful real-time dashboard display
- Backward compatibility (plain mode for CI/logs)
- Easy testing (mock display adapters)
- Graceful degradation for non-TTY environments

---

## Current State

### Problem
- CLI uses plain `print()` statements that scroll/duplicate
- Documentation shows fancy mockups that don't match reality
- No real-time updating - output pushes old content up
- Poor user experience for monitoring sessions

### Current Implementation
```python
# cli.py - simple print-based output
print("=" * 70)
print("MCP Analyze - Collect Session Data")
print(f"Platform: {platform}")
print(f"Total tokens: {session.token_usage.total_tokens:,}")
```

---

## Solution: Rich Library with Live Display

### Why Rich?

| Criteria | Rich | Textual | Curses |
|----------|------|---------|--------|
| GitHub Stars | 49K+ | 25K+ | stdlib |
| Complexity | Low | High | Medium |
| Cross-platform | Yes | Yes | Limited |
| Dependencies | Zero | Rich | None |
| Learning Curve | Easy | Moderate | Steep |
| Our Use Case Fit | Perfect | Overkill | Too low-level |

**Decision**: Rich with `Live` display - provides exactly what we need without full TUI framework complexity.

### Key Rich Features We'll Use

```python
from rich.console import Console
from rich.live import Live          # In-place updating
from rich.table import Table        # Formatted tables
from rich.panel import Panel        # Bordered sections
from rich.layout import Layout      # Dashboard layout
from rich.text import Text          # Styled text
```

---

## Architecture: Display Adapter Pattern

### Design Principles

1. **Separation of Concerns**: Display logic completely separate from tracking logic
2. **Backward Compatibility**: Plain mode still works for CI/logging
3. **Testability**: Display adapters can be mocked/stubbed
4. **Graceful Degradation**: Falls back to plain output if Rich unavailable or non-TTY

### Module Structure

```
src/mcp_audit/
├── display/
│   ├── __init__.py          # Exports + factory function
│   ├── base.py              # DisplayAdapter ABC
│   ├── rich_display.py      # Rich TUI implementation
│   ├── plain_display.py     # Scrolling print fallback
│   ├── null_display.py      # Silent mode
│   └── snapshot.py          # DisplaySnapshot dataclass
├── base_tracker.py          # Modified to accept display adapter
├── cli.py                   # New --tui/--plain/--quiet flags
└── ...
```

### Core Interfaces

```python
# display/base.py
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional
from collections import deque


@dataclass
class DisplaySnapshot:
    """Immutable snapshot of session state for display."""
    project: str
    platform: str
    start_time: datetime
    duration_seconds: float

    # Token metrics
    input_tokens: int
    output_tokens: int
    cache_tokens: int
    total_tokens: int
    cache_efficiency: float
    cost_estimate: float

    # Tool metrics
    total_tool_calls: int
    unique_tools: int
    top_tools: List[tuple]  # [(name, calls, tokens, avg), ...]

    # Recent activity
    recent_events: deque  # [(timestamp, tool_name, tokens), ...]


class DisplayAdapter(ABC):
    """Abstract base class for display implementations."""

    @abstractmethod
    def start(self, snapshot: DisplaySnapshot) -> None:
        """Initialize display with initial state."""
        pass

    @abstractmethod
    def update(self, snapshot: DisplaySnapshot) -> None:
        """Update display with new snapshot."""
        pass

    @abstractmethod
    def on_event(self, tool_name: str, tokens: int, timestamp: datetime) -> None:
        """Handle individual event (for recent activity)."""
        pass

    @abstractmethod
    def stop(self, snapshot: DisplaySnapshot) -> None:
        """Finalize display and show summary."""
        pass

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        return False
```

### RichDisplay Implementation

```python
# display/rich_display.py
from collections import deque
from datetime import datetime
from typing import Optional

from rich.console import Console
from rich.live import Live
from rich.table import Table
from rich.panel import Panel
from rich.layout import Layout
from rich.text import Text

from .base import DisplayAdapter, DisplaySnapshot


class RichDisplay(DisplayAdapter):
    """Rich-based TUI with in-place updating."""

    def __init__(self, refresh_rate: float = 0.5):
        self.console = Console()
        self.refresh_rate = refresh_rate
        self.live: Optional[Live] = None
        self.recent_events: deque = deque(maxlen=5)
        self._current_snapshot: Optional[DisplaySnapshot] = None

    def start(self, snapshot: DisplaySnapshot) -> None:
        self._current_snapshot = snapshot
        self.live = Live(
            self._build_layout(snapshot),
            console=self.console,
            refresh_per_second=1/self.refresh_rate,
            transient=False
        )
        self.live.start()

    def update(self, snapshot: DisplaySnapshot) -> None:
        self._current_snapshot = snapshot
        if self.live:
            self.live.update(self._build_layout(snapshot))

    def on_event(self, tool_name: str, tokens: int, timestamp: datetime) -> None:
        self.recent_events.append((timestamp, tool_name, tokens))

    def stop(self, snapshot: DisplaySnapshot) -> None:
        if self.live:
            self.live.stop()
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
            "Input:", f"{snapshot.input_tokens:,}",
            "Output:", f"{snapshot.output_tokens:,}",
            "Cache:", f"{snapshot.cache_tokens:,}"
        )
        table.add_row(
            "Total:", f"{snapshot.total_tokens:,}",
            "Efficiency:", f"{snapshot.cache_efficiency:.0%}",
            "Cost:", f"${snapshot.cost_estimate:.4f}"
        )

        return Panel(table, title="Token Usage", border_style="green")

    def _build_tools(self, snapshot: DisplaySnapshot) -> Panel:
        """Build MCP tools table."""
        table = Table(box=None)
        table.add_column("Tool", style="cyan", no_wrap=True)
        table.add_column("Calls", justify="right")
        table.add_column("Tokens", justify="right")
        table.add_column("Avg/Call", justify="right", style="dim")

        for name, calls, tokens, avg in snapshot.top_tools[:5]:
            # Truncate long tool names
            display_name = name if len(name) <= 35 else name[:32] + "..."
            table.add_row(
                display_name,
                str(calls),
                f"{tokens:,}",
                f"{avg:,}"
            )

        if not snapshot.top_tools:
            table.add_row("No MCP tools called yet", "", "", "")

        return Panel(table, title=f"MCP Tools ({snapshot.total_tool_calls} calls)", border_style="yellow")

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
        return Text("Press Ctrl+C to stop and save session", style="dim italic", justify="center")

    def _format_duration(self, seconds: float) -> str:
        """Format duration as HH:MM:SS."""
        hours, remainder = divmod(int(seconds), 3600)
        minutes, secs = divmod(remainder, 60)
        return f"{hours:02d}:{minutes:02d}:{secs:02d}"

    def _print_final_summary(self, snapshot: DisplaySnapshot) -> None:
        """Print final summary after stopping."""
        self.console.print()
        self.console.print(Panel(
            f"[bold green]Session Complete![/bold green]\n\n"
            f"Total tokens: {snapshot.total_tokens:,}\n"
            f"Cost estimate: ${snapshot.cost_estimate:.4f}\n"
            f"MCP tool calls: {snapshot.total_tool_calls}\n"
            f"Cache efficiency: {snapshot.cache_efficiency:.0%}",
            title="Session Summary",
            border_style="green"
        ))
```

### PlainDisplay Implementation

```python
# display/plain_display.py
from datetime import datetime
from .base import DisplayAdapter, DisplaySnapshot


class PlainDisplay(DisplayAdapter):
    """Simple print-based display for CI/logging."""

    def __init__(self):
        self._last_print_time = 0
        self._print_interval = 5.0  # Print update every 5 seconds

    def start(self, snapshot: DisplaySnapshot) -> None:
        print("=" * 70)
        print(f"MCP Audit - {snapshot.platform}")
        print(f"Project: {snapshot.project}")
        print("=" * 70)
        print("Tracking started. Press Ctrl+C to stop.")
        print()

    def update(self, snapshot: DisplaySnapshot) -> None:
        # Rate-limit updates to avoid log spam
        import time
        now = time.time()
        if now - self._last_print_time >= self._print_interval:
            self._last_print_time = now
            print(f"[{snapshot.duration_seconds:.0f}s] "
                  f"Tokens: {snapshot.total_tokens:,} | "
                  f"MCP calls: {snapshot.total_tool_calls} | "
                  f"Cost: ${snapshot.cost_estimate:.4f}")

    def on_event(self, tool_name: str, tokens: int, timestamp: datetime) -> None:
        time_str = timestamp.strftime("%H:%M:%S")
        print(f"  [{time_str}] {tool_name} ({tokens:,} tokens)")

    def stop(self, snapshot: DisplaySnapshot) -> None:
        print()
        print("=" * 70)
        print("Session Complete")
        print("=" * 70)
        print(f"Total tokens: {snapshot.total_tokens:,}")
        print(f"Cost estimate: ${snapshot.cost_estimate:.4f}")
        print(f"MCP tool calls: {snapshot.total_tool_calls}")
        print(f"Cache efficiency: {snapshot.cache_efficiency:.0%}")
```

### NullDisplay Implementation

```python
# display/null_display.py
from datetime import datetime
from .base import DisplayAdapter, DisplaySnapshot


class NullDisplay(DisplayAdapter):
    """Silent display for --quiet mode."""

    def start(self, snapshot: DisplaySnapshot) -> None:
        pass

    def update(self, snapshot: DisplaySnapshot) -> None:
        pass

    def on_event(self, tool_name: str, tokens: int, timestamp: datetime) -> None:
        pass

    def stop(self, snapshot: DisplaySnapshot) -> None:
        pass
```

### Factory Function

```python
# display/__init__.py
import sys
from typing import Optional
from .base import DisplayAdapter, DisplaySnapshot
from .plain_display import PlainDisplay
from .null_display import NullDisplay


def create_display(
    mode: str = "auto",
    refresh_rate: float = 0.5
) -> DisplayAdapter:
    """
    Factory function to create appropriate display adapter.

    Args:
        mode: "tui", "plain", "quiet", or "auto"
        refresh_rate: Refresh rate for TUI mode (default 0.5s = 2Hz)

    Returns:
        DisplayAdapter instance
    """
    if mode == "quiet":
        return NullDisplay()

    if mode == "plain":
        return PlainDisplay()

    if mode == "tui" or mode == "auto":
        # Check if stdout is a TTY
        if not sys.stdout.isatty():
            if mode == "tui":
                print("Warning: --tui requested but stdout is not a TTY. Falling back to plain mode.",
                      file=sys.stderr)
            return PlainDisplay()

        # Try to import Rich
        try:
            from .rich_display import RichDisplay
            return RichDisplay(refresh_rate=refresh_rate)
        except ImportError:
            if mode == "tui":
                raise ImportError(
                    "Rich TUI mode requires the 'rich' package. "
                    "Install with: pip install mcp-audit[tui] or pip install rich"
                )
            return PlainDisplay()

    raise ValueError(f"Unknown display mode: {mode}")


__all__ = [
    "DisplayAdapter",
    "DisplaySnapshot",
    "PlainDisplay",
    "NullDisplay",
    "create_display",
]
```

---

## CLI Integration

### Updated CLI Flags

```python
# cli.py - updated collect command
collect_parser.add_argument(
    "--tui",
    action="store_true",
    default=True,
    help="Use rich TUI display (default)"
)

collect_parser.add_argument(
    "--plain",
    action="store_true",
    help="Use plain text output (for CI/logs)"
)

collect_parser.add_argument(
    "--quiet",
    action="store_true",
    help="Suppress all display output"
)

collect_parser.add_argument(
    "--refresh-rate",
    type=float,
    default=0.5,
    help="TUI refresh rate in seconds (default: 0.5)"
)
```

### Display Mode Selection Logic

```python
def get_display_mode(args) -> str:
    """Determine display mode from CLI args."""
    if args.quiet:
        return "quiet"
    if args.plain:
        return "plain"
    if args.no_logs:
        return "quiet"
    return "auto"  # Will use TUI if TTY, else plain
```

---

## Target UI Design

```
╭─────────────────────────────────────────────────────────────────╮
│ MCP Audit - Live Session                        [claude-code]   │
│ Project: mcp-audit                    Duration: 00:05:32        │
╰─────────────────────────────────────────────────────────────────╯

┌─ Token Usage ───────────────────────────────────────────────────┐
│  Input:      45,231  │  Output:    12,543  │  Cache:   125,432  │
│  Total:     183,206  │  Efficiency:   68%  │  Cost:      $0.23  │
└─────────────────────────────────────────────────────────────────┘

┌─ MCP Tools (42 calls) ──────────────────────────────────────────┐
│  Tool                         Calls    Tokens    Avg/Call       │
│  mcp__zen__thinkdeep              3   112,345      37,448       │
│  mcp__zen__chat                  15    45,678       3,045       │
│  mcp__brave-search__web           8    23,456       2,932       │
│  mcp__context7__lookup            5    12,345       2,469       │
│  mcp__zen__debug                  4     8,765       2,191       │
└─────────────────────────────────────────────────────────────────┘

┌─ Recent Activity ───────────────────────────────────────────────┐
│  [10:32:15] mcp__zen__chat (3,421 tokens)                       │
│  [10:32:45] mcp__brave-search__web (8,765 tokens)               │
│  [10:33:12] mcp__zen__thinkdeep (45,678 tokens)                 │
└─────────────────────────────────────────────────────────────────┘

Press Ctrl+C to stop and save session
```

---

## Implementation Timeline

### Phase 1: Core Display Module (Days 1-2)

**Day 1:**
- [ ] Create `src/mcp_audit/display/` directory structure
- [ ] Implement `DisplaySnapshot` dataclass
- [ ] Implement `DisplayAdapter` ABC
- [ ] Implement `PlainDisplay` adapter
- [ ] Implement `NullDisplay` adapter
- [ ] Write unit tests for Plain and Null displays

**Day 2:**
- [ ] Implement `RichDisplay` adapter
- [ ] Implement factory function with TTY detection
- [ ] Add Rich to optional dependencies
- [ ] Write unit tests for RichDisplay layout building

### Phase 2: Integration (Days 3-4)

**Day 3:**
- [ ] Update `cli.py` with new display flags
- [ ] Modify `BaseTracker` to accept display adapter
- [ ] Wire display updates into tracker monitor loops
- [ ] Update `ClaudeCodeAdapter` integration

**Day 4:**
- [ ] Update `CodexCLIAdapter` integration
- [ ] Update `GeminiCLIAdapter` integration
- [ ] Integration tests with mock trackers
- [ ] Test all three display modes

### Phase 3: Polish (Days 5-6)

**Day 5:**
- [ ] Responsive layout (handle narrow terminals)
- [ ] Truncate long tool names gracefully
- [ ] Add color themes (optional)
- [ ] Error handling and fallback robustness

**Day 6:**
- [ ] Update all documentation
- [ ] Update README with TUI screenshots
- [ ] Update platform guides
- [ ] Create backlog task and mark complete

---

## Dependencies

### pyproject.toml Changes

```toml
[project.optional-dependencies]
dev = [
    # ... existing dev deps
]
tui = [
    "rich>=13.0.0",
]
all = [
    "mcp-audit[dev,tui]",
]

# Or include Rich by default (recommended - zero dependencies, small size)
[project]
dependencies = [
    "rich>=13.0.0",
]
```

**Recommendation**: Include Rich by default. It's zero-dependency, ~5MB, and provides significant UX improvement.

---

## Testing Strategy

### Unit Tests

```python
# tests/test_display.py

def test_plain_display_start():
    """Test PlainDisplay prints header."""
    display = PlainDisplay()
    snapshot = create_test_snapshot()

    with captured_output() as output:
        display.start(snapshot)

    assert "MCP Audit" in output.getvalue()
    assert snapshot.project in output.getvalue()


def test_rich_display_layout_building():
    """Test RichDisplay builds correct layout structure."""
    display = RichDisplay()
    snapshot = create_test_snapshot()

    layout = display._build_layout(snapshot)

    assert "header" in layout.children
    assert "tokens" in layout.children
    assert "tools" in layout.children
    assert "activity" in layout.children


def test_null_display_is_silent():
    """Test NullDisplay produces no output."""
    display = NullDisplay()
    snapshot = create_test_snapshot()

    with captured_output() as output:
        display.start(snapshot)
        display.update(snapshot)
        display.stop(snapshot)

    assert output.getvalue() == ""


def test_factory_returns_plain_for_non_tty():
    """Test factory falls back to plain when not TTY."""
    # Mock sys.stdout.isatty() to return False
    display = create_display(mode="auto")
    assert isinstance(display, PlainDisplay)
```

### Integration Tests

```python
def test_cli_tui_mode():
    """Test CLI with --tui flag."""
    result = runner.invoke(cli, ["collect", "--platform", "claude-code", "--tui"])
    # Verify TUI initialized (would need mock)


def test_cli_plain_mode():
    """Test CLI with --plain flag."""
    result = runner.invoke(cli, ["collect", "--platform", "claude-code", "--plain"])
    assert "MCP Audit" in result.output


def test_cli_quiet_mode():
    """Test CLI with --quiet flag."""
    result = runner.invoke(cli, ["collect", "--platform", "claude-code", "--quiet"])
    assert result.output == ""
```

---

## Error Handling

### Graceful Fallback

```python
class RichDisplay(DisplayAdapter):
    def update(self, snapshot: DisplaySnapshot) -> None:
        try:
            if self.live:
                self.live.update(self._build_layout(snapshot))
        except Exception as e:
            # Log warning once, then disable live updates
            if not self._fallback_warned:
                print(f"Warning: TUI rendering failed ({e}), falling back to plain output",
                      file=sys.stderr)
                self._fallback_warned = True
            # Continue without crashing
```

### Idempotent Stop

```python
def stop(self, snapshot: DisplaySnapshot) -> None:
    """Stop display (idempotent - safe to call multiple times)."""
    if self.live and self.live.is_started:
        self.live.stop()
        self.live = None
    self._print_final_summary(snapshot)
```

---

## Risks and Mitigations

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Terminal compatibility issues | Low | Medium | Rich handles most terminals; PlainDisplay fallback |
| Performance overhead | Low | Low | Rich's Live is efficient; 2Hz refresh cap |
| Threading issues | Low | High | Single-threaded design; document constraints |
| Rich not installed | Medium | Low | Factory function with clear error message |
| Narrow terminal width | Medium | Low | Responsive layout with truncation |

---

## Success Criteria

1. **Functional**: TUI displays real-time token/tool stats without scrolling
2. **Fallback**: Plain mode works in CI/non-TTY environments
3. **Performance**: No noticeable overhead on tracking
4. **Compatibility**: Works on macOS, Linux, Windows (with Rich support)
5. **Tests**: 90%+ coverage on display module
6. **Documentation**: README updated with TUI screenshots

---

## References

- [Rich Documentation](https://rich.readthedocs.io/)
- [Rich Live Display](https://rich.readthedocs.io/en/stable/live.html)
- [Rich Layout](https://rich.readthedocs.io/en/stable/layout.html)
- [Building Rich Terminal Dashboards](https://www.willmcgugan.com/blog/tech/post/building-rich-terminal-dashboards/)
- [Real Python: The Python Rich Package](https://realpython.com/python-rich-package/)

---

## Appendix: Expert Analysis Summary

### GPT-5.1 Recommendations (via zen thinkdeep)

1. **Display Adapter Boundary**: Keep interface small and orthogonal to tracking
2. **Snapshot-Driven Updates**: Trackers compute snapshots, display just renders (stateless)
3. **Rich.Live Lifecycle**: Single-threaded, use `Live(refresh_per_second=2)` for rate limiting
4. **TTY Detection Precedence**: quiet > plain > (tui if TTY else plain)
5. **Error Handling**: Catch render errors, fallback gracefully, make stop() idempotent
6. **Testing**: Test layout building, not terminal output; use captured streams for plain
