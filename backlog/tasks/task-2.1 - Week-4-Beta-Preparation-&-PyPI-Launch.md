---
id: task-2.1
title: 'Week 4: Beta Preparation & PyPI Launch'
status: In Progress
assignee: []
created_date: '2025-11-24 06:13'
updated_date: '2025-11-25 03:01'
labels: []
dependencies: []
parent_task_id: task-2
priority: high
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Make tool pip-installable BEFORE beta launch. This is CRITICAL and moved from Week 13 because beta requires 'pip install', not 'git clone'.

**CRITICAL**: PyPI distribution is the foundation for beta adoption. Users must be able to install with a single command.

**Key Deliverables**:
- PyPI package distribution setup and tested
- Installation verification on all platforms (macOS, Linux, Windows WSL)
- Automated PyPI upload via GitHub Actions
- Installation tests (fresh virtualenv, dependency resolution)
- Beta testing with 5-10 developers recruited

**Success Criteria**:
- pip install mcp-audit works globally (not just git clone)
- Installation works on all platforms
- Beta testers can complete setup in <5 minutes
- Zero critical bugs from beta feedback
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 CRITICAL: PyPI package distribution setup complete
- [ ] #2 PyPI account created and test upload successful
- [ ] #3 Installation verified on clean macOS system
- [ ] #4 Installation verified on clean Linux system
- [ ] #5 Installation verified on clean Windows WSL system
- [ ] #6 Package metadata configured (description, keywords, classifiers)
- [ ] #7 README renders correctly on PyPI page
- [ ] #8 Automated PyPI upload configured via GitHub Actions on release
- [ ] #9 npm wrapper marked as OPTIONAL - only if beta shows demand
- [ ] #10 Fresh virtualenv installation test passed
- [ ] #11 All dependencies resolve correctly
- [ ] #12 Smoke tests pass for all CLI commands
- [ ] #13 pip install mcp-audit test successful from PyPI
- [ ] #14 Beta testers recruited from AI dev communities (Twitter, Reddit r/LocalLLaMA)
- [ ] #15 Feedback template created for beta testers
- [ ] #16 Weekly check-in schedule established with beta testers
- [ ] #17 Update this task with daily progress notes in Implementation Notes
- [ ] #18 Test all deliverables: PyPI installation on all platforms
- [ ] #19 Update this task if any scope changes or blockers occur

- [ ] #20 pipx installation documented as primary method (isolated environment best practice)
- [ ] #21 pipx install mcp-audit tested and verified on all platforms
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
## 2025-11-25 Progress

### Completed
- ✅ Package restructured to src/ layout for PyPI
- ✅ pyproject.toml configured for modern Python packaging
- ✅ GitHub Actions publish workflow created (.github/workflows/publish.yml)
- ✅ CI pipeline passing (tests, mypy, ruff, black)
- ✅ All 227 tests pass
- ✅ Package builds successfully (python -m build)
- ✅ Local installation test successful (pip install -e .)
- ✅ CLI command mcp-analyze --version works

### BLOCKED - Waiting for PyPI Approval
- ⏳ **littlebearapps PyPI organization** - registration pending approval
- ⏳ **mcp-audit trusted publisher** - registration pending approval

### Next Steps (after PyPI approval)
1. Re-create GitHub release v0.3.0 to trigger publish workflow
2. Verify pip install mcp-audit works from PyPI
3. Test on clean systems (macOS, Linux, Windows WSL)
4. Begin beta tester recruitment
<!-- SECTION:NOTES:END -->
