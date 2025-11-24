# Features - MCP Audit

Detailed feature documentation: cross-platform compatibility, signal handling, validation, and output.

---

## Cross-Platform Compatibility

### Unified MCP Tracking

Both trackers support unified MCP tracking with automatic normalization across platforms:

**Claude Code Format:**
- `mcp__brave-search__brave_web_search`
- `mcp__zen__chat`
- `mcp__zen__thinkdeep`

**Codex CLI Format:**
- `mcp__brave-search-mcp__brave_web_search` (note `-mcp` suffix)
- `mcp__zen-mcp__chat`
- `mcp__zen-mcp__thinkdeep`

**Normalization Strategy:**
- Strips `-mcp` suffix from Codex tool names
- Normalizes to Claude Code format for consistent tracking
- Single MCP data file per server (no duplicates)

### Built-in vs MCP Tools

**Claude Code Built-ins:**
- `Read`, `Write`, `Edit`, `Bash`, `Glob`, `Grep`
- `TodoWrite`, `Task`, `WebFetch`
- Tracked separately from MCP tools

**Codex CLI Built-ins:**
- `execute_zsh`, `read_file`, `write_to_file`
- `list_directory`, `glob_search`
- Different from Claude Code, tracked separately

**Benefit**: Clear separation of MCP tool costs vs built-in tool costs

---

## Signal Handling

### Ctrl+C Safety

Both trackers handle Ctrl+C (SIGINT) gracefully:

