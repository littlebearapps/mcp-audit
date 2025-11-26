---
id: task-15
title: Context Slices Data Model
status: Roadmap
assignee: []
created_date: '2025-11-26 05:37'
labels:
  - idea
  - data-model
  - schema
dependencies: []
priority: high
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Upgrade the core data model to include "context slices" per model call, with attributes showing where tokens came from (tools, thoughts, instructions, files, messages). Enables precise attribution with normalized event schema supporting token_breakdown fields for input_total, output_total, cache, tool_results, thoughts, overhead_static, overhead_history.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 80%+ of input tokens attributed to specific categories
- [ ] #2 Context breakdown available for all supported platforms
- [ ] #3 Users can identify top 3 context consumers per session
<!-- AC:END -->
