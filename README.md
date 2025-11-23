# MCP Audit

**Purpose**: Internal MCP efficiency measurement and token usage analysis for Claude Code and Codex CLI sessions.

**Status**: Week 1 Complete + Codex MCP Tracking ✅ (full parity with Claude Code tracker)

---

## Overview

This folder contains tools for analyzing MCP (Model Context Protocol) tool efficiency and token usage across AI coding assistant sessions (Claude Code, Codex CLI).

**Use Case**: Internal analysis of custom MCP server (~50 tools) to identify:
- Token bloat and high-cost operations
- Duplicate/redundant tool calls
- Anomalies (high variance, high frequency)
- Cross-session patterns and trends

---

## Quick Start

### 1. Track a Claude Code Session

```bash
# From project root
npm run cc:live              # Start live tracking
npm run cc:live:quiet        # Quiet mode (less verbose)
npm run cc:live:no-logs      # Skip saving session logs
npm run cc:help              # Show help
```

This starts real-time monitoring and creates session logs in `scripts/ai-mcp-audit/logs/sessions/`.

### 2. Track a Codex CLI Session

```bash
# From project root
npm run codex:live           # Start Codex tracking
npm run codex:help           # Show help
```

### 3. Analyze All Sessions

```bash
# From project root
npm run mcp:analyze          # Analyze all sessions
npm run mcp:help             # Show help

# Or run directly with custom path
python3 scripts/ai-mcp-audit/analyze-mcp-efficiency.py /path/to/sessions
```

---

## Tools

### Live Session Trackers

**Claude Code**: `live-cc-session-tracker.py` ✅ **Updated 2025-11-23**
- Real-time token tracking for current session
- MCP tool usage breakdown
- Cache efficiency analysis
- Duplicate call detection
- Enhanced anomaly detection
- Auto-generates session logs on exit (including Ctrl+C)
- Validates MCP file completeness

**Codex CLI**: `live-codex-session-tracker.py` ✅ **Updated 2025-11-22**
- **Full MCP tracking parity** with Claude Code tracker
- Per-MCP server and per-tool token tracking
- Cross-platform server name normalization (`-mcp` suffix handling)
- Built-in vs MCP tool differentiation
- Adapted for Codex CLI output format (response_item/event_msg)

**Shell Wrapper**: `live-session-tracker.sh`
- Simple bash wrapper for live monitoring
- Color-coded terminal output

### Cross-Session Analyzer

**Script**: `analyze-mcp-efficiency.py`

**What it does**:
- Loads all session data from `logs/sessions/`
- **Automatically recovers incomplete sessions from events.jsonl** ✨
- Aggregates tool statistics across sessions
- Identifies outliers and patterns
- Exports detailed CSV report

**Output**:
- Top 10 most expensive tools (by total tokens)
- Top 10 most frequent tools (by call count)
- Outlier warnings:
  - High average tokens (>100K per call)
  - High call frequency (>10 calls/session)
  - High variance (>5x difference min/max)
- CSV export: `mcp-efficiency-report.csv`

### Usage Reports

**Claude Code**: `usage-wp-nav.sh`
- Historical usage via ccusage
- Project-filtered session data

**Codex CLI**: `usage-codex-wpnav.sh`
- Historical Codex usage via @ccusage/codex
- Cache efficiency metrics

---

## Files

### Python Scripts
- `live-cc-session-tracker.py` - Claude Code real-time tracker
- `live-codex-session-tracker.py` - Codex CLI real-time tracker
- `analyze-mcp-efficiency.py` - Cross-session analysis
- `investigate-codex-format.py` - Codex format investigation

### Shell Scripts
- `live-session-tracker.sh` - Bash wrapper
- `usage-wp-nav.sh` - ccusage helper
- `usage-codex-wpnav.sh` - Codex usage helper

### Documentation
- `README.md` - Original tool documentation (comprehensive)
- `MCP-EFFICIENCY-MEASUREMENT-PLAN.md` - Implementation plan (GPT-5 validated)
- `MCP-EFFICIENCY-CODE-ANALYSIS.md` - Code analysis
- `MCP-EFFICIENCY-PLAN-UPDATES.md` - Plan updates
- `ENHANCEMENTS-5-8-SUMMARY.md` - Enhancement summary
- `docs/CODEX-CLAUDE-FORMAT-DIFFERENCES.md` - Cross-platform format comparison ✨ **New**
- `docs/CODEX-MCP-TRACKING-IMPLEMENTATION.md` - Codex MCP tracking implementation ✨ **New**

### Data
- `model-pricing.json` - Token pricing for cost calculations
- `logs/sessions/` - Session data storage (auto-created)

---

## Session Data Structure

Each session creates a folder: `logs/sessions/{project}-{timestamp}/`

**Files created**:
- `summary.json` - Session totals, redundancy analysis, anomalies
- `mcp-{server}.json` - Per-server tool statistics
- `events.jsonl` - Event stream (optional)

