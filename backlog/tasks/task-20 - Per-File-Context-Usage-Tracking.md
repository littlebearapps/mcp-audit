---
id: task-20
title: Per-File Context Usage Tracking
status: Roadmap
assignee: []
created_date: '2025-11-26 05:37'
labels:
  - idea
  - file-analysis
  - context-tracking
dependencies: []
priority: medium
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Track which files are consuming the most context tokens, including how many times each file is read/summarized and the approximate token cost. Helps users identify files that need better documentation, splitting, or summary tools. Reports by token usage, read frequency, and file type.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 File analysis available for 80%+ of sessions
- [ ] #2 Top 10 files by tokens shown in reports
- [ ] #3 Actionable recommendations for files >5k tokens
<!-- AC:END -->
