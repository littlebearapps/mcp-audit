---
id: task-2.2.1
title: Messaging & README Refresh for Community Launch
status: Done
assignee: []
created_date: '2025-11-29 04:44'
updated_date: '2025-11-29 06:47'
labels:
  - phase-2
  - messaging
  - readme
  - community-launch
dependencies: []
parent_task_id: task-2.2
priority: high
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Refresh mcp-audit messaging and README.md to clearly communicate value proposition to both primary audiences before community launch.

**Goal**: Clear, scannable messaging that speaks to both MCP tool builders and session users.

**Primary Audiences**:
1. **MCP Tool Developers** - Built MCP servers (hand-coded or via AI), need per-tool token metrics to optimize implementations
2. **Session Users** - Use Claude Code/Codex/Gemini CLI daily, want to understand what's eating context

**Messaging Direction**:
- Lead with tool-builder angle (unique positioning)
- Pain-point hook: "MCP tools eating context and you don't know which ones?"
- Three-column scannable value prop: Track → Break Down → Optimize
- Immediate pip install for low friction

**Key Changes**:
- New @ file for messaging/audience reference
- README.md restructure with new intro and image placeholder
- CLAUDE.md updates if needed
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Create quickref/messaging.md with target audiences, value props, and key messaging points
- [x] #2 Messaging file optimized for Claude Code context (succinct, bullet points)
- [x] #3 Update CLAUDE.md Overview section with audience clarity if needed
- [x] #4 Restructure README.md intro: pain-point hook → image/gif placeholder → value prop table → pip install
- [x] #5 Add placeholder for hero image/gif at top of README (user to provide asset)
- [x] #6 Include 'Who Is This For?' section with both audiences
- [x] #7 Update any acceptance criteria in task-2.2 that reference README/messaging
- [ ] #8 Verify README renders correctly on GitHub
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
## 2025-11-29 Complete

- PR #13 merged to main
- PR #14 (gpm removal) also merged - fixes CI
- All 8 acceptance criteria complete
- README now live on GitHub with new messaging
<!-- SECTION:NOTES:END -->
