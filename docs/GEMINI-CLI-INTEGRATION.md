# Gemini CLI Integration Plan

**Document Version**: 2.0.0
**Created**: 2025-11-25
**Updated**: 2025-11-25 (Major revision after OpenTelemetry discovery)
**Target Task**: task-3.1 (Weeks 7-8: Gemini CLI Integration)
**Status**: Research Complete - High Confidence - Ready for Implementation

---

## Executive Summary

This document outlines the implementation plan for adding Gemini CLI support to mcp-audit. Gemini CLI is Google's open-source agentic coding assistant that brings Gemini models directly to the terminal.

**Major Discovery**: Gemini CLI has **built-in OpenTelemetry support** with comprehensive metrics for token usage and MCP tool tracking. This dramatically simplifies integration.

**Key Findings**:
1. **Native telemetry system** with file export option
2. **Dedicated MCP tool metrics** (`tool_type: "mcp"` vs `"native"`)
3. **Per-tool token tracking** with latency data
4. **Standard MCP naming** (same as Claude Code, no normalization needed)

**Confidence Level**: 85-90% (upgraded from initial 60-70%)

**Estimated Effort**: 3-4 days implementation + 1 day testing

---

## 1. Gemini CLI Overview

### 1.1 Architecture

Gemini CLI uses a modular TypeScript architecture:

```
gemini-cli/
├── packages/
│   ├── cli/                 # Terminal UI (React/Ink)
│   │   └── index.ts         # Entry point
│   └── core/                # Core logic (@google/gemini-cli-core)
│       └── src/
│           ├── core/
│           │   ├── geminiChat.ts       # API communication
│           │   └── coreToolScheduler.ts # Tool execution
│           ├── tools/              # Built-in tools
│           ├── mcp/                # MCP integration
│           │   ├── mcp-client.ts   # Server discovery
│           │   └── mcp-tool.ts     # Tool execution wrapper
│           ├── telemetry/          # ⭐ OpenTelemetry metrics
│           │   └── telemetry.ts    # Main telemetry implementation
│           └── output/             # Logging/output
```

**Current Version**: `0.19.0-nightly` (as of 2025-11-25)

**Key Dependencies**:
- `@google/genai` (1.30.0) - Gemini API SDK
- `@modelcontextprotocol/sdk` (1.22.0) - MCP support
- `@opentelemetry/sdk-node` - Telemetry infrastructure
- Multiple OTLP exporters for metrics/traces/logs

### 1.2 MCP Configuration

Gemini CLI configures MCP servers in `~/.gemini/settings.json`:

```json
{
  "mcpServers": {
    "zen": {
      "command": "node",
      "args": ["/path/to/zen-server/index.js"],
      "trust": false,
      "timeout": 600000
    },
    "brave-search": {
      "command": "npx",
      "args": ["-y", "@anthropic/mcp-brave-search"],
      "env": {
        "BRAVE_API_KEY": "${BRAVE_API_KEY}"
      }
    }
  }
}
```

### 1.3 Tool Naming Convention

Gemini CLI uses the **same MCP tool naming pattern as Claude Code**:

```
mcp__{server}__{tool_name}
```

Examples:
- `mcp__zen__chat`
- `mcp__brave-search__brave_web_search`
- `mcp__zen__thinkdeep`

**No normalization required** - unlike Codex CLI's `-mcp` suffix.

---

## 2. OpenTelemetry Telemetry System (Key Discovery)

### 2.1 Available Metrics

Gemini CLI exposes comprehensive OpenTelemetry metrics:

#### Token Usage Metrics

| Metric | Type | Description | Attributes |
|--------|------|-------------|------------|
| `gemini_cli.token.usage` | Counter | Tokens by model/type | `model`, `type` |
| `gen_ai.client.token.usage` | Histogram | Tokens per operation | `gen_ai.token.type`, `gen_ai.request.model` |

