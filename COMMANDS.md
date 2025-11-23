# AI MCP Audit - Quick Command Reference

**Last Updated**: 2025-11-22

---

## Claude Code Session Tracking

### Start Live Tracker
```bash
npm run cc:live              # Standard mode (full output + session logging)
npm run cc:live:quiet        # Quiet mode (less verbose output)
npm run cc:live:no-logs      # No session logging (real-time only)
npm run cc:help              # Show help and available flags
```

**What it does**: Monitors current Claude Code session in real-time
- Shows live token usage updates
- Tracks MCP tool calls and costs
- Saves session data on exit (Ctrl+C)

---

## Codex CLI Session Tracking

### Start Codex Tracker
```bash
npm run codex:live           # Start Codex CLI tracking
npm run codex:help           # Show help
```

**What it does**: Monitors current Codex CLI session in real-time
- Tracks input/output/reasoning tokens
- Shows cost estimates
- Saves session data on exit

---

## Cross-Session Analysis

### Analyze All Sessions
```bash
npm run mcp:analyze          # Analyze all collected sessions
npm run mcp:help             # Show analyzer help
```

**What it does**: Analyzes patterns across all recorded sessions
- Top 10 most expensive tools (by total tokens)
- Top 10 most frequent tools (by call count)
- Identifies outliers (high tokens, high frequency, high variance)
- Exports detailed CSV report

**Custom path**:
```bash
python3 scripts/ai-mcp-audit/analyze-mcp-efficiency.py /custom/sessions/path
```

---

## Historical Usage (Legacy ccusage)

### Claude Code History
```bash
npm run usage:wpnav          # Historical usage via ccusage
```

### Codex CLI History
```bash
npm run usage:codex-wpnav    # Historical Codex usage via @ccusage/codex
```

---

## Available Flags

### Claude Code Tracker (`cc:live`)
- `--quiet` - Suppress verbose output
- `--no-logs` - Don't save session logs to disk
- `-h, --help` - Show help message

### Codex Tracker (`codex:live`)
- `-h, --help` - Show help message

### Analyzer (`mcp:analyze`)
- `[sessions_dir]` - Custom sessions directory (optional positional arg)
- `-h, --help` - Show help message

---

## Quick Workflow

```bash
# 1. Start tracking
npm run cc:live

# 2. Work normally in Claude Code
# (Real-time stats displayed)

# 3. Stop tracking (Ctrl+C)
# Session saved to: scripts/ai-mcp-audit/logs/sessions/

# 4. After 5-10 sessions, analyze
npm run mcp:analyze

# 5. Review results
open mcp-efficiency-report.csv
```

---

## Output Locations

**Session Logs**:
```
scripts/ai-mcp-audit/logs/sessions/{project}-{timestamp}/
├── summary.json          # Totals, redundancy, anomalies
├── mcp-{server}.json     # Per-server tool stats
└── events.jsonl          # Event stream (optional)
```

**Analysis Output**:
```
mcp-efficiency-report.csv  # Detailed statistics for all tools
```

---

## Help Commands

```bash
npm run cc:help              # Claude Code tracker help
npm run codex:help           # Codex tracker help
npm run mcp:help             # Analyzer help
```

Each help command shows:
- Usage examples
- Available flags
- What it tracks/analyzes
- Output locations
- Requirements

---

## Command Aliases (Old → New)

| Old Command | New Command |
|-------------|-------------|
| `npm run usage:live-session` | `npm run cc:live` |
| `npm run codex:live-session` | `npm run codex:live` |
| N/A | `npm run mcp:analyze` (new!) |
| N/A | `npm run cc:help` (new!) |
| N/A | `npm run codex:help` (new!) |
| N/A | `npm run mcp:help` (new!) |

**Old commands removed** - use new short names instead!

---

**See Also**: `README-AI-MCP-AUDIT.md` for complete documentation
