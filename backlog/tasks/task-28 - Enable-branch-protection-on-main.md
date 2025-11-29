---
id: task-28
title: Enable branch protection on main
status: Roadmap
assignee: []
created_date: '2025-11-29 06:52'
labels:
  - github
  - maintenance
  - ci-cd
dependencies: []
priority: low
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Enable GitHub branch protection rules for main branch to prevent accidental direct pushes.

**Requirements (solo dev):**
- Require status checks to pass before merging
- Do NOT require pull request reviews (solo dev)
- Require branches to be up to date before merging
- Do not restrict who can push (admin override allowed)

**Status Checks to Require:**
- Quality Gate (pytest, mypy, ruff, black)
- CodeQL analysis

**Why:**
- Prevents accidental pushes directly to main
- Ensures CI always passes before merge
- Maintains clean git history
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Enable branch protection on main branch
- [ ] #2 Require Quality Gate status check to pass
- [ ] #3 Require CodeQL status check to pass
- [ ] #4 Do NOT require PR reviews (solo dev)
- [ ] #5 Allow admin bypass for emergencies
- [ ] #6 Test by creating a PR and verifying protection works
<!-- AC:END -->
