# Codex CLI vs Claude Code Format Differences

**Last Updated**: 2025-11-22
**Purpose**: Document data format differences between Codex CLI and Claude Code session logs for MCP tracking implementation

---

## Overview

Both Codex CLI and Claude Code log session data to JSONL files, but they use different data structures and field names. This document details the differences to enable unified MCP tracking across both platforms.

---

## Session File Locations

| Platform | Location | Format |
|----------|----------|--------|
| **Claude Code** | `~/.config/claude/projects/{project-id}/*.jsonl` | One file per session |
| **Codex CLI** | `~/.codex/sessions/{year}/{month}/{day}/*.jsonl` | Organized by date |

---

## Entry Type Comparison

### Claude Code Entry Types

```json
{
  "type": "assistant",
  "message": {
    "model": "claude-sonnet-4-5-20250929",
    "usage": {...},
    "content": [...]
  }
}
```

### Codex CLI Entry Types

```json
{
  "type": "response_item" | "event_msg" | "session_meta" | "turn_context",
  "timestamp": "2025-11-21T07:00:08.562Z",
  "payload": {...}
}
```

**Key Entry Types:**
- `response_item` - Tool calls, messages, reasoning
- `event_msg` - Token counts, status updates
- `session_meta` - Session initialization
- `turn_context` - Turn-level metadata

---

## Tool Call Format

### Claude Code Format

**Entry Structure:**
```json
{
  "type": "assistant",
  "message": {
    "content": [
      {
        "type": "tool_use",
        "name": "mcp__brave-search__brave_web_search",
        "input": {
          "query": "example search"
        }
      }
    ]
  }
}
```

**Tool Naming:**
- Format: `mcp__{server}__{tool}`
- Example: `mcp__brave-search__brave_web_search`
- Server: `brave-search`
- Tool: `brave_web_search`

### Codex CLI Format

**Entry Structure:**
```json
{
  "type": "response_item",
  "timestamp": "2025-11-21T07:00:08.562Z",
  "payload": {
    "type": "function_call",
    "name": "mcp__brave-search-mcp__brave_web_search",
    "arguments": "{\"query\":\"example search\"}",
    "call_id": "call_DVHBxILAncNdarfVzjqxF1si"
  }
}
```

**Tool Naming:**
- Format: `mcp__{server-name-with-mcp}__{tool}`
- Example: `mcp__brave-search-mcp__brave_web_search`
- Server: `brave-search-mcp` (includes `-mcp` suffix!)
- Tool: `brave_web_search`

**Built-in Tools:**
- `shell` - Shell command execution
- `shell_command` - Alternate shell execution
- `update_plan` - Plan updates
- `list_mcp_resources` - MCP resource listing
- `list_mcp_resource_templates` - MCP template listing

---

## Token Usage Format

### Claude Code Format

**Location:** Same entry as tool use

```json
{
  "type": "assistant",
  "message": {
    "usage": {
      "input_tokens": 9471,
      "output_tokens": 114,
      "cache_creation_input_tokens": 0,
      "cache_read_input_tokens": 8960
    },
    "content": [...]
  }
}
```

**Token Fields:**
- `input_tokens` - Input tokens
- `output_tokens` - Output tokens
- `cache_creation_input_tokens` - Cache creation
- `cache_read_input_tokens` - Cache reads

### Codex CLI Format

**Location:** Separate `event_msg` entry

```json
{
  "type": "event_msg",
  "timestamp": "2025-11-21T07:00:09.503Z",
  "payload": {
    "type": "token_count",
    "info": {
      "last_token_usage": {
        "input_tokens": 9471,
        "cached_input_tokens": 8960,
        "output_tokens": 114,
        "reasoning_output_tokens": 64,
        "total_tokens": 9585
      },
      "total_token_usage": {
        "input_tokens": 18442,
        "cached_input_tokens": 17152,
        "output_tokens": 221,
        "reasoning_output_tokens": 128,
        "total_tokens": 18663
      }
    }
  }
}
```

**Token Fields:**
- `input_tokens` - Input tokens
- `cached_input_tokens` - Cache reads (different name!)
- `output_tokens` - Output tokens
- `reasoning_output_tokens` - Reasoning tokens (NEW!)
- `total_tokens` - Sum of all tokens

**Token Usage Types:**
- `last_token_usage` - Most recent operation
- `total_token_usage` - Cumulative session totals

---

## MCP Server Naming Differences

### Comparison Table

