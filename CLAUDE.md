# CLAUDE.md - MCP Audit

**Last Updated**: 2025-11-25

---

## Overview

Open-source MCP efficiency analyzer. Tracks token usage and costs across AI coding sessions.

**Purpose**: Development Tools & Analytics
- Real-time session tracking (Claude Code + Codex CLI)
- Cross-session pattern analysis
- Token efficiency measurement
- MCP tool cost optimization
- **Status**: Phase 1 Complete ✅ | v1.0 target: Week 14

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

### Core Modules (Phase 1)
- `storage.py` - JSONL session storage with indexing (650 lines)
- `base_tracker.py` - Platform abstraction layer (520 lines)
- `pricing_config.py` - Configurable model pricing (360 lines)
- `mcp_analyze_cli.py` - CLI interface (collect, report commands)

### Platform Adapters
- `claude_code_adapter.py` - Claude Code tracker (300 lines)
- `codex_cli_adapter.py` - Codex CLI tracker (220 lines)

### Utilities
- `normalization.py` - Server/tool name normalization
- `session_manager.py` - Session lifecycle management
- `privacy.py` - Data redaction and sanitization

**See**: @./quickref/architecture.md for complete file documentation

---

## Development Status

**Current**: v0.2.0 | Phase 1 Complete ✅ | Next: Phase 2 (Public Beta)

**Progress**:
- ✅ Phase 1 (Weeks 1-3): Foundation & Restructure - **77 ACs complete**
- ⏳ Phase 2 (Weeks 4-6): Public Beta Release
- ⏳ Phase 3 (Weeks 7-12): Platform Expansion (Gemini CLI, Ollama CLI)
- ⏳ Phase 4 (Weeks 13-14): Distribution & Polish
- ⏳ Phase 5 (Ongoing): Community Growth

**Phase 1 Deliverables**:
- ✅ BaseTracker abstraction with platform adapters
- ✅ Schema v1.0.0 locked with data contract
- ✅ Pricing configuration system
- ✅ CI/CD pipeline (GitHub Actions, MyPy strict)
- ✅ JSONL storage with indexing (57 tests)
- ✅ Complete documentation suite

**See**: `docs/ROADMAP.md` for 14-week plan | Backlog for task details

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

**Quick Reference** (internal context):
- @./quickref/commands.md - Commands and workflows
- @./quickref/architecture.md - Architecture and files
- @./quickref/features.md - Features and capabilities
- @./quickref/troubleshooting.md - Common issues
- @./quickref/integration.md - Integration points

**Public Documentation** (docs/):
- `README.md` - User-facing documentation
- `docs/architecture.md` - System design and data model
- `docs/data-contract.md` - Backward compatibility guarantees
- `docs/contributing.md` - How to contribute and add platforms
- `docs/privacy-security.md` - Data handling policies
- `docs/platforms/claude-code.md` - Claude Code setup
- `docs/platforms/codex-cli.md` - Codex CLI setup

**Planning**:
- `docs/ROADMAP.md` - 14-week plan (consensus-validated)

---

## Current Focus

**Date**: 2025-11-25
**Status**: Phase 1 Complete ✅ | Ready for Phase 2
**Next**: Public Beta Release (Weeks 4-6)

**Phase 1 Complete** (2025-11-25):
- ✅ Week 1: BaseTracker abstraction, schema v1.0.0, 142 tests (21 ACs)
- ✅ Week 2: Pricing config, CI/CD, CLI interface (23 ACs)
- ✅ Week 3: JSONL storage, documentation suite, examples (33 ACs)

**Phase 2 Preview** (Weeks 4-6):
- Week 4: PyPI package distribution, beta testing
- Week 5: Public launch, community announcements
- Week 6: Day 1 value workflows, Team/CI examples

**See**: `docs/ROADMAP.md` | Backlog: task-2 (Phase 2)
