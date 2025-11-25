---
id: task-12
title: Update CLAUDE.md with PR merge approval requirement
status: Done
assignee: []
created_date: '2025-11-25 06:25'
updated_date: '2025-11-25 06:29'
labels:
  - claude-md
  - workflow
  - safety
dependencies: []
priority: high
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Add clear instruction to CLAUDE.md that Claude Code should NEVER merge a PR without explicit user approval.

**Add to Git Workflow section:**
- Never auto-merge PRs
- Always ask user before merging
- User must explicitly approve merge

This prevents accidental merges and ensures user maintains control over what goes to main branch.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 CLAUDE.md has explicit instruction to never merge without approval
- [x] #2 Instruction is in Git Workflow section
- [x] #3 Language is clear and unambiguous
<!-- AC:END -->
