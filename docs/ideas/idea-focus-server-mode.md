# Idea: Focus Server Mode

**Status**: Proposed
**Priority**: Low
**Phase**: v1.0+
**Related**: idea-static-mcp-footprint-analyzer.md, idea-mcp-authoring-hints.md

---

## Summary

Add report filtering to focus on a single MCP server, providing detailed metrics for server authors evaluating their own servers or teams budgeting third-party server costs.

---

## Problem Statement

While aggregate reports are useful, specific use cases need server-focused views:

1. **Server authors**: Want detailed metrics on their own server's efficiency
2. **Team leads**: Need to evaluate cost/benefit of specific third-party servers
3. **Optimization**: Drilling into one server's behavior before/after changes

The same data is collected; this is a filtering/presentation enhancement.

---

## Proposed Solution

### CLI Filtering

```bash
# Focus on single server
mcp-analyze report --focus-server mcp__omnisearch

# Compare two servers
mcp-analyze report --compare-servers mcp__zen,mcp__brave-search

# Exclude servers from report
mcp-analyze report --exclude-server mcp__debug

# Filter by time range
mcp-analyze report --focus-server mcp__docs --last 7
```

### Focused Report Output

```
Server Focus Report: mcp__omnisearch
════════════════════════════════════════════════════════════════

Overview (Last 7 Days)
────────────────────────────────────────────────────────────────
Sessions using server:        12 of 15 (80%)
Total tool calls:             156
Total tokens:                 891,331
  • Static metadata:           14,214 (per session)
  • Dynamic outputs:          777,117
Estimated cost:               $2.67
Cache hit rate:               12%

% of Total Context:           33% (largest contributor)

Tool Breakdown
────────────────────────────────────────────────────────────────
Tool                     Calls    Tokens      Avg      Cost
────────────────────────────────────────────────────────────────
web_search                 68    523,100    7,693    $1.57
ai_search                  42    167,580    3,990    $0.50
firecrawl_process          28    112,028    4,001    $0.34
batch_lookup               12     52,320    4,360    $0.16
configure                   6     35,889    5,981    $0.11
────────────────────────────────────────────────────────────────

Efficiency Metrics
────────────────────────────────────────────────────────────────
Cache hit rate:           12% (low - mostly unique content)
Compaction waste:         54% (half of output later trimmed)
Error rate:               2.3% (acceptable)
Avg latency:              1,240ms (slower than avg)

Compaction Analysis
────────────────────────────────────────────────────────────────
This server contributed 520,000 tokens to compacted content (37%)

Top compacted tools:
  • web_search:      312,000 tokens lost
  • ai_search:       124,000 tokens lost
  • firecrawl:        84,000 tokens lost

→ Consider: Use summarized results instead of raw content

Trend (7 Days)
────────────────────────────────────────────────────────────────
Day         Calls    Tokens      Cost    Cache%
────────────────────────────────────────────────────────────────
Nov 20        18     98,231     $0.29      15%
Nov 21        25    142,100     $0.43      11%
Nov 22        22    118,450     $0.36      14%
Nov 23        31    178,200     $0.53       9%
Nov 24        28    156,780     $0.47      10%
Nov 25        19    108,320     $0.32      13%
Nov 26        13     89,250     $0.27      15%
────────────────────────────────────────────────────────────────

Recommendations for mcp__omnisearch
────────────────────────────────────────────────────────────────
⚠️  HIGH: 54% of outputs get compacted
    → Outputs too large for context retention
    → Consider: Add summarization option, reduce default result count

⚠️  MEDIUM: Low cache rate (12%)
    → Content rarely reused
    → Expected for search (unique queries), no action needed

ℹ️  LOW: 5 tools never used in 7 days
    → batch_lookup: 0 calls
    → Consider: Document use cases or move to advanced server
```

### Server Comparison Mode

```bash
mcp-analyze report --compare-servers mcp__zen,mcp__brave-search
```

Output:
```
Server Comparison
════════════════════════════════════════════════════════════════

                          mcp__zen    mcp__brave-search
────────────────────────────────────────────────────────────────
Static metadata              8,340              2,100
Sessions used               15/15             12/15
Total calls                    187                 89
Total tokens               245,670           312,450
Avg tokens/call              1,313              3,511
Cache rate                     68%               15%
Compaction waste               23%               42%
Cost                         $0.74             $0.94
────────────────────────────────────────────────────────────────

Analysis:
  → mcp__zen: Lower tokens/call, better cache (more efficient)
  → mcp__brave-search: Higher compaction waste (outputs too large)
```

---

## Implementation Details

### Filter Implementation