**Token Types** (in `type` attribute):
- `input` - Prompt tokens
- `output` - Response tokens
- `thought` - Reasoning/thinking tokens (Gemini-specific)
- `cache` - Cached content tokens
- `tool` - Tool-related tokens

#### Tool Call Metrics

| Metric | Type | Description | Attributes |
|--------|------|-------------|------------|
| `gemini_cli.tool.call.count` | Counter | Tool invocations | `function_name`, `tool_type`, `success`, `decision` |
| `gemini_cli.tool.call.latency` | Histogram | Execution duration (ms) | `function_name` |

**Critical Attribute**: `tool_type` distinguishes:
- `"mcp"` - MCP server tools (what we track)
- `"native"` - Built-in tools (file ops, shell, etc.)

#### Inference Events

| Event | Data Fields |
|-------|-------------|
| `gen_ai.client.inference.operation.details` | `gen_ai.usage.input_tokens`, `gen_ai.usage.output_tokens`, `gen_ai.usage.cached_content_token_count` |

### 2.2 Telemetry Configuration

Enable telemetry in `~/.gemini/settings.json`:

```json
{
  "telemetry": {
    "enabled": true,
    "target": "local",
    "outfile": ".gemini/telemetry.log"
  }
}
```

**Configuration Options**:

| Setting | Env Variable | Values | Default |
|---------|--------------|--------|---------|
| `enabled` | `GEMINI_TELEMETRY_ENABLED` | true/false | false |
| `target` | `GEMINI_TELEMETRY_TARGET` | "gcp"/"local" | "local" |
| `outfile` | `GEMINI_TELEMETRY_OUTFILE` | file path | — |
| `otlpEndpoint` | `GEMINI_TELEMETRY_OTLP_ENDPOINT` | URL | http://localhost:4317 |
| `otlpProtocol` | `GEMINI_TELEMETRY_OTLP_PROTOCOL` | "grpc"/"http" | "grpc" |
| `logPrompts` | `GEMINI_TELEMETRY_LOG_PROMPTS` | true/false | true |

### 2.3 Data Mapping to mcp-audit Schema

| OpenTelemetry Metric | mcp-audit Field | Notes |
|---------------------|-----------------|-------|
| `gemini_cli.token.usage` (type=input) | `input_tokens` | Per-request input |
| `gemini_cli.token.usage` (type=output) | `output_tokens` | Per-request output |
| `gemini_cli.token.usage` (type=thought) | `platform_data.thoughts_tokens` | Gemini-specific |
| `gemini_cli.token.usage` (type=cache) | `cache_read_tokens` | Cache hits |
| `gemini_cli.tool.call.count` (tool_type=mcp) | MCP tool tracking | Filter by tool_type |
| `gemini_cli.tool.call.latency` | `duration_ms` | Per-tool latency |

---

## 3. Recommended Integration Approach

### 3.1 Primary: Telemetry File Parser (Recommended)

**Similar to Claude Code adapter pattern** - file monitoring approach.

```python
class GeminiCLIAdapter(BaseTracker):
    """
    Gemini CLI platform adapter using OpenTelemetry file export.

    Monitors ~/.gemini/telemetry.log for metrics and extracts
    MCP tool usage and token counts.
    """

    def __init__(self, project: str, gemini_dir: Optional[Path] = None):
        super().__init__(project=project, platform="gemini-cli")

        self.gemini_dir = gemini_dir or Path.home() / ".gemini"
        self.telemetry_file = self.gemini_dir / "telemetry.log"
        self.file_position: int = 0

        # Gemini-specific tracking
        self.thoughts_tokens: int = 0

    def start_tracking(self) -> None:
        """
        Start tracking by monitoring telemetry file.

        1. Ensure telemetry is enabled in settings
        2. Tail telemetry.log for new entries
        3. Parse OpenTelemetry format
        4. Extract MCP tool calls (tool_type="mcp")
        """
        self._ensure_telemetry_enabled()

        # Start from end of file (track NEW events only)
        if self.telemetry_file.exists():
            self.file_position = self.telemetry_file.stat().st_size

        print(f"[Gemini CLI] Monitoring: {self.telemetry_file}")

        while True:
            try:
                self._process_new_telemetry()
                time.sleep(0.5)
            except KeyboardInterrupt:
                break

    def parse_event(self, event_data: Any) -> Optional[Tuple[str, Dict[str, Any]]]:
        """
        Parse OpenTelemetry metric/event.

        Focus on:
        - gemini_cli.tool.call.count where tool_type="mcp"
        - gemini_cli.token.usage for all token types
        - gemini_cli.tool.call.latency for duration
        """
        # Implementation: parse OTLP JSON format
        pass
```

