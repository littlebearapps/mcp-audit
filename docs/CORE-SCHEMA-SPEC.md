# Core Schema Specification

**Version**: 1.0.0
**Date**: 2025-11-24
**Status**: Locked - Breaking changes require major version bump

---

## Overview

This document defines the core data structures for MCP Audit session tracking. The schema is **locked** and any breaking changes require a major version bump.

**Schema Version**: `1.0.0`

**Versioning Policy**:
- **Major version** (1.x.x → 2.x.x): Breaking changes (field removal, type changes)
- **Minor version** (x.1.x → x.2.x): Additive changes (new optional fields)
- **Patch version** (x.x.1 → x.x.2): Documentation updates, no schema changes

---

## Core Data Structures

### 1. Session

Top-level container for a complete tracking session.

```python
from typing import Dict, List, Optional
from datetime import datetime

class Session:
    """Complete session data for MCP tracking"""

    # Schema version (REQUIRED)
    schema_version: str = "1.0.0"

    # Session metadata (REQUIRED)
    project: str                    # Project name (e.g., "mcp-audit")
    platform: str                   # Platform name (e.g., "claude-code", "codex-cli", "gemini-cli")
    timestamp: datetime             # Session start time (ISO 8601)
    session_id: str                 # Unique session identifier

    # Token usage (REQUIRED)
    token_usage: TokenUsage

    # Cost estimate (REQUIRED)
    cost_estimate: float            # Estimated cost in USD

    # MCP tool tracking (REQUIRED)
    mcp_tool_calls: MCPToolCalls

    # Server sessions (REQUIRED)
    server_sessions: Dict[str, ServerSession]  # Key: server name (e.g., "zen", "brave-search")

    # Redundancy analysis (OPTIONAL)
    redundancy_analysis: Optional[RedundancyAnalysis] = None

    # Anomalies detected (OPTIONAL)
    anomalies: List[Anomaly] = []

    # Session end time (OPTIONAL - only if session completed)
    end_timestamp: Optional[datetime] = None

    # Session duration (OPTIONAL - only if session completed)
    duration_seconds: Optional[float] = None
```

**JSON Example**:

```json
{
  "schema_version": "1.0.0",
  "project": "mcp-audit",
  "platform": "claude-code",
  "timestamp": "2025-11-24T10:30:00Z",
  "session_id": "mcp-audit-2025-11-24T10-30-00",
  "token_usage": {
    "input_tokens": 45231,
    "output_tokens": 12543,
    "cache_created_tokens": 8123,
    "cache_read_tokens": 125432,
    "total_tokens": 191329,
    "cache_efficiency": 0.93
  },
  "cost_estimate": 0.1234,
  "mcp_tool_calls": {
    "total_calls": 42,
    "unique_tools": 12,
    "most_called": "mcp__zen__chat (15 calls)"
  },
  "server_sessions": {
    "zen": { ... },
    "brave-search": { ... }
  },
  "redundancy_analysis": { ... },
  "anomalies": [],
  "end_timestamp": "2025-11-24T11:15:00Z",
  "duration_seconds": 2700
}
```

---

### 2. ServerSession

Per-MCP-server statistics within a session.

```python
class ServerSession:
    """Statistics for a single MCP server"""

    # Schema version (REQUIRED)
    schema_version: str = "1.0.0"

    # Server identification (REQUIRED)
    server: str                     # Server name (e.g., "zen", "brave-search")

    # Tool calls (REQUIRED)
    tools: Dict[str, ToolStats]     # Key: tool name (e.g., "mcp__zen__chat")

    # Server-level aggregates (REQUIRED)
    total_calls: int                # Total tool calls for this server
    total_tokens: int               # Total tokens for this server

    # Platform-specific metadata (OPTIONAL)
    metadata: Optional[Dict[str, any]] = None
```

**JSON Example**:

```json
{
  "schema_version": "1.0.0",
  "server": "zen",
  "tools": {
    "mcp__zen__chat": {
      "calls": 15,
      "total_tokens": 45123,
      "avg_tokens": 3008,
      "call_history": [ ... ]
    },
    "mcp__zen__thinkdeep": {
      "calls": 3,
      "total_tokens": 234567,
      "avg_tokens": 78189,
      "call_history": [ ... ]
    }
  },
  "total_calls": 18,
  "total_tokens": 279690,
  "metadata": null
}
```

---

### 3. Call

Individual tool call record with timing information.

```python
class Call:
    """Single MCP tool call record"""

    # Schema version (REQUIRED)
    schema_version: str = "1.0.0"

    # Call identification (REQUIRED)
    timestamp: datetime             # When the call was made (ISO 8601)
    tool_name: str                  # Full tool name (e.g., "mcp__zen__chat")

    # Token usage (REQUIRED)
    input_tokens: int               # Input tokens for this call
    output_tokens: int              # Output tokens for this call
    cache_created_tokens: int       # Cache created tokens (0 if not applicable)
    cache_read_tokens: int          # Cache read tokens (0 if not applicable)
    total_tokens: int               # Sum of all token types

    # Timing information (REQUIRED for time-based tracking)
    duration_ms: int                # Call duration in milliseconds (0 if not available)

    # Call content hash (OPTIONAL - for duplicate detection)
    content_hash: Optional[str] = None  # SHA256 hash of input parameters

    # Platform-specific data (OPTIONAL)
    platform_data: Optional[Dict[str, any]] = None
```

