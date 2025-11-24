---
id: task-1.2
title: 'Week 2: Repository Setup & Core Configuration'
status: Roadmap
assignee: []
created_date: '2025-11-24 06:12'
updated_date: '2025-11-24 07:37'
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
- [x] #1 CRITICAL: Pricing configuration system implemented in mcp-analyze.toml
- [x] #2 [pricing] section created - maps model_name to cost_per_input_token and cost_per_output_token
- [x] #3 Support for custom models - users can define costs for any model/alias
- [x] #4 Documentation added for configuring pricing for new models
- [x] #5 Validation implemented - warns when model has no pricing config
- [x] #6 New standalone GitHub repository created (not nested in claude-code-tools)
- [ ] #7 All WP Navigator Pro references removed from codebase
- [x] #8 CI/CD setup complete with GitHub Actions (automated tests on PR)
- [x] #9 Linting configured (ruff, black, mypy)
- [x] #10 Code coverage reporting enabled
- [x] #11 Dependabot configured for dependency updates
- [x] #12 LICENSE file added (MIT)
- [x] #13 Issue templates created (bug, feature request, platform support)
- [x] #14 PR template created
- [x] #15 CODE_OF_CONDUCT.md added
- [x] #16 SECURITY.md added
- [x] #17 Basic CLI interface implemented: mcp-analyze collect
- [x] #18 Basic CLI interface implemented: mcp-analyze report
- [x] #19 --help documentation added for all commands
- [x] #20 Update this task with daily progress notes in Implementation Notes
- [ ] #21 Test all deliverables: pricing config, CI/CD, CLI commands
- [ ] #22 Update this task if any scope changes or blockers occur

- [ ] #23 CI/CD includes MyPy strict type checking (uses mypy.ini from Week 1)
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
### 2025-11-24: Pricing Configuration System Complete

**Status**: ✅ AC #1-5 COMPLETE (Pricing configuration system)

**Deliverables**:
- `mcp-analyze.toml` - User-configurable pricing file (TOML format)
  - [pricing.claude] section with 3 models (Opus, Sonnet, Haiku)
  - [pricing.openai] section with 5 models (GPT-4o variants, O series)
  - [pricing.custom] section for user-defined models (with examples)
  - [metadata] section with currency, exchange rates, last_updated
- `pricing_config.py` - Pricing loader and validator module (360 lines)
  - PricingConfig class with load(), get_model_pricing(), calculate_cost()
  - Automatic validation with warnings for missing pricing
  - Support for Python 3.8+ (tomllib built-in for 3.11+, toml package fallback)
  - Built-in test suite (manual testing verified)
- `test_pricing_config.py` - Comprehensive test suite (320 lines, 40+ tests)
  - Loading tests, pricing lookup tests, cost calculation tests
  - Validation tests, metadata tests, edge cases, integration tests
  - Ready for pytest when development environment set up
- `docs/PRICING-CONFIGURATION.md` - Complete user guide (270 lines)
  - Configuration format and examples
  - Finding provider pricing
  - Validation and troubleshooting
  - Python API reference
  - Migration guide from JSON format
- `requirements-dev.txt` - Updated with toml>=0.10.2 dependency

**Validation**:
- ✓ Manual testing passed (python3 pricing_config.py)
- ✓ Loaded 8 models (3 Claude, 5 OpenAI)
- ✓ Validation passed with no errors
- ✓ Cost calculation verified: 10K input + 5K output + 50K cache = $0.1200

**Key Features**:
- User-configurable model pricing (any model/alias supported)
- Automatic warnings for missing pricing
- TOML format (human-readable, Python 3.11+ built-in support)
- Backward compatible with model-pricing.json
- Zero-cost local models supported
- Exchange rate metadata for display

