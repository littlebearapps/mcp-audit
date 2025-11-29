---
id: task-16
title: Static MCP Server Footprint Analyzer
status: Roadmap
assignee: []
created_date: '2025-11-26 05:37'
labels:
  - idea
  - mcp-analysis
  - cli
dependencies: []
priority: high
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Promote existing analyze-mcp-efficiency.py to a first-class CLI subcommand that analyzes MCP server metadata token costs, caches results, and surfaces findings in session reports automatically. Adds `mcp-audit footprint` command with cached results and session report integration.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Footprint analysis runs in <5 seconds for 10 servers
- [ ] #2 Cache hit rate >80% for repeated analyses
- [ ] #3 Users can identify servers consuming >10k tokens
<!-- AC:END -->