**Rationale for `duration_ms` field**:
- **Ollama requirement**: Ollama CLI has variable response times (local GPU processing)
- **Performance analysis**: Identify slow tool calls across all platforms
- **Cost-time tradeoff**: Analyze token cost vs execution time
- **Set to 0 if unavailable**: Platforms that don't provide timing data

**JSON Example**:

```json
{
  "schema_version": "1.0.0",
  "timestamp": "2025-11-24T10:32:15Z",
  "tool_name": "mcp__zen__chat",
  "input_tokens": 2341,
  "output_tokens": 1067,
  "cache_created_tokens": 0,
  "cache_read_tokens": 8543,
  "total_tokens": 11951,
  "duration_ms": 2340,
  "content_hash": "sha256:abc123...",
  "platform_data": {
    "model": "claude-sonnet-4-5",
    "request_id": "req_abc123"
  }
}
```

---

### 4. ToolStats

Aggregated statistics for a single tool.

```python
class ToolStats:
    """Statistics for a single MCP tool"""

    # Schema version (REQUIRED)
    schema_version: str = "1.0.0"

    # Call count (REQUIRED)
    calls: int                      # Number of times this tool was called

    # Token usage (REQUIRED)
    total_tokens: int               # Sum of all tokens for this tool
    avg_tokens: float               # Average tokens per call

    # Call history (REQUIRED)
    call_history: List[Call]        # List of all calls for this tool

    # Timing statistics (OPTIONAL - only if duration_ms available)
    total_duration_ms: Optional[int] = None      # Sum of all call durations
    avg_duration_ms: Optional[float] = None      # Average duration per call
    max_duration_ms: Optional[int] = None        # Longest call duration
    min_duration_ms: Optional[int] = None        # Shortest call duration
```

**JSON Example**:

```json
{
  "schema_version": "1.0.0",
  "calls": 15,
  "total_tokens": 45123,
  "avg_tokens": 3008,
  "call_history": [
    { "timestamp": "2025-11-24T10:30:15Z", ... },
    { "timestamp": "2025-11-24T10:32:15Z", ... }
  ],
  "total_duration_ms": 35100,
  "avg_duration_ms": 2340,
  "max_duration_ms": 4560,
  "min_duration_ms": 1230
}
```

---

## Supporting Data Structures

### TokenUsage

```python
class TokenUsage:
    """Token usage statistics for a session"""

    input_tokens: int               # Total input tokens
    output_tokens: int              # Total output tokens
    cache_created_tokens: int       # Total cache creation tokens
    cache_read_tokens: int          # Total cache read tokens
    total_tokens: int               # Sum of all token types
    cache_efficiency: float         # cache_read_tokens / total_tokens
```

### MCPToolCalls

```python
class MCPToolCalls:
    """MCP tool call summary"""

    total_calls: int                # Total number of MCP tool calls
    unique_tools: int               # Number of unique tools called
    most_called: str                # Most frequently called tool (with count)
```

### RedundancyAnalysis

```python
class RedundancyAnalysis:
    """Analysis of duplicate/redundant tool calls"""

    duplicate_calls: int            # Number of duplicate calls detected
    potential_savings: int          # Estimated token savings from caching
    duplicate_groups: List[DuplicateGroup]  # Grouped duplicates
```

### DuplicateGroup

```python
class DuplicateGroup:
    """Group of duplicate tool calls"""

    tool_name: str                  # Tool that was called
    content_hash: str               # SHA256 hash of input
    call_count: int                 # Number of times called with same input
    total_wasted_tokens: int        # Tokens that could be saved
    timestamps: List[datetime]      # When each duplicate occurred
```

### Anomaly

```python
class Anomaly:
    """Detected anomaly in tool usage"""

    type: str                       # Anomaly type ("high_frequency", "high_variance", "high_avg_tokens")
    tool: str                       # Tool name
    metric_value: float             # Value that triggered anomaly
    threshold: float                # Threshold that was exceeded
    description: str                # Human-readable description
```

---

## Schema Versioning

### Version Field Requirements

**All data structures MUST include `schema_version` field**:

```python
schema_version: str = "1.0.0"
```

**Why schema versioning?**:
1. **Forward compatibility** - Future versions can detect old schemas
2. **Migration support** - Automated schema upgrades
3. **Validation** - Reject incompatible schemas early
4. **Debugging** - Identify mixed-version issues

### Version Checking

```python
def validate_schema_version(data: dict) -> bool:
    """Validate schema version compatibility"""
    if "schema_version" not in data:
        raise ValueError("Missing schema_version field")

    major, minor, patch = parse_version(data["schema_version"])
    current_major, current_minor, _ = parse_version("1.0.0")

    # Major version must match
    if major != current_major:
        raise ValueError(f"Incompatible major version: {major} != {current_major}")

    # Minor version can be older (forward compatible)
    if minor > current_minor:
        warnings.warn(f"Future minor version detected: {minor} > {current_minor}")

    return True
```

