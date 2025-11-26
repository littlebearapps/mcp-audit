# Idea: Cross-Platform Comparison

**Status**: Proposed
**Priority**: Medium
**Phase**: v1.0+
**Related**: idea-context-categories-reports.md

---

## Summary

Enable users to compare token usage, costs, and efficiency metrics across different platforms (Claude Code, Codex CLI, Gemini CLI) normalized by time or task, helping them choose the right tool for different workflows.

---

## Problem Statement

Users working across multiple AI coding assistants want to know:

- Which platform is most cost-effective for their workflow?
- How do token usage patterns differ between platforms?
- Where should they invest MCP server optimization first?
- Are some tasks better suited to specific platforms?

---

## Proposed Solution

### Comparison Modes

#### 1. Per-Hour Normalized Comparison

```bash
mcp-analyze report --compare-platforms --last 7
```

Output:
```
7-Day Platform Comparison (normalized per hour of active use)
════════════════════════════════════════════════════════════════

Platform        Sessions    Hours    Tokens/hr    Cost/hr    MCP %
────────────────────────────────────────────────────────────────
Claude Code          12     8.5       52,000      $0.18      63%
Codex CLI             8     5.2       39,000      $0.14      41%
Gemini CLI            6     4.1       61,000      $0.12      38%
────────────────────────────────────────────────────────────────

Key Insights:
  → Gemini CLI: Highest tokens/hr but lowest cost (larger window, cheaper)
  → Claude Code: Highest MCP share - consider trimming MCP servers
  → Codex CLI: Most efficient for MCP-light workflows
```

#### 2. Same-Task Comparison

Compare sessions doing similar work:

```bash
mcp-analyze report --compare-platforms --tag "code-review"
```

Output:
```
Task Comparison: code-review
════════════════════════════════════════════════════════════════

Platform        Sessions    Avg Time    Avg Tokens    Avg Cost
────────────────────────────────────────────────────────────────
Claude Code          4       12 min       45,000       $0.14
Codex CLI            3       15 min       38,000       $0.11
Gemini CLI           2       10 min       52,000       $0.08
────────────────────────────────────────────────────────────────

Winner by cost: Gemini CLI ($0.08/review)
Winner by time: Gemini CLI (10 min/review)
Winner by efficiency: Codex CLI (2,533 tokens/min)
```

#### 3. MCP Server Efficiency by Platform

```bash
mcp-analyze report --compare-platforms --by-server
```

Output:
```
MCP Server Efficiency by Platform
════════════════════════════════════════════════════════════════

mcp__zen
────────────────────────────────────────────────────────────────
Platform        Calls    Tokens/call    Cache %    Cost/call
────────────────────────────────────────────────────────────────
Claude Code        45       3,200         72%       $0.010
Codex CLI          32       2,800         65%       $0.008
Gemini CLI         28       3,500         78%       $0.006
────────────────────────────────────────────────────────────────
Best: Gemini CLI (highest cache %, lowest cost)

mcp__brave-search
────────────────────────────────────────────────────────────────
Platform        Calls    Tokens/call    Cache %    Cost/call
────────────────────────────────────────────────────────────────
Claude Code        23       8,500         12%       $0.026
Codex CLI          18       7,200         15%       $0.021
Gemini CLI         15       9,100          8%       $0.015
────────────────────────────────────────────────────────────────
Best: Gemini CLI (lowest cost despite low cache)
```

---

## Implementation Details

### Data Structures

```python
from dataclasses import dataclass
from typing import Dict, List, Optional
from datetime import timedelta

@dataclass
class PlatformMetrics:
    platform: str
    session_count: int
    total_duration: timedelta
    total_tokens: int
    total_cost: float
    mcp_tokens: int
    cache_tokens: int

    @property
    def tokens_per_hour(self) -> float:
        hours = self.total_duration.total_seconds() / 3600
        return self.total_tokens / hours if hours > 0 else 0

    @property
    def cost_per_hour(self) -> float:
        hours = self.total_duration.total_seconds() / 3600
        return self.total_cost / hours if hours > 0 else 0

    @property
    def mcp_share(self) -> float:
        return (self.mcp_tokens / self.total_tokens * 100) if self.total_tokens > 0 else 0

    @property
    def cache_rate(self) -> float:
        return (self.cache_tokens / self.total_tokens * 100) if self.total_tokens > 0 else 0


@dataclass
class PlatformComparison:
    metrics: Dict[str, PlatformMetrics]
    time_range_days: int
    normalized_by: str  # "hour" | "session" | "task"

    def rank_by_cost(self) -> List[str]:
        return sorted(self.metrics.keys(), key=lambda p: self.metrics[p].cost_per_hour)

    def rank_by_efficiency(self) -> List[str]:
        # Lower tokens per hour with similar output = more efficient
        return sorted(self.metrics.keys(), key=lambda p: self.metrics[p].tokens_per_hour)

    def winner(self, metric: str) -> str:
        if metric == "cost":
            return self.rank_by_cost()[0]
        elif metric == "efficiency":
            return self.rank_by_efficiency()[0]
        elif metric == "cache":
            return max(self.metrics.keys(), key=lambda p: self.metrics[p].cache_rate)
        return ""
```

