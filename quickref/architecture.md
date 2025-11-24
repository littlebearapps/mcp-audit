# Architecture - MCP Audit

File descriptions, data structures, and development principles.

---

## Directory Structure

```
mcp-audit/main/
├── CLAUDE.md                           # Project context (main file)
├── quickref/                           # Quick reference docs
│   ├── commands.md                     # npm scripts + workflows
│   ├── architecture.md                 # This file
│   ├── features.md                     # Feature details
│   ├── troubleshooting.md              # Common issues
│   └── integration.md                  # Tool relationships
├── docs/                               # Implementation docs
│   ├── MCP-EFFICIENCY-MEASUREMENT-PLAN.md
│   ├── CODEX-CLAUDE-FORMAT-DIFFERENCES.md
│   ├── CODEX-MCP-TRACKING-IMPLEMENTATION.md
│   ├── CLAUDE-MD-IMPROVEMENT-PLAN.md
│   └── ...
├── logs/sessions/                      # Session data (auto-generated)
│   └── {project}-{timestamp}/
│       ├── summary.json
│       ├── mcp-{server}.json
│       └── events.jsonl
├── live-cc-session-tracker.py          # Claude Code tracker
├── live-codex-session-tracker.py       # Codex CLI tracker
├── live-session-tracker.sh             # Bash wrapper
├── analyze-mcp-efficiency.py           # Cross-session analyzer
├── investigate-codex-format.py         # Format investigation
├── model-pricing.json                  # Token pricing data
├── .claude-settings.json               # Claude Code settings
├── COMMANDS.md                         # Quick command reference
├── README.md                           # Comprehensive docs
└── package.json                        # npm scripts
```

---

## Key Files

### Live Session Trackers

**live-cc-session-tracker.py** - Claude Code real-time monitoring (v2025-11-23)
- Token usage tracking (input, output, cache created/read)
- MCP tool call analysis with per-server breakdowns
- Duplicate detection (redundancy_analysis)
- Auto-generates session logs on exit (Ctrl+C safe)
- Signal handling for graceful shutdown
- Writes to `logs/sessions/{project}-{timestamp}/`

**live-codex-session-tracker.py** - Codex CLI real-time monitoring (v2025-11-22)
- Full parity with Claude Code tracker
- Cross-platform server name normalization (`-mcp` suffix stripping)
- Built-in vs MCP tool differentiation
- Same output format as Claude Code tracker

**live-session-tracker.sh** - Bash wrapper with color output
- Color-coded terminal display
- Passes arguments to Python trackers
- Simple invocation: `bash live-session-tracker.sh <tracker.py> [args]`

---

### Analysis Tools

**analyze-mcp-efficiency.py** - Cross-session aggregate analysis
- Loads all sessions from `logs/sessions/`
- Auto-recovery from incomplete sessions (events.jsonl fallback)
- Identifies outliers and patterns:
  - High average tokens (>100K per call)
  - High frequency (>10 calls per session)
  - High variance (>5x standard deviation)
- Exports CSV reports: `mcp-efficiency-report.csv`
- Top 10 rankings:
  - Most expensive tools (total tokens)
  - Most frequent tools (call count)

**investigate-codex-format.py** - Codex format investigation
- Used during development to understand Codex CLI output format
- Compares with Claude Code format
- See `docs/CODEX-CLAUDE-FORMAT-DIFFERENCES.md` for findings

---

### Configuration Files

**model-pricing.json** - Token pricing for cost calculations
- Pricing data for Sonnet 4.5
- Input/output/cache rates
- Updated when model pricing changes

**.claude-settings.json** - Claude Code project settings
- Working directory configuration
- MCP server settings
- Tool permissions

**COMMANDS.md** - Quick command reference
- One-page reference for all npm scripts
- Minimal version of `quickref/commands.md`

---

### Documentation

**README.md** - Comprehensive tool documentation (315 lines)
- Full project overview
- Installation and setup
- Usage examples
- Development roadmap

**docs/MCP-EFFICIENCY-MEASUREMENT-PLAN.md** - GPT-5 validated implementation plan
- Original project plan
- Week-by-week breakdown
- Success criteria

**docs/CODEX-CLAUDE-FORMAT-DIFFERENCES.md** - Cross-platform format comparison (520 lines)
- Detailed format analysis
- Normalization strategies
- Implementation decisions

**docs/CODEX-MCP-TRACKING-IMPLEMENTATION.md** - Codex tracking implementation
- Implementation details
- Challenges and solutions

**docs/CLAUDE-MD-IMPROVEMENT-PLAN.md** - Context documentation restructuring
- Best practices research
- Modular structure design
- Implementation guide

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

- **quickref/commands.md** - npm scripts and workflows
- **quickref/features.md** - Feature details
- **quickref/troubleshooting.md** - Common issues
- **README.md** - Comprehensive tool docs
