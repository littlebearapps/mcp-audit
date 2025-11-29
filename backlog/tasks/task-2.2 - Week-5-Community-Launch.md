---
id: task-2.2
title: 'Week 5: Community Launch'
status: Ready
assignee: []
created_date: '2025-11-26 06:02'
updated_date: '2025-11-29 04:50'
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
- [x] #4 Blog post or README announcement section written
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
- [ ] #17 PREREQ: Run mcp-audit collect on a real Claude Code session and verify output
- [x] #18 PREREQ: Run mcp-audit report and verify report generation

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

### Report Command ✅ FIXED
- ~~Legacy session data (pre-v1.0) fails: 'Session data missing schema_version field'~~
- ~~Example sessions also fail: 'No valid sessions found'~~
- **Fixed 2025-11-26**: Consolidated storage to JSONL format only
  - Removed legacy `logs/sessions/` directory structure
  - Updated `BaseTracker` to use `StorageManager` (JSONL)
  - Updated `cmd_report()` to load JSONL files via `StorageManager`
  - Deprecated `SessionManager` class with deprecation warning
  - Verified: `mcp-audit report examples/` loads all 3 example sessions correctly

### Storage Consolidation (2025-11-26)
- **Before**: Two formats - legacy `logs/sessions/{id}/summary.json` + JSONL `~/.mcp-audit/`
- **After**: Single JSONL format only (`~/.mcp-audit/sessions/<platform>/<date>/*.jsonl`)
- BaseTracker now writes events directly to JSONL via StorageManager
- Session reconstruction from JSONL events implemented in `_session_from_events()`

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

## 2025-11-29 Messaging Refresh

- Created subtask task-2.2.1 for messaging/README refresh
- Two primary audiences identified:
  1. MCP Tool Developers - need per-tool metrics to optimize their implementations
  2. Session Users - want to understand what's eating context
- Lead with tool-builder angle (unique positioning)
- Pain-point hook + scannable table + immediate pip install
- See task-2.2.1 for detailed acceptance criteria

## 2025-11-29 README Refresh Complete (task-2.2.1)

- New pain-point hook: "MCP tools eating context and you don't know which ones?"
- Added hero image/gif placeholder (user to provide asset)
- Added 3-column value prop table: Track → Break Down → Optimize
- Added "Who Is This For?" section with both audiences
- Created quickref/messaging.md for consistent messaging reference
- Updated CLAUDE.md with audience clarity
- AC #4 (README announcement section): Satisfied by new intro + "Who Is This For?" section
- AC #20 still needs verification on GitHub/PyPI
<!-- SECTION:NOTES:END -->