```python
class ReportFilter:
    def __init__(
        self,
        focus_server: str | None = None,
        exclude_servers: List[str] | None = None,
        compare_servers: List[str] | None = None
    ):
        self.focus_server = focus_server
        self.exclude_servers = exclude_servers or []
        self.compare_servers = compare_servers

    def apply(self, session: Session) -> Session:
        """Filter session data based on server criteria."""
        if self.focus_server:
            return self._focus_on_server(session, self.focus_server)
        elif self.exclude_servers:
            return self._exclude_servers(session, self.exclude_servers)
        return session

    def _focus_on_server(self, session: Session, server: str) -> Session:
        """Keep only data from specified server."""
        filtered_servers = [
            s for s in session.server_sessions
            if s.server_name_normalized == server
        ]
        return session.copy(server_sessions=filtered_servers)

    def _exclude_servers(self, session: Session, servers: List[str]) -> Session:
        """Remove data from specified servers."""
        filtered_servers = [
            s for s in session.server_sessions
            if s.server_name_normalized not in servers
        ]
        return session.copy(server_sessions=filtered_servers)


class FocusedReportGenerator:
    def __init__(self, server: str, sessions: List[Session]):
        self.server = server
        self.sessions = sessions

    def generate(self) -> str:
        metrics = self._calculate_metrics()
        tools = self._analyze_tools()
        trends = self._calculate_trends()
        recommendations = self._generate_recommendations(metrics, tools)

        return self._format_report(metrics, tools, trends, recommendations)

    def _calculate_metrics(self) -> dict:
        total_calls = 0
        total_tokens = 0
        cache_tokens = 0
        sessions_using = 0

        for session in self.sessions:
            server_session = self._get_server_session(session)
            if server_session:
                sessions_using += 1
                total_calls += len(server_session.calls)
                total_tokens += server_session.total_tokens
                cache_tokens += server_session.cache_tokens

        return {
            "sessions_using": sessions_using,
            "total_sessions": len(self.sessions),
            "total_calls": total_calls,
            "total_tokens": total_tokens,
            "cache_rate": cache_tokens / total_tokens if total_tokens > 0 else 0,
            # ... more metrics
        }

    def _get_server_session(self, session: Session):
        for ss in session.server_sessions:
            if ss.server_name_normalized == self.server:
                return ss
        return None
```

### CLI Integration

```python
@app.command()
def report(
    focus_server: str = typer.Option(None, help="Focus on single MCP server"),
    exclude_server: List[str] = typer.Option(None, help="Exclude servers"),
    compare_servers: str = typer.Option(None, help="Compare servers (comma-separated)"),
    last: int = typer.Option(7, help="Days to include"),
):
    """Generate report with optional server filtering."""
    sessions = load_sessions(days=last)

    if focus_server:
        generator = FocusedReportGenerator(focus_server, sessions)
        print(generator.generate())
    elif compare_servers:
        servers = compare_servers.split(",")
        generator = ServerComparisonGenerator(servers, sessions)
        print(generator.generate())
    else:
        # Standard report with optional exclusions
        filter = ReportFilter(exclude_servers=exclude_server)
        filtered_sessions = [filter.apply(s) for s in sessions]
        print(generate_standard_report(filtered_sessions))
```

---

## Use Cases

### 1. Server Author Evaluating Own Server

```bash
# "How efficient is my server across all my users' sessions?"
mcp-analyze report --focus-server mcp__myserver --last 30
```

Get detailed metrics on:
- How often tools are used
- Token efficiency per tool
- Cache behavior
- Compaction waste
- Actionable recommendations

### 2. Team Evaluating Third-Party Server

```bash
# "Is mcp__omnisearch worth the context cost?"
mcp-analyze report --focus-server mcp__omnisearch --last 7
```

See:
- Total cost contribution
- % of context consumed
- Compaction waste (are outputs worth keeping?)
- Comparison with alternatives

### 3. Before/After Optimization

```bash
# Week before optimization
mcp-analyze report --focus-server mcp__docs --days-ago 14 --days 7

# Week after optimization
mcp-analyze report --focus-server mcp__docs --last 7

# Compare
mcp-analyze report --focus-server mcp__docs --compare-periods "14-7,7-0"
```

---

## User Value

- **Server authors**: Detailed feedback on their server's efficiency
- **Teams**: Cost/benefit analysis for third-party servers
- **Optimization**: Clear before/after comparison for changes
- **Budgeting**: Attribute costs to specific servers

---

## Dependencies

- Per-server session data (existing)
- Filtering logic for sessions
- Focused report templates

---

## Success Metrics

- Focused reports generated in <5 seconds
- All server metrics available in focused view
- Server authors can identify optimization opportunities

---

## References

- MCP server evaluation best practices
- Cost attribution methodologies
- Server comparison frameworks
