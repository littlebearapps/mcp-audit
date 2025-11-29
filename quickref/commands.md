# Commands & Workflows - MCP Audit

Quick reference for mcp-audit CLI commands and common workflows.

---

## Track Claude Code Session

```bash
# Standard mode - full output with session logging
mcp-audit collect --platform claude-code

# With Rich TUI display (auto-detected for TTY)
mcp-audit collect --platform claude-code --tui

# Plain text output (for CI/pipes)
mcp-audit collect --platform claude-code --plain

# Silent mode (logs only, no display)
mcp-audit collect --platform claude-code --quiet
```

---

## Display Modes

MCP Audit auto-detects TTY and chooses the best display:

| Mode | Flag | Use Case |
|------|------|----------|
| TUI | `--tui` | Interactive terminals (default for TTY) |
| Plain | `--plain` | CI/CD pipelines, log files |
| Quiet | `--quiet` | Background processes, logs only |
| Auto | (default) | Auto-detect based on TTY |

```bash
# Custom refresh rate for TUI (default: 0.5s)
mcp-audit collect --platform claude-code --refresh-rate 1.0
```

---

## Track Codex CLI Session

```bash
# Start Codex tracking
mcp-audit collect --platform codex-cli

# With display options (same as Claude Code)
mcp-audit collect --platform codex-cli --tui
mcp-audit collect --platform codex-cli --plain
```

---

## Track Gemini CLI Session

```bash
# Requires telemetry enabled in Gemini CLI
mcp-audit collect --platform gemini-cli
```

---

## Generate Reports

```bash
# Analyze collected sessions
mcp-audit report ~/.mcp-audit/sessions/

# Export as CSV
mcp-audit report ~/.mcp-audit/sessions/ --format csv --output report.csv

# Generate markdown report
mcp-audit report ~/.mcp-audit/sessions/ --format markdown --output report.md

# Show help
mcp-audit report --help
```

---

## Common Workflows

### Single Session Analysis

```bash
# 1. Start tracking (run in a separate terminal)
mcp-audit collect --platform claude-code

# 2. Work normally in Claude Code
# (Real-time stats displayed in terminal)

# 3. Stop tracking (Ctrl+C)
# Session saved to ~/.mcp-audit/sessions/claude_code/{date}/

# 4. Review session data
mcp-audit report ~/.mcp-audit/sessions/
```

**Output Location**: `~/.mcp-audit/sessions/<platform>/<date>/<session-id>.jsonl`

---

### Multi-Session Pattern Analysis

```bash
# 1. Collect 5-10 sessions over time
# (Repeat single session workflow multiple times)

# 2. Run cross-session analysis
mcp-audit report ~/.mcp-audit/sessions/

# 3. Export to CSV for further analysis
mcp-audit report ~/.mcp-audit/sessions/ --format csv --output mcp-report.csv

# 4. Identify optimization targets
# - High-token tools (>100K avg tokens)
# - High-frequency tools
# - High-variance tools (>5x standard deviation)
```

---

### Using in Any Project

Since mcp-audit is installed via pip, you can use it from any directory:

```bash
# Install globally (recommended)
pip install mcp-audit

# Or with pipx (isolated environment)
pipx install mcp-audit

# Works from any Claude Code working directory
cd /path/to/your/project
mcp-audit collect --platform claude-code
```

No project-specific setup required!

---

## Session Data Structure

### Location
`~/.mcp-audit/sessions/<platform>/<YYYY-MM-DD>/<session-id>.jsonl`

Example: `~/.mcp-audit/sessions/claude_code/2025-11-29/session-20251129T143045-abc123.jsonl`

### What's Tracked

- Token counts (input, output, cache created/read)
- Cost estimates based on model pricing
- MCP tool calls (per server, per tool)
- Timestamps and durations
- Anomaly detection (high frequency, duplicates)

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

### Report Output

```
Top 10 Most Expensive Tools (Total Tokens)
═══════════════════════════════════════════════════════════════
Tool                              Calls    Tokens    Avg/Call
mcp__zen__thinkdeep                  12   450,231      37,519
mcp__brave-search__web               45   123,456       2,743
mcp__zen__chat                       89    98,765       1,109

Estimated Total Cost: $2.34 (across 15 sessions)

⚠️  OUTLIERS DETECTED:
- mcp__zen__thinkdeep: High average tokens (37,519 per call)
- mcp__zen__chat: High frequency (89 calls across 15 sessions)
```

---

## Advanced Usage

### Custom Output Directory

```bash
# Save sessions to a custom location
mcp-audit collect --platform claude-code --output /path/to/custom/dir
```

### Custom Project Name

```bash
# Override auto-detected project name
mcp-audit collect --platform claude-code --project my-feature
```

---

## CLI Reference

```bash
# Show main help
mcp-audit --help

# Show version
mcp-audit --version

# Show collect help
mcp-audit collect --help

# Show report help
mcp-audit report --help
```

---

## Related Documentation

- **README.md** - Comprehensive tool documentation
- **quickref/architecture.md** - File descriptions and data structures
- **quickref/troubleshooting.md** - Common issues and solutions
