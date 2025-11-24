# Integration - MCP Audit

Tool relationships and integration points with other MCP servers and utilities.

---

## ccusage MCP Server

### Overview

**Purpose**: Historical usage data and long-term trends
**Scope**: All Claude Code sessions (global)
**Timeframe**: Weeks to months
**Complement**: MCP Audit tracks session-level details

### Integration Points

**Historical Data via @ccusage Tools:**
- `@ccusage` - View usage statistics from ccusage MCP
- Query historical token usage across all projects
- Compare long-term trends vs session-level details

**Use Cases:**
- **Long-term cost tracking**: Monthly or quarterly spending
- **Project comparison**: Which projects consume most tokens
- **Trend analysis**: Token usage increasing or decreasing over time

**MCP Audit Focus:**
- **Session-level details**: Individual session token breakdown
- **MCP tool costs**: Which MCP tools are most expensive
- **Optimization targets**: Identify specific tools to optimize

### Complementary Usage

**Workflow:**
1. Use **ccusage** to identify high-cost projects or periods
2. Use **MCP Audit** to drill down into specific sessions
3. Identify which MCP tools drove the high costs
4. Optimize tool usage based on session-level data
5. Verify improvements with **ccusage** long-term trends

**Example:**
```bash
# Step 1: Check overall usage with ccusage (via Claude Code)
# "Use @ccusage to show my token usage this month"

# Step 2: If costs high, track recent sessions with MCP Audit
npm run cc:live

# Step 3: Analyze MCP tool usage patterns
npm run mcp:analyze

# Step 4: Identify expensive tools (e.g., thinkdeep, consensus)
# Optimize usage (use sparingly, batch queries)

# Step 5: Next month, check if costs decreased
# "Use @ccusage to compare this month vs last month"
```

### Modern CLI Interface

**Recommended Usage:**
- Use `mcp-analyze collect` for real-time session tracking
- Use `mcp-analyze report` for cross-session analysis
- Python-based with platform auto-detection
- Replaces all legacy project-specific scripts

---

## Zen MCP Server

### Overview

**Purpose**: Primary analysis target for MCP Audit
**Tools**: ~50 tools across multiple categories
**Usage**: Custom MCP server with thinking, planning, consensus, etc.
**Tracking**: Per-server tracking in `mcp-zen.json`

### Monitored Tools

**Thinking & Analysis:**
- `mcp__zen__thinkdeep` - Multi-stage investigation and reasoning
- `mcp__zen__debug` - Systematic debugging and root cause analysis
- `mcp__zen__chat` - General chat and collaborative thinking
- `mcp__zen__consensus` - Multi-model consensus building
- `mcp__zen__planner` - Sequential planning for complex projects

**Code Review:**
- `mcp__zen__codereview` - Systematic code review with validation
- `mcp__zen__precommit` - Git change validation before commit

**Specialized:**
- `mcp__zen__challenge` - Critical thinking and reasoned analysis
- `mcp__zen__apilookup` - Current API/SDK documentation lookup

### Per-Server Tracking

**File**: `mcp-zen.json`

**Structure:**
```json
{
  "server": "zen",
  "tools": {
    "mcp__zen__chat": {
      "calls": 15,
      "total_tokens": 45123,
      "avg_tokens": 3008
    },
    "mcp__zen__thinkdeep": {
      "calls": 3,
      "total_tokens": 234567,
      "avg_tokens": 78189
    },
    "mcp__zen__consensus": {
      "calls": 2,
      "total_tokens": 187654,
      "avg_tokens": 93827
    }
  },
  "total_calls": 20,
  "total_tokens": 467344
}
```

### Optimization Targets

**High-Cost Tools** (based on typical usage):
1. **thinkdeep** - 75K-150K tokens per call
   - Use for complex bugs and architectural decisions
   - Avoid for simple questions or code review
   - Consider chat or debug instead for lighter tasks

2. **consensus** - 80K-120K tokens per call
   - Use for major architectural decisions
   - Requires multiple model consultations
   - Batch questions to minimize calls