| Server | Claude Code Format | Codex CLI Format |
|--------|-------------------|------------------|
| Brave Search | `mcp__brave-search__*` | `mcp__brave-search-mcp__*` |
| File System | `mcp__fs__*` | `mcp__fs-mcp__*` |
| Ripgrep | `mcp__rg__*` | `mcp__rg-mcp__*` |
| Zen | `mcp__zen__*` | N/A (not observed) |
| Backlog | `mcp__backlog__*` | N/A (not observed) |

**Key Difference:** Codex CLI includes `-mcp` suffix in server names

**Extraction Pattern:**
```python
# Claude Code
"mcp__brave-search__brave_web_search"
# Extract: server = "brave-search"

# Codex CLI
"mcp__brave-search-mcp__brave_web_search"
# Extract: server = "brave-search-mcp"
# Normalize: server = "brave-search" (strip -mcp suffix)
```

---

## Token-to-Tool Correlation

### Claude Code

**Direct Correlation:** Tokens and tools in same entry
```json
{
  "message": {
    "usage": {...},      // Tokens here
    "content": [         // Tools here
      {"type": "tool_use", "name": "..."}
    ]
  }
}
```

### Codex CLI

**Indirect Correlation:** Separate entries, must correlate by timestamp

**Sequence:**
```
07:00:08.562  →  response_item (function_call: mcp__fs-mcp__fs_read)
07:00:09.503  →  event_msg (token_count: 9,585 tokens)
```

**Correlation Methods:**
1. **Timestamp proximity** - Match events within 1-2 seconds
2. **Sequential order** - Next token_count after function_call
3. **Call ID tracking** - Track call_id through function_call → function_call_output → token_count

---

## Data Structure Examples

### Complete Claude Code Entry

```json
{
  "type": "assistant",
  "message": {
    "id": "msg_123",
    "model": "claude-sonnet-4-5-20250929",
    "role": "assistant",
    "usage": {
      "input_tokens": 9471,
      "output_tokens": 114,
      "cache_creation_input_tokens": 0,
      "cache_read_input_tokens": 8960
    },
    "content": [
      {
        "type": "tool_use",
        "id": "toolu_123",
        "name": "mcp__brave-search__brave_web_search",
        "input": {
          "query": "MCP protocol documentation"
        }
      }
    ],
    "stop_reason": "tool_use"
  }
}
```

### Complete Codex CLI Sequence

**1. Function Call:**
```json
{
  "timestamp": "2025-11-21T07:00:08.562Z",
  "type": "response_item",
  "payload": {
    "type": "function_call",
    "name": "mcp__fs-mcp__fs_read",
    "arguments": "{\"path\":\"/path/to/file.md\"}",
    "call_id": "call_DVHBxILAncNdarfVzjqxF1si"
  }
}
```

**2. Function Output:**
```json
{
  "timestamp": "2025-11-21T07:00:08.562Z",
  "type": "response_item",
  "payload": {
    "type": "function_call_output",
    "call_id": "call_DVHBxILAncNdarfVzjqxF1si",
    "output": "... file contents ..."
  }
}
```

**3. Token Count:**
```json
{
  "timestamp": "2025-11-21T07:00:09.503Z",
  "type": "event_msg",
  "payload": {
    "type": "token_count",
    "info": {
      "last_token_usage": {
        "input_tokens": 9471,
        "cached_input_tokens": 8960,
        "output_tokens": 114,
        "reasoning_output_tokens": 64,
        "total_tokens": 9585
      }
    }
  }
}
```

---

## Implementation Considerations

### Server Name Normalization

**Problem:** Different naming conventions between platforms

**Solution:**
```python
def normalize_mcp_server(server_name):
    """Normalize MCP server name across platforms

    Args:
        server_name: Raw server name from tool call

    Returns:
        Normalized server name (without -mcp suffix)
    """
    # Strip -mcp suffix from Codex CLI format
    if server_name.endswith('-mcp'):
        return server_name[:-4]
    return server_name

# Examples:
# "brave-search-mcp" → "brave-search"
# "brave-search" → "brave-search" (unchanged)
```

### Token Attribution Strategy

**Claude Code:** Direct attribution (tokens in same entry as tool)

**Codex CLI:** Requires correlation logic

