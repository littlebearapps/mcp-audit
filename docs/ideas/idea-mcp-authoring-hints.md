# Idea: MCP Authoring Hints

**Status**: Proposed
**Priority**: Medium
**Phase**: v1.0+
**Related**: idea-static-mcp-footprint-analyzer.md, idea-what-if-simulations.md

---

## Summary

Provide lightweight "lint-style" suggestions for MCP server authors based on observed tool metadata and usage patterns, helping them optimize descriptions, consolidate tools, and reduce context overhead.

---

## Problem Statement

MCP server authors often don't realize their servers are consuming excessive context. Common issues:

- Verbose tool descriptions (80+ tokens when 10-20 would suffice)
- Multiple similar tools that could be consolidated
- Large parameter schemas with redundant fields
- Tools that are rarely used but always loaded

Case study: Consolidating tools and trimming descriptions reduced MCP metadata tokens by 60% for one server.

---

## Proposed Solution

### Automated Hints

Analyze MCP server metadata and generate actionable suggestions:

```
MCP Authoring Hints
════════════════════════════════════════════════════════════════

mcp__omnisearch
────────────────────────────────────────────────────────────────
Stats:
  • 20 tools, 14,214 metadata tokens (avg 710/tool)
  • 5 tools never called in last 7 days
  • Description verbosity: HIGH (avg 80 tokens/tool)

Suggestions:
  ⚠️  HIGH IMPACT: Similar tools detected
      Tools with near-identical schemas: tavily_search, brave_search,
      kagi_search, exa_search
      → Consider: Consolidate to one `web_search` tool with `provider` param
      → Estimated savings: 2,400 tokens (17%)

  ⚠️  MEDIUM IMPACT: Verbose descriptions
      Average description: 80 tokens (recommended: 10-20)
      Worst offenders:
        • ai_search: 145 tokens
        • web_search: 120 tokens
        • firecrawl_process: 98 tokens
      → Consider: Trim to essential functionality only
      → Estimated savings: 1,200 tokens (8%)

  ℹ️  LOW IMPACT: Unused tools
      Never called in 7 days: batch_process, export_results,
                              advanced_config, legacy_search, debug_mode
      → Consider: Move to separate "advanced" server or lazy-load
      → Estimated savings: 3,500 tokens (25%)

mcp__docs
────────────────────────────────────────────────────────────────
Stats:
  • 12 tools, 9,120 metadata tokens (avg 760/tool)
  • Description verbosity: MEDIUM (avg 45 tokens/tool)

Suggestions:
  ℹ️  LOW IMPACT: Schema optimization
      Tools with large inputSchema: semantic_search (42 fields)
      → Consider: Use $ref for common field groups
      → Estimated savings: 400 tokens (4%)
```

### Hint Categories

| Category | Description | Impact |
|----------|-------------|--------|
| **Consolidation** | Similar tools that could be merged | High |
| **Verbosity** | Descriptions longer than recommended | Medium |
| **Unused Tools** | Tools not called in recent sessions | Medium |
| **Schema Size** | Large inputSchema definitions | Low |
| **Examples Bloat** | Excessive examples in tool definitions | Low |

---

## Implementation Details

### Hint Detection Rules

