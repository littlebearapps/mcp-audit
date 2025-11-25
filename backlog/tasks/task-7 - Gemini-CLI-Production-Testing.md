---
id: task-7
title: Gemini CLI Production Testing
status: Ready
assignee: []
created_date: '2025-11-25 04:10'
labels:
  - testing
  - gemini-cli
  - phase-3
  - production
dependencies:
  - task-6
priority: high
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
End-to-end validation of mcp-audit with real Gemini CLI sessions.

**Prerequisites**:
- Gemini CLI installed (`npm install -g @google/gemini-cli`)
- Google account authenticated
- MCP servers configured in `~/.gemini/settings.json`
- Telemetry enabled (GEMINI_TELEMETRY_ENABLED=true)

**Test Scenarios**:
1. Basic session tracking (start, use MCP tools, stop)
2. Token attribution accuracy
3. Thinking token capture
4. Per-tool latency tracking
5. Signal handling (Ctrl+C graceful shutdown)
6. Session recovery from telemetry file

**Success Criteria**:
- All MCP tool calls captured correctly
- Token counts match Gemini CLI's own reporting
- Thinking tokens tracked separately
- Latency data correlates with actual tool execution time
- No data loss on session interruption
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Gemini CLI installed and authenticated
- [ ] #2 Telemetry enabled and verified (check ~/.gemini/telemetry.log grows)
- [ ] #3 MCP servers configured (zen, brave-search, or similar)
- [ ] #4 mcp-analyze collect --platform gemini-cli starts successfully
- [ ] #5 MCP tool calls tracked correctly (filtered by tool_type: mcp)
- [ ] #6 Token usage matches Gemini CLI reporting
- [ ] #7 Thinking tokens captured in platform_data.thoughts_tokens
- [ ] #8 Per-tool latency tracked accurately
- [ ] #9 Ctrl+C saves session data without loss
- [ ] #10 Session report generates correctly
- [ ] #11 No critical bugs found during testing
<!-- AC:END -->
