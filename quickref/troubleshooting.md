# Troubleshooting - MCP Audit

Common issues and solutions for MCP Audit tools.

---

## Missing Session Data

### Symptoms
- Can't find session directory in `logs/sessions/`
- Empty session directory
- Missing `summary.json` or `mcp-*.json` files

### Solutions

**Check Session Directory Location:**
```bash
# List all sessions
ls -la logs/sessions/

# Check specific session
ls -la logs/sessions/mcp-audit-2025-11-23T14-30-45/
```

**Look for events.jsonl (Recovery Source):**
```bash
# Check if events.jsonl exists
cat logs/sessions/mcp-audit-2025-11-23T14-30-45/events.jsonl | wc -l

# Should show number of events (e.g., 234)
```

**Run Analyzer with Auto-Recovery:**
```bash
# Analyzer auto-recovers from events.jsonl
npm run mcp:analyze

# Watch for recovery messages:
# ✓ Recovered 2 MCP files from events.jsonl (505,123 tokens)
```

### Prevention
- ✅ Always use Ctrl+C to stop tracker (don't kill -9)
- ✅ Wait for "Session data saved" message before closing terminal
- ✅ Check `logs/sessions/` after each tracking session

---

## Incomplete Sessions

### Symptoms
- Analyzer warns: "Incomplete session found"
- Missing MCP files but events.jsonl exists
- Session interrupted before completion

### Solutions

**Let Analyzer Auto-Recover:**
```bash
# Analyzer automatically recovers from events.jsonl
npm run mcp:analyze

# Output should show:
# ⚠️  WARNING: Incomplete session found
# Attempting recovery from events.jsonl...
# ✓ Recovered 2 MCP files from events.jsonl
```

**Manual Recovery (If Needed):**
```bash
# 1. Navigate to incomplete session
cd logs/sessions/mcp-audit-2025-11-23T14-30-45/

# 2. Check what files exist
ls -la

# 3. If events.jsonl exists, recovery is possible
# Let analyzer handle it automatically
```

**Signal Handler Verification:**
- ✅ Both trackers handle Ctrl+C gracefully (v2025-11-23+)
- ✅ Signal handler completes summary before exit
- ✅ Writes all MCP data before termination
- ✅ No data loss on manual termination

### Prevention
- ✅ Use Ctrl+C to stop tracker (signal handler active)
- ✅ Don't use kill -9 or force quit
- ✅ Wait for graceful shutdown message

---

## npm Script Errors

### Symptoms
- `npm run cc:live` → "command not found"
- `npm run mcp:analyze` → "no such file"
- Scripts run but Python errors

### Solutions

**Verify Scripts Exist in package.json:**
```bash
# Check package.json scripts section
cat package.json | grep -A 10 '"scripts"'

# Should show:
# "scripts": {
#   "cc:live": "bash live-session-tracker.sh live-cc-session-tracker.py",
#   "mcp:analyze": "python3 analyze-mcp-efficiency.py",
#   ...
# }
```

**Add Missing Scripts:**
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

**Check Python Script Paths (Relative to Project Root):**
```bash
# Verify scripts exist
ls -la live-cc-session-tracker.py
ls -la live-codex-session-tracker.py
ls -la analyze-mcp-efficiency.py

# Should show files with execute permissions
```

**Ensure Python 3 Installed:**
```bash
# Check Python version
python3 --version

# Should show: Python 3.x.x (3.8+ recommended)

# If not installed:
# macOS: brew install python3
# Linux: apt-get install python3
```

### Prevention
- ✅ Use npm scripts (not direct Python invocation)
- ✅ Keep scripts in project root (relative paths work)
- ✅ Test new project setup with `npm run cc:help`

---

## Python Environment Issues

### Symptoms
- `ModuleNotFoundError: No module named 'json'`
- Import errors for standard library modules
- Script runs but produces no output

### Solutions

**Verify Python Installation:**
```bash
# Check Python 3 path
which python3

# Check if standard library accessible
python3 -c "import json; print('OK')"

# Should output: OK
```

**Check Script Permissions:**
```bash
# Make scripts executable
chmod +x live-cc-session-tracker.py
chmod +x live-codex-session-tracker.py
chmod +x analyze-mcp-efficiency.py
chmod +x live-session-tracker.sh
```

**Test Direct Invocation:**
```bash
# Test without npm script
python3 live-cc-session-tracker.py --help

# Should show help message
```

### Prevention
- ✅ Use Python 3.8+ (built-in json, pathlib, signal modules)
- ✅ No external dependencies required (pure stdlib)
- ✅ Scripts are cross-platform (macOS, Linux, Windows WSL)

---

## MCP Connectivity Problems

### Symptoms
- Tracker runs but shows 0 MCP tool calls
- No `mcp-*.json` files generated
- Real-time display shows no MCP activity

### Solutions

**Verify MCP Servers Running:**
```bash
# In Claude Code session, check MCP status
/mcp

# Should show active MCP servers:
# - zen (or similar)
# - brave-search
# - etc.
```

**Check Project .mcp.json Configuration:**
```bash
# View MCP config
cat .mcp.json

# Should show configured servers
```

**Test MCP Tools in Claude Code:**
```bash
# In Claude Code session, try MCP tool
# Example: "Use brave-search to look up something"

# Tracker should show activity in real-time
```

**Verify Tracker Is Monitoring Correct Stream:**
- Claude Code tracker: Monitors `~/.claude/cache/*/debug.log`
- Codex CLI tracker: Monitors Codex API stream
- Check that stream exists and is active

### Prevention
- ✅ Start tracker BEFORE starting Claude Code/Codex session
- ✅ Verify MCP servers configured in project
- ✅ Test MCP tools to confirm connectivity

---

## Analyzer No Sessions Found

### Symptoms
- `npm run mcp:analyze` → "No sessions found"
- Empty `logs/sessions/` directory
- Analysis runs but shows 0 sessions

### Solutions

**Run Tracker First:**
```bash
# Track at least one session
npm run cc:live

# Work in Claude Code for a few minutes
# Stop with Ctrl+C

# Then run analyzer
npm run mcp:analyze
```

**Check Session Directory Structure:**
```bash
# List session directories
ls -la logs/sessions/

# Should show directories like:
# mcp-audit-2025-11-23T14-30-45/

# If empty, no sessions have been tracked yet
```

**Verify Working Directory:**
```bash
# Analyzer looks in ./logs/sessions/ relative to CWD
pwd

# Should be in project root (where package.json is)
```

### Prevention
- ✅ Track at least 5-10 sessions before analyzing
- ✅ Run analyzer from project root
- ✅ Don't delete `logs/sessions/` directory

---

## High Token Usage Unexplained

### Symptoms
- Session shows very high token counts
- Cache efficiency lower than expected (<85%)
- Cost estimates seem inflated

### Solutions

**Review MCP Tool Calls:**
```bash
# Check which tools used most tokens
cat logs/sessions/*/mcp-zen.json

# Look for high avg_tokens tools
```

**Identify Duplicate Calls:**
```bash
# Check redundancy_analysis in summary.json
cat logs/sessions/*/summary.json | grep -A 5 "redundancy_analysis"

# Shows potential savings from duplicates
```

**Run Cross-Session Analysis:**
```bash
# Identify outliers and patterns
npm run mcp:analyze

# Look for:
# - High average tokens (>100K per call)
# - High frequency tools (>10 calls/session)
# - High variance (>5x standard deviation)
```

**Check Model Pricing:**
```bash
# Verify pricing data is current
cat model-pricing.json

# Update if model pricing changed
```

### Prevention
- ✅ Avoid redundant tool calls (check cache first)
- ✅ Use expensive tools (thinkdeep, consensus) sparingly
- ✅ Monitor real-time display during session
- ✅ Review session summaries after each session

---

## CSV Export Fails

### Symptoms
- `npm run mcp:analyze` runs but no CSV generated
- CSV file empty or corrupt
- Import errors in spreadsheet

### Solutions

**Check File Permissions:**
```bash
# Verify analyzer can write to current directory
touch test.csv && rm test.csv

# Should work without errors
```

**Run with Verbose Output:**
```bash
# Check for error messages
python3 analyze-mcp-efficiency.py --verbose

# Look for write errors or exceptions
```

**Specify Custom Output Path:**
```bash
# Try writing to different location
python3 analyze-mcp-efficiency.py --output ~/Desktop/mcp-report.csv

# Check if file created
ls -la ~/Desktop/mcp-report.csv
```

**Verify CSV Format:**
```bash
# Check first few lines
head -5 mcp-efficiency-report.csv

# Should show header + data rows
```

### Prevention
- ✅ Run analyzer from project root (write permissions)
- ✅ Don't run with sudo (permission issues)
- ✅ Check disk space before analysis

---

## Related Documentation

- **quickref/commands.md** - npm scripts and workflows
- **quickref/architecture.md** - File descriptions and data structures
- **quickref/features.md** - Feature details and capabilities
- **README.md** - Comprehensive tool documentation
- **docs/CODEX-MCP-TRACKING-IMPLEMENTATION.md** - Implementation details
