---
id: task-13
title: Add comprehensive public documentation to docs/
status: Done
assignee: []
created_date: '2025-11-25 06:25'
updated_date: '2025-11-25 06:29'
labels:
  - documentation
  - pypi
dependencies: []
priority: medium
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Ensure docs/ directory has all necessary public documentation for users and contributors.

**Essential docs:**
- docs/CHANGELOG.md - Version history
- docs/CONTRIBUTING.md - How to contribute
- docs/platforms/ - Platform-specific setup guides
- docs/architecture.md - System design (already exists)
- docs/data-contract.md - API stability guarantees (already exists)

**Nice to have:**
- docs/FAQ.md - Common questions
- docs/tutorials/getting-started.md - Step-by-step tutorial

**PyPI package considerations:**
- Include key docs in MANIFEST.in
- README.md is automatically shown on PyPI
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 CHANGELOG.md exists with version history
- [x] #2 CONTRIBUTING.md has clear contribution guidelines
- [x] #3 Platform docs cover Claude Code, Codex CLI, Gemini CLI
- [x] #4 Docs are linked from README
<!-- AC:END -->
