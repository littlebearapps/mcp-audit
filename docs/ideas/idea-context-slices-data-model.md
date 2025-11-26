# Idea: Context Slices Data Model

**Status**: Proposed
**Priority**: High
**Phase**: v1.0+
**Related**: idea-context-bloat-sources.md, idea-context-categories-reports.md

---

## Summary

Upgrade the core data model to include "context slices" per model call, with attributes showing where tokens came from (tools, thoughts, instructions, files, messages). This enables precise attribution of context consumption.

---

## Problem Statement

Current MCP Audit tracks per-call token usage but doesn't break down WHERE those tokens came from. Users can see total tokens but not:

- How much is static overhead vs dynamic content
- Which specific tools/files contributed to each call
- Whether context is dominated by tool outputs, history, or metadata

---

## Proposed Solution

### Normalized Event Schema (Cross-Platform)

```json
{
  "timestamp": "2025-11-26T10:30:00Z",
  "platform": "claude_code | codex_cli | gemini_cli",
  "session_id": "abc123",
  "model": "claude-sonnet-4-5 | gpt-5-codex | gemini-2.5-pro",
  "event_type": "model_call | tool_call | tool_result | file_context | chat_compression | system",
  "mcp_server": "mcp__brave-search",
  "mcp_tool": "web_search",
  "tool_type": "mcp | native",
  "file": "src/foo/bar.py",
  "token_breakdown": {
    "input_total": 12345,
    "output_total": 678,
    "cache": 1000,
    "tool_results": 4000,
    "thoughts": 1200,
    "overhead_static": 2000,
    "overhead_history": 4145
  }
}
```

### Token Breakdown Fields

| Field | Description | Platforms |
|-------|-------------|-----------|
| `input_total` | Total input tokens for this call | All |
| `output_total` | Total output tokens | All |
| `cache` | Cached/reused tokens | All |
| `tool_results` | Tokens from tool outputs in context | All |
| `thoughts` | Hidden reasoning tokens | Gemini |
| `overhead_static` | Tool definitions, instructions (estimated) | All |
| `overhead_history` | Previous messages, prior tool results | All |

---

## Implementation Details

### Per-Platform Data Sources

#### Claude Code
- OTel metrics: `claude_code.token.usage`, `claude_code.cost.usage`
- Events: User Prompt, Tool Result, API Request, Tool Decision
- Static analysis: MCP metadata tokenization, CLAUDE.md tokenization

#### Codex CLI
- OTel events: `codex.api_request`, `codex.user_prompt`, `codex.tool_result`
- Heuristic: `overhead_tokens ≈ input_tokens - prompt_tokens`
- Static analysis: AGENTS.md tokenization, MCP metadata

#### Gemini CLI
- Direct fields: `input_token_count`, `output_token_count`, `cached_content_token_count`, `thoughts_token_count`, `tool_token_count`
- Events: `gemini_cli.api_response`, `gemini_cli.tool_call`, `gemini_cli.file_operation`

### Filling Partial Data

Not every field will be available for every platform. Strategy:

1. **Fill what's directly available** from telemetry
2. **Estimate what's derivable** (e.g., static overhead from known MCP metadata)
3. **Leave unknown as null** rather than guessing

```python
@dataclass
class TokenBreakdown:
    input_total: int
    output_total: int
    cache: int | None = None
    tool_results: int | None = None
    thoughts: int | None = None
    overhead_static: int | None = None
    overhead_history: int | None = None

    @property
    def known_total(self) -> int:
        """Sum of known breakdown components."""
        return sum(v for v in [
            self.cache, self.tool_results, self.thoughts,
            self.overhead_static, self.overhead_history
        ] if v is not None)

    @property
    def unattributed(self) -> int:
        """Tokens not yet attributed to a category."""
        return self.input_total - self.known_total
```

---

## Report Capabilities

With context slices, build:

### 1. "Top Context Hogs" Tables

Per session, rank what's consuming the most context:

```
Top Context Contributors
────────────────────────
1. mcp__zen__thinkdeep outputs     45,231 tokens (32%)
2. MCP tool definitions            28,400 tokens (20%)
3. Conversation history            18,200 tokens (13%)
4. mcp__brave-search outputs       12,100 tokens (9%)
5. Instructions (CLAUDE.md)         7,890 tokens (6%)
```

### 2. Time Series of Overhead Share

Track "% of context that's overhead vs useful" across a session:

```
Time    Input    Overhead%   Notes
10:03   12,000   40%         first big tool usage
10:08   38,000   68%         multiple tools; compression fired
10:12   17,500   52%         conversation continues
```

### 3. Per-MCP Server/Tool Attribution

Not just tokens sent/returned, but tokens living in window thereafter:

```
mcp__omnisearch
  • Static metadata:  14,214 tokens
  • Tool outputs:     91,331 tokens (in context after calls)
  • Share of context: 33%
```

---

## User Value

- **Precise attribution**: Know exactly what's consuming context
- **Optimization guidance**: Target the right components for reduction
- **Cross-platform consistency**: Compare apples-to-apples across CLIs
- **Trend analysis**: See how context composition changes over time

---

## Dependencies

- Platform adapters updated to emit `token_breakdown`
- MCP metadata analyzer for `overhead_static` estimation
- Session-level aggregation logic

---

## Success Metrics

- 80%+ of input tokens attributed to specific categories
- Context breakdown available for all supported platforms
- Users can identify top 3 context consumers per session

---

## References

- Gemini CLI telemetry docs (most complete token breakdown)
- Claude Code OTel specification
- Codex CLI security guide
