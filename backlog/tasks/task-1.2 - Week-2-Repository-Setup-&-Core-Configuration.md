---
id: task-1.2
title: 'Week 2: Repository Setup & Core Configuration'
status: Roadmap
assignee: []
created_date: '2025-11-24 06:12'
updated_date: '2025-11-24 06:28'
labels: []
dependencies: []
parent_task_id: task-1
priority: high
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Create standalone public repository with critical pricing configuration system. This week focuses on infrastructure setup and CI/CD automation.

**CRITICAL**: Pricing configuration system is moved to Week 2 (from Week 11 in original plan) because we cannot launch a cost tracker without configurable model pricing.

**Key Deliverables**:
- Pricing configuration system (mcp-analyze.toml)
- New standalone GitHub repository (separate from claude-code-tools)
- CI/CD pipeline with GitHub Actions
- Repository templates (issues, PRs, CODE_OF_CONDUCT, SECURITY)
- Basic CLI interface (collect, report commands)
- MIT license and community standards

**Success Criteria**:
- Clean public repository structure
- CI/CD pipeline green on main branch
- CLI installable locally (pip install -e .)
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 CRITICAL: Pricing configuration system implemented in mcp-analyze.toml
- [ ] #2 [pricing] section created - maps model_name to cost_per_input_token and cost_per_output_token
- [ ] #3 Support for custom models - users can define costs for any model/alias
- [ ] #4 Documentation added for configuring pricing for new models
- [ ] #5 Validation implemented - warns when model has no pricing config
- [ ] #6 New standalone GitHub repository created (not nested in claude-code-tools)
- [ ] #7 All WP Navigator Pro references removed from codebase
- [ ] #8 CI/CD setup complete with GitHub Actions (automated tests on PR)
- [ ] #9 Linting configured (ruff, black, mypy)
- [ ] #10 Code coverage reporting enabled
- [ ] #11 Dependabot configured for dependency updates
- [ ] #12 LICENSE file added (MIT)
- [ ] #13 Issue templates created (bug, feature request, platform support)
- [ ] #14 PR template created
- [ ] #15 CODE_OF_CONDUCT.md added
- [ ] #16 SECURITY.md added
- [ ] #17 Basic CLI interface implemented: mcp-analyze collect
- [ ] #18 Basic CLI interface implemented: mcp-analyze report
- [ ] #19 --help documentation added for all commands
- [ ] #20 Update this task with daily progress notes in Implementation Notes
- [ ] #21 Test all deliverables: pricing config, CI/CD, CLI commands
- [ ] #22 Update this task if any scope changes or blockers occur

- [ ] #23 CI/CD includes MyPy strict type checking (uses mypy.ini from Week 1)
<!-- AC:END -->