```python
from dataclasses import dataclass
from typing import List, Dict
from enum import Enum

class HintSeverity(Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


@dataclass
class AuthoringHint:
    severity: HintSeverity
    category: str
    title: str
    description: str
    affected_tools: List[str]
    estimated_savings: int  # tokens
    recommendation: str


class HintDetector:
    # Thresholds
    VERBOSE_DESCRIPTION_THRESHOLD = 50  # tokens
    IDEAL_DESCRIPTION_LENGTH = 15  # tokens
    SIMILAR_SCHEMA_THRESHOLD = 0.8  # 80% similarity
    UNUSED_DAYS_THRESHOLD = 7

    def __init__(self, footprint: ServerFootprint, usage: ServerUsage):
        self.footprint = footprint
        self.usage = usage

    def detect_all(self) -> List[AuthoringHint]:
        hints = []
        hints.extend(self._detect_consolidation_opportunities())
        hints.extend(self._detect_verbose_descriptions())
        hints.extend(self._detect_unused_tools())
        hints.extend(self._detect_schema_bloat())
        return sorted(hints, key=lambda h: h.severity.value)

    def _detect_consolidation_opportunities(self) -> List[AuthoringHint]:
        """Find tools with similar schemas that could be merged."""
        hints = []
        similar_groups = self._find_similar_tools()

        for group in similar_groups:
            if len(group) >= 3:
                savings = sum(
                    self.footprint.tools[t].total
                    for t in group[1:]  # Keep one, remove others
                )
                hints.append(AuthoringHint(
                    severity=HintSeverity.HIGH,
                    category="consolidation",
                    title="Similar tools detected",
                    description=f"Tools with near-identical schemas: {', '.join(group)}",
                    affected_tools=group,
                    estimated_savings=savings,
                    recommendation=f"Consolidate to one tool with a 'provider' or 'type' parameter"
                ))

        return hints

    def _detect_verbose_descriptions(self) -> List[AuthoringHint]:
        """Find tools with overly long descriptions."""
        verbose_tools = []

        for tool_name, tool in self.footprint.tools.items():
            if tool.description_tokens > self.VERBOSE_DESCRIPTION_THRESHOLD:
                verbose_tools.append((tool_name, tool.description_tokens))

        if verbose_tools:
            avg_current = sum(t[1] for t in verbose_tools) / len(verbose_tools)
            savings = sum(
                t[1] - self.IDEAL_DESCRIPTION_LENGTH
                for t in verbose_tools
            )

            return [AuthoringHint(
                severity=HintSeverity.MEDIUM,
                category="verbosity",
                title="Verbose descriptions",
                description=f"Average description: {avg_current:.0f} tokens (recommended: {self.IDEAL_DESCRIPTION_LENGTH})",
                affected_tools=[t[0] for t in verbose_tools],
                estimated_savings=savings,
                recommendation="Trim descriptions to essential functionality only"
            )]

        return []

    def _detect_unused_tools(self) -> List[AuthoringHint]:
        """Find tools not called in recent sessions."""
        unused = []
        for tool_name in self.footprint.tools:
            if tool_name not in self.usage.tools_called:
                unused.append(tool_name)

        if unused and len(unused) >= 2:
            savings = sum(
                self.footprint.tools[t].total
                for t in unused
            )
            return [AuthoringHint(
                severity=HintSeverity.MEDIUM,
                category="unused",
                title="Unused tools",
                description=f"Never called in {self.UNUSED_DAYS_THRESHOLD} days: {', '.join(unused[:5])}{'...' if len(unused) > 5 else ''}",
                affected_tools=unused,
                estimated_savings=savings,
                recommendation="Move to separate 'advanced' server or implement lazy-loading"
            )]

        return []

    def _detect_schema_bloat(self) -> List[AuthoringHint]:
        """Find tools with excessively large schemas."""
        hints = []
        for tool_name, tool in self.footprint.tools.items():
            if tool.schema_tokens > 200:  # Arbitrary threshold
                hints.append(AuthoringHint(
                    severity=HintSeverity.LOW,
                    category="schema",
                    title="Large schema",
                    description=f"Tool '{tool_name}' has {tool.schema_tokens} schema tokens",
                    affected_tools=[tool_name],
                    estimated_savings=tool.schema_tokens // 2,
                    recommendation="Use $ref for common field groups or simplify parameters"
                ))
        return hints

    def _find_similar_tools(self) -> List[List[str]]:
        """Group tools by schema similarity."""
        # Simplified: group by parameter names
        groups = {}
        for tool_name, tool in self.footprint.tools.items():
            param_signature = frozenset(tool.parameters.keys())
            if param_signature not in groups:
                groups[param_signature] = []
            groups[param_signature].append(tool_name)

        return [g for g in groups.values() if len(g) > 1]
```

### Report Generator

```python
def generate_hints_report(hints: List[AuthoringHint], server: str) -> str:
    lines = [
        f"MCP Authoring Hints: {server}",
        "═" * 64,
        ""
    ]

    # Group by severity
    by_severity = {s: [] for s in HintSeverity}
    for hint in hints:
        by_severity[hint.severity].append(hint)

    total_savings = sum(h.estimated_savings for h in hints)

    for severity in [HintSeverity.HIGH, HintSeverity.MEDIUM, HintSeverity.LOW]:
        severity_hints = by_severity[severity]
        if not severity_hints:
            continue

        icon = "⚠️" if severity in [HintSeverity.HIGH, HintSeverity.MEDIUM] else "ℹ️"

        for hint in severity_hints:
            lines.extend([
                f"{icon}  {severity.value.upper()} IMPACT: {hint.title}",
                f"    {hint.description}",
                f"    → {hint.recommendation}",
                f"    → Estimated savings: {hint.estimated_savings:,} tokens",
                ""
            ])

    lines.extend([
        "─" * 64,
        f"Total potential savings: {total_savings:,} tokens",
    ])

    return "\n".join(lines)
```

---

## CLI Interface

```bash
# Analyze all configured MCP servers
mcp-audit hints

# Analyze specific server
mcp-audit hints --server mcp__omnisearch

# Include usage data for unused tool detection
mcp-audit hints --with-usage --last 7

# Output as JSON for automation
mcp-audit hints --format json

# Only show high-impact hints
mcp-audit hints --severity high
```

---

## User Value

- **Actionable optimization**: Specific suggestions with estimated impact
- **For server authors**: Improve their servers for all users
- **For server users**: Understand overhead from third-party servers
- **Quantified impact**: Token savings estimates guide prioritization

---

## Example Optimizations

### Before: 4 Similar Search Tools

```json
{
  "tools": [
    {"name": "tavily_search", "description": "Search using Tavily API..."},
    {"name": "brave_search", "description": "Search using Brave API..."},
    {"name": "kagi_search", "description": "Search using Kagi API..."},
    {"name": "exa_search", "description": "Search using Exa API..."}
  ]
}
```
**Cost**: 2,800 tokens

### After: 1 Unified Search Tool

```json
{
  "tools": [{
    "name": "web_search",
    "description": "Web search with provider selection",
    "inputSchema": {
      "provider": {"enum": ["tavily", "brave", "kagi", "exa"]},
      "query": {"type": "string"}
    }
  }]
}
```
**Cost**: 700 tokens
**Savings**: 2,100 tokens (75%)

---

## Dependencies

- Static footprint analyzer (for metadata token counts)
- Usage tracking (for unused tool detection)
- Schema parsing (for similarity detection)

---

## Success Metrics

- Hints generated for all servers with >5 tools
- At least one actionable hint per server
- Estimated savings within 20% of actual

---

## References

- "Optimising MCP Context Usage" article (60% reduction case study)
- MCP tool definition best practices
- Token optimization strategies
