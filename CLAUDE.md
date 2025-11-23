# CLAUDE.md - MCP Audit

**Last Updated**: 2025-11-23

---

## Overview

Internal devtools for analyzing MCP (Model Context Protocol) efficiency and token usage across AI coding sessions.

**Purpose**: Development Tools & Analytics
- Real-time session tracking (Claude Code + Codex CLI)
- Cross-session pattern analysis
- Token efficiency measurement
- MCP tool cost optimization

---

## Directory Structure

- `/` - Python tracking scripts and shell wrappers
- `/docs/` - Implementation plans, format analysis, enhancement docs
- `/logs/sessions/` - Session data storage (auto-generated)
- `model-pricing.json` - Token pricing for cost calculations

---

## Key Files

### Live Session Trackers
- `live-cc-session-tracker.py` - Claude Code real-time monitoring (v2025-11-23)
  - Token usage tracking (input, output, cache)
  - MCP tool call analysis
  - Duplicate detection
  - Auto-generates session logs on exit (Ctrl+C safe)
- `live-codex-session-tracker.py` - Codex CLI real-time monitoring (v2025-11-22)
  - Full parity with Claude Code tracker
  - Cross-platform server name normalization
  - Built-in vs MCP tool differentiation
- `live-session-tracker.sh` - Bash wrapper with color output

### Analysis Tools
- `analyze-mcp-efficiency.py` - Cross-session aggregate analysis
  - Loads all sessions from logs/sessions/
  - Auto-recovery from incomplete sessions (events.jsonl fallback)
  - Identifies outliers and patterns
  - Exports CSV reports
- `investigate-codex-format.py` - Codex format investigation

### Configuration
- `model-pricing.json` - Pricing data for Sonnet 4.5
- `.claude-settings.json` - Claude Code project settings
- `COMMANDS.md` - Quick command reference

### Documentation
- `README.md` - Comprehensive tool documentation
- `docs/MCP-EFFICIENCY-MEASUREMENT-PLAN.md` - GPT-5 validated implementation plan
- `docs/CODEX-CLAUDE-FORMAT-DIFFERENCES.md` - Cross-platform format comparison (520 lines)
- `docs/CODEX-MCP-TRACKING-IMPLEMENTATION.md` - Codex tracking implementation details

---

## Quick Start

### Track Claude Code Session
```bash
# From any project with npm scripts configured
npm run cc:live              # Standard mode
npm run cc:live:quiet        # Less verbose
npm run cc:live:no-logs      # Real-time only, no disk writes
npm run cc:help              # Show help
```

### Track Codex CLI Session
```bash
npm run codex:live           # Start Codex tracking
npm run codex:help           # Show help
```

### Analyze All Sessions
```bash
npm run mcp:analyze          # Analyze collected sessions
npm run mcp:help             # Show analyzer help
```

---

## Session Data Structure

**Location**: `logs/sessions/{project}-{timestamp}/`

**Files**:
- `summary.json` - Session totals, redundancy analysis, anomalies
- `mcp-{server}.json` - Per-server tool statistics (zen, brave-search, etc.)
- `events.jsonl` - Event stream (optional, for recovery)

**Recovery**: Analyzer auto-recovers incomplete sessions from events.jsonl if MCP files are missing

---

## Development Status

**Week 1**: ✅ Complete
- Duplicate detection (redundancy_analysis in summary.json)
- Cross-session analysis (analyze-mcp-efficiency.py)
- Enhanced anomaly detection (high frequency, high variance)
- Codex MCP tracking (full parity with Claude Code)
- Session recovery from events.jsonl (2025-11-23)

**Week 2**: Pending
- Data collection phase (5-10 typical sessions)
- Build session history

**Week 3**: Pending
- Pattern analysis
- Optimization (top 5 problem tools)
- Measurement of improvements

---

## Key Features

### Cross-Platform Compatibility
Both trackers support unified MCP tracking with automatic normalization:
- **Claude Code**: `mcp__brave-search__brave_web_search`
- **Codex CLI**: `mcp__brave-search-mcp__brave_web_search`
- **Normalization**: Strips `-mcp` suffix for consistent tracking

### Signal Handling
Both trackers handle Ctrl+C gracefully:
- Completes session summary on interrupt
- Writes all MCP data before exit
- No data loss on manual termination

### Validation
- Checks for missing MCP files at startup
- Warns about incomplete sessions
- Auto-recovery from events.jsonl

---

## Output Examples

