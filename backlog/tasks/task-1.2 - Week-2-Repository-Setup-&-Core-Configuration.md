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
<!-- SECTION:NOTES:END -->