**Advantages**:
- Uses official telemetry system (stable API)
- Accurate MCP vs native tool distinction
- Per-tool latency tracking included
- Token breakdown by type (input/output/thought/cache)
- Non-invasive (passive monitoring)

**Configuration Required**:
```bash
# Enable telemetry (one-time setup)
# Add to ~/.gemini/settings.json or use env var:
export GEMINI_TELEMETRY_ENABLED=true
export GEMINI_TELEMETRY_OUTFILE=~/.gemini/telemetry.log
```

### 3.2 Alternative: Process Wrapper (Fallback)

If telemetry approach has issues, fall back to subprocess wrapper:

```python
class GeminiCLIAdapter(BaseTracker):
    def start_tracking(self):
        self.process = subprocess.Popen(
            ["gemini"] + self.gemini_args,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1
        )
        # Parse stdout for tool calls
```

**When to use**:
- Telemetry file format changes unexpectedly
- User cannot enable telemetry
- Real-time stdout visibility needed

### 3.3 Approach Comparison

| Aspect | Telemetry File (Recommended) | Process Wrapper |
|--------|------------------------------|-----------------|
| Accuracy | ⭐⭐⭐ High (official metrics) | ⭐⭐ Medium (parsing) |
| MCP/Native distinction | ⭐⭐⭐ Built-in (`tool_type`) | ⭐ Manual detection |
| Token breakdown | ⭐⭐⭐ Full (5 types) | ⭐⭐ Partial |
| Latency tracking | ⭐⭐⭐ Native support | ❌ Not available |
| Setup complexity | ⭐⭐ Enable telemetry | ⭐⭐⭐ None |
| Stability | ⭐⭐⭐ Official API | ⭐⭐ Output may change |

---

## 4. Implementation Plan

### 4.1 Phase 1: Core Adapter (2-3 days)

#### Day 1: Telemetry Parser

Create `src/mcp_audit/gemini_cli_adapter.py`:

