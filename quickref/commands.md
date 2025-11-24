# Commands & Workflows - MCP Audit

Quick reference for all npm scripts and common workflows.

---

## Track Claude Code Session

```bash
# Standard mode - full output with session logging
npm run cc:live

# Quiet mode - less verbose output
npm run cc:live:quiet

# No logs mode - real-time only, no disk writes
npm run cc:live:no-logs

# Show help
npm run cc:help
```

---

## Track Codex CLI Session

```bash
# Start Codex tracking
npm run codex:live

# Show help
npm run codex:help
```

---

## Analyze All Sessions

```bash
# Analyze collected sessions
npm run mcp:analyze

# Show analyzer help
npm run mcp:help
```

---

## Common Workflows

### Single Session Analysis

```bash
# 1. Start tracking
npm run cc:live

# 2. Work normally in Claude Code
# (Real-time stats displayed in terminal)

# 3. Stop tracking (Ctrl+C)
# Session saved to logs/sessions/{project}-{timestamp}/

# 4. Review session data
cat logs/sessions/*/summary.json
```

**Output Location**: `logs/sessions/{project}-{timestamp}/`
- `summary.json` - Session totals, redundancy analysis, anomalies
- `mcp-{server}.json` - Per-server tool statistics
- `events.jsonl` - Event stream (for recovery)

---

### Multi-Session Pattern Analysis

```bash
# 1. Collect 5-10 sessions over time
# (Repeat single session workflow multiple times)

# 2. Run cross-session analysis
npm run mcp:analyze

# 3. Review terminal output + CSV
open mcp-efficiency-report.csv

# 4. Identify optimization targets
# - High-token tools (>100K avg tokens)
# - Duplicates (redundancy_analysis)
# - High-variance tools (>5x variance)
```

**Analysis Output**:
- Top 10 most expensive tools (total tokens)
- Top 10 most frequent tools (call count)
- Outlier warnings (high frequency >10 calls/session, high variance)
- CSV export: `mcp-efficiency-report.csv`

---

### Add to New Project

```bash
# 1. Copy scripts to target project
cp -r ~/claude-code-tools/lba/apps/devtools/mcp-audit/main/* /path/to/project/

# 2. Add npm scripts to package.json
# (See COMMANDS.md for reference scripts)

# 3. Test connectivity
npm run cc:help

# 4. Run first session
npm run cc:live
```

**Required npm Scripts** (add to package.json):
```json
{
  "scripts": {
    "cc:live": "bash live-session-tracker.sh live-cc-session-tracker.py",
    "cc:live:quiet": "bash live-session-tracker.sh live-cc-session-tracker.py --quiet",
    "cc:live:no-logs": "bash live-session-tracker.sh live-cc-session-tracker.py --no-logs",
    "cc:help": "python3 live-cc-session-tracker.py --help",
    "codex:live": "bash live-session-tracker.sh live-codex-session-tracker.py",
    "codex:help": "python3 live-codex-session-tracker.py --help",
    "mcp:analyze": "python3 analyze-mcp-efficiency.py",
    "mcp:help": "python3 analyze-mcp-efficiency.py --help"
  }
}
```

---

## Session Data Structure

### Location
`logs/sessions/{project}-{timestamp}/`

Example: `logs/sessions/mcp-audit-2025-11-23T14-30-45/`

### Files Generated

**summary.json** - Session totals and analysis
- Token counts (input, output, cache created/read)
- Total cost estimate
- Redundancy analysis (duplicate tool calls)
- Anomaly detection (high frequency, high variance)

**mcp-{server}.json** - Per-server statistics
- `mcp-zen.json` - Zen MCP server tools
- `mcp-brave-search.json` - Brave Search MCP tools
- Per-tool token tracking and call counts

**events.jsonl** - Event stream (optional)
- Used for recovery if session interrupted
- Line-delimited JSON (one event per line)
- Auto-recovery by analyzer if MCP files missing

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

MCP Tool Calls
  Total calls:                42
  Unique tools:               12
  Most called: mcp__zen__chat (15 calls)
```

### Cross-Session Analysis (Terminal)

```
=== MCP Efficiency Analysis ===

Loaded 8 sessions from logs/sessions/

Top 10 Most Expensive Tools (Total Tokens):
1. mcp__zen__thinkdeep          - 1,234,567 tokens (8 calls)
2. mcp__zen__consensus          - 987,654 tokens (5 calls)
3. mcp__brave-search__web       - 456,789 tokens (23 calls)
...

Top 10 Most Frequent Tools:
1. mcp__zen__chat               - 45 calls
2. mcp__brave-search__web       - 23 calls
3. mcp__zen__debug              - 18 calls
...

⚠️  OUTLIERS DETECTED:
- mcp__zen__thinkdeep: High average tokens (154,321 per call)
- mcp__zen__chat: High frequency (45 calls across 8 sessions)

CSV exported to: mcp-efficiency-report.csv
```

---

## Advanced Usage

### Custom Session Tracking

```bash
# Run tracker with custom project name
PROJECT_NAME="my-feature" npm run cc:live

# Track with no logs (real-time only)
npm run cc:live:no-logs
```

### Session Recovery

```bash
# If session was interrupted, analyzer auto-recovers
npm run mcp:analyze

# Manual recovery: check events.jsonl
cat logs/sessions/mcp-audit-2025-11-23T14-30-45/events.jsonl
```

### Filter Analysis

```bash
# Analyze only recent sessions
npm run mcp:analyze -- --recent 5

# Export to custom CSV location
npm run mcp:analyze -- --output ./reports/mcp-analysis.csv
```

**Note**: Custom flags depend on analyzer implementation. Check `npm run mcp:help` for current options.

---

## Related Documentation

- **COMMANDS.md** - Quick command reference card
- **README.md** - Comprehensive tool documentation
- **quickref/architecture.md** - File descriptions and data structures
- **quickref/troubleshooting.md** - Common issues and solutions
