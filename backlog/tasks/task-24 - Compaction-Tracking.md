---
id: task-24
title: Compaction Tracking
status: Roadmap
assignee: []
created_date: '2025-11-26 05:37'
updated_date: '2025-11-26 05:49'
labels:
  - idea
  - compaction
  - waste-tracking
dependencies:
  - task-15
priority: medium
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Track detailed compaction/compression events across all platforms, including what content was likely removed (using LRU model), the cost of removed content, and patterns that trigger frequent compaction. Attributes waste to specific servers and tools.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Detect 90%+ of compaction events
- [ ] #2 Attribute 80%+ of removed tokens to sources
- [ ] #3 Generate actionable recommendations
<!-- AC:END -->