**Next**: CLI interface implementation (AC #17-19)

### 2025-11-24: Basic CLI Interface Complete

**Status**: ✅ AC #17-19 COMPLETE (Basic CLI interface)

**Deliverables**:
- `mcp_analyze_cli.py` (540 lines) - Complete CLI application
  - Main entry point with argparse
  - Two subcommands: collect, report
  - Auto-platform detection (Claude Code, Codex CLI, Gemini CLI)
  - Comprehensive --help documentation
  
**collect command** (AC #17):
- Platform auto-detection or manual selection
- Output directory configuration
- Project name auto-detection
- Integration with adapters (Claude Code, Codex CLI)
- Real-time monitoring with Ctrl+C safety
- Session summary on completion

**report command** (AC #18):
- Multiple format support: JSON, Markdown, CSV
- Single session or multi-session analysis
- Configurable output (file or stdout)
- Top-N tools display (default: 10)
- Aggregate statistics across sessions

**--help documentation** (AC #19):
- Main help with examples and GitHub link
- Subcommand help with detailed descriptions
- All options documented with defaults
- Usage examples for common workflows

**Validation**:
- ✓ Main help tested: mcp-analyze --help
- ✓ collect help tested: mcp-analyze collect --help
- ✓ report help tested: mcp-analyze report --help
- ✓ All options display correctly

**Features**:
- Platform-agnostic design (works with any adapter)
- Graceful error handling
- Progress indicators and status messages
- Flexible output options (file/stdout)
- CSV export for external analysis

**Next**: Repository setup tasks (AC #6-16) and CI/CD configuration

### 2025-11-24: Repository Infrastructure Complete

**Status**: ✅ AC #6, #8-16 COMPLETE (Repository setup, CI/CD, templates)

**Pre-Verification**:
- ✓ Verified repository already standalone at https://github.com/littlebearapps/mcp-audit.git
- ✓ Not nested in claude-code-tools (AC #6 already complete)
- ✓ Analyzed gpm integration patterns (see docs/GPM-CI-INTEGRATION-PLAN.md)
- ✓ Recommended minimal CI approach (pytest + mypy + ruff + black)

**Deliverables**:

**CI/CD Pipeline** (AC #8-11, #23):
- `.github/workflows/ci.yml` - Complete GitHub Actions workflow
  - Security scan job (gpm security with JSON report)
  - Quality gate job (pytest + coverage, mypy strict, ruff lint, black format)
  - Coverage upload to Codecov
  - Artifact uploads (security report, coverage reports)
- `pyproject.toml` - Project configuration and tool settings
  - Project metadata (name, version, dependencies)
  - pytest configuration with strict markers
  - coverage configuration with exclusions
  - mypy strict mode (Python 3.8 target)
  - ruff linting rules (pycodestyle, pyflakes, isort, bugbear, etc.)
  - black formatting (100 char line length)
- `.github/dependabot.yml` - Automated dependency updates (AC #11)
  - Weekly Python dependency updates (pip)
  - Weekly GitHub Actions updates
  - Auto-assign PRs to nathanschram

**Community Standards** (AC #12-16):
- `LICENSE` - MIT License (AC #12)
  - Copyright (c) 2025 Little Bear Apps
  - Standard MIT License text
- `CODE_OF_CONDUCT.md` - Contributor Covenant 2.1 (AC #15)
  - Community standards and enforcement guidelines
  - Contact email placeholder (needs update)
- `SECURITY.md` - Security policy (AC #16)
  - Supported versions (0.2.x supported, 0.1.x deprecated)
  - Vulnerability reporting process
  - Security considerations for session data
  - Privacy protection utilities
  - Known security features and planned enhancements

**Repository Templates** (AC #13-14):
- `.github/PULL_REQUEST_TEMPLATE.md` (AC #14)
  - Description, type of change, testing, platform support
  - Comprehensive checklist (tests, docs, types, format)
- `.github/ISSUE_TEMPLATE/bug_report.md` (AC #13)
  - Bug description, environment, steps to reproduce
  - Platform-specific details (Claude Code, Codex CLI, etc.)
- `.github/ISSUE_TEMPLATE/feature_request.md` (AC #13)
  - Feature description, use case, proposed solution
  - Platform relevance and priority
- `.github/ISSUE_TEMPLATE/platform_support.md` (AC #13)
  - Platform information and technical details
  - Integration strategy and implementation willingness

**gpm Configuration Updates**:
- `.gpm.yml` - Updated with CI integration
  - Added quality-gate to requireStatusChecks
  - Added deleteBranchOnMerge: true (AC #6 user request)
  - Set PR template path
  - Branch protection configured (no PR reviews for solo dev)

**Key Features**:
- Solo developer workflow (no PR review requirements)
- Auto-delete branches on merge (user requested)
- Security scan runs first (fail fast pattern)
- Quality gate includes strict type checking (mypy)
- Coverage reporting with HTML + XML + Codecov
- Comprehensive issue/PR templates for community
- Standard open source licenses and policies

**Validation**:
- ⏳ Pending: Commit and push to test CI workflow
- ⏳ Pending: Verify quality-gate job passes
- ⏳ Pending: Verify security scan completes
- ⏳ Pending: Verify branch auto-delete on merge

**Remaining**:
- [ ] AC #7: Remove WP Navigator Pro references (18 found in docs/code)
- [ ] AC #21: Test all deliverables after CI verification
- [ ] AC #22: Document any scope changes or blockers

**Next**: Commit all repository infrastructure, test CI, remove WP Navigator Pro references
<!-- SECTION:NOTES:END -->