```python
#!/usr/bin/env python3
"""
GeminiCLIAdapter - Platform adapter for Gemini CLI tracking

Implements BaseTracker using Gemini CLI's OpenTelemetry telemetry export.
"""

import json
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from .base_tracker import BaseTracker


class GeminiCLIAdapter(BaseTracker):
    """
    Gemini CLI platform adapter.

    Monitors OpenTelemetry telemetry file for MCP tool usage
    and token counts. Uses file watcher approach similar to
    Claude Code adapter.
    """

    # OpenTelemetry metric names
    METRIC_TOKEN_USAGE = "gemini_cli.token.usage"
    METRIC_TOOL_CALL_COUNT = "gemini_cli.tool.call.count"
    METRIC_TOOL_CALL_LATENCY = "gemini_cli.tool.call.latency"

    def __init__(
        self,
        project: str,
        gemini_dir: Optional[Path] = None,
        telemetry_file: Optional[Path] = None
    ):
        """
        Initialize Gemini CLI adapter.

        Args:
            project: Project name
            gemini_dir: Gemini config directory (default: ~/.gemini)
            telemetry_file: Custom telemetry file path
        """
        super().__init__(project=project, platform="gemini-cli")

        self.gemini_dir = gemini_dir or Path.home() / ".gemini"
        self.telemetry_file = telemetry_file or self.gemini_dir / "telemetry.log"
        self.file_position: int = 0

        # Gemini-specific: track thinking tokens separately
        self.thoughts_tokens: int = 0

        # Model detection
        self.detected_model: Optional[str] = None
        self.model_name: str = "Unknown Model"

    def _ensure_telemetry_enabled(self) -> bool:
        """Check if telemetry is enabled, warn if not."""
        settings_file = self.gemini_dir / "settings.json"

        if not settings_file.exists():
            print("[Gemini CLI] Warning: settings.json not found")
            print("[Gemini CLI] Enable telemetry with:")
            print('  export GEMINI_TELEMETRY_ENABLED=true')
            print('  export GEMINI_TELEMETRY_OUTFILE=~/.gemini/telemetry.log')
            return False

        try:
            with open(settings_file) as f:
                settings = json.load(f)

            telemetry = settings.get("telemetry", {})
            if not telemetry.get("enabled", False):
                print("[Gemini CLI] Warning: Telemetry not enabled in settings")
                return False

            return True
        except Exception as e:
            print(f"[Gemini CLI] Error reading settings: {e}")
            return False

    def start_tracking(self) -> None:
        """
        Start tracking Gemini CLI session.

        Monitors telemetry file for new OpenTelemetry metrics.
        """
        print(f"[Gemini CLI] Initializing tracker for: {self.project}")

        # Check telemetry configuration
        self._ensure_telemetry_enabled()

        print(f"[Gemini CLI] Monitoring: {self.telemetry_file}")

        # Start from end of file (track NEW content only)
        if self.telemetry_file.exists():
            self.file_position = self.telemetry_file.stat().st_size

        print("[Gemini CLI] Tracking started. Press Ctrl+C to stop.")

        # Main monitoring loop
        while True:
            try:
                self._process_new_telemetry()
                time.sleep(0.5)
            except KeyboardInterrupt:
                print("\n[Gemini CLI] Stopping tracker...")
                break

    def _process_new_telemetry(self) -> None:
        """Read and process new telemetry entries."""
        if not self.telemetry_file.exists():
            return

        try:
            with open(self.telemetry_file) as f:
                f.seek(self.file_position)
                new_content = f.read()

                if new_content:
                    for line in new_content.strip().split("\n"):
                        if line:
                            result = self.parse_event(line)
                            if result:
                                tool_name, usage = result
                                self._process_tool_call(tool_name, usage)

                self.file_position = f.tell()
        except Exception as e:
            self.handle_unrecognized_line(f"Error reading telemetry: {e}")

    def parse_event(self, event_data: Any) -> Optional[Tuple[str, Dict[str, Any]]]:
        """
        Parse OpenTelemetry metric event.

        Args:
            event_data: JSON line from telemetry file

        Returns:
            Tuple of (tool_name, usage_dict) if MCP tool call, None otherwise
        """
        try:
            data = json.loads(event_data)

            # Check metric name
            metric_name = data.get("name") or data.get("metric_name", "")

            # Handle tool call count metric
            if self.METRIC_TOOL_CALL_COUNT in metric_name:
                attributes = data.get("attributes", {})

                # Only track MCP tools
                if attributes.get("tool_type") != "mcp":
                    return None

                function_name = attributes.get("function_name", "")
                if not function_name.startswith("mcp__"):
                    return None

                # Extract token usage if available in same event
                usage_dict = {
                    "input_tokens": 0,
                    "output_tokens": 0,
                    "cache_created_tokens": 0,
                    "cache_read_tokens": 0,
                    "success": attributes.get("success", True),
                    "decision": attributes.get("decision", "auto_accept"),
                }

                return (function_name, usage_dict)

            # Handle token usage metric (aggregate separately)
            if self.METRIC_TOKEN_USAGE in metric_name:
                attributes = data.get("attributes", {})
                token_type = attributes.get("type", "")
                value = data.get("value", 0)

                # Track thinking tokens separately
                if token_type == "thought":
                    self.thoughts_tokens += value

                # Model detection
                model = attributes.get("model")
                if model and not self.detected_model:
                    self.detected_model = model
                    self.model_name = model

            return None

        except (json.JSONDecodeError, KeyError) as e:
            self.handle_unrecognized_line(f"Parse error: {e}")
            return None

    def get_platform_metadata(self) -> Dict[str, Any]:
        """Get Gemini CLI platform metadata."""
        return {
            "model": self.detected_model,
            "model_name": self.model_name,
            "gemini_dir": str(self.gemini_dir),
            "telemetry_file": str(self.telemetry_file),
            "thoughts_tokens": self.thoughts_tokens,
        }

    def _process_tool_call(self, tool_name: str, usage: Dict[str, Any]) -> None:
        """Process a single MCP tool call."""
        content_hash = None
        platform_data = {
            "model": self.detected_model,
            "success": usage.get("success", True),
            "decision": usage.get("decision"),
        }

        self.record_tool_call(
            tool_name=tool_name,
            input_tokens=usage["input_tokens"],
            output_tokens=usage["output_tokens"],
            cache_created_tokens=usage["cache_created_tokens"],
            cache_read_tokens=usage["cache_read_tokens"],
            duration_ms=usage.get("duration_ms", 0),
            content_hash=content_hash,
            platform_data=platform_data,
        )
```