```python
# Option 1: Timestamp-based (current implementation)
# - Track last N tool calls with timestamps
# - Match token_count to nearest preceding function_call

# Option 2: Sequential buffering
# - Buffer tool calls until next token_count
# - Attribute tokens to all buffered tools

# Option 3: Call ID tracking (most accurate)
# - Track call_id through entire lifecycle
# - Match tokens when call completes
```

**Recommendation:** Use **sequential buffering** for simplicity and reliability

### Cache Token Field Mapping

| Token Type | Claude Code Field | Codex CLI Field |
|------------|------------------|-----------------|
| Cache creation | `cache_creation_input_tokens` | N/A (not provided) |
| Cache reads | `cache_read_input_tokens` | `cached_input_tokens` |

**Note:** Codex CLI doesn't distinguish cache creation from reads

---

## Usage Statistics (Real Data)

**From November 2025 Codex sessions:**

### MCP Server Usage

| MCP Server | Total Calls | Tools Used |
|------------|-------------|------------|
| fs-mcp | 40 | fs_read (36), fs_glob (4) |
| rg-mcp | 15 | rg_search (15) |
| brave-search-mcp | 7 | brave_web_search (7) |
| testrun-mcp | 2 | testrun_run (2) |

### Built-in Tool Usage

| Tool | Total Calls | Percentage |
|------|-------------|------------|
| shell | 3,764 | 94.8% |
| update_plan | 205 | 5.2% |
| list_mcp_resources | 14 | 0.4% |
| shell_command | 8 | 0.2% |

---

## Cross-Platform Compatibility

### Unified MCP Server Tracking

**Goal:** Track MCP usage consistently across both platforms

**Approach:**
1. Extract server name from tool name
2. Normalize server name (strip `-mcp` suffix if present)
3. Track stats using normalized name
4. Display with original format where needed

**Example:**
```python
# Codex CLI: "mcp__brave-search-mcp__brave_web_search"
# Extract: "brave-search-mcp"
# Normalize: "brave-search"
# Store as: mcp_stats["brave-search"]

# Claude Code: "mcp__brave-search__brave_web_search"
# Extract: "brave-search"
# Normalize: "brave-search" (no change)
# Store as: mcp_stats["brave-search"]

# Result: Same tracking key for both platforms!
```

---

## Testing Recommendations

### Validation Steps

1. **Format Detection:**
   - Test with recent Claude Code session
   - Test with recent Codex CLI session
   - Verify correct parser selection

2. **MCP Server Extraction:**
   - Test Claude Code format: `mcp__zen__chat`
   - Test Codex CLI format: `mcp__fs-mcp__fs_read`
   - Verify both normalize to same server name

3. **Token Attribution:**
   - Claude Code: Verify direct attribution
   - Codex CLI: Verify correlation accuracy
   - Compare totals between platforms

4. **Logging Output:**
   - Verify summary.json format consistency
   - Verify mcp-{server}.json structure matches
   - Test cross-session analysis with mixed data

---

## Future Considerations

### Potential Changes

1. **Codex CLI may align with Claude Code format** in future versions
2. **New token types** may be added (e.g., vision tokens, code analysis)
3. **MCP naming conventions** may standardize across platforms

### Compatibility Strategy

- **Version detection** - Check CLI version in session_meta
- **Format detection** - Auto-detect based on entry structure
- **Graceful degradation** - Handle missing fields
- **Backward compatibility** - Support older session formats

---

## Quick Reference

### Key Differences Summary

| Feature | Claude Code | Codex CLI |
|---------|-------------|-----------|
| Entry type | `assistant` | `response_item` + `event_msg` |
| Tool location | `message.content[]` | `payload` (separate entry) |
| Token location | Same entry | Separate `event_msg` |
| Server naming | `mcp__server__tool` | `mcp__server-mcp__tool` |
| Cache field | `cache_read_input_tokens` | `cached_input_tokens` |
| Reasoning tokens | Not present | `reasoning_output_tokens` |
| Tool-token link | Direct (same object) | Indirect (timestamp) |

### Extraction Patterns

**Claude Code:**
```python
tool_name = content_block.get('name')  # Direct
mcp_server = extract_mcp_server(tool_name)
tokens = message['usage']  # Same entry
```

**Codex CLI:**
```python
tool_name = payload.get('name')  # From response_item
mcp_server = extract_mcp_server(tool_name)
tokens = next_event_msg['payload']['info']['last_token_usage']  # Separate entry
```

---

**Document Version**: 1.0
**Investigation Date**: 2025-11-22
**Session Samples**: 5 recent Codex sessions, 64 total tool calls analyzed
