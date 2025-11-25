# Architecture - MCP Audit

File descriptions, data structures, and development principles. Phase 1 complete.

---

## Directory Structure

```
mcp-audit/main/
├── CLAUDE.md                           # Project context (main file)
├── quickref/                           # Internal quick reference docs
├── docs/                               # Public documentation
│   ├── architecture.md                 # System design and data model
│   ├── data-contract.md                # Backward compatibility guarantees
│   ├── contributing.md                 # How to contribute
│   ├── privacy-security.md             # Data handling policies
│   ├── platforms/claude-code.md        # Claude Code setup
│   ├── platforms/codex-cli.md          # Codex CLI setup
│   └── ROADMAP.md                      # 14-week plan
├── examples/                           # Sanitized example sessions
│   ├── claude-code-session/
│   └── codex-cli-session/
│
├── # Core Modules (Phase 1)
├── storage.py                          # JSONL storage with indexing (650 lines)
├── base_tracker.py                     # Platform abstraction (520 lines)
├── pricing_config.py                   # Model pricing config (360 lines)
├── mcp_analyze_cli.py                  # CLI interface (540 lines)
│
├── # Platform Adapters
├── claude_code_adapter.py              # Claude Code tracker (300 lines)
├── codex_cli_adapter.py                # Codex CLI tracker (220 lines)
│
├── # Display Module
├── display/
│   ├── __init__.py                     # Factory function, TTY detection
│   ├── base.py                         # DisplayAdapter ABC
│   ├── snapshot.py                     # DisplaySnapshot dataclass
│   ├── rich_display.py                 # Rich TUI implementation
│   ├── plain_display.py                # CI/logging fallback
│   └── null_display.py                 # Silent mode
│
├── # Utilities
├── normalization.py                    # Server/tool name normalization
├── session_manager.py                  # Session lifecycle management
├── privacy.py                          # Data redaction/sanitization
│
├── # Configuration
├── mcp-analyze.toml                    # User pricing config
├── pyproject.toml                      # Project config (pytest, mypy, ruff)
├── .github/workflows/ci.yml            # CI/CD pipeline
│
├── # Tests
├── test_storage.py                     # Storage tests (57 tests)
└── README.md                           # User-facing documentation
```

---

## Key Files

### Core Modules (Phase 1)

**storage.py** - JSONL session storage with indexing (650 lines)
- Directory structure: `~/.mcp-audit/sessions/<platform>/<YYYY-MM-DD>/`
- SessionIndex, DailyIndex, PlatformIndex for efficient queries
- StorageManager class with full CRUD operations
- Migration helpers for v0.x to v1.x format
- 57 tests in test_storage.py

**base_tracker.py** - Platform abstraction layer (520 lines)
- Abstract adapter interface for platform trackers
- Core data structures (Session, ServerSession, Call, ToolStats)
- Schema v1.0.0 with versioning
- Duplicate detection, anomaly analysis
- Signal handling for graceful shutdown

**pricing_config.py** - Configurable model pricing (360 lines)
- TOML-based configuration (mcp-analyze.toml)
- Claude, OpenAI, and custom model support
- Validation with warnings for unknown models
- Cost calculation with cache token handling

**mcp_analyze_cli.py** - CLI interface (540 lines)
- `mcp-analyze collect` - Real-time session tracking
- `mcp-analyze report` - Cross-session analysis
- Auto-platform detection
- Multiple output formats (JSON, Markdown, CSV)

---

### Platform Adapters

**claude_code_adapter.py** - Claude Code tracker (300 lines)
- File watcher approach (monitors debug.log)
- Inherits from BaseTracker
- 77% code reduction from legacy tracker

**codex_cli_adapter.py** - Codex CLI tracker (220 lines)
- Process wrapper approach (stdout/stderr)
- Automatic `-mcp` suffix normalization
- 77% code reduction from legacy tracker

---

### Display Module

**display/__init__.py** - Factory and exports
- `create_display(mode, refresh_rate)` factory function
- Auto TTY detection for mode selection
- Exports: DisplayAdapter, DisplaySnapshot, RichDisplay, PlainDisplay, NullDisplay

**display/snapshot.py** - Immutable display state
- Frozen dataclass capturing session metrics
- All primitive/tuple fields for thread safety
- Created via `DisplaySnapshot.create()` factory

**display/rich_display.py** - Rich TUI implementation
- Live updating dashboard with Rich library
- Panels: header, tokens, tools, activity, footer
- Configurable refresh rate (default 0.5s)

**display/plain_display.py** - CI/logging fallback
- Rate-limited print output
- Works in non-TTY environments

**display/null_display.py** - Silent mode
- No-op implementations for all methods
- Used with `--quiet` flag

---

### Utilities

**normalization.py** - Cross-platform name normalization
- Server name extraction from tool names
- `-mcp` suffix handling for Codex format
- MCP vs built-in tool detection

**session_manager.py** - Session lifecycle management
- Session directory creation
- Save/load with schema validation
- Incomplete session detection

**privacy.py** - Data redaction and sanitization
- Regex-based sensitive data detection
- API keys, emails, passwords, IPs, etc.
- Safe export for sharing sessions

