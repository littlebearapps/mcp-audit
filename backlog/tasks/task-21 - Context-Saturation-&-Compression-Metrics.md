---
id: task-21
title: Context Saturation & Compression Metrics
status: Roadmap
assignee: []
created_date: '2025-11-26 05:37'
updated_date: '2025-11-26 05:49'
labels:
  - idea
  - compression
  - saturation
dependencies:
  - task-15
priority: medium
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Track context saturation levels and compression events to help users understand when approaching context limits. Monitors utilization %, compression events, tokens trimmed, and saturation timeline. Includes warning thresholds (approaching 70%, high 85%, critical 95%).
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Saturation metrics available for all sessions
- [ ] #2 Compression events detected within 5 seconds
- [ ] #3 Users warned before hitting 90% utilization
<!-- AC:END -->