### Live Tracker (Terminal)
```
╔════════════════════════════════════════════════════════════════╗
║ MCP Audit - Live Session Tracker                              ║
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

### Cross-Session Analysis
- Top 10 most expensive tools (total tokens)
- Top 10 most frequent tools (call count)
- Outlier warnings (high avg tokens >100K, high frequency >10 calls/session, high variance >5x)
- CSV export: `mcp-efficiency-report.csv`

---

## Common Workflows

### Single Session Analysis
```bash
# 1. Start tracking
npm run cc:live

# 2. Work normally in Claude Code
# (Real-time stats displayed)

# 3. Stop tracking (Ctrl+C)
# Session saved to logs/sessions/{project}-{timestamp}/

# 4. Review session data
cat logs/sessions/*/summary.json
```

### Multi-Session Pattern Analysis
```bash
# 1. Collect 5-10 sessions over time
# (Repeat single session workflow)

# 2. Run cross-session analysis
npm run mcp:analyze

# 3. Review terminal output + CSV
open mcp-efficiency-report.csv

# 4. Identify optimization targets
# (High-token tools, duplicates, high-variance tools)
```

### Add to New Project
```bash
# 1. Copy scripts to project
cp -r ~/claude-code-tools/lba/apps/devtools/mcp-audit/main/* .

# 2. Add npm scripts to package.json
# (See COMMANDS.md for reference)

# 3. Test connectivity
npm run cc:help
```

---

## Integration with Other Tools

### ccusage MCP Server
- Historical usage data via `@ccusage` tools
- Legacy scripts: `usage-wp-nav.sh`, `usage-codex-wpnav.sh`
- Use for long-term trends, MCP Audit for session-level analysis

### Zen MCP Server
- Primary analysis target (custom MCP with ~50 tools)
- Per-server tracking in `mcp-zen.json`
- Monitors thinkdeep, chat, consensus, etc.

---

## Development Principles

### File Management
- ALWAYS edit existing tracker scripts (don't create variants)
- Session logs are append-only (never edit past sessions)
- Use events.jsonl as source of truth for recovery

### Data Integrity
- Validate session completeness before analysis
- Auto-recovery from events.jsonl when needed
- Preserve all raw event data

### Performance
- Minimal overhead on live sessions
- Efficient JSONL streaming for event logs
- Lazy loading for cross-session analysis

---

## Troubleshooting

### Missing Session Data
- Check `logs/sessions/{project}-{timestamp}/`
- Look for `events.jsonl` (recovery source)
- Run `npm run mcp:analyze` (auto-recovers)

### Incomplete Sessions
- Signal handler writes summary on Ctrl+C
- Events.jsonl used for recovery if MCP files missing
- Validation warns at analyzer startup

### npm Script Errors
- Verify scripts exist in package.json
- Check Python script paths (relative to project root)
- Ensure Python 3 installed (`python3 --version`)

---

## Recent Updates

**2025-11-23**: ✅ Session Recovery & Validation
- Fixed signal handler for complete logs on Ctrl+C
- Auto-recovery from events.jsonl for incomplete sessions
- Validation check warns about missing MCP files
- Recovered 505K tokens from 2 incomplete sessions

**2025-11-22**: ✅ Codex MCP Tracking Complete
- Full MCP tracking parity with Claude Code
- Cross-platform server name normalization
- Per-server and per-tool token tracking

---

## For More Information

**Primary Docs**:
- `README.md` - Comprehensive tool documentation (315 lines)
- `COMMANDS.md` - Quick command reference

**Implementation Details**:
- `docs/MCP-EFFICIENCY-MEASUREMENT-PLAN.md` - Original plan (GPT-5 validated)
- `docs/CODEX-CLAUDE-FORMAT-DIFFERENCES.md` - Platform format differences (520 lines)
- `docs/CODEX-MCP-TRACKING-IMPLEMENTATION.md` - Codex tracking implementation

**Enhancement History**:
- `docs/ENHANCEMENTS-5-8-SUMMARY.md` - Enhancement summary
- `docs/MCP-EFFICIENCY-PLAN-UPDATES.md` - Plan updates
- `docs/MCP-EFFICIENCY-CODE-ANALYSIS.md` - Code analysis

---

## Current Focus

**Date**: 2025-11-23
**Status**: Week 1 Complete ✅ (All planned features implemented)
**Next**: Data collection phase (Week 2) - track 5-10 typical sessions

**Completed**:
- ✅ Duplicate detection system
- ✅ Cross-session analysis tool
- ✅ Enhanced anomaly detection
- ✅ Codex MCP tracking (full parity)
- ✅ Session recovery from events.jsonl
- ✅ MCP file validation

**Pending**:
- ⏳ Data collection (5-10 sessions)
- ⏳ Pattern analysis and optimization
- ⏳ Effectiveness measurement