#### Day 2: Token Attribution & Latency

Enhance adapter to correlate token usage with tool calls:

```python
def _correlate_tokens_to_tools(self) -> None:
    """
    Correlate token usage events with tool calls.

    Strategy:
    1. Buffer token events with timestamps
    2. Match to nearest tool call by timestamp
    3. Attribute tokens to specific MCP tools
    """
    # Implementation for accurate per-tool attribution
    pass
```

#### Day 3: Integration Testing

- Install Gemini CLI: `npm install -g @google/gemini-cli`
- Enable telemetry in settings
- Test with MCP servers (zen, brave-search)
- Verify metrics extraction
- Test Ctrl+C signal handling

### 4.2 Phase 2: Pricing & Configuration (1 day)

Update `mcp-audit.toml`:

```toml
[pricing.gemini]
# Gemini 2.5 Pro (as of 2025-11-25)
"gemini-2.5-pro" = { input = 1.25, output = 10.00, cache_read = 0.3125 }
"gemini-2.5-pro-preview" = { input = 1.25, output = 10.00, cache_read = 0.3125 }

# Gemini 2.5 Flash
"gemini-2.5-flash" = { input = 0.075, output = 0.30, cache_read = 0.01875 }
"gemini-2.5-flash-preview" = { input = 0.075, output = 0.30, cache_read = 0.01875 }

# Gemini 2.0 Flash
"gemini-2.0-flash" = { input = 0.075, output = 0.30, cache_read = 0.01875 }

# Gemini 2.0 Flash Lite
"gemini-2.0-flash-lite" = { input = 0.0375, output = 0.15, cache_read = 0.009375 }

# Gemini 3 Pro (when available)
"gemini-3-pro-preview" = { input = 1.25, output = 10.00, cache_read = 0.3125 }
```

### 4.3 Phase 3: Documentation (0.5 days)

Create `docs/platforms/gemini-cli.md`:

```markdown
# Gemini CLI Setup Guide

## Prerequisites
- Gemini CLI installed (`npm install -g @google/gemini-cli`)
- Google account authenticated

## Enable Telemetry

mcp-audit uses Gemini CLI's OpenTelemetry system. Enable it:

### Option 1: Settings File
Add to `~/.gemini/settings.json`:
```json
{
  "telemetry": {
    "enabled": true,
    "target": "local",
    "outfile": ".gemini/telemetry.log"
  }
}
```

### Option 2: Environment Variables
```bash
export GEMINI_TELEMETRY_ENABLED=true
export GEMINI_TELEMETRY_OUTFILE=~/.gemini/telemetry.log
```

## Start Tracking
```bash
mcp-audit collect --platform gemini-cli
```

## Metrics Captured
- MCP tool calls (distinguished from native tools)
- Token usage by type (input, output, thought, cache)
- Per-tool execution latency
- Model identification
```

