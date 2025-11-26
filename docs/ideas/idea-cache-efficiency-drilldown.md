# Idea: Cache Efficiency Drilldown

**Status**: Proposed
**Priority**: Medium
**Phase**: v1.0+
**Related**: idea-context-categories-reports.md

---

## Summary

Extend cache tracking beyond session totals to provide per-model, per-server, and per-tool cache hit analysis, helping users identify optimization opportunities and potential savings.

---

## Problem Statement

MCP Audit already tracks cached vs non-cached tokens and costs, but users need deeper insights:

- Which models have the best cache hit rates?
- Which MCP servers produce highly cacheable outputs?
- Which tools produce unique outputs every time (low reuse)?
- How much money could be saved with better caching?

---

## Proposed Solution

### Multi-Level Cache Analysis

#### 1. Per-Model Cache Efficiency

```
Cache Efficiency by Model
─────────────────────────────────────────────────────────
Model                   Hit Rate    Cached     Cost Saved
─────────────────────────────────────────────────────────
claude-sonnet-4-5          73%     125,000       $0.94
gpt-5-codex                45%      38,000       $0.28
gemini-2.5-pro             82%     210,000       $0.42
─────────────────────────────────────────────────────────
```

#### 2. Per-MCP Server Cache Efficiency

```
Cache Efficiency by MCP Server
─────────────────────────────────────────────────────────
Server                  Outputs    Cached     Hit Rate
─────────────────────────────────────────────────────────
mcp__project_docs        15,000    11,100        74%   ← Best
mcp__zen                 45,000    18,000        40%
mcp__brave-search        38,000     1,900         5%   ← Worst
─────────────────────────────────────────────────────────
```

#### 3. Per-Tool Cache Analysis

```
Cache Efficiency by Tool
─────────────────────────────────────────────────────────
Tool                         Calls    Cached%    Reuse Score
─────────────────────────────────────────────────────────
mcp__project_docs__faq          12       74%        High
mcp__zen__chat                  45       40%        Medium
mcp__docs__semantic_search      18        5%        Low
mcp__websearch__raw_html         8        0%        None
─────────────────────────────────────────────────────────

⚠️  Low reuse tools:
  → mcp__websearch__raw_html: Always different pages (expected)
  → mcp__docs__semantic_search: Consider caching search results
```

---

## Implementation Details

### Data Structures

```python
from dataclasses import dataclass
from typing import Dict

@dataclass
class CacheMetrics:
    total_tokens: int
    cached_tokens: int
    cache_cost_rate: float  # Cost per cached token vs regular

    @property
    def hit_rate(self) -> float:
        if self.total_tokens == 0:
            return 0.0
        return self.cached_tokens / self.total_tokens

    @property
    def cost_saved(self) -> float:
        # Cached tokens are typically 10x cheaper
        regular_cost = self.cached_tokens * 0.003 / 1000  # Example rate
        cached_cost = self.cached_tokens * 0.0003 / 1000
        return regular_cost - cached_cost


@dataclass
class CacheReport:
    by_model: Dict[str, CacheMetrics]
    by_server: Dict[str, CacheMetrics]
    by_tool: Dict[str, CacheMetrics]

    @property
    def total_cached(self) -> int:
        return sum(m.cached_tokens for m in self.by_model.values())

    @property
    def total_saved(self) -> float:
        return sum(m.cost_saved for m in self.by_model.values())

    def worst_offenders(self, n: int = 5) -> list:
        """Return tools with lowest cache hit rates."""
        sorted_tools = sorted(
            self.by_tool.items(),
            key=lambda x: x[1].hit_rate
        )
        return sorted_tools[:n]

    def best_performers(self, n: int = 5) -> list:
        """Return tools with highest cache hit rates."""
        sorted_tools = sorted(
            self.by_tool.items(),
            key=lambda x: x[1].hit_rate,
            reverse=True
        )
        return sorted_tools[:n]
```

### Cache Analyzer