---

### Public Documentation

**docs/architecture.md** - System design documentation
- Storage directory structure
- Core data model (Session, Call, ServerSession)
- BaseTracker abstraction
- Platform adapter interface

**docs/data-contract.md** - Backward compatibility guarantees
- Schema versioning policy
- Migration support documentation
- Breaking change process

**docs/contributing.md** - Contribution guide
- Adding platform adapters (step-by-step)
- Plugin system documentation
- Testing requirements, PR workflow

**docs/privacy-security.md** - Privacy documentation
- What data is/isn't collected
- Local-only operation
- Redaction hooks

---

## Session Data Structure

### File Locations

Sessions are stored in: `logs/sessions/{project}-{timestamp}/`

Example: `logs/sessions/mcp-audit-2025-11-23T14-30-45/`

### Generated Files

**summary.json** - Session totals and analysis
```json
{
  "project": "mcp-audit",
  "timestamp": "2025-11-23T14:30:45",
  "token_usage": {
    "input_tokens": 45231,
    "output_tokens": 12543,
    "cache_created_tokens": 8123,
    "cache_read_tokens": 125432,
    "total_tokens": 191329,
    "cache_efficiency": 0.93
  },
  "cost_estimate": 0.1234,
  "mcp_tool_calls": {
    "total_calls": 42,
    "unique_tools": 12,
    "most_called": "mcp__zen__chat (15 calls)"
  },
  "redundancy_analysis": {
    "duplicate_calls": 3,
    "potential_savings": 1234
  },
  "anomalies": [
    {
      "type": "high_frequency",
      "tool": "mcp__zen__chat",
      "calls": 15
    }
  ]
}
```

**mcp-{server}.json** - Per-server tool statistics

Example: `mcp-zen.json`
```json
{
  "server": "zen",
  "tools": {
    "mcp__zen__chat": {
      "calls": 15,
      "total_tokens": 45123,
      "avg_tokens": 3008
    },
    "mcp__zen__thinkdeep": {
      "calls": 3,
      "total_tokens": 234567,
      "avg_tokens": 78189
    }
  },
  "total_calls": 18,
  "total_tokens": 279690
}
```

**events.jsonl** - Event stream (optional, for recovery)
- Line-delimited JSON (one event per line)
- Used for auto-recovery if session interrupted
- Contains full conversation event data
- Analyzer rebuilds MCP files from events if needed

### Recovery Process

1. Analyzer checks for `summary.json` and `mcp-*.json` files
2. If missing, looks for `events.jsonl`
3. Rebuilds MCP data from event stream
4. Warns about incomplete sessions but includes in analysis

---

## Development Principles

### File Management

**ALWAYS edit existing tracker scripts** (don't create variants)
- Edit `live-cc-session-tracker.py`, not `live-cc-session-tracker-v2.py`
- Edit `analyze-mcp-efficiency.py`, not `analyze-mcp-efficiency-new.py`
- Prevents script proliferation and confusion

**Session logs are append-only** (never edit past sessions)
- Historical data is immutable
- Analysis depends on accurate historical records
- If session data is wrong, annotate in separate file

**Use events.jsonl as source of truth for recovery**
- Always generate events.jsonl during tracking
- Enables recovery from incomplete sessions
- Acts as audit trail for debugging

---

### Data Integrity

**Validate session completeness before analysis**
- Check for required files (summary.json, mcp-*.json)
- Warn about incomplete sessions
- Auto-recover when possible

**Auto-recovery from events.jsonl when needed**
- Rebuild MCP data from event stream
- Preserve all available information
- Continue analysis with recovered data

**Preserve all raw event data**
- Never delete events.jsonl
- Keep complete conversation history
- Enable future re-analysis with improved tools

---

### Performance

**Minimal overhead on live sessions**
- Async event processing
- Efficient JSONL streaming
- No blocking operations during tracking

**Efficient JSONL streaming for event logs**
- Line-by-line processing (no full file load)
- Memory-efficient for large sessions
- Supports real-time tailing

**Lazy loading for cross-session analysis**
- Load sessions on-demand
- Process incrementally
- Scale to hundreds of sessions

---

## Code Organization

### Tracker Scripts

**Shared Patterns:**
- Signal handling (Ctrl+C safety)
- JSONL event logging
- Per-server MCP tracking
- Token usage accumulation
- Cost estimation

**Platform-Specific:**
- Claude Code: Direct MCP tool names
- Codex CLI: Normalize `-mcp` suffix
- Built-in tool filtering (different per platform)

### Analyzer Script

**Phases:**
1. Session discovery (`logs/sessions/*`)
2. Validation (check for required files)
3. Recovery (rebuild from events.jsonl if needed)
4. Aggregation (combine all session data)
5. Analysis (outliers, patterns, rankings)
6. Export (CSV report generation)

---

## Related Documentation

**Internal (quickref/)**:
- commands.md - CLI commands and workflows
- features.md - Feature details
- troubleshooting.md - Common issues

**Public (docs/)**:
- architecture.md - System design
- data-contract.md - Compatibility guarantees
- contributing.md - How to contribute
- privacy-security.md - Data handling