---

## Cross-Platform Compatibility ✨ **New**

Both trackers now support **unified MCP tracking** across Claude Code and Codex CLI:

**Key Difference Handled**:
- **Claude Code**: `mcp__brave-search__brave_web_search`
- **Codex CLI**: `mcp__brave-search-mcp__brave_web_search`

**Solution**: Automatic server name normalization (strips `-mcp` suffix) enables consistent tracking across platforms.

**See**: `docs/CODEX-CLAUDE-FORMAT-DIFFERENCES.md` for complete format comparison (520 lines)

---

## Week 1 Implementation (Complete ✅)

### Task 1: Duplicate Detection
- Tracks tool calls by signature (tool + params)
- Detects identical calls made multiple times
- Records wasted tokens and occurrence count
- Generates warnings for duplicates
- New `redundancy_analysis` in summary.json

### Task 2: Cross-Session Analysis
- `analyze-mcp-efficiency.py` script (400+ lines)
- Loads all sessions from logs/sessions/
- Aggregates per-tool statistics
- Calculates derived stats (avg, median, variance)
- Identifies outliers (3 categories)
- Terminal report + CSV export

### Task 3: Enhanced Anomaly Detection
- High call frequency (>5 calls/session)
- High variance (>5x difference min/max tokens)
- Per-tool token history tracking
- Automatic detection in write_summary()

---

## Week 2 & Week 3 (Pending)

**Week 2**: Data Collection
- Run 5-10 typical Claude Code sessions
- Let trackers capture data naturally
- Build up session history

**Week 3**: Analysis & Optimization
- Run cross-session analysis
- Identify top 5 problem tools
- Fix duplicates, optimize high-token tools
- Measure improvement

---

## npm Scripts

```bash
# Claude Code tracking
npm run cc:live                 # Start live tracker
npm run cc:live:quiet           # Quiet mode
npm run cc:live:no-logs         # Skip session logging
npm run cc:help                 # Show help

# Codex CLI tracking
npm run codex:live              # Start Codex tracker
npm run codex:help              # Show help

# Cross-session analysis
npm run mcp:analyze             # Analyze all sessions
npm run mcp:help                # Show analyzer help

# Historical usage (legacy)
npm run usage:wpnav             # Claude Code historical
npm run usage:codex-wpnav       # Codex historical
```

---

## Example Workflow

```bash
# 1. Start tracking session
npm run cc:live

# 2. Do normal work in Claude Code
# (live tracker shows real-time stats)

# 3. Exit tracker (Ctrl+C)
# Session data saved to logs/sessions/

# 4. Repeat for 5-10 sessions over a few days/weeks

# 5. Analyze all sessions
npm run mcp:analyze

# 6. Review terminal output + CSV
open mcp-efficiency-report.csv

# 7. Identify and fix issues
# (duplicates, high-token tools, etc.)

# 8. Re-run analysis to measure improvement
npm run mcp:analyze
```

---

## Output Examples

### Live Tracker (Terminal)
```
╔════════════════════════════════════════════════════════════════╗
║ WP Navigator Pro - Live Session Tracker                       ║
╚════════════════════════════════════════════════════════════════╝

Token Usage (This Session)
  Input tokens:           45,231
  Output tokens:          12,543
  Cache created:           8,123
  Cache read:            125,432

  Total tokens:          191,329
  Cache efficiency:           93%

  Estimated Cost:  $0.1234
```

### Cross-Session Analysis (Terminal)
```
═══════════════════════════════════════════════════════════════
Top 10 Most Expensive Tools (Total Tokens)
═══════════════════════════════════════════════════════════════
Tool                                                 Calls       Tokens    Avg/Call
zen__thinkdeep                                         12      450,231      37,519
Read                                                   45      123,456       2,743

⚠️  Tools with High Average Tokens (>100,000)
═══════════════════════════════════════════════════════════════
Tool                                                 Avg Tokens/Call
zen__thinkdeep                                              150,234

✓ No tools with high call frequency (all <10 calls/session)
✓ No tools with high variance (all <5x)
```

---

## Recent Updates

**2025-11-23**: ✅ **Session Recovery & Validation**
- Fixed signal handler to write complete logs on Ctrl+C exit
- Added automatic recovery from events.jsonl for incomplete sessions
- Added validation check to warn about missing MCP files
- Recovered 505K tokens of previously lost MCP data from 2 incomplete sessions

**2025-11-22**: ✅ **Codex MCP Tracking Complete**
- Implemented full MCP tracking for Codex CLI tracker
- Achieved 100% parity with Claude Code tracker
- Cross-platform server name normalization
- Per-server and per-tool token tracking
- Comprehensive documentation added

**Last Updated**: 2025-11-23
**Status**: Week 1 Complete + Codex MCP Tracking ✅ + Session Recovery ✅, Week 2-3 Pending (Data Collection & Optimization)
