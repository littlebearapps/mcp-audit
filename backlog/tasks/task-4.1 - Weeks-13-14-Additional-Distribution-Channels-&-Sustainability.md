---
id: task-4.1
title: 'Weeks 13-14: Additional Distribution Channels & Sustainability'
status: Roadmap
assignee: []
created_date: '2025-11-24 06:17'
labels: []
dependencies: []
parent_task_id: task-4
priority: high
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Add Homebrew and Docker distribution, setup automated maintenance tooling, and establish funding/governance for long-term sustainability.

**Note**: PyPI already completed in Week 4, so this focuses on additional channels and sustainability infrastructure.

**Key Deliverables**:
- Homebrew formula for brew install mcp-audit
- Docker image for containerized usage (optional)
- Automated maintenance tooling (stale bot, release drafter)
- Funding mechanism setup
- Governance policy documented

**Success Criteria**:
- Multi-channel distribution (PyPI + Homebrew minimum)
- Installation friction reduced (<2 mins)
- Automated tooling reduces maintenance burden
- Funding mechanism in place
- Governance policy documented
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 NOTE: PyPI distribution already completed in Week 4
- [ ] #2 Homebrew formula created for macOS: brew install mcp-audit
- [ ] #3 Homebrew formula submitted to Homebrew core or tap created
- [ ] #4 Docker image created (optional): docker run mcp-audit
- [ ] #5 Docker image published to Docker Hub (optional)
- [ ] #6 Stale bot configured and tested - auto-closes inactive issues
- [ ] #7 Release drafter configured and tested - auto-generates release notes
- [ ] #8 Dependabot confirmed active from Week 2 configuration
- [ ] #9 GitHub Sponsors page setup OR OpenCollective page setup
- [ ] #10 Lightweight governance policy created in GOVERNANCE.md
- [ ] #11 Governance: Who can merge PRs documented
- [ ] #12 Governance: Release cadence documented (e.g., monthly minor releases)
- [ ] #13 Governance: Platform ownership documented (e.g., maintainer owns Gemini adapter)
- [ ] #14 Installation documentation updated for all channels (PyPI, Homebrew, Docker)
- [ ] #15 Multi-channel distribution achieved: PyPI + Homebrew minimum
- [ ] #16 Installation friction reduced to <2 minutes on any platform
- [ ] #17 Automated tooling verified: stale bot and release drafter working
- [ ] #18 Funding mechanism active and documented
- [ ] #19 Governance policy reviewed by community
- [ ] #20 v1.0 RELEASE COMPLETE - all Phase 1-4 deliverables shipped
- [ ] #21 Update this task with daily progress on distribution channels
- [ ] #22 Test installation on all platforms: pip, brew, docker
- [ ] #23 Update this task if governance or funding approach changes
<!-- AC:END -->
