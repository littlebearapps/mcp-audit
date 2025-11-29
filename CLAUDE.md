# CLAUDE.md - MCP Audit

**Last Updated**: 2025-11-29

---

## Overview

Open-source MCP efficiency analyzer. Tracks token usage and costs across AI coding sessions.

**Distribution**: Free, open-source tool released via public GitHub repo and PyPI.

**Audiences**: MCP tool developers (optimize their implementations) + session users (understand context usage).

**Purpose**: Development Tools & Analytics
- Real-time session tracking (Claude Code + Codex CLI + Gemini CLI)
- Per-server, per-tool token breakdown
- Cross-session pattern analysis
- MCP tool optimization with real usage data
- **Status**: Phase 1 Complete ✅ | v1.0 target: Week 14

**See**: @./quickref/messaging.md for target audiences and value props

---

## Quick Start

### Essential Commands

```bash
# Track Claude Code session
mcp-audit collect --platform claude-code

# Track Codex CLI session
mcp-audit collect --platform codex-cli

# Generate a report
mcp-audit report ~/.mcp-audit/sessions/
```

**See**: @./quickref/commands.md for all commands and workflows

---

## Git Workflow

**All changes require PR with passing CI.** Never push directly to main.

⚠️ **NEVER merge a PR without explicit user approval.** Always ask before merging.

```bash
git checkout -b feat/my-feature   # Create feature branch
# ... make changes ...
make all                          # Run lint/typecheck/test locally
git push -u origin feat/my-feature
gh pr create                      # Create PR → wait CI → (ASK USER before merge)
```

**PyPI Release** (after PR merged to main):
```bash
git tag v0.3.1 && git push --tags  # Triggers publish workflow
```

**CI Requirements**: pytest, mypy, ruff, black

**Note**: Branches auto-delete on merge. No cleanup needed.

---

## Key Files

All source code is in `src/mcp_audit/` (installed via `pip install mcp-audit`).

### Core Modules
- `cli.py` - CLI interface (mcp-audit command)
- `storage.py` - JSONL session storage with indexing
- `base_tracker.py` - Platform abstraction layer
- `pricing_config.py` - Configurable model pricing

### Platform Adapters
- `claude_code_adapter.py` - Claude Code tracker
- `codex_cli_adapter.py` - Codex CLI tracker
- `gemini_cli_adapter.py` - Gemini CLI tracker

### Display Module
- `display/__init__.py` - Factory function with TTY detection
- `display/rich_display.py` - Rich TUI with Live updates
- `display/plain_display.py` - CI/logging fallback
- `display/null_display.py` - Silent mode

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

- ✅ Cross-platform MCP tracking (Claude Code + Codex CLI + Gemini CLI)
- ✅ Rich TUI display with auto TTY detection (--tui, --plain, --quiet)
- ✅ Auto-recovery from incomplete sessions (events.jsonl)
- ✅ Duplicate detection and anomaly analysis
- ✅ Ctrl+C safe signal handling (no data loss)
- ✅ Per-server and per-tool token tracking

**See**: @./quickref/features.md for detailed feature documentation

---

## Common Issues

### Missing Session Data
- Check `~/.mcp-audit/sessions/<platform>/<date>/`
- Run `mcp-audit report ~/.mcp-audit/sessions/` (auto-recovers from events.jsonl)

### Incomplete Sessions
- Signal handler writes summary on Ctrl+C
- Auto-recovery from events.jsonl if MCP files missing

### CLI Not Found
- Ensure installed: `pip install mcp-audit` or `pipx install mcp-audit`
- Check Python 3 installed: `python3 --version`

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
- `docs/platforms/gemini-cli.md` - Gemini CLI setup

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
