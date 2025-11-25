---
id: task-8
title: TUI Implementation with Rich Library
status: Done
assignee: []
created_date: '2025-11-25 05:12'
updated_date: '2025-11-25 05:22'
labels:
  - enhancement
  - ui
  - phase-2
dependencies: []
priority: medium
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Implement proper terminal UI for mcp-audit collect command using the Rich library with Display Adapter Pattern architecture. Replace current scrolling print() output with in-place updating dashboard.

**Architecture**: Display Adapter Pattern
- DisplaySnapshot: Immutable dataclass for display state
- DisplayAdapter ABC: Abstract interface for displays
- RichDisplay: Full Rich-based TUI with Live updates
- PlainDisplay: Simple print() fallback for non-TTY
- NullDisplay: Silent mode for scripting

**Key Features**:
- In-place updating dashboard (no scrolling)
- Session header with metadata
- Token usage panel with cache efficiency
- MCP tool calls panel with live updates
- Recent activity feed
- Graceful TTY detection and fallback

**CLI Integration**:
- --tui flag (default, auto-detect)
- --plain flag (force simple output)
- --quiet flag (minimal output)

**Implementation Plan**: See docs/TUI-IMPLEMENTATION-PLAN.md for full details including code examples, mockups, and timeline.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Rich library added as dependency in pyproject.toml
- [x] #2 DisplaySnapshot dataclass implemented with all fields
- [x] #3 DisplayAdapter ABC with render() and cleanup() methods
- [x] #4 RichDisplay implementation with Live context manager
- [x] #5 PlainDisplay implementation matching current output style
- [x] #6 NullDisplay implementation for --quiet mode
- [x] #7 CLI flags: --tui, --plain, --quiet working correctly
- [x] #8 Auto-detection of TTY environment for display selection
- [x] #9 Dashboard shows session header with timestamp and platform
- [x] #10 Token usage panel shows input/output/cache with efficiency %
- [x] #11 MCP tools panel shows calls count and top tools
- [x] #12 Recent activity shows last 5 tool calls with timing
- [x] #13 Graceful handling of terminal resize
- [x] #14 All existing tests pass with new display system
- [x] #15 New unit tests for DisplaySnapshot and adapters
- [x] #16 Integration test for CLI flag combinations
- [x] #17 Documentation updated with new CLI options
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
## Implementation Progress (2025-11-25)

### Completed
- Rich library added as dependency (>=13.0.0)
- Display module created at src/mcp_audit/display/
- DisplaySnapshot dataclass implemented (frozen, immutable)
- DisplayAdapter ABC with start/update/on_event/stop lifecycle
- RichDisplay with Live context manager for real-time TUI
- PlainDisplay for CI/logging environments
- NullDisplay for quiet/scripting mode
- Factory function with TTY detection and graceful fallback
- CLI flags: --tui, --plain, --quiet, --refresh-rate
- ClaudeCodeAdapter integrated with display updates
- 25 new unit tests for display module
- All 287 tests passing

### Files Created
- src/mcp_audit/display/__init__.py
- src/mcp_audit/display/base.py
- src/mcp_audit/display/snapshot.py
- src/mcp_audit/display/plain_display.py
- src/mcp_audit/display/null_display.py
- src/mcp_audit/display/rich_display.py
- tests/test_display.py

### Files Modified
- pyproject.toml (added rich dependency)
- src/mcp_audit/__init__.py (added display exports)
- src/mcp_audit/base_tracker.py (added start/monitor/stop methods)
- src/mcp_audit/claude_code_adapter.py (display integration)
- src/mcp_audit/cli.py (new CLI flags and display support)

### Final Implementation (2025-11-25)
- Added 6 CLI integration tests (total 31 tests)
- Updated README.md with new CLI options documentation
- All 293 tests passing (287 existing + 6 new CLI tests)
- Task complete: 17/17 acceptance criteria met
<!-- SECTION:NOTES:END -->
