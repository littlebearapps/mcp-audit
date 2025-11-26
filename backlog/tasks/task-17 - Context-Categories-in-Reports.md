---
id: task-17
title: Context Categories in Reports
status: Roadmap
assignee: []
created_date: '2025-11-26 05:37'
updated_date: '2025-11-26 05:49'
labels:
  - idea
  - reports
  - context-analysis
dependencies:
  - task-15
priority: high
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Add normalized context breakdown to all reports, categorizing tokens into: user_prompts, tool_outputs, mcp_tool_metadata, instructions_memory, thoughts, cache, and other_history. Provides consistent view across all platforms with ASCII bar charts and percentage breakdowns.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Context breakdown shown in 100% of session reports
- [ ] #2 All 7 categories populated (even if estimated)
- [ ] #3 Users identify top bloat category in <10 seconds
<!-- AC:END -->