---

## 5. Technical Specifications

### 5.1 Dependencies

**No new dependencies required**:
- `json` - Parse OpenTelemetry JSON
- `pathlib` - File path handling
- `time` - File polling

### 5.2 Schema Compatibility

Existing schema (v1.0.0) fully supports Gemini CLI:

```python
@dataclass
class Call:
    input_tokens: int = 0       # gemini_cli.token.usage (type=input)
    output_tokens: int = 0      # gemini_cli.token.usage (type=output)
    cache_read_tokens: int = 0  # gemini_cli.token.usage (type=cache)
    duration_ms: int = 0        # gemini_cli.tool.call.latency

    # Gemini-specific data
    platform_data: Optional[Dict[str, Any]] = None
    # {
    #   "thoughts_tokens": 89,
    #   "success": true,
    #   "decision": "auto_accept"
    # }
```

**No schema changes required.**

### 5.3 OpenTelemetry Format Reference

Expected telemetry file format (JSON lines):

```json
{"name":"gemini_cli.tool.call.count","attributes":{"function_name":"mcp__zen__chat","tool_type":"mcp","success":true,"decision":"auto_accept"},"value":1,"timestamp":"2025-11-25T10:30:00Z"}
{"name":"gemini_cli.token.usage","attributes":{"model":"gemini-2.5-pro","type":"input"},"value":1234,"timestamp":"2025-11-25T10:30:01Z"}
{"name":"gemini_cli.token.usage","attributes":{"model":"gemini-2.5-pro","type":"output"},"value":567,"timestamp":"2025-11-25T10:30:02Z"}
{"name":"gemini_cli.tool.call.latency","attributes":{"function_name":"mcp__zen__chat"},"value":1523,"timestamp":"2025-11-25T10:30:02Z"}
```

---

## 6. Risk Assessment (Updated)

### Risk 1: Telemetry Format Changes (Low Risk)

**Risk**: OpenTelemetry format may change in future versions.

**Mitigation**:
- OpenTelemetry is a standard - format is stable
- Version check on Gemini CLI startup
- Fallback to process wrapper if needed

**Confidence**: 90% (using standard format)

### Risk 2: Telemetry Disabled by Default (Medium Risk)

**Risk**: Users must enable telemetry manually.

**Mitigation**:
- Clear setup instructions in docs
- Auto-detection with helpful warning message
- Environment variable option (no file editing)

**Confidence**: 85%

### Risk 3: Token-to-Tool Attribution (Low Risk)

**Risk**: Token events may not directly correlate with tool calls.

**Mitigation**:
- `tool_type: "mcp"` attribute distinguishes MCP calls
- Timestamp correlation for attribution
- Session-level totals as fallback

**Confidence**: 85%

---

## 7. Success Criteria

### Acceptance Criteria

- [ ] GeminiCLIAdapter implements BaseTracker interface
- [ ] MCP tool calls tracked (filtered by `tool_type: "mcp"`)
- [ ] Token usage captured (input, output, cache, thought)
- [ ] Per-tool latency tracked via `tool.call.latency`
- [ ] Thinking tokens stored in `platform_data`
- [ ] Gemini model pricing configured
- [ ] Session summary on Ctrl+C
- [ ] Tests pass (unit + integration)
- [ ] Platform documentation complete

### Validation Tests

```bash
# 1. Enable telemetry
export GEMINI_TELEMETRY_ENABLED=true
export GEMINI_TELEMETRY_OUTFILE=~/.gemini/telemetry.log

# 2. Start mcp-audit tracking
mcp-audit collect --platform gemini-cli

# 3. In another terminal, use Gemini CLI with MCP
gemini
> @zen analyze this codebase

# 4. Stop tracking (Ctrl+C in mcp-audit terminal)

# 5. Verify session data
cat ~/.mcp-audit/sessions/gemini-cli/*/summary.json

# 6. Generate report
mcp-audit report --platform gemini-cli
```

