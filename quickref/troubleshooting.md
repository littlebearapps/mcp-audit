# Troubleshooting - MCP Audit

Common issues and solutions for MCP Audit tools.

---

## Missing Session Data

### Symptoms
- Can't find session directory in `~/.mcp-audit/sessions/`
- Empty session directory
- Missing session JSONL files

### Solutions

**Check Session Directory Location:**
```bash
# List all sessions
ls -la ~/.mcp-audit/sessions/

# Check specific platform
ls -la ~/.mcp-audit/sessions/claude_code/
```

**Look for events.jsonl (Recovery Source):**
```bash
# Check if session file exists
ls ~/.mcp-audit/sessions/claude_code/2025-11-29/
```

**Run Report with Auto-Recovery:**
```bash
# Report auto-recovers from events.jsonl
mcp-audit report ~/.mcp-audit/sessions/

# Watch for recovery messages:
# ✓ Recovered 2 MCP files from events.jsonl (505,123 tokens)
```

### Prevention
- ✅ Always use Ctrl+C to stop tracker (don't kill -9)
- ✅ Wait for "Session data saved" message before closing terminal
- ✅ Check `~/.mcp-audit/sessions/` after each tracking session

---

## Incomplete Sessions

### Symptoms
- Report warns: "Incomplete session found"
- Missing MCP files but events.jsonl exists
- Session interrupted before completion

### Solutions

**Let Report Auto-Recover:**
```bash
# Report automatically recovers from events.jsonl
mcp-audit report ~/.mcp-audit/sessions/

# Output should show:
# ⚠️  WARNING: Incomplete session found
# Attempting recovery from events.jsonl...
# ✓ Recovered 2 MCP files from events.jsonl
```

**Signal Handler Verification:**
- ✅ All trackers handle Ctrl+C gracefully
- ✅ Signal handler completes summary before exit
- ✅ Writes all MCP data before termination
- ✅ No data loss on manual termination

### Prevention
- ✅ Use Ctrl+C to stop tracker (signal handler active)
- ✅ Don't use kill -9 or force quit
- ✅ Wait for graceful shutdown message

---

## CLI Not Found

### Symptoms
- `mcp-audit` → "command not found"
- `pip install mcp-audit` → version mismatch

### Solutions

**Install via pip or pipx:**
```bash
# Install globally
pip install mcp-audit

# Or install with pipx (recommended for CLI tools)
pipx install mcp-audit

# Verify installation
mcp-audit --version
```

**Check PATH:**
```bash
# Check if pip bin is in PATH
which mcp-audit

# If not found, add to PATH
export PATH="$HOME/.local/bin:$PATH"
```

**Upgrade to Latest:**
```bash
pip install --upgrade mcp-audit
# or
pipx upgrade mcp-audit
```

### Prevention
- ✅ Use pipx for isolated CLI installations
- ✅ Ensure `~/.local/bin` is in PATH
- ✅ Check version: `mcp-audit --version`

---

## Python Environment Issues

### Symptoms
- `ModuleNotFoundError: No module named 'rich'`
- Import errors for dependencies
- Script runs but produces no output

### Solutions

**Verify Python Installation:**
```bash
# Check Python 3 path
which python3

# Check version (3.8+ required)
python3 --version
```

**Reinstall with Dependencies:**
```bash
# Reinstall mcp-audit
pip uninstall mcp-audit
pip install mcp-audit

# Check rich is installed
python3 -c "import rich; print('OK')"
```

### Prevention
- ✅ Use Python 3.8+
- ✅ Use pip or pipx for installation
- ✅ Don't manually copy source files

---

## MCP Connectivity Problems

### Symptoms
- Tracker runs but shows 0 MCP tool calls
- Real-time display shows no MCP activity
- No session data collected

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
- Gemini CLI tracker: Monitors telemetry output

### Prevention
- ✅ Start tracker BEFORE starting Claude Code/Codex/Gemini session
- ✅ Verify MCP servers configured in project
- ✅ Test MCP tools to confirm connectivity

---

## No Sessions Found

### Symptoms
- `mcp-audit report` → "No sessions found"
- Empty `~/.mcp-audit/sessions/` directory
- Analysis runs but shows 0 sessions

### Solutions

**Run Tracker First:**
```bash
# Track at least one session
mcp-audit collect --platform claude-code

# Work in Claude Code for a few minutes
# Stop with Ctrl+C

# Then run report
mcp-audit report ~/.mcp-audit/sessions/
```

**Check Session Directory Structure:**
```bash
# List session directories
ls -la ~/.mcp-audit/sessions/

# Should show platform directories:
# claude_code/
# codex_cli/
# gemini_cli/
```

### Prevention
- ✅ Track at least a few sessions before analyzing
- ✅ Check sessions saved after Ctrl+C
- ✅ Don't delete `~/.mcp-audit/sessions/` directory

---

## High Token Usage Unexplained

### Symptoms
- Session shows very high token counts
- Cache efficiency lower than expected (<85%)
- Cost estimates seem inflated

### Solutions

**Review MCP Tool Calls:**
```bash
# Generate detailed report
mcp-audit report ~/.mcp-audit/sessions/ --format markdown

# Look for high avg_tokens tools
```

**Identify Patterns:**
```bash
# Export to CSV for analysis
mcp-audit report ~/.mcp-audit/sessions/ --format csv --output analysis.csv

# Look for:
# - High average tokens (>100K per call)
# - High frequency tools (>10 calls/session)
# - Repeated identical calls
```

**Check Model Pricing:**
```bash
# Verify pricing config
cat ~/.mcp-audit/config/mcp-audit.toml

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
- `mcp-audit report --format csv` runs but no CSV generated
- CSV file empty or corrupt
- Import errors in spreadsheet

### Solutions

**Check File Permissions:**
```bash
# Verify can write to output location
touch test.csv && rm test.csv

# Should work without errors
```

**Specify Output Path:**
```bash
# Export to specific location
mcp-audit report ~/.mcp-audit/sessions/ --format csv --output ~/Desktop/mcp-report.csv

# Check if file created
ls -la ~/Desktop/mcp-report.csv
```

**Verify CSV Format:**
```bash
# Check first few lines
head -5 ~/Desktop/mcp-report.csv

# Should show header + data rows
```

### Prevention
- ✅ Specify output path with --output
- ✅ Check disk space before export
- ✅ Use absolute paths for output

---

## Related Documentation

- **quickref/commands.md** - CLI commands and workflows
- **quickref/architecture.md** - File descriptions and data structures
- **quickref/features.md** - Feature details and capabilities
- **README.md** - User-facing documentation
