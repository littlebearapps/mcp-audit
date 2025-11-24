# CLAUDE.md - MCP Audit

**Last Updated**: 2025-11-24

---

## Overview

MCP efficiency analyzer transforming from internal tool to open-source project. Tracks token usage and costs across AI coding sessions.

**Purpose**: Development Tools & Analytics
- Real-time session tracking (Claude Code + Codex CLI)
- Cross-session pattern analysis
- Token efficiency measurement
- MCP tool cost optimization
- **Target**: Universal open-source analyzer (v1.0 by Week 14)

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

**Current**: v0.1.0-internal → Planning transformation to v1.0 (Week 14)

**5 Phases, 14 Weeks**:
- Phase 1 (Weeks 1-3): Foundation & Restructure
- Phase 2 (Weeks 4-6): Public Beta Release
- Phase 3 (Weeks 7-12): Platform Expansion (Gemini CLI, Ollama CLI)
- Phase 4 (Weeks 13-14): Distribution & Polish
- Phase 5 (Ongoing): Community Growth

**v0.1.0 Complete** (2025-11-23):
- ✅ Duplicate detection system
- ✅ Cross-session analysis tool
- ✅ Enhanced anomaly detection
- ✅ Codex MCP tracking (full parity)
- ✅ Session recovery from events.jsonl

**See**: `docs/ROADMAP.md` for complete 14-week plan and backlog tasks

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
- `docs/ROADMAP.md` - 14-week transformation plan to v1.0 (consensus-validated)
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
**Status**: Planning Phase - Roadmap to v1.0 Complete ✅
**Next**: Begin Phase 1 (Weeks 1-3: Foundation & Restructure)

**Recent Completion** (2025-11-24):
- ✅ 14-week roadmap to v1.0 (consensus-validated by GPT-5.1 + Gemini)
- ✅ 16 backlog tasks created (5 phases + 11 week/multi-week subtasks)
- ✅ Language decision: Python 3.8+ confirmed optimal (9/10 confidence)
- ✅ ROADMAP.md updated with language decision and implementation recommendations
- ✅ Backlog tasks updated with MyPy, optional dependencies, pipx installation
- ✅ CLAUDE.md modular restructuring (319 → 105 lines, 67% reduction)

**Week 1 Completed** (2025-11-23):
- ✅ Duplicate detection system
- ✅ Cross-session analysis tool
- ✅ Enhanced anomaly detection
- ✅ Codex MCP tracking (full parity)
- ✅ Session recovery from events.jsonl
- ✅ MCP file validation

**Next Steps** (Phase 1 - Weeks 1-3):
- ⏳ Week 1: Code restructure (BaseTracker abstraction, schema lock, MyPy setup)
- ⏳ Week 2: Repository setup (pricing config, CI/CD, public repo)
- ⏳ Week 3: Documentation (platform-agnostic docs, data architecture)

**See**: `docs/ROADMAP.md` for complete plan | Backlog tasks: task-1, task-1.1, task-1.2, task-1.3
