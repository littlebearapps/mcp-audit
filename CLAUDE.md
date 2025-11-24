# CLAUDE.md - MCP Audit

**Last Updated**: 2025-11-24

---

## Overview

Internal devtools for analyzing MCP (Model Context Protocol) efficiency and token usage across AI coding sessions.

**Purpose**: Development Tools & Analytics
- Real-time session tracking (Claude Code + Codex CLI)
- Cross-session pattern analysis
- Token efficiency measurement
- MCP tool cost optimization

---

## Quick Start

### Essential Commands

```bash
# Track Claude Code session
npm run cc:live

# Track Codex CLI session
npm run codex:live

# Analyze all sessions
npm run mcp:analyze
```

**See**: @./quickref/commands.md for all commands and workflows

---

## Key Files

### Core Trackers
- `live-cc-session-tracker.py` - Claude Code real-time monitoring (v2025-11-23)
- `live-codex-session-tracker.py` - Codex CLI real-time monitoring (v2025-11-22)
- `analyze-mcp-efficiency.py` - Cross-session aggregate analysis

**See**: @./quickref/architecture.md for complete file documentation and data structures

---

## Development Status

**Week 1**: ✅ Complete (All planned features implemented)
- Duplicate detection system
- Cross-session analysis tool
- Enhanced anomaly detection
- Codex MCP tracking (full parity)
- Session recovery from events.jsonl

**Week 2**: Data collection phase (5-10 sessions)

**Week 3**: Pattern analysis and optimization

**Latest**: 2025-11-23 - Session recovery & validation complete

---

## Key Features

- ✅ Cross-platform MCP tracking (Claude Code + Codex CLI)
- ✅ Auto-recovery from incomplete sessions (events.jsonl)
- ✅ Duplicate detection and anomaly analysis
- ✅ Ctrl+C safe signal handling (no data loss)
- ✅ Per-server and per-tool token tracking

**See**: @./quickref/features.md for detailed feature documentation

---

## Common Issues

### Missing Session Data
- Check `logs/sessions/{project}-{timestamp}/`
- Run `npm run mcp:analyze` (auto-recovers from events.jsonl)

### Incomplete Sessions
- Signal handler writes summary on Ctrl+C
- Auto-recovery from events.jsonl if MCP files missing

### npm Script Errors
- Verify scripts exist in package.json
- Check Python script paths (relative to project root)
- Ensure Python 3 installed (`python3 --version`)

**See**: @./quickref/troubleshooting.md for comprehensive solutions

---

## Integration

### ccusage MCP Server
- **Purpose**: Historical usage data (long-term trends)
- **Timeframe**: Weeks to months
- **Use MCP Audit for**: Session-level details and optimization

### Zen MCP Server
- **Purpose**: Primary analysis target (~50 tools)
- **Tracking**: Per-server tracking in `mcp-zen.json`
- **Tools**: thinkdeep, chat, consensus, debug, codereview, etc.

**See**: @./quickref/integration.md for integration details and optimization tips

---

## For More Information

**Quick Reference**: Import detailed docs above for:
- Commands and workflows → @./quickref/commands.md
- Architecture and files → @./quickref/architecture.md
- Features and capabilities → @./quickref/features.md
- Troubleshooting → @./quickref/troubleshooting.md
- Integration points → @./quickref/integration.md

**Primary Docs**:
- `README.md` - Comprehensive tool documentation (315 lines)
- `COMMANDS.md` - Quick command reference

**Implementation Details**:
- `docs/MCP-EFFICIENCY-MEASUREMENT-PLAN.md` - GPT-5 validated implementation plan
- `docs/CODEX-CLAUDE-FORMAT-DIFFERENCES.md` - Cross-platform format comparison (520 lines)
- `docs/CODEX-MCP-TRACKING-IMPLEMENTATION.md` - Codex tracking implementation details
- `docs/CLAUDE-MD-IMPROVEMENT-PLAN.md` - Context documentation restructuring plan

**Enhancement History**:
- `docs/ENHANCEMENTS-5-8-SUMMARY.md` - Enhancement summary
- `docs/MCP-EFFICIENCY-PLAN-UPDATES.md` - Plan updates
- `docs/MCP-EFFICIENCY-CODE-ANALYSIS.md` - Code analysis

---

## Current Focus

**Date**: 2025-11-24
**Status**: Week 1 Complete ✅ + CLAUDE.md Restructured
**Next**: Data collection phase (Week 2) - track 5-10 typical sessions

**Recent Completion** (2025-11-24):
- ✅ CLAUDE.md modular restructuring
  - 319 lines → 105 lines (67% reduction)
  - 5 quickref files with @-imports
  - Follows Anthropic best practices
  - No information loss, improved token efficiency

**Week 1 Completed** (2025-11-23):
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

**See**: README.md for detailed status and roadmap