1. **Catch interrupt signal**
2. **Complete session summary** (don't lose data)
3. **Write all MCP data** to disk
4. **Close events.jsonl** cleanly
5. **Exit gracefully** with status message

**Example:**
```
^C
Interrupt received. Completing session summary...
✓ Session data saved to logs/sessions/mcp-audit-2025-11-23T14-30-45/
✓ summary.json written (8 KB)
✓ mcp-zen.json written (12 KB)
✓ mcp-brave-search.json written (4 KB)
✓ events.jsonl closed (234 events)
```

### No Data Loss

**Before signal handling:**
- ❌ Ctrl+C → incomplete session data
- ❌ Lost all MCP tracking for that session
- ❌ Wasted time and tokens

**After signal handling:**
- ✅ Ctrl+C → complete session summary
- ✅ All MCP data preserved
- ✅ Can analyze even interrupted sessions

---

## Validation

### Session Completeness Checks

**At Analyzer Startup:**
1. Scan `logs/sessions/` for all session directories
2. Check each session for required files:
   - `summary.json` (required)
   - `mcp-*.json` (one per MCP server used)
3. Warn about incomplete sessions
4. Attempt auto-recovery from `events.jsonl`

**Example Output:**
```
Loading sessions from logs/sessions/...

⚠️  WARNING: Incomplete session found
    Path: logs/sessions/mcp-audit-2025-11-22T10-15-30/
    Missing: mcp-zen.json, mcp-brave-search.json
    Attempting recovery from events.jsonl...

✓ Recovered 2 MCP files from events.jsonl (505,123 tokens)
```

### Auto-Recovery from events.jsonl

**Recovery Process:**
1. Check if `events.jsonl` exists
2. Parse all events line-by-line
3. Extract MCP tool calls and token usage
4. Rebuild missing `mcp-*.json` files
5. Continue analysis with recovered data

**When Recovery Needed:**
- Session interrupted before writing MCP files
- Signal handler didn't complete (rare)
- Manual termination (kill -9, system crash)
- Development/testing incomplete sessions

### Validation Warnings

**Incomplete Sessions:**
- Warns at analyzer startup
- Shows which files are missing
- Indicates if recovery was successful

**Corrupt Data:**
- Invalid JSON in summary.json or MCP files
- Skips corrupt sessions with warning
- Continues analysis with remaining sessions

**Missing Sessions:**
- Empty `logs/sessions/` directory
- No valid sessions found
- Prompts user to run tracker first

---

## Development Status Tracking

### Week-by-Week Progress

**Week 1** (2025-11-18 to 2025-11-23): ✅ Complete
- Duplicate detection system
  - `redundancy_analysis` in summary.json
  - Identifies repeated tool calls with same inputs
  - Calculates potential token savings
- Cross-session analysis tool
  - `analyze-mcp-efficiency.py`
  - Aggregate stats across all sessions
  - CSV export for further analysis
- Enhanced anomaly detection
  - High frequency (>10 calls/session)
  - High average tokens (>100K/call)
  - High variance (>5x standard deviation)
- Codex MCP tracking
  - Full parity with Claude Code tracker
  - Cross-platform normalization
  - Per-server and per-tool tracking
- Session recovery from events.jsonl
  - Auto-recovery for incomplete sessions
  - Validation at analyzer startup
  - No data loss on interruption

**Week 2** (Current): Data Collection Phase
- Track 5-10 typical sessions
- Build session history
- Gather diverse workload samples

**Week 3** (Pending): Pattern Analysis
- Identify common patterns
- Optimize top 5 problem tools
- Measure effectiveness of improvements

---

## Recent Updates

### 2025-11-23: Session Recovery & Validation
- ✅ Fixed signal handler for complete logs on Ctrl+C
- ✅ Auto-recovery from events.jsonl for incomplete sessions
- ✅ Validation check warns about missing MCP files
- ✅ Recovered 505K tokens from 2 incomplete sessions

**Impact**: Zero data loss on interruption, complete session history

### 2025-11-22: Codex MCP Tracking Complete
- ✅ Full MCP tracking parity with Claude Code
- ✅ Cross-platform server name normalization
- ✅ Per-server and per-tool token tracking

**Impact**: Can now track both Claude Code and Codex CLI sessions with unified data format

### 2025-11-18 to 2025-11-21: Week 1 Implementation
- ✅ Duplicate detection system
- ✅ Cross-session analysis tool
- ✅ Enhanced anomaly detection

**Impact**: Complete feature set for efficiency measurement and optimization

---

## Output Capabilities

### Live Tracker Display

**Real-time Terminal Output:**
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

Recent Activity:
  [14:32:15] mcp__zen__chat (3,421 tokens)
  [14:32:45] mcp__brave-search__web (8,765 tokens)
  [14:33:12] mcp__zen__debug (12,345 tokens)
```

**Features:**
- ✅ Real-time token tracking
- ✅ Cache efficiency calculation
- ✅ Cost estimation (based on model-pricing.json)
- ✅ MCP tool call monitoring
- ✅ Recent activity log (last 5 calls)

### Cross-Session Analysis Output

**Terminal Summary:**
```
=== MCP Efficiency Analysis ===

Loaded 8 sessions from logs/sessions/

Session Summary:
  Total sessions:              8
  Total tokens:          1,234,567
  Total cost:              $12.34
  Avg tokens/session:    154,321
  Avg cache efficiency:       91%

Top 10 Most Expensive Tools (Total Tokens):
1. mcp__zen__thinkdeep          - 1,234,567 tokens (8 calls)
2. mcp__zen__consensus          - 987,654 tokens (5 calls)
3. mcp__brave-search__web       - 456,789 tokens (23 calls)
4. mcp__zen__debug              - 345,678 tokens (18 calls)
5. mcp__zen__chat               - 234,567 tokens (45 calls)
...

Top 10 Most Frequent Tools:
1. mcp__zen__chat               - 45 calls
2. mcp__brave-search__web       - 23 calls
3. mcp__zen__debug              - 18 calls
...

⚠️  OUTLIERS DETECTED:
- mcp__zen__thinkdeep: High average tokens (154,321 per call)
  → Recommendation: Use sparingly for complex debugging only
- mcp__zen__chat: High frequency (45 calls across 8 sessions)
  → Recommendation: Consider batching queries
- mcp__brave-search__web: High variance (variance: 8.2x)
  → Recommendation: Investigate query patterns

CSV exported to: mcp-efficiency-report.csv
```

**Features:**
- ✅ Aggregate statistics across all sessions
- ✅ Top 10 rankings (expensive + frequent)
- ✅ Outlier detection with recommendations
- ✅ CSV export for further analysis
- ✅ Trend identification

### CSV Export Format

**File**: `mcp-efficiency-report.csv`

**Columns:**
- `tool_name` - MCP tool identifier
- `total_calls` - Number of invocations across all sessions
- `total_tokens` - Sum of all tokens consumed
- `avg_tokens` - Average tokens per call
- `max_tokens` - Maximum single call tokens
- `min_tokens` - Minimum single call tokens
- `variance` - Token usage variance
- `total_cost` - Estimated total cost
- `sessions_used` - Number of sessions that used this tool

**Use Cases:**
- Import into spreadsheet for custom analysis
- Generate charts and graphs
- Share with team for optimization discussions
- Track improvements over time

---

## Related Documentation

- **quickref/commands.md** - npm scripts and workflows
- **quickref/architecture.md** - File descriptions and data structures
- **quickref/troubleshooting.md** - Common issues and solutions
- **README.md** - Comprehensive tool documentation
