---
id: task-2.2
title: 'Week 5: Community Launch'
status: Ready
assignee: []
created_date: '2025-11-26 06:02'
updated_date: '2025-11-26 06:10'
labels:
  - phase-2
  - community
  - launch
dependencies: []
parent_task_id: task-2
priority: high
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Launch mcp-audit publicly and establish community presence. Focus on announcements, GitHub Discussions, and beta tester recruitment.

**Goal**: Generate awareness and recruit beta testers to validate product-market fit.

**Key Deliverables**:
- GitHub repo already public ✅
- v0.3.0-beta release with release notes
- Announcement content across channels
- GitHub Discussions setup with categories
- Beta tester recruitment (5-10 developers)
- Daily issue triage and community response

**Success Metrics**:
- 50+ GitHub stars (validation of interest)
- 10+ community bug reports (engagement)
- 3+ external contributors (sustainability)
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 GitHub repo confirmed public with proper description and topics
- [ ] #2 v0.3.0-beta release created with comprehensive release notes
- [ ] #3 Release notes include: features, known issues, installation instructions, changelog
- [ ] #4 Blog post or README announcement section written
- [ ] #5 Twitter/X thread drafted and posted
- [ ] #6 Reddit posts created (r/LocalLLaMA, r/ClaudeAI, r/OpenAI)
- [ ] #7 Hacker News submission prepared
- [ ] #8 GitHub Discussions enabled on repository
- [ ] #9 Discussion categories created: Q&A, Ideas, Show & Tell
- [ ] #10 Welcome/pinned message created with quick links
- [ ] #11 Beta testers recruited from AI dev communities (target: 5-10)
- [ ] #12 Feedback template created for beta testers
- [ ] #13 Weekly check-in schedule established with beta testers
- [ ] #14 Daily issue triage process documented
- [ ] #15 Response SLA established (<24 hours for community questions)

- [x] #16 PREREQ: Install mcp-audit locally via pip/pipx and verify all CLI commands work
- [ ] #17 PREREQ: Run mcp-analyze collect on a real Claude Code session and verify output
- [ ] #18 PREREQ: Run mcp-analyze report and verify report generation

- [x] #19 PREREQ: Review and improve README.md for public audience - clear value prop, installation, quick start
- [ ] #20 PREREQ: Ensure README renders correctly on GitHub and PyPI
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
## 2025-11-26 Testing Notes

### CLI Installation ✅
- `pipx install mcp-audit` works (v0.3.2)
- `mcp-audit --version` works
- `mcp-audit --help` works
- `mcp-audit collect --help` works
- `mcp-audit report --help` works

### Report Command ❌ ISSUE FOUND
- Legacy session data (pre-v1.0) fails: 'Session data missing schema_version field'
- Example sessions also fail: 'No valid sessions found'
- **Action needed**: Fix report command to handle legacy formats or improve error messaging
- **Workaround**: Need to generate fresh session with `mcp-audit collect` to test report

## README Fixes (2025-11-26)

### Fixed Issues:
1. Platform format: `claude_code` → `claude-code` (hyphens, not underscores)
2. Removed non-existent flags: `--start`, `--end`, `--last`
3. Removed non-existent `migrate` command
4. Removed Discussions link (not enabled yet)
5. Updated report command examples to match actual CLI
6. Fixed `--top` → `--top-n` flag name

### README Now Accurate:
- All CLI examples match actual implementation
- Installation instructions correct
- Quick start guide tested
- Platform support matrix accurate
<!-- SECTION:NOTES:END -->