3. **codereview** - 40K-80K tokens per call
   - Use for comprehensive reviews only
   - Consider targeted reviews for small changes
   - Use precommit for git-specific validation

**Medium-Cost Tools**:
4. **debug** - 20K-50K tokens per call
5. **planner** - 15K-40K tokens per call
6. **precommit** - 10K-30K tokens per call

**Low-Cost Tools**:
7. **chat** - 2K-5K tokens per call
8. **challenge** - 3K-8K tokens per call
9. **apilookup** - 5K-15K tokens per call

### Usage Recommendations

**Before Using Expensive Tools:**
1. Check if cheaper tool can answer question
2. Batch multiple questions into single call
3. Use chat to gather context first
4. Review previous session data (avoid duplicates)

**After Using Expensive Tools:**
1. Review session summary for token usage
2. Check if call was necessary
3. Consider alternatives for future
4. Update project documentation to avoid repeat calls

---

## brave-search MCP Server

### Overview

**Purpose**: Web search capabilities for Claude Code
**Usage**: Research, documentation lookup, current information
**Tracking**: Per-server tracking in `mcp-brave-search.json`

### Common Tools

**brave_web_search** - General web search
- Typical: 5K-20K tokens per call
- Use for broad information gathering
- Consider context7 or mult-fetch for specific docs

**brave_local_search** - Local business search
- Lower usage in development context
- Tracked separately if used

### Optimization Tips

**Reduce Search Token Usage:**
- Be specific in queries (fewer results to process)
- Use context7 MCP for library docs instead
- Batch related searches into single query
- Cache search results (avoid duplicate searches)

---

## context7 MCP Server

### Overview

**Purpose**: Up-to-date library/framework documentation
**Best For**: React, Node.js, Python packages, API references
**Alternative To**: brave-search for docs (more efficient)

### Integration Strategy

**Use context7 INSTEAD of brave-search for:**
- ✅ Library/framework documentation
- ✅ API references and integration guides
- ✅ Package-specific information

**Use brave-search for:**
- ✅ General web research
- ✅ Best practices and blog posts
- ✅ Broad topic exploration

**Token Efficiency:**
- context7: Specialized, more focused results
- brave-search: General, broader results (more tokens)

---

## mult-fetch MCP Server

### Overview

**Purpose**: General web scraping and content fetching
**Use Cases**: Specific pages, APIs, structured data
**Alternative To**: brave-search for targeted content

### When to Use

**mult-fetch for:**
- ✅ Fetching specific documentation pages
- ✅ API endpoint responses
- ✅ Structured data extraction
- ✅ Pagination and content chunking

**brave-search for:**
- ✅ Finding relevant pages first
- ✅ Broad topic research
- ✅ Multiple source comparison

---

## Future Integration Points

### Planned Integrations

**Git MCP Server** (if added):
- Track git-related MCP tool usage
- Separate from built-in git commands
- Analyze git workflow efficiency

**Linear MCP Server** (if added):
- Track issue/ticket management tool usage
- Analyze project management costs
- Optimize ticket-related queries

**Cloudflare MCP Server** (if added):
- Track infrastructure/deployment tool usage
- Separate from development tools
- Analyze DevOps costs

### Extension Points

**Custom MCP Servers:**
- Add tracking in `live-*-session-tracker.py`
- Per-server JSON file auto-generated
- Include in cross-session analysis
- No code changes needed (dynamic detection)

**New Analysis Metrics:**
- Per-project MCP usage comparison
- Time-of-day usage patterns
- Tool combination analysis (which tools used together)
- Cost forecasting based on historical data

---

## Related Documentation

- **quickref/commands.md** - npm scripts and workflows
- **quickref/architecture.md** - File descriptions and data structures
- **quickref/features.md** - Feature details and capabilities
- **quickref/troubleshooting.md** - Common issues and solutions
- **README.md** - Comprehensive tool documentation
