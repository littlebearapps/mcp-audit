# Idea: Context Bloat Sources Analysis

**Status**: Proposed
**Priority**: High
**Phase**: v1.0+
**Related**: idea-context-slices-data-model.md, idea-static-mcp-footprint-analyzer.md

---

## Summary

Provide comprehensive analysis of where context bloat originates across all supported platforms (Claude Code, Codex CLI, Gemini CLI), enabling users to understand and optimize their context usage.

---

## Problem Statement

Users with many MCP tools (e.g., 50-60 tools in one server) experience severe context bloat. Scott Spence's analysis showed 20 tools consuming 14,214 tokens (41% of context window) before any conversation started. Users currently have no visibility into:

- Static footprint per session (what's already in context before doing anything)
- How much of each model call is "useful" vs overhead
- Platform-specific bloat patterns

---

## Proposed Solution

### Shared Bloat Patterns (All Platforms)

Track and categorize context consumption across these universal categories:

**System Stuff**
- System prompt
- Built-in tool descriptions
- Safety scaffolding / routing instructions

**Static Instructions**
- AGENTS.md / CLAUDE.md / GEMINI.md files
- Per-project config files
- Custom memory files

**MCP Metadata**
- Tool definitions (names, descriptions, parameter schemas, examples)
- Per-server metadata (auth notes, warnings, etc.)

**Dynamic Context**
- Conversation history
- Tool outputs (MCP + built-ins)
- Workspace context (file snippets, diffs, logs)
- Reasoning traces (especially Gemini 2.5 Pro)

### Platform-Specific Analysis

#### Claude Code Bloat Sources

1. **MCP tool definitions** - Every tool's description + schema in "System tools" / "MCP tools" chunk
2. **Custom instructions & memory** - CLAUDE.md, project docs, custom subagents
3. **Dynamic tool output** - File search, semantic search, external APIs
4. **Conversation history** - Long sessions without `/clear`

Data sources:
- OTel telemetry (token usage, cost, latency)
- `/context` command breakdown (if available)
- AGENTS/CLAUDE files auto-loaded

#### Codex CLI Bloat Sources

1. **AGENTS.md and instructions** - Codex leans heavily on AGENTS.md
2. **MCP tool metadata** - Tool descriptions pulled like Claude
3. **Workspace context** - Files, diffs, error logs fed to model
4. **Tool outputs** - MCP servers for GitHub, Datadog, etc.
5. **Conversation history** - Rolling chat in interactive TUI

Data sources:
- OTel telemetry (codex.api_request, codex.tool_result)
- Heuristic analysis (no `/context` equivalent)

#### Gemini CLI Bloat Sources

1. **Tool results** - Large doc/code retrieval via MCP
2. **Thought traces** - `thoughts_token_count` (hidden reasoning)
3. **Cached content** - `cached_content_token_count` uses logical window
4. **Chat compression** - When CLI compacts history
5. **MCP servers & extensions** - `tool_type = mcp | native`

Data sources (most observability-friendly):
- `gemini_cli.api_response` with input/output/cached/thoughts/tool token counts
- `gemini_cli.tool_call` with function_name, duration, content_length
- `gemini_cli.file_operation` with diff stats
- `gemini_cli.chat_compression` with tokens_before/after

---

## Implementation Details

### Data Collection

For each platform adapter, emit bloat source events:

```python
class BloatSourceEvent:
    timestamp: datetime
    platform: str  # claude_code | codex_cli | gemini_cli
    session_id: str
    category: str  # system | instructions | mcp_metadata | tool_output | history | thoughts
    source: str    # specific file, tool, or component
    tokens: int
    is_static: bool  # True for pre-conversation overhead
```

### Report Output

```
Context Bloat Analysis (Claude Code Session)
────────────────────────────────────────────
Total window: 200k tokens
  • System prompt                  3.1k  (1.5%)
  • System tools                  12.4k  (6.2%)
  • MCP tool metadata             82.0k (41.0%)   ← BLOAT WARNING
  • Custom agents                    584 (0.3%)
  • Memory files                     312 (0.2%)
  • Conversation history          18.2k  (9.1%)
  • Tool outputs                  42.3k (21.2%)
  • Reserved + free               41.1k (20.5%)
```

---

## User Value

- **Visibility**: See exactly where context is being consumed
- **Optimization**: Identify which MCP servers/tools to trim
- **Comparison**: Compare bloat patterns across platforms
- **Prevention**: Catch bloat before hitting context limits

---

## Dependencies

- Platform telemetry access (OTel for all three)
- MCP metadata analyzer (existing `analyze-mcp-efficiency.py`)
- File tokenization for instruction files

---

## Success Metrics

- Users can identify top 3 bloat sources in any session
- Static overhead percentage visible before first prompt
- Platform-specific recommendations generated automatically

---

## References

- Scott Spence MCP metadata analysis (14,214 tokens for 20 tools)
- Claude Code `/context` command output format
- Gemini CLI telemetry documentation
- Codex CLI security guide (OTel events)
