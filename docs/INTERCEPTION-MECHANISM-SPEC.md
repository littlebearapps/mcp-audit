# Interception Mechanism Specification

**Version**: 1.0
**Date**: 2025-11-24
**Status**: Approved for Implementation

---

## Overview

This document specifies the interception mechanisms for tracking MCP tool usage across three AI CLI platforms: Claude Code, Codex CLI, and Gemini CLI.

---

## Platform Comparison

| Platform | Approach | Data Source | Real-time | Recovery |
|----------|----------|-------------|-----------|----------|
| **Claude Code** | File Watcher | `~/.claude/cache/*/debug.log` | ✅ Yes | ✅ From debug.log |
| **Codex CLI** | Process Wrapper | stdout/stderr of `codex` command | ✅ Yes | ✅ From events.jsonl |
| **Gemini CLI** | Process Wrapper | stdout/stderr of `gemini --debug` | ✅ Yes | ✅ From checkpoints |

---

## Claude Code: File Watcher Approach

### Implementation

```python
# Monitor debug.log file in real-time
debug_log = find_latest_debug_log("~/.claude/cache/*/debug.log")
tail_file(debug_log, callback=parse_event)
```

### Data Source

- **Location**: `~/.claude/cache/<session_id>/debug.log`
- **Format**: JSONL (one event per line)
- **Content**: Full conversation events including MCP tool calls

### Event Structure

```json
{
  "type": "conversation",
  "message": {
    "type": "toolUse",
    "name": "mcp__zen__chat",
    "input": {...}
  },
  "usage": {
    "inputTokens": 1234,
    "outputTokens": 567,
    "cacheCreationInputTokens": 89,
    "cacheReadInputTokens": 1000
  }
}
```

### Pros & Cons

**Pros**:
- ✅ No process modification required
- ✅ Complete event history
- ✅ Automatic session tracking

**Cons**:
- ❌ Requires finding active debug.log
- ❌ File location may change
- ❌ Delayed tracking (file buffering)

---

## Codex CLI: Process Wrapper Approach

### Implementation

```python
# Wrap codex command and capture output
process = subprocess.Popen(
    ["codex", *args],
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    text=True
)

# Read output in real-time
for line in process.stdout:
    parse_event(line)
```

### Data Source

- **Location**: stdout/stderr of `codex` process
- **Format**: Text output with JSON events embedded
- **Content**: Conversation events, tool calls, token usage

### Event Structure

```json
{
  "type": "conversation",
  "message": {
    "type": "toolUse",
    "name": "mcp__zen-mcp__chat",
    "input": {...}
  },
  "usage": {
    "inputTokens": 1234,
    "outputTokens": 567,
    "cacheReadInputTokens": 1000
  }
}
```

### Normalization Required

```python
# Strip -mcp suffix from server names
"mcp__zen-mcp__chat" → "mcp__zen__chat"
```

### Pros & Cons

**Pros**:
- ✅ Real-time event streaming
- ✅ No file system dependency
- ✅ Portable across systems

**Cons**:
- ❌ Requires process wrapper
- ❌ User must use wrapper script
- ❌ No access to historical data

---

## Gemini CLI: Hybrid Approach (RECOMMENDED)

### Implementation Strategy

**Primary: Process Wrapper** (like Codex CLI)

```python
# Wrap gemini command with debug mode
process = subprocess.Popen(
    ["gemini", "--debug", *args],
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    text=True
)

# Parse debug output for MCP events
for line in process.stderr:  # Debug output goes to stderr
    if is_mcp_event(line):
        parse_event(line)
```

**Fallback: Checkpoint Files** (for recovery)

```python
# If session interrupted, recover from checkpoints
checkpoint_dir = Path.home() / ".gemini/tmp" / project_hash / "checkpoints"
for checkpoint_file in checkpoint_dir.glob("*.json"):
    recover_session(checkpoint_file)
```

### Data Sources

#### 1. Debug Output (Primary)

- **Location**: stderr when running `gemini --debug`
- **Format**: Text logs with JSON events
- **Content**: MCP tool calls, API requests, responses

#### 2. Checkpoint Files (Fallback)

- **Location**: `~/.gemini/tmp/<project_hash>/checkpoints/`
- **Format**: JSON files (one per checkpoint)
- **Content**: Full conversation history, tool calls, file states

**Checkpoint Structure**:
```json
{
  "timestamp": "2025-11-24T10:30:00Z",
  "conversation": [
    {
      "role": "user",
      "content": "Use brave-search to find..."
    },
    {
      "role": "assistant",
      "toolCalls": [
        {
          "name": "mcp__brave-search__web",
          "input": {...}
        }
      ]
    }
  ],
  "usage": {
    "totalTokens": 5432,
    "inputTokens": 3210,
    "outputTokens": 2222
  }
}
```

