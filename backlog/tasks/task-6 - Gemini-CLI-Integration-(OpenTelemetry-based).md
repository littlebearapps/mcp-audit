---
id: task-6
title: Gemini CLI Integration (OpenTelemetry-based)
status: Done
assignee:
  - claude
created_date: '2025-11-25 03:55'
updated_date: '2025-11-25 04:07'
labels:
  - platform
  - gemini-cli
  - phase-3
  - weeks-7-8
dependencies: []
priority: medium
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Implement Gemini CLI platform adapter for mcp-audit using the built-in OpenTelemetry telemetry system.

**Key Discovery**: Gemini CLI has native telemetry with `tool_type: "mcp"` attribute for MCP tool distinction. No complex parsing needed.

**Approach**: File watcher pattern (like Claude Code adapter) monitoring `~/.gemini/telemetry.log`

**Metrics Available**:
- `gemini_cli.token.usage` - tokens by type (input, output, thought, cache)
- `gemini_cli.tool.call.count` - tool invocations with tool_type attribute
- `gemini_cli.tool.call.latency` - per-tool execution duration

**Estimated Effort**: 3-4 days implementation + 1 day testing

**Reference**: docs/GEMINI-CLI-INTEGRATION.md (v2.0.0)
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 GeminiCLIAdapter implements BaseTracker interface
- [x] #2 MCP tool calls tracked (filtered by tool_type: 'mcp')
- [x] #3 Token usage captured (input, output, cache, thought types)
- [x] #4 Per-tool latency tracked via gemini_cli.tool.call.latency metric
- [x] #5 Thinking tokens stored in platform_data.thoughts_tokens
- [x] #6 Gemini model pricing configured in mcp-audit.toml
- [x] #7 Session summary generated on Ctrl+C (signal handling)
- [x] #8 Unit tests pass for telemetry parsing and adapter methods
- [x] #9 Integration tests pass with real Gemini CLI telemetry file
- [x] #10 Platform documentation complete (docs/platforms/gemini-cli.md)
- [x] #11 README.md updated with Gemini CLI support
- [x] #12 No schema changes required (schema v1.0.0 compatible)
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
## Implementation Complete (2025-11-25)

### Files Created
- `src/mcp_audit/gemini_cli_adapter.py` - GeminiCLIAdapter class (~330 lines)
- `tests/test_gemini_cli_adapter.py` - 35 unit tests
- `docs/platforms/gemini-cli.md` - Platform documentation

### Files Modified
- `src/mcp_audit/__init__.py` - Added GeminiCLIAdapter export
- `mcp-audit.toml` - Added Gemini model pricing (7 models)
- `README.md` - Updated platform support, examples, CLI reference

### Key Features
1. **OpenTelemetry-based tracking** - Uses Gemini CLI's native telemetry system
2. **MCP tool filtering** - Filters by `tool_type: "mcp"` attribute
3. **Token types**: input, output, cache, thought (Gemini-specific)
4. **Per-tool latency tracking** - From `gemini_cli.tool.call.latency` metric
5. **Model detection** - Auto-detects Gemini model from events
6. **Telemetry config detection** - Checks env vars and settings.json

### Tests
- 35 unit tests covering all adapter functionality
- 262 total tests pass (including existing tests)
- Ruff linting passes
- Import verification successful

### Pricing Added
- gemini-2.5-pro, gemini-2.5-flash
- gemini-2.0-flash, gemini-2.0-flash-lite
- gemini-3-pro-preview (future)

## Example Session Added (2025-11-25)

Created `examples/gemini-cli-session/` with:
- `README.md` - Documentation and usage
- `telemetry-sample.jsonl` - Sample OpenTelemetry events

Sample includes:
- Token usage events (input, output, cache, thought)
- MCP tool calls (zen chat, zen thinkdeep, brave-search)
- Tool latency events
- Native tool filtered out (read_file with tool_type: native)
<!-- SECTION:NOTES:END -->
