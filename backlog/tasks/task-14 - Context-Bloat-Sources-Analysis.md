---
id: task-14
title: Context Bloat Sources Analysis
status: Roadmap
assignee: []
created_date: '2025-11-26 05:37'
updated_date: '2025-11-26 05:49'
labels:
  - idea
  - context-analysis
  - cross-platform
dependencies:
  - task-15
priority: high
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Comprehensive analysis of where context bloat originates across all platforms (Claude Code, Codex CLI, Gemini CLI). Track and categorize context consumption: system stuff, static instructions, MCP metadata, and dynamic context. Provides visibility into static footprint per session and platform-specific bloat patterns.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Users can identify top 3 bloat sources in any session
- [ ] #2 Static overhead percentage visible before first prompt
- [ ] #3 Platform-specific recommendations generated automatically
<!-- AC:END -->
