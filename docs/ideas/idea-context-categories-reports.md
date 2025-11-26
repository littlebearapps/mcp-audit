# Idea: Context Categories in Reports

**Status**: Proposed
**Priority**: High
**Phase**: v1.0
**Related**: idea-context-slices-data-model.md, idea-context-bloat-sources.md

---

## Summary

Add a normalized context breakdown to all reports, categorizing tokens into: user_prompts, tool_outputs, mcp_tool_metadata, instructions_memory, thoughts, cache, and other_history. This provides a consistent view across all platforms.

---

## Problem Statement

Users see total token counts but can't easily understand:

- What percentage of context is their actual work vs overhead
- Which category is consuming the most tokens
- How to reduce context usage effectively

A standardized breakdown enables quick diagnosis regardless of platform.

---

## Proposed Solution

### Standard Categories

| Category | Description | Example Sources |
|----------|-------------|-----------------|
| `user_prompts` | User messages/instructions | Direct user input |
| `tool_outputs` | Results from tool calls | MCP tool responses, file reads |
| `mcp_tool_metadata` | Static tool definitions | Tool descriptions, schemas |
| `instructions_memory` | Config files, memory | CLAUDE.md, AGENTS.md, custom memory |
| `thoughts` | Hidden reasoning | Gemini 2.5 Pro reasoning traces |
| `cache` | Cached/reused tokens | Previously seen content |
| `other_history` | Conversation history | Prior assistant responses, context |

### Report Format

```
Context Composition (per model input)
─────────────────────────────────────
Category                  Tokens      Share
─────────────────────────────────────
User prompts              24,310      18%
Tool outputs              61,520      45%    ← Largest
MCP tool definitions      28,400      21%
Instructions & memory      7,890       6%
Thoughts (hidden)         10,200       7%
Other history              4,680       3%
─────────────────────────────────────
Total                    137,000     100%
```

### Visualization Options

**Bar chart (ASCII)**:
```
User prompts      ████████░░░░░░░░░░░░░  18%
Tool outputs      █████████████████████  45%
MCP metadata      ██████████░░░░░░░░░░░  21%
Instructions      ███░░░░░░░░░░░░░░░░░░   6%
Thoughts          ████░░░░░░░░░░░░░░░░░   7%
Other history     ██░░░░░░░░░░░░░░░░░░░   3%
```

**Pie chart (for HTML export)**:
- Color-coded segments per category
- Hover for exact values

---

## Implementation Details

### Data Structure

```python
from dataclasses import dataclass
from typing import Dict

@dataclass
class ContextCategories:
    user_prompts: int = 0
    tool_outputs: int = 0
    mcp_tool_metadata: int = 0
    instructions_memory: int = 0
    thoughts: int = 0
    cache: int = 0
    other_history: int = 0

    @property
    def total(self) -> int:
        return sum([
            self.user_prompts,
            self.tool_outputs,
            self.mcp_tool_metadata,
            self.instructions_memory,
            self.thoughts,
            self.cache,
            self.other_history
        ])

    def as_percentages(self) -> Dict[str, float]:
        total = self.total
        if total == 0:
            return {k: 0.0 for k in self.__dataclass_fields__}
        return {
            "user_prompts": self.user_prompts / total * 100,
            "tool_outputs": self.tool_outputs / total * 100,
            "mcp_tool_metadata": self.mcp_tool_metadata / total * 100,
            "instructions_memory": self.instructions_memory / total * 100,
            "thoughts": self.thoughts / total * 100,
            "cache": self.cache / total * 100,
            "other_history": self.other_history / total * 100
        }
```

### Platform-Specific Mapping

**Claude Code**:
```python
def map_claude_categories(event) -> ContextCategories:
    categories = ContextCategories()

    if event.type == "user_prompt":
        categories.user_prompts = event.tokens
    elif event.type == "tool_result":
        categories.tool_outputs = event.tokens
    elif event.type == "api_request":
        # Estimate breakdown from total
        categories.mcp_tool_metadata = estimate_static_overhead(event)
        categories.other_history = event.input_tokens - categories.mcp_tool_metadata

    return categories
```

**Gemini CLI** (most precise):
```python
def map_gemini_categories(api_response) -> ContextCategories:
    return ContextCategories(
        tool_outputs=api_response.tool_token_count,
        thoughts=api_response.thoughts_token_count,
        cache=api_response.cached_content_token_count,
        # Estimate remainder
        other_history=api_response.input_token_count - (
            api_response.tool_token_count +
            api_response.thoughts_token_count +
            api_response.cached_content_token_count
        )
    )
```

**Codex CLI**:
```python
def map_codex_categories(event) -> ContextCategories:
    categories = ContextCategories()

    if event.type == "user_prompt":
        categories.user_prompts = event.token_count
    elif event.type == "tool_result":
        categories.tool_outputs = estimate_tokens(event.content_length)

    # Overhead = total - known components
    categories.other_history = event.total_input - categories.total

    return categories
```

### Report Generator

```python
def generate_context_report(session: Session) -> str:
    categories = aggregate_categories(session.calls)
    percentages = categories.as_percentages()

    lines = [
        "Context Composition (per model input)",
        "─" * 37,
        f"{'Category':<25} {'Tokens':>10} {'Share':>8}",
        "─" * 37,
    ]

    for name, tokens in [
        ("User prompts", categories.user_prompts),
        ("Tool outputs", categories.tool_outputs),
        ("MCP tool definitions", categories.mcp_tool_metadata),
        ("Instructions & memory", categories.instructions_memory),
        ("Thoughts (hidden)", categories.thoughts),
        ("Cache", categories.cache),
        ("Other history", categories.other_history),
    ]:
        if tokens > 0:
            pct = percentages[name.lower().replace(" ", "_").replace("&", "and")]
            lines.append(f"{name:<25} {tokens:>10,} {pct:>7.1f}%")

    lines.append("─" * 37)
    lines.append(f"{'Total':<25} {categories.total:>10,} {'100.0%':>8}")

    return "\n".join(lines)
```

---

## User Value

- **Quick diagnosis**: See at a glance what's consuming context
- **Actionable insights**: Know which category to optimize
- **Platform consistency**: Same breakdown format across all CLIs
- **Trend tracking**: Compare categories across sessions

---

## CLI Flags

```bash
# Include context breakdown in report
mcp-analyze report --context-breakdown

# Show only categories above threshold
mcp-analyze report --context-breakdown --min-share 5%

# Output as JSON for further processing
mcp-analyze report --context-breakdown --format json
```

---

## Dependencies

- Context slices data model (idea-context-slices-data-model.md)
- Platform adapters updated to emit category data
- Static footprint analyzer for MCP metadata estimates

---

## Success Metrics

- Context breakdown shown in 100% of session reports
- All 7 categories populated (even if estimated)
- Users identify top bloat category in <10 seconds

---

## References

- Claude `/context` command output format
- Gemini CLI telemetry token breakdown