### Comparison Analyzer

```python
class PlatformComparisonAnalyzer:
    def __init__(self, storage: StorageManager):
        self.storage = storage

    def compare(
        self,
        days: int = 7,
        tag: Optional[str] = None,
        platforms: Optional[List[str]] = None
    ) -> PlatformComparison:
        """Compare platforms over time range."""

        # Load sessions for each platform
        metrics = {}
        for platform in platforms or ["claude_code", "codex_cli", "gemini_cli"]:
            sessions = self.storage.load_sessions(
                platform=platform,
                days=days,
                tag=tag
            )

            if sessions:
                metrics[platform] = self._calculate_metrics(platform, sessions)

        return PlatformComparison(
            metrics=metrics,
            time_range_days=days,
            normalized_by="hour"
        )

    def _calculate_metrics(self, platform: str, sessions: List[Session]) -> PlatformMetrics:
        total_duration = sum(
            (s.ended_at - s.started_at for s in sessions if s.ended_at),
            timedelta()
        )
        total_tokens = sum(s.total_tokens for s in sessions)
        total_cost = sum(s.total_cost for s in sessions)
        mcp_tokens = sum(s.mcp_tokens for s in sessions)
        cache_tokens = sum(s.cache_tokens for s in sessions)

        return PlatformMetrics(
            platform=platform,
            session_count=len(sessions),
            total_duration=total_duration,
            total_tokens=total_tokens,
            total_cost=total_cost,
            mcp_tokens=mcp_tokens,
            cache_tokens=cache_tokens
        )

    def compare_by_server(self, days: int = 7) -> Dict[str, Dict[str, PlatformMetrics]]:
        """Compare MCP server usage across platforms."""
        by_server = {}

        for platform in ["claude_code", "codex_cli", "gemini_cli"]:
            sessions = self.storage.load_sessions(platform=platform, days=days)

            for session in sessions:
                for server_session in session.server_sessions:
                    server = server_session.server_name_normalized
                    if server not in by_server:
                        by_server[server] = {}

                    if platform not in by_server[server]:
                        by_server[server][platform] = PlatformMetrics(
                            platform=platform,
                            session_count=0,
                            total_duration=timedelta(),
                            total_tokens=0,
                            total_cost=0,
                            mcp_tokens=0,
                            cache_tokens=0
                        )

                    # Aggregate server metrics
                    metrics = by_server[server][platform]
                    metrics.total_tokens += server_session.total_tokens
                    metrics.total_cost += server_session.total_cost
                    metrics.session_count += 1

        return by_server
```

### Report Generator

```python
def generate_comparison_report(comparison: PlatformComparison) -> str:
    lines = [
        f"{comparison.time_range_days}-Day Platform Comparison (normalized per hour)",
        "═" * 64,
        "",
        f"{'Platform':<15} {'Sessions':>10} {'Hours':>8} {'Tokens/hr':>12} {'Cost/hr':>10} {'MCP %':>8}",
        "─" * 64,
    ]

    for platform, metrics in sorted(comparison.metrics.items()):
        hours = metrics.total_duration.total_seconds() / 3600
        lines.append(
            f"{platform:<15} {metrics.session_count:>10} {hours:>8.1f} "
            f"{metrics.tokens_per_hour:>12,.0f} ${metrics.cost_per_hour:>9.2f} "
            f"{metrics.mcp_share:>7.0f}%"
        )

    lines.extend([
        "─" * 64,
        "",
        "Key Insights:",
    ])

    # Add insights
    cost_winner = comparison.winner("cost")
    cache_winner = comparison.winner("cache")

    lines.append(f"  → Lowest cost per hour: {cost_winner}")
    lines.append(f"  → Best cache rate: {cache_winner}")

    # Platform-specific recommendations
    for platform, metrics in comparison.metrics.items():
        if metrics.mcp_share > 50:
            lines.append(f"  → {platform}: High MCP share ({metrics.mcp_share:.0f}%) - consider trimming servers")

    return "\n".join(lines)
```

---

## CLI Interface

```bash
# Basic comparison (last 7 days)
mcp-analyze report --compare-platforms

# Custom time range
mcp-analyze report --compare-platforms --last 30

# Filter by tag/task type
mcp-analyze report --compare-platforms --tag "refactoring"

# Compare specific platforms
mcp-analyze report --compare-platforms --platforms claude_code,gemini_cli

# Compare by MCP server
mcp-analyze report --compare-platforms --by-server

# Export comparison data
mcp-analyze report --compare-platforms --format json > comparison.json
```

---

## User Value

- **Informed tool selection**: Choose the right platform for each task
- **Cost optimization**: Know which platform is cheapest for your workflow
- **MCP investment**: Focus optimization on highest-impact platform
- **Workflow analysis**: Understand how different tools perform for you

---

## Dependencies

- Multi-platform session storage
- Consistent session schema across platforms
- Duration tracking per session

---

## Success Metrics

- Comparison available when 2+ platforms have data
- Normalized metrics within 5% accuracy
- Users can identify best platform for their workflow

---

## References

- Platform pricing documentation (Anthropic, OpenAI, Google)
- Token usage patterns by platform
- Context window sizes by model