---

## 8. Timeline

| Phase | Days | Deliverables |
|-------|------|--------------|
| Phase 1: Core Adapter | 2-3 | `gemini_cli_adapter.py`, telemetry parsing |
| Phase 2: Pricing | 0.5 | TOML config, cost calculation |
| Phase 3: Docs | 0.5 | Platform guide, README update |
| **Total** | **3-4** | Full Gemini CLI support |

**Target**: Weeks 7-8 per roadmap (task-3.1)

---

## 9. References

### Official Documentation
- [Gemini CLI GitHub](https://github.com/google-gemini/gemini-cli)
- [Gemini CLI Telemetry Docs](https://github.com/google-gemini/gemini-cli/blob/main/docs/cli/telemetry.md)
- [Gemini CLI MCP Integration](https://google-gemini.github.io/gemini-cli/docs/tools/mcp-server.html)
- [Gemini API Pricing](https://ai.google.dev/gemini-api/docs/pricing)

### Telemetry Metrics Reference
- `gemini_cli.token.usage` - Token counts by type
- `gemini_cli.tool.call.count` - Tool invocations with `tool_type` attribute
- `gemini_cli.tool.call.latency` - Execution duration
- `gen_ai.client.token.usage` - GenAI semantic convention metrics

### Community Resources
- [Token Usage Feature Discussion](https://github.com/google-gemini/gemini-cli/discussions/4489)
- [Telemetry Infrastructure Issue](https://github.com/google-gemini/gemini-cli/issues/3723)

### mcp-audit Resources
- `src/mcp_audit/base_tracker.py` - Base adapter class
- `src/mcp_audit/claude_code_adapter.py` - Reference for file monitoring approach
- `docs/contributing.md` - Adapter development guide

---

## 10. Appendix

### A. Gemini CLI Installation

```bash
# Recommended: npm global install
npm install -g @google/gemini-cli

# Version check
gemini --version
# Expected: 0.19.0 or later
```

### B. Telemetry Quick Setup

```bash
# One-liner to enable telemetry
cat >> ~/.gemini/settings.json << 'EOF'
{
  "telemetry": {
    "enabled": true,
    "target": "local",
    "outfile": ".gemini/telemetry.log"
  }
}
EOF

# Or use environment variables (no file editing)
echo 'export GEMINI_TELEMETRY_ENABLED=true' >> ~/.bashrc
echo 'export GEMINI_TELEMETRY_OUTFILE=~/.gemini/telemetry.log' >> ~/.bashrc
source ~/.bashrc
```

### C. OpenTelemetry Metric Examples

```json
// MCP tool call
{
  "name": "gemini_cli.tool.call.count",
  "attributes": {
    "function_name": "mcp__zen__thinkdeep",
    "tool_type": "mcp",
    "success": true,
    "decision": "accept"
  },
  "value": 1
}

// Token usage (input)
{
  "name": "gemini_cli.token.usage",
  "attributes": {
    "model": "gemini-2.5-pro",
    "type": "input"
  },
  "value": 12345
}

// Token usage (thinking/reasoning)
{
  "name": "gemini_cli.token.usage",
  "attributes": {
    "model": "gemini-2.5-pro",
    "type": "thought"
  },
  "value": 890
}

// Tool latency
{
  "name": "gemini_cli.tool.call.latency",
  "attributes": {
    "function_name": "mcp__zen__thinkdeep"
  },
  "value": 2345
}
```

### D. Confidence Assessment Summary

| Aspect | Initial | After Research | Reason |
|--------|---------|----------------|--------|
| Overall feasibility | 60-70% | **85-90%** | OpenTelemetry discovery |
| Token tracking | 50% | **90%** | Native metrics available |
| MCP tool distinction | 40% | **95%** | `tool_type: "mcp"` attribute |
| Implementation effort | 6-7 days | **3-4 days** | Simpler file parsing |
| Long-term stability | 60% | **85%** | Using standard OTEL format |