---

## Breaking Change Policy

### What Constitutes a Breaking Change?

**Major version bump required (1.x.x → 2.x.x)**:
- ❌ Removing a required field
- ❌ Changing a field type (e.g., `int` → `str`)
- ❌ Renaming a field
- ❌ Changing field semantics

**Minor version bump allowed (x.1.x → x.2.x)**:
- ✅ Adding a new optional field
- ✅ Adding a new data structure
- ✅ Extending an enum with new values

**Patch version only (x.x.1 → x.x.2)**:
- ✅ Documentation clarifications
- ✅ Example updates
- ✅ Comment improvements

### Migration Strategy

When breaking changes are needed:

1. **Announce deprecation** in current version (warnings)
2. **Add migration guide** in documentation
3. **Bump major version** and implement changes
4. **Provide migration tool** to upgrade old data

Example migration:

```python
def migrate_1_to_2(session_v1: dict) -> dict:
    """Migrate Session schema from v1.x.x to v2.x.x"""
    session_v2 = session_v1.copy()

    # Apply breaking changes
    session_v2["schema_version"] = "2.0.0"
    session_v2["new_required_field"] = default_value()

    return session_v2
```

---

## Unrecognized Fields Policy

**Parsers MUST handle unrecognized fields gracefully**:

```python
def parse_session(data: dict) -> Session:
    """Parse session data with forward compatibility"""
    validate_schema_version(data)

    # Extract known fields
    session = Session(
        schema_version=data["schema_version"],
        project=data["project"],
        platform=data["platform"],
        # ... other fields
    )

    # Store unrecognized fields for debugging
    known_fields = set(Session.__annotations__.keys())
    unrecognized = set(data.keys()) - known_fields

    if unrecognized:
        warnings.warn(f"Unrecognized fields: {unrecognized}")
        session.metadata["unrecognized_fields"] = {
            k: data[k] for k in unrecognized
        }

    return session
```

---

## Platform-Specific Extensions

### Claude Code

```python
platform_data = {
    "model": "claude-sonnet-4-5-20250929",
    "debug_log_path": "~/.claude/cache/abc123/debug.log",
    "request_id": "req_abc123"
}
```

### Codex CLI

```python
platform_data = {
    "model": "gpt-4o",
    "codex_session_id": "codex-abc123",
    "git_branch": "feature/new-feature"
}
```

### Gemini CLI

```python
platform_data = {
    "model": "gemini-3-pro",
    "checkpoint_path": "~/.gemini/tmp/abc123/checkpoints/",
    "project_hash": "abc123"
}
```

### Ollama CLI (Future)

```python
platform_data = {
    "model": "llama3:70b",
    "local_gpu": "NVIDIA RTX 4090",
    "quantization": "q4_K_M"
}
```

---

## File Format

### Session Summary (summary.json)

**Location**: `logs/sessions/{project}-{timestamp}/summary.json`

**Content**: Complete Session object

**Example**:
```json
{
  "schema_version": "1.0.0",
  "project": "mcp-audit",
  "platform": "claude-code",
  ...
}
```

### Server Session (mcp-{server}.json)

**Location**: `logs/sessions/{project}-{timestamp}/mcp-{server}.json`

**Content**: ServerSession object for one server

**Example**: `mcp-zen.json`
```json
{
  "schema_version": "1.0.0",
  "server": "zen",
  "tools": { ... },
  "total_calls": 18,
  "total_tokens": 279690
}
```

### Event Stream (events.jsonl)

**Location**: `logs/sessions/{project}-{timestamp}/events.jsonl`

**Format**: Line-delimited JSON (one event per line)

**Content**: Raw conversation events (platform-specific)

**Purpose**: Recovery source if MCP files missing

---

## Implementation Checklist

- [ ] Define Python dataclasses for all core structures
- [ ] Add schema_version to all classes
- [ ] Implement version validation logic
- [ ] Add duration_ms field to Call class
- [ ] Create unrecognized field handler
- [ ] Write schema validation tests
- [ ] Document migration strategy
- [ ] Create example JSON files for each structure

---

## References

- **Session Tracking**: `live-cc-session-tracker.py`, `live-codex-session-tracker.py`
- **Data Structures**: Current implementation in tracker scripts
- **Recovery Logic**: `analyze-mcp-efficiency.py` (events.jsonl recovery)

---

## Version History

- **v1.0.0** (2025-11-24) - Initial locked schema
  - Session, ServerSession, Call, ToolStats structures
  - schema_version field for all structures
  - duration_ms field for time-based tracking (Ollama)
  - Platform-specific extensions support
  - Unrecognized field handling policy

---

## Approval

**Approved by**: Claude (MCP Audit Development)
**Date**: 2025-11-24
**Status**: LOCKED - Breaking changes require major version bump
**Next Review**: After BaseTracker implementation