```python
class CacheAnalyzer:
    def __init__(self, session: Session):
        self.session = session

    def analyze(self) -> CacheReport:
        by_model = self._analyze_by_model()
        by_server = self._analyze_by_server()
        by_tool = self._analyze_by_tool()

        return CacheReport(
            by_model=by_model,
            by_server=by_server,
            by_tool=by_tool
        )

    def _analyze_by_model(self) -> Dict[str, CacheMetrics]:
        metrics = {}
        for call in self.session.calls:
            model = call.model or "unknown"
            if model not in metrics:
                metrics[model] = CacheMetrics(0, 0, 0.1)

            metrics[model].total_tokens += call.input_tokens
            metrics[model].cached_tokens += call.cache_read_tokens or 0

        return metrics

    def _analyze_by_server(self) -> Dict[str, CacheMetrics]:
        metrics = {}
        for server_session in self.session.server_sessions:
            server = server_session.server_name_normalized
            total = sum(c.input_tokens for c in server_session.calls)
            cached = sum(c.cache_read_tokens or 0 for c in server_session.calls)

            metrics[server] = CacheMetrics(total, cached, 0.1)

        return metrics

    def _analyze_by_tool(self) -> Dict[str, CacheMetrics]:
        metrics = {}
        for server_session in self.session.server_sessions:
            for call in server_session.calls:
                tool = f"{server_session.server_name_normalized}__{call.tool_name}"
                if tool not in metrics:
                    metrics[tool] = CacheMetrics(0, 0, 0.1)

                metrics[tool].total_tokens += call.input_tokens or 0
                metrics[tool].cached_tokens += call.cache_read_tokens or 0

        return metrics
```

### Potential Savings Calculator

```python
def calculate_potential_savings(report: CacheReport) -> dict:
    """Calculate potential savings if cache rates improved."""

    # What if low-cache tools matched average?
    avg_hit_rate = sum(m.hit_rate for m in report.by_tool.values()) / len(report.by_tool)

    potential_savings = 0
    recommendations = []

    for tool, metrics in report.by_tool.items():
        if metrics.hit_rate < avg_hit_rate * 0.5:  # Less than half of average
            # Calculate tokens that could be cached
            potential_cached = metrics.total_tokens * avg_hit_rate
            additional_cached = potential_cached - metrics.cached_tokens

            if additional_cached > 0:
                savings = additional_cached * 0.0027 / 1000  # Cost difference
                potential_savings += savings
                recommendations.append({
                    "tool": tool,
                    "current_rate": metrics.hit_rate,
                    "target_rate": avg_hit_rate,
                    "potential_savings": savings
                })

    return {
        "total_potential_savings": potential_savings,
        "recommendations": recommendations
    }
```

---

## Report Output

```
Cache Efficiency Analysis
════════════════════════════════════════════════════════════════

Summary
────────────────────────────────────────────────────────────────
Total cached tokens:        125,000
Effective savings:          $0.94 (28% of potential cost)
Overall hit rate:           67%

By Model
────────────────────────────────────────────────────────────────
claude-sonnet-4-5           73% hit rate    $0.62 saved
gpt-5-codex                 45% hit rate    $0.18 saved
gemini-2.5-pro              82% hit rate    $0.14 saved

Worst Cache Performers (Optimization Targets)
────────────────────────────────────────────────────────────────
mcp__websearch__raw_html          0% reuse (always different pages)
mcp__docs__semantic_search        5% reuse
mcp__github__get_issues          12% reuse

Best Cache Performers
────────────────────────────────────────────────────────────────
mcp__project_docs__faq           74% reuse
mcp__zen__apilookup              68% reuse
mcp__config__read                65% reuse

Potential Savings
────────────────────────────────────────────────────────────────
If low-cache tools matched average (67%):
  → Additional cached:     38,000 tokens
  → Additional savings:    $0.28/session

Recommendations:
  → mcp__docs__semantic_search: Cache search results for 5 minutes
  → mcp__github__get_issues: Use cached issue list for recent queries
```

---

## CLI Flags

```bash
# Include cache drilldown in report
mcp-analyze report --cache-analysis

# Focus on specific model
mcp-analyze report --cache-analysis --model claude-sonnet-4-5

# Show only low-cache tools
mcp-analyze report --cache-analysis --low-cache-only

# Export for further analysis
mcp-analyze report --cache-analysis --format csv > cache-report.csv
```

---

## User Value

- **Cost optimization**: Identify where caching could save money
- **Tool selection**: Choose tools with better cache behavior
- **Server evaluation**: Compare servers by cache efficiency
- **Actionable recommendations**: Specific suggestions per tool

---

## Dependencies

- Cache token tracking in session data (existing)
- Per-tool and per-server aggregation (existing)
- Pricing configuration for savings calculations

---

## Success Metrics

- Cache analysis available for all sessions
- Identifies top 5 cache optimization opportunities
- Potential savings estimates within 20% accuracy

---

## References

- Anthropic cache pricing documentation
- OpenAI cached token handling
- Gemini cached content behavior