#### 3. Chat Save Files (Manual Saves)

- **Location**: `~/.gemini/tmp/`
- **Format**: JSON (via `/chat save <tag>` command)
- **Content**: Complete conversation state

### Normalization Requirements

**Server Name Normalization**:
- Unknown at this stage (need to test Gemini CLI MCP format)
- May require similar `-mcp` suffix stripping as Codex CLI
- Or may match Claude Code format exactly

**Action**: Test with live Gemini CLI session to determine exact format.

### Pros & Cons

**Pros**:
- ✅ Real-time tracking via process wrapper
- ✅ Rich debug output from `--debug` flag
- ✅ Checkpoint files for recovery
- ✅ Manual save files for historical analysis
- ✅ Official Google documentation available

**Cons**:
- ❌ Requires testing to determine exact format
- ❌ Debug output format may change between versions
- ❌ Checkpoint location uses project hash (need to derive)

---

## Implementation Recommendations

### Phase 1: Core Abstraction (Current)

1. **Lock core schema** - Session/ServerSession/Call with `schema_version` field
2. **Create BaseTracker** - Abstract class with stable adapter interface
3. **Unrecognized line handler** - Gracefully handle format changes

### Phase 2: Platform Adapters

1. **ClaudeCodeAdapter** - Refactor existing file watcher
2. **CodexCLIAdapter** - Refactor existing process wrapper
3. **GeminiCLIAdapter** - New hybrid implementation

### Phase 3: Testing & Validation

1. **Test Gemini CLI MCP format** - Determine exact event structure
2. **Add format tests** - Validate parsing for all three platforms
3. **Add recovery tests** - Verify checkpoint/events.jsonl fallback

---

## Decision Matrix

### When to Use File Watcher

✅ **Use When**:
- Platform provides structured log files
- Log location is stable and documented
- Real-time tailing is sufficient
- No process modification allowed

❌ **Avoid When**:
- Log format changes frequently
- Log location is unstable
- Need sub-second latency
- Historical data not available in logs

### When to Use Process Wrapper

✅ **Use When**:
- Direct access to stdout/stderr
- Real-time event streaming needed
- Platform supports debug/verbose mode
- Process lifecycle matches session lifecycle

❌ **Avoid When**:
- Users cannot modify launch command
- Process output format is unstable
- Need historical session recovery
- Platform doesn't expose events in output

### When to Use Hybrid

✅ **Use When**:
- Platform supports both approaches
- Need real-time + recovery capabilities
- Format stability is uncertain
- Official checkpointing exists

❌ **Avoid When**:
- Complexity outweighs benefits
- Only one approach is stable
- Maintenance burden is too high

---

## Gemini CLI Decision: Hybrid Approach

**Selected**: Process Wrapper (Primary) + Checkpoint Files (Fallback)

**Rationale**:
1. **Real-time tracking** - Process wrapper with `--debug` flag
2. **Recovery capability** - Checkpoint files in `~/.gemini/tmp/`
3. **Flexibility** - Can adapt if one approach fails
4. **Official support** - Both debug mode and checkpointing are documented

**Next Steps**:
1. ✅ Test live Gemini CLI session with MCP servers
2. ✅ Capture debug output to determine exact format
3. ✅ Implement GeminiCLIAdapter with BaseTracker
4. ✅ Add checkpoint recovery mechanism
5. ✅ Write format tests for validation

---

## References

### Claude Code
- Debug log location: `~/.claude/cache/*/debug.log`
- Format: JSONL conversation events
- Documentation: Internal (based on investigation)

### Codex CLI
- Process wrapper: Implemented in `live-codex-session-tracker.py`
- Format: Text with JSON events
- Normalization: Strip `-mcp` suffix from server names

### Gemini CLI
- Debug mode: `gemini --debug` (stderr output)
- Checkpoints: `~/.gemini/tmp/<project_hash>/checkpoints/`
- Chat saves: `~/.gemini/tmp/`
- Documentation: https://gemini-cli.xyz/docs/en/checkpointing

---

## Version History

- **v1.0** (2025-11-24) - Initial specification
  - Three-platform comparison
  - Hybrid approach for Gemini CLI
  - Implementation recommendations

---

## Approval

**Approved by**: Claude (MCP Audit Development)
**Date**: 2025-11-24
**Next Review**: After Gemini CLI adapter implementation
