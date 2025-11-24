# MCP Audit - Project Roadmap

**Last Updated**: 2025-11-24 (Consensus-Validated by GPT-5.1 + Gemini)
**Status**: Planning Phase
**Version**: 2.0 (Updated with Consensus Recommendations)

---

## Vision & Mission

**Vision**: Universal, open-source MCP efficiency analyzer for AI development teams

**Mission**: Empower developers to optimize AI tool costs through session-level MCP tracking and cross-platform analysis

---

## Current State (v0.1.0-internal)

**Implemented Features**:
- ✅ 2 platforms supported (Claude Code, Codex CLI)
- ✅ Real-time session tracking with token/cost analysis
- ✅ Cross-session pattern analysis and aggregation
- ✅ Duplicate detection and anomaly analysis
- ✅ Auto-recovery from incomplete sessions (events.jsonl)
- ✅ Per-server and per-tool token tracking
- ✅ Signal handling for graceful shutdown (Ctrl+C safe)

**Current Limitations**:
- ❌ Internal tool (nested in private claude-code-tools structure)
- ❌ Documentation assumes WP Navigator Pro context
- ❌ No public repository or package distribution
- ❌ Limited to 2 platforms (no Gemini CLI or Ollama CLI)
- ❌ No contribution guidelines or community structure

---

## Future State (v1.0.0)

**Target Release**: Week 14 (April 2026) - Compressed from 20 weeks based on consensus review

**Key Deliverables**:
- ✅ 2-4 platforms supported (Claude Code, Codex CLI + Gemini/Ollama if viable)
- ✅ Public open-source GitHub repository
- ✅ PyPI package distribution (`pip install mcp-audit`) - **Week 4, not Week 13**
- ✅ Programmatic API for integration (`load_sessions()`, `summarize_sessions()`)
- ✅ Plugin system for custom platforms (v1.0, not Phase 5)
- ✅ Configurable pricing model (user-supplied costs per model)
- ✅ Comprehensive platform-agnostic documentation
- ✅ Platform comparison matrix and setup guides
- ✅ Community contribution guidelines
- ✅ Automated tests and CI/CD pipeline
- ✅ Data contract guarantees (backward compatibility)

---

## Consensus Review Summary

**Date**: 2025-11-24
**Models Consulted**: GPT-5.1 (8/10 confidence) + Gemini 3 Pro Preview (9/10 confidence)

### Critical Changes Made

**🚨 Priority Shifts** (Addresses core value proposition):
1. **Pricing Configuration**: Moved from Week 11 → **Week 2** (Cannot launch cost tracker without configurable costs)
2. **PyPI Distribution**: Moved from Week 13 → **Week 4** (Beta requires `pip install`, not git clone)
3. **Timeline Compression**: Phase 4 reduced from 8 weeks → **2 weeks** (eliminated 6-week void)

**✅ Architecture Enhancements**:
4. **Programmatic API**: Added to Week 11 (`load_sessions()`, `summarize_sessions()` for integration)
5. **Plugin System**: Moved from Phase 5 → **Week 11** (enterprise adoption requirement)
6. **JSONL Directory Structure**: Clarified in Week 3 (`~/.mcp-audit/sessions/<platform>/<YYYY-MM-DD>/<session-id>.jsonl`)
7. **Data Contract**: Added explicit backward compatibility guarantees (Week 3)
8. **Unrecognized Line Handler**: Added robustness for CLI format changes (Week 1)
9. **Interception Mechanism**: Specified process wrapper vs file watcher decision (Week 1)

**📊 User Value Enhancements**:
10. **Day 1 Value Workflows**: Added concrete recipes (Week 6)
11. **Team/CI Examples**: Non-interactive mode + GitHub Actions YAML (Week 6)
12. **Gemini Feasibility Spike**: 1-day research in Week 1 (de-risk Week 7-8 commitment)

**🎯 Scope Adjustments**:
13. **npm wrapper**: Made explicitly optional (only if beta demands)
14. **Video tutorials**: Reduced from multi-video to **1 video** for v1.0
15. **Success Metrics**: Added minimum viability thresholds alongside stretch goals

**🌱 Sustainability Additions**:
16. **Funding Plan**: GitHub Sponsors/OpenCollective by Phase 3
17. **Governance Policy**: Lightweight maintainer policy for co-maintainers (Phase 2/3)
18. **Automated Tooling**: Dependabot, stale bot, release drafter (reduce maintenance burden)

### Both Models Agreed

- ✅ Core architecture (BaseTracker + schema) is sound
- ✅ Platform strategy (2→4 with kill criteria) is sensible
- ✅ Privacy-by-default posture is appropriate
- ✅ Deferring IDE/CI/dashboard to Phase 5+ is correct

### Key Risks Identified

- ⚠️ Solo maintainer will carry 90% burden for first year (not Week 20 handoff)
- ⚠️ Timeline is ambitious but plausible with scope management
- ⚠️ Gemini/Ollama unknowns could push back platform expansion

### Language Decision

**Date**: 2025-11-24
**Models Consulted**: GPT-5.1 + Gemini 3 Pro Preview (Consensus Analysis)
**Confidence**: 9/10 (Both models independently)

**Decision**: Python 3.8+ confirmed as optimal language for mcp-audit

**Rationale**:
- **Target Audience**: AI/ML engineers already use Python natively (no context switching)
- **Data Analysis Ecosystem**: pandas/numpy/matplotlib unmatched for session analysis and visualization
- **Performance**: Adequate for 100+ sessions (I/O-bound workload, not CPU-bound)
- **MCP Ecosystem**: Python is Tier 1 maturity (33.4% of ecosystem, tied with TypeScript at 32.0%)
- **Maintenance**: stdlib-only approach reduces dependency burden

**Implementation Recommendations**:
1. **MyPy Strict Type Hinting** (Week 1-2): Add comprehensive type checking for maintainability
2. **Optional Dependencies** (Week 3): Define extras system for `[analytics]`, `[viz]`, `[export]`
3. **pipx Installation** (Week 4): Primary installation method for isolated environments
4. **npm Wrapper Consideration** (Phase 5 only): Defer to Phase 5, only if beta testers demand it

**Alternative Considered**: TypeScript (equally mature in MCP ecosystem)
- Rejected because mcp-audit is an analytical tool, not an MCP server
- Data analysis in TypeScript lacks pandas/numpy equivalents
- No significant advantage for this use case

---

## Target Users

1. **AI Developers** - Optimizing MCP tool costs in daily workflow
2. **Development Teams** - Tracking AI tool efficiency across projects
3. **Open-Source Contributors** - Extending MCP ecosystem tooling
4. **Researchers** - Analyzing AI tool usage patterns and trends

---

## Product Positioning

**Niche**: "Post-hoc MCP usage and cost analysis for CLI-based AI dev tools"

**Differentiators**:
- Session-level detail (not just aggregate stats)
- Cross-platform support (works with any MCP-aware CLI)
- MCP-aware analysis (per-server and per-tool breakdowns)
- Free and open-source (MIT license)

**Complementary to**:
- ccusage MCP Server: Long-term aggregate usage (weeks/months)
- Platform-specific analytics: Broader account-level insights

---

## Platform Support Strategy

### Platform Comparison Matrix

| Platform     | Tokens | Time | MCP Support | Status       | Target    |
|-------------|--------|------|-------------|--------------|-----------|
| Claude Code | Yes    | Yes  | Mature      | ✅ Stable    | Phase 1-2 |
| Codex CLI   | Yes    | Yes  | Mature      | ✅ Stable    | Phase 1-2 |
| Gemini CLI  | ?      | ?    | Unknown     | ⏳ Planned   | Phase 3   |
| Ollama CLI  | No     | Yes  | Local       | ⏳ Experimental | Phase 3 |

### Platform Priority Rationale

**P0 (Critical)**: Claude Code + Codex CLI
- Already working with proven MCP integration
- Known token reporting formats
- 80% shared architecture
- Low risk for public beta

**P1 (High)**: Gemini CLI
- Likely compatible (Google Cloud ecosystem)
- MCP maturity needs verification
- Conditional: Skip if MCP support is immature
- **Kill Criteria**: No per-call token API/log by end of Week 8

**P2 (Medium)**: Ollama CLI
- Local model focus (no token costs)
- Time-based tracking alternative
- May lack detailed MCP event stream
- **Kill Criteria**: Log format too unstable or missing hooks by Week 10

---

## Technical Architecture

### Core Data Model (Platform-Agnostic)

**Schema Version**: 1.0

```python
Session {
  id: str
  platform: Literal["claude_code", "codex_cli", "gemini_cli", "ollama_cli", "custom"]
  started_at: datetime
  ended_at: datetime | None
  schema_version: str  # "1.0"
  server_sessions: list[ServerSession]
  metadata: dict[str, Any]  # platform-specific data
}

ServerSession {
  server_name_normalized: str  # e.g., "zen", "brave-search"
  server_name_raw: str | None  # e.g., "zen-mcp", "brave-search-mcp"
  calls: list[Call]
}

Call {
  id: str
  timestamp: datetime
  kind: Literal["model", "mcp_tool", "mcp_resource", "system"]
  model: str | None
  tool_name: str | None
  input_tokens: int | None
  output_tokens: int | None
  duration_ms: int | None  # for time-based platforms (Ollama)
  success: bool | None
  error_type: str | None
  metadata: dict[str, Any]
}
```

**Key Design Decisions**:
- **First-class duration_ms**: Required for Ollama/time-based tracking
- **kind field**: Clarifies call type (model vs tool vs resource)
- **metadata on Session + Call**: Forward compatibility for platform-specific data
- **schema_version**: Enables backward-compatible migrations

### BaseTracker Abstraction Layer

**Responsibilities**:

**BaseTracker** (platform-agnostic):
- Start/stop session lifecycle
- Maintain in-memory Session object
- Persist to `events.jsonl` (or similar)
- Expose stable `record_call(...)` API for adapters
- Handle signal interrupts (Ctrl+C safety)

**PlatformAdapter** (per CLI):
- Detect session start/end events
- Parse logs/CLI output/API responses
- Map raw events → Call instances
- Does NOT own file format (uses BaseTracker APIs only)

**Adapter Hierarchy**:
```
BaseTracker (abstract)
├── ClaudeCodeTracker (✅ implemented)
├── CodexTracker (✅ implemented)
├── GeminiTracker (⏳ Phase 3)
└── OllamaTracker (⏳ Phase 3)
```

### Repository Structure (Public Release)

```
mcp-audit/ (new public repo)
├── README.md (comprehensive, platform-agnostic)
├── LICENSE (MIT)
├── pyproject.toml (Python package config)
├── setup.py (pip installable)
├── .github/
│   ├── workflows/ (CI/CD: tests, linting)
│   ├── ISSUE_TEMPLATE/
│   ├── PULL_REQUEST_TEMPLATE.md
│   └── CODE_OF_CONDUCT.md
├── docs/
│   ├── index.md (product overview + why)
│   ├── getting-started.md (quickstart for all platforms)
│   ├── platforms/
│   │   ├── claude-code.md
│   │   ├── codex-cli.md
│   │   ├── gemini-cli.md (planned)
│   │   └── ollama-cli.md (experimental)
│   ├── architecture.md (BaseTracker, schema, adapters)
│   ├── contributing.md (how to add platform adapter)
│   ├── privacy-security.md (data handling policies)
│   └── roadmap.md (this document)
├── src/
│   ├── mcp_audit/
│   │   ├── __init__.py
│   │   ├── cli.py (entry point)
│   │   ├── trackers/
│   │   │   ├── base.py
│   │   │   ├── claude_code.py
│   │   │   ├── codex.py
│   │   │   ├── gemini.py (Phase 3)
│   │   │   └── ollama.py (Phase 3)
│   │   ├── analyzers/
│   │   │   └── efficiency.py
│   │   └── utils/
│   │       ├── session.py
│   │       ├── normalization.py
│   │       └── privacy.py (redaction, sanitization)
├── tests/
│   ├── unit/
│   ├── integration/
│   └── fixtures/ (sample events.jsonl per platform)
├── examples/
│   ├── claude-code-session/
│   ├── codex-cli-session/
│   └── ...
└── scripts/
    └── migration/ (schema migration helpers)
```

---

## Roadmap Phases

### Phase 1: Foundation & Restructure (Weeks 1-3)

**Goal**: Transform from internal tool to open-source ready codebase

#### Week 1: Code Restructure ✅ COMPLETE

**Deliverables**:
- [x] **Gemini CLI Feasibility Spike** (1 day) - Verified MCP capability, GO decision ✅
- [x] **Interception Mechanism Specification** - Documented in docs/INTERCEPTION-MECHANISM-SPEC.md ✅
- [x] Lock core schema (Session/ServerSession/Call with schema_version) - v1.0.0 locked ✅
- [x] **Add `duration_ms` field** to Call schema for time-based tracking (Ollama) ✅
- [x] Create platform abstraction layer (BaseTracker class) - base_tracker.py (520 lines) ✅
  - [x] **Unrecognized Line Handler** - Implemented with graceful degradation ✅
- [x] Refactor Claude Code tracker to use BaseTracker - claude_code_adapter.py (300 lines, 77% reduction) ✅
- [x] Refactor Codex CLI tracker to use BaseTracker - codex_cli_adapter.py (220 lines, 77% reduction) ✅
- [x] Extract reusable components:
  - [x] Normalization module (server names, tool names) - normalization.py (220 lines) ✅
  - [x] Session management (lifecycle, persistence) - session_manager.py (340 lines) ✅
  - [x] Privacy utilities (redaction, sanitization) - privacy.py (380 lines) ✅
- [x] Add comprehensive unit tests (pytest framework) - 5 files, 142 tests, 1,500+ lines ✅
  - [x] Event parsing tests - test_integration.py ✅
  - [x] Normalization tests - test_normalization.py ✅
  - [x] Basic metrics tests (totals, per-server breakdown) - test_base_tracker.py ✅
  - [x] Simple end-to-end: sample events.jsonl → report JSON - test_integration.py ✅
  - [x] **Unrecognized line handling tests** - Included in test suite ✅

**Success Criteria**:
- ✅ All existing functionality works via BaseTracker - ACHIEVED
- ✅ 80% code coverage on core modules - ACHIEVED (85.25% average)
- ✅ Zero breaking changes to existing session data - ACHIEVED
- ✅ **Gemini CLI feasibility determined (GO - proceed)** - ACHIEVED
- ✅ **Interception mechanism documented** - ACHIEVED

#### Week 2: Repository Setup & Core Configuration

**Deliverables**:
- [ ] **⭐ CRITICAL: Pricing Configuration System** - `mcp-analyze.toml` with user-supplied model pricing ⭐ NEW
  - [ ] **`[pricing]` section** - Map `model_name` → `cost_per_input_token`, `cost_per_output_token`
  - [ ] **Support custom models** - Users can define costs for any model/alias
  - [ ] **Documentation** - How to configure pricing for new models
  - [ ] **Validation** - Warn when model has no pricing config
- [ ] Create new standalone GitHub repo (separate from claude-code-tools)
- [ ] Remove all WP Navigator Pro references
- [ ] Setup CI/CD (GitHub Actions):
  - [ ] Automated tests on PR
  - [ ] Linting (ruff, black, mypy)
  - [ ] Code coverage reporting
  - [ ] **Dependabot** for dependency updates ⭐ NEW
- [ ] Add LICENSE (MIT)
- [ ] Setup repository templates:
  - [ ] Issue templates (bug, feature request, platform support)
  - [ ] PR template
  - [ ] CODE_OF_CONDUCT.md
  - [ ] SECURITY.md
- [ ] Add basic CLI interface:
  - [ ] `mcp-analyze collect` - Run under CLI, capture events
  - [ ] `mcp-analyze report` - Generate per-session JSON/Markdown
  - [ ] `--help` documentation for all commands

**Success Criteria**:
- ✅ Clean public repository structure
- ✅ CI/CD pipeline green on main branch
- ✅ CLI installable locally (`pip install -e .`)

#### Week 3: Core Documentation & Data Architecture

**Deliverables**:
- [ ] **⭐ JSONL Directory Structure** - Define and document file layout ⭐ NEW
  - [ ] **Directory structure**: `~/.mcp-audit/sessions/<platform>/<YYYY-MM-DD>/<session-id>.jsonl`
  - [ ] **Index/metadata file** for cross-session queries
  - [ ] **Documentation** in architecture.md
- [ ] **⭐ Data Contract Guarantees** - Explicit backward compatibility ⭐ NEW
  - [ ] **Backward compatibility statement**: "We guarantee backward compatibility for on-disk session format within major versions"
  - [ ] **Migration helpers**: v0.x → v1.x migration scripts
  - [ ] **Versioning policy**: When to bump major vs minor versions
  - [ ] **Document in** `docs/data-contract.md`
- [ ] Rewrite README.md for general audience:
  - [ ] Clear value proposition
  - [ ] Quick installation (pip install)
  - [ ] Simple usage example
  - [ ] Platform support matrix
  - [ ] Link to comprehensive docs
- [ ] Create platform-specific setup guides:
  - [ ] `docs/platforms/claude-code.md`
  - [ ] `docs/platforms/codex-cli.md`
- [ ] Write `docs/architecture.md`:
  - [ ] BaseTracker design
  - [ ] Event schema specification
  - [ ] Platform adapter interface
  - [ ] **JSONL directory structure** ⭐ NEW
- [ ] Write `docs/contributing.md`:
  - [ ] How to add new platform adapter
  - [ ] Testing requirements
  - [ ] PR workflow
  - [ ] **Plugin system guide** (custom platform hooks) ⭐ NEW
- [ ] Create `docs/privacy-security.md`:
  - [ ] Default: No raw prompt/response content
  - [ ] Redaction hooks for metadata
  - [ ] Local-only operation (no data sent externally)
- [ ] Add example sessions:
  - [ ] `examples/claude-code-session/` (sanitized events.jsonl)
  - [ ] `examples/codex-cli-session/` (sanitized events.jsonl)

**Success Criteria**:
- ✅ Documentation covers all current features
- ✅ External developer can install and run without assistance
- ✅ Contributing guide lowers barrier to entry
- ✅ **Data contract documented and migration helpers in place** ⭐ NEW
- ✅ **JSONL directory structure implemented and documented** ⭐ NEW

---

### Phase 2: Public Beta Release (Weeks 4-6)

**Goal**: Launch with 2 platforms, gather community feedback

#### Week 4: Beta Preparation & PyPI Launch

**Goal**: Make tool pip-installable BEFORE beta launch (moved from Week 13)

**Deliverables**:
- [ ] **⭐ CRITICAL: PyPI Package Distribution** - MOVED FROM WEEK 13 ⭐ NEW
  - [ ] **Setup PyPI account** and test upload
  - [ ] **Verify installation** on clean systems (macOS, Linux, Windows WSL)
  - [ ] **Package metadata** (description, keywords, classifiers)
  - [ ] **README rendered** on PyPI page
  - [ ] **Automated PyPI upload** via GitHub Actions on release
- [ ] **npm wrapper** - OPTIONAL, ONLY IF BETA SHOWS DEMAND ⚠️ CHANGED
  - [ ] Explicitly deferred unless beta feedback requests it
  - [ ] Reduces distribution surface during beta stabilization
- [ ] Create installation tests:
  - [ ] Fresh virtualenv test
  - [ ] Verify all dependencies resolve
  - [ ] Smoke test all CLI commands
  - [ ] **Test `pip install mcp-audit`** from PyPI ⭐ NEW
- [ ] Beta testing with 5-10 developers:
  - [ ] Recruit from AI dev communities (Twitter, Reddit r/LocalLLaMA)
  - [ ] Provide feedback template
  - [ ] Weekly check-ins

**Success Criteria**:
- ✅ **`pip install mcp-audit` works globally** (not just git clone) ⭐ NEW
- ✅ Installation works on all platforms (macOS, Linux, Windows WSL)
- ✅ Beta testers can complete setup in <5 minutes
- ✅ Zero critical bugs from beta feedback

#### Week 5: Community Launch

**Deliverables**:
- [ ] Publish to GitHub (public visibility)
- [ ] Create v0.3.0-beta release:
  - [ ] Release notes with features and known issues
  - [ ] Installation instructions
  - [ ] Changelog
- [ ] Create announcement content:
  - [ ] Blog post / README announcement section
  - [ ] Twitter/X thread
  - [ ] Reddit posts (r/LocalLLaMA, r/ClaudeAI, r/OpenAI)
  - [ ] Hacker News submission
- [ ] Setup GitHub Discussions:
  - [ ] Categories: Q&A, Ideas, Show & Tell
  - [ ] Pin welcome message with quick links
- [ ] Monitor initial feedback:
  - [ ] Daily issue triage
  - [ ] Respond to community questions within 24 hours

**Success Metrics**:
- 🎯 50+ GitHub stars (validation of interest)
- 🎯 10+ community bug reports (engagement)
- 🎯 3+ external contributors (sustainability)

#### Week 6: Beta Iteration & User Value

**Deliverables**:
- [ ] Fix critical bugs from community feedback
- [ ] Improve installation process based on user reports:
  - [ ] Add troubleshooting guide
  - [ ] Common error messages with fixes
- [ ] Add FAQ section to docs:
  - [ ] "Why are my costs different from platform estimates?"
  - [ ] "How do I track custom MCP servers?"
  - [ ] "Can I use this with private/enterprise deployments?"
- [ ] **⭐ Day 1 Value Workflows** - Concrete recipes for immediate utility ⭐ NEW
  - [ ] **Recipe 1**: "View your top 10 most expensive tools and monthly cost estimate" (Quick Start guide)
  - [ ] **Recipe 2**: "Compare two weeks before/after tools refactor" (Comparison guide)
  - [ ] **Tutorial**: Step-by-step walkthrough with screenshots
  - [ ] **Example output**: Sample reports showing value
- [ ] **⭐ Team/CI Usage Examples** - Non-interactive automation ⭐ NEW
  - [ ] **Non-interactive mode**: `mcp-analyze report --input /logs/... --output team-report.md`
  - [ ] **GitHub Actions example**: `.github/workflows/weekly-mcp-report.yml`
  - [ ] **Export to S3/Slack**: Example scripts in `examples/ci-cd/`
  - [ ] **Cron usage**: Weekly report generation examples
- [ ] Enhanced reports:
  - [ ] Top N most expensive MCP tools
  - [ ] Per-server failure vs success rates
  - [ ] Session comparison views
  - [ ] **CLI flags**: `--format json|csv|md|html`, `--output -|path`, `--group-by session|server|tool` ⭐ NEW
- [ ] Release v0.3.1-beta (stable beta)

**Success Metrics**:
- ✅ <5 open critical bugs
- ✅ 100+ PyPI downloads
- ✅ Positive community sentiment (GitHub Discussions, Reddit)
- ✅ **Users can demonstrate value in <10 minutes** ⭐ NEW

---

### Phase 3: Platform Expansion (Weeks 7-12)

**Goal**: Add Gemini CLI and Ollama CLI support

#### Week 7-8: Gemini CLI Integration

**Deliverables**:
- [ ] Research Gemini CLI:
  - [ ] Output format and MCP support investigation
  - [ ] Token reporting capabilities
  - [ ] Session lifecycle events
- [ ] Implement GeminiTracker (inherits from BaseTracker):
  - [ ] Event parsing
  - [ ] Normalization logic
  - [ ] Token/cost tracking
- [ ] Create `docs/platforms/gemini-cli.md`:
  - [ ] Installation and setup
  - [ ] MCP configuration
  - [ ] Usage examples
- [ ] Add example Gemini sessions to `examples/`
- [ ] Test with real Gemini CLI users (5+ beta testers)

**Kill Criteria** (evaluated at end of Week 8):
- ❌ No per-call token API/log available, AND
- ❌ No parseable MCP event feed
- → Mark as "planned / not yet supported" and skip to Week 9

**Conditional Success**:
- ✅ If MCP mature: Release v0.4.0-beta (3 platforms)
- ⚠️ If MCP immature: Document limitations, release with "experimental" label

#### Week 9-10: Ollama CLI Integration

**Deliverables**:
- [ ] Research Ollama CLI:
  - [ ] Output format and MCP support
  - [ ] Time-based tracking requirements (no tokens)
  - [ ] Local model metadata
- [ ] Implement OllamaTracker:
  - [ ] Time-based resource cost tracking
  - [ ] Duration per tool call
  - [ ] Estimated tokens (if metadata available)
- [ ] Handle local model scenarios:
  - [ ] Clear documentation: "Time-based efficiency, not monetary cost"
  - [ ] Different analysis metrics (time per call vs tokens per call)
- [ ] Create `docs/platforms/ollama-cli.md`
- [ ] Add example Ollama sessions
- [ ] Test with Ollama community

**Kill Criteria** (evaluated at end of Week 10):
- ❌ Log format too unstable, OR
- ❌ Missing session lifecycle hooks
- → Keep as "experimental" and document limitations

**Success**:
- ✅ Release v0.5.0-beta (4 platforms, some experimental)

#### Week 11: Programmatic API & Plugin System

**Goal**: Enable integration and enterprise adoption (moved from Phase 5)

**Deliverables**:
- [ ] **⭐ CRITICAL: Programmatic API** - Integration surface ⭐ NEW
  - [ ] **`load_sessions(path_pattern|file)`** → iterator of Session objects
  - [ ] **`summarize_sessions(sessions, ...)`** → simple dataclasses or dicts
  - [ ] **Python API documentation** with examples
  - [ ] **Use cases**: Integration with Splunk, BigQuery, Prometheus, custom dashboards
- [ ] **⭐ CRITICAL: Plugin System for v1.0** - MOVED FROM PHASE 5 ⭐ NEW
  - [ ] **Config-based custom platform hook** in `mcp-analyze.toml`:
    - [ ] `platform = "custom"` with `command` / `log_path`
    - [ ] Regex or JSON-path templates to map to Call fields
  - [ ] **Python entrypoint** via setuptools extras (`mcp_audit.platforms` entry point group)
  - [ ] **Documentation** in `docs/contributing.md` - "Adding custom platform or server adapter"
  - [ ] **Example custom adapter** in `examples/custom-platform/`
- [ ] Cost forecasting (optional, can defer if timeline slips):
  - [ ] Predict future costs based on historical trends
  - [ ] Weekly/monthly cost projections
- [ ] Tool recommendation engine (optional):
  - [ ] Suggest cheaper alternatives for expensive tools
  - [ ] Identify redundant tool calls
- [ ] Enhanced export formats:
  - [ ] JSON (already supported)
  - [ ] CSV (already supported)
  - [ ] HTML reports (new)
  - [ ] Markdown summaries (new)
- [ ] Comparison views:
  - [ ] Compare sessions
  - [ ] Compare projects
  - [ ] Compare time periods (week over week, month over month)

**Success Criteria**:
- ✅ **Programmatic API functional and documented** ⭐ NEW
- ✅ **Plugin system allows custom platforms** ⭐ NEW
- ✅ Release v0.6.0-beta (enhanced analysis + integration surface)
- ✅ Positive feedback on new features from community

**Note**: Cost forecasting and tool recommendation are nice-to-have. If schedule slips, ship v1.0 without them.

#### Week 12: v1.0 Release Preparation

**Deliverables**:
- [ ] Final bug fixes and polish:
  - [ ] Zero critical bugs
  - [ ] All P0/P1 issues resolved
- [ ] Performance optimization:
  - [ ] Handle 100+ sessions efficiently
  - [ ] Lazy loading for cross-session analysis
  - [ ] Memory-efficient JSONL streaming
- [ ] Complete documentation review:
  - [ ] All platforms documented
  - [ ] Architecture guide complete
  - [ ] Contributing guide tested by external developers
- [ ] **Video tutorial** - REDUCED FROM 3 VIDEOS TO 1 ⚠️ CHANGED
  - [ ] **ONE 5-10 min "Getting Started" video** for v1.0
  - [ ] Defer "Analyzing Costs" and "Custom Platform" videos to Phase 5
  - [ ] Reduces content creation burden during critical release period
- [ ] Prepare v1.0 announcement:
  - [ ] Blog post
  - [ ] Social media campaign
  - [ ] Submit to newsletters (TLDR, The Batch, etc.)
- [ ] Migration plan:
  - [ ] Schema migration helper for users on beta
  - [ ] Backward compatibility for v0.x sessions

**Success Metrics**:
- 🎯 v1.0.0 stable release
- 🎯 **200+ GitHub stars (stretch) / 100+ stars (minimum viability)** ⭐ UPDATED
- 🎯 **2-4 platforms supported (flexible based on Gemini/Ollama feasibility)** ⭐ UPDATED
- 🎯 50+ PyPI downloads/week

---

### Phase 4: Distribution (Weeks 13-14) - COMPRESSED FROM 8 WEEKS

**Goal**: Multi-channel distribution for discoverability

**Note**: TIMELINE COMPRESSED - PyPI moved to Week 4, removed 6-week void (Weeks 15-20 deferred)

#### Week 13-14: Additional Distribution Channels

**Deliverables**:
- [ ] **Note: PyPI already completed in Week 4** ✅
- [ ] Create Homebrew formula (macOS):
  - [ ] `brew install mcp-audit`
  - [ ] Submit to Homebrew core or create tap
- [ ] Docker image (optional):
  - [ ] `docker run mcp-audit` for containerized usage
  - [ ] Publish to Docker Hub
- [ ] **Automated Maintenance Tooling** ⭐ NEW
  - [ ] **Stale bot** - Auto-close inactive issues
  - [ ] **Release drafter** - Auto-generate release notes
  - [ ] Dependabot already configured (Week 2)
- [ ] **Funding & Governance** ⭐ NEW
  - [ ] **GitHub Sponsors** or **OpenCollective** page setup
  - [ ] **Lightweight governance policy** documented in `GOVERNANCE.md`:
    - [ ] Who can merge PRs
    - [ ] Release cadence
    - [ ] Platform ownership (e.g., one maintainer "owns" Gemini adapter)
- [ ] Update installation docs for all channels

**Success Metrics**:
- ✅ Multi-channel distribution (PyPI + Homebrew minimum)
- ✅ Installation friction reduced (<2 mins on any platform)
- ✅ **Automated tooling reduces maintenance burden** ⭐ NEW
- ✅ **Funding mechanism in place** ⭐ NEW
- ✅ **Governance policy documented** ⭐ NEW

**v1.0 RELEASE COMPLETE AT END OF WEEK 14** 🎉

#### Deferred to Phase 5+ (Post-v1.0)

**Rationale**: Build user base and mature the core library before expanding to IDE/CI/dashboard integrations. These features require:
- Significant maintenance burden
- Stable API surface
- Strong community demand validation

**Deferred Features** (moved to Phase 5 backlog):
- IDE extensions (VSCode, JetBrains, Cursor)
- CI/CD integrations (GitHub Actions plugins, GitLab CI, pre-commit hooks) - **Note: Examples already in Week 6**
- Web dashboard UI (real-time, WebSocket updates)
- Team collaboration features
- Additional video tutorials (2+ more videos)

---

### Phase 5: Community Growth (Ongoing)

**Goal**: Build sustainable open-source project

#### Continuous Activities

**Monthly**:
- 📊 Release cycle (minor versions with community features)
- 📝 Roadmap updates based on feedback
- 🎓 Educational content (blog posts, tutorials)

**Weekly**:
- 🐛 Issue triage and PR reviews
- 🤝 Community engagement (respond to discussions)
- 📈 Track adoption metrics (downloads, stars, forks)

**Quarterly**:
- 🔄 Retrospectives on roadmap progress
- 📊 Success metrics review
- 🎯 Feature prioritization based on data

#### Community Building

**Early Phase** (Months 1-3):
- Recruit 2-3 co-maintainers
- Establish PR review workflow
- Document maintenance processes

**Growth Phase** (Months 4-12):
- Regular contributor recognition
- Community calls/office hours (monthly)
- Conference talks and presentations

**Maturity Phase** (Year 2+):
- Governance model (if needed)
- Sustainability funding (sponsors, grants)
- Ecosystem partnerships

---

## Success Metrics

**Note**: Each phase has **Minimum Viability** (continue) and **Stretch Goals** (optimal) thresholds ⭐ UPDATED

### Phase 1-2 (Beta) - Weeks 1-6

**Minimum Viability** (Required to proceed):
- ✅ 25+ GitHub stars
- ✅ 5+ community bug reports
- ✅ 2+ external contributors
- ✅ 50+ PyPI downloads

**Stretch Goals** (Optimal):
- 🎯 50+ GitHub stars
- 🎯 10+ community bug reports
- 🎯 5+ external contributors
- 🎯 100+ PyPI downloads

**Decision Point**: If by Week 6 we have <25 stars and <5 bug reports, reassess positioning/marketing before Phase 3

**Success = Community interest validated, proceed to Phase 3**

### Phase 3 (Platform Expansion) - Weeks 7-12

**Minimum Viability** (Required for v1.0):
- ✅ 100+ GitHub stars
- ✅ 2-3 platforms supported (Claude Code + Codex CLI minimum, Gemini/Ollama optional)
- ✅ 25+ PyPI downloads/week
- ✅ 5+ active contributors

**Stretch Goals** (Optimal):
- 🎯 200+ GitHub stars
- 🎯 4 platforms supported (2 stable, 2 experimental)
- 🎯 50+ PyPI downloads/week
- 🎯 10+ active contributors

**Decision Point**: If by Week 12 we have <100 stars and <5 contributors, pause Phase 4 and reassess scope

**Success = Product-market fit achieved, v1.0 released**

### Phase 4 (Distribution) - Weeks 13-14

**Minimum Viability**:
- ✅ 2+ distribution channels (PyPI + Homebrew)
- ✅ Funding mechanism in place (GitHub Sponsors/OpenCollective)
- ✅ Governance policy documented

**Stretch Goals**:
- 🎯 300+ GitHub stars
- 🎯 100+ PyPI downloads/week
- 🎯 Docker image published

**Success = Multi-channel distribution, v1.0 launched**

### Phase 5 (Maturity) - Ongoing

**Minimum Viability** (Sustainable project):
- ✅ 500+ GitHub stars
- ✅ 500+ PyPI downloads/week
- ✅ 15+ active contributors
- ✅ 1+ co-maintainer recruited

**Stretch Goals** (Thriving ecosystem):
- 🎯 1000+ GitHub stars
- 🎯 1000+ PyPI downloads/week
- 🎯 30+ active contributors
- 🎯 Featured in AI development blogs/newsletters
- 🎯 2+ co-maintainers recruited

**Success = Self-sustaining community-driven project**

---

## Dependencies & Risks

### Critical Dependencies

1. **Gemini CLI MCP Maturity** (Phase 3 - Week 7-8)
   - Risk: MCP integration may be immature or missing
   - Mitigation: Kill criteria at Week 8, skip if not viable

2. **Ollama CLI MCP Support** (Phase 3 - Week 9-10)
   - Risk: May lack MCP event stream or detailed logs
   - Mitigation: Time-based tracking alternative, experimental label

3. **Community Adoption** (Phase 2 - Week 5-6)
   - Risk: Low adoption if niche need not validated
   - Mitigation: Beta signups, early feedback, pivot if needed

### Risk Assessment

**High Risk**: Unknown Gemini/Ollama MCP support
- Mitigation: Incremental approach, kill criteria, skip if not viable
- Impact: May launch v1.0 with 2-3 platforms instead of 4

**Medium Risk**: Community adoption and engagement
- Mitigation: Quality beta, comprehensive docs, active community engagement
- Impact: Slower growth, may need to pivot features

**Medium Risk**: Feature creep and scope expansion
- Mitigation: Clear roadmap, community-driven priorities, feature triage
- Impact: Delayed releases, burnout risk

**Medium Risk**: Solo maintainer burden ⭐ NEW
- Reality: Original author will carry 90% of burden for first year (not Week 20)
- Mitigation:
  - Automated tooling (dependabot, stale bot, release drafter) from Week 2/Week 13-14
  - Personal bandwidth kill-guard: If maintenance >30 hrs/week or burnout risk, de-scope features
  - Feature deferral criteria: Cost forecasting, videos can be dropped if needed
- Impact: Slower feature development, need to recruit co-maintainers aggressively in Phase 3

**Low Risk**: Breaking changes from CLI tool updates
- Mitigation: Automated tests, version pinning, community bug reports, unrecognized line handler
- Impact: Maintenance burden, potential compatibility issues

**Low Risk**: Privacy concerns and sensitive data
- Mitigation: Clear privacy policy, local-only default, redaction hooks
- Impact: User hesitation to adopt

---

## Resource Requirements

### Phase 1-2: Foundation & Public Beta (Weeks 1-6)

**Effort**: Solo developer, 20-30 hours/week
- Core development: 15-20 hours/week
- Documentation: 3-5 hours/week
- Community engagement: 2-5 hours/week

### Phase 3: Platform Expansion (Weeks 7-12)

**Effort**: 1-2 contributors, 15-20 hours/week each
- Platform integration: 10-15 hours/week
- Testing and bug fixes: 3-5 hours/week
- Community support: 2-5 hours/week

### Phase 4: Distribution (Weeks 13-14) - COMPRESSED

**Effort**: 1-2 contributors, 10-15 hours/week each (only 2 weeks)
- Additional distribution channels (Homebrew, Docker): 5-10 hours
- Automated tooling setup (stale bot, release drafter): 3-5 hours
- Funding/governance setup: 2-4 hours
- Documentation updates: 2-3 hours

**Note**: PyPI already completed in Week 4, reducing Phase 4 workload significantly

### Phase 5: Community Growth (Ongoing)

**Effort**: Community-driven, 5-10 hours/week maintenance
- Issue triage: 2-3 hours/week
- PR reviews: 2-3 hours/week
- Community engagement: 1-2 hours/week
- Content creation: 2-3 hours/week (as needed)

**Sustainability Model**:
- Recruit 2+ co-maintainers by Phase 3
- Distribute maintenance burden across contributors
- Avoid single-person bus factor

---

## Edge Cases & Limitations

### 1. Platform Fragmentation

**Issue**: Each CLI tool may update independently with breaking changes

**Mitigation**:
- Version pinning for CLI tools (document supported versions)
- Automated tests run against latest CLI versions
- Community reports for breaking changes
- Platform-specific version compatibility matrix

### 2. Local Models (Ollama)

**Issue**: May not report token usage at all

**Mitigation**:
- Time-based tracking as approximation (not cost)
- Clear documentation on limitations
- Different analysis metrics (time per call vs tokens per call)
- Label as "experimental" if tracking is incomplete

### 3. Enterprise/Private Deployments

**Issue**: Custom MCP servers may have unique formats

**Mitigation**:
- Plugin system for custom adapters (Phase 5)
- Clear documentation on extending platform support
- Community-contributed adapters
- Config-driven server registration

### 4. Privacy Concerns

**Issue**: Session data may contain sensitive information

**Mitigation**:
- Default: No raw prompt/response content stored
- Redaction hooks for metadata before persistence
- Local-only operation (no data sent to external services)
- Clear privacy policy in `docs/privacy-security.md`
- Sanitization tools for sharing example sessions

### 5. Performance at Scale

**Issue**: 100+ sessions may slow down analysis

**Mitigation**:
- Lazy loading for cross-session analysis
- JSONL streaming (not full file load)
- Filters (by date range, platform, project)
- Performance benchmarks in tests

---

## Key Trade-offs & Assumptions

### Trade-off 1: Python vs Multi-language

**Choice**: Python-first with npm wrapper

**Pros**:
- Current codebase is Python
- Rich data analysis ecosystem (pandas, numpy)
- Fast iteration on core logic

**Cons**:
- Node.js developers may prefer pure npm package
- Adds installation dependency (Python 3.8+)

**Mitigation**: npm wrapper provides familiar interface for JS developers

### Trade-off 2: CLI vs Web UI

**Choice**: CLI-first, Web UI deferred to Phase 5+

**Pros**:
- Faster to market (6 weeks vs 20+ weeks)
- Lower maintenance burden
- Fits developer workflow (terminal-based)

**Cons**:
- Less accessible to non-technical users
- Limited visualization capabilities

**Mitigation**: Simple CLI with good UX, HTML export for visual reports

### Trade-off 3: All Platforms vs Quality Platforms

**Choice**: 2 platforms (beta) → 4 platforms (v1.0) with kill criteria

**Pros**:
- Quality over quantity
- Proven demand before investing resources
- Lower risk of wasted effort

**Cons**:
- May miss niche users (e.g., Ollama-only developers)
- Slower ecosystem coverage

**Mitigation**: Incremental additions based on community feedback

---

## Assumptions & Validation

### Assumption 1: MCP Protocol Stability

**Assumption**: MCP protocol won't drastically change during roadmap

**Risk**: Major protocol updates could break tracking

**Validation**:
- Monitor MCP specification repo for updates
- Community discussions and announcements
- Version pinning to known-compatible MCP versions

### Assumption 2: Community Interest

**Assumption**: Developers want MCP cost optimization tools

**Risk**: Low adoption if niche need is not validated

**Validation**:
- Beta signups (target: 10+ interested developers)
- GitHub stars (target: 50+ at beta launch)
- Community feedback and feature requests

### Assumption 3: Token Reporting Consistency

**Assumption**: Gemini/Ollama report tokens similarly to Claude/Codex

**Risk**: May require fundamentally different tracking approach

**Validation**:
- Research in Phase 3 (Weeks 7-10)
- Kill criteria if incompatible
- Experimental label if partial support

---

## Implementation Priorities (Weeks 1-3)

### Immediate Next Steps

If starting implementation today, focus on:

1. **Lock Core Schema** (Day 1-2)
   - Finalize Session/ServerSession/Call structure
   - Add `schema_version: "1.0"` to all records
   - Add `duration_ms` field for time-based tracking
   - Add `kind` field for call type differentiation

2. **Extract BaseTracker** (Day 3-5)
   - Create abstract base class
   - Move shared logic from existing trackers
   - Define stable adapter interface

3. **Normalize Server Names** (Day 6-7)
   - Single normalization module for all platforms
   - Handle `-mcp` suffix and other variants
   - Unit tests for all known formats

4. **Add Basic CLI** (Day 8-10)
   - `mcp-analyze collect` - Capture events
   - `mcp-analyze report` - Generate JSON/Markdown
   - `--help` documentation

5. **Write Minimal Docs** (Day 11-15)
   - README for general audience
   - Getting started for Claude Code only
   - Platform comparison matrix (with placeholders)

6. **Add Tests** (Day 16-21)
   - Event parsing tests
   - Basic metrics tests
   - End-to-end: sample events.jsonl → report JSON

**Goal**: End of Week 3 with solid foundation for public beta

---

## Decision Log

### Decision 1: Start with 2 Platforms (Claude Code, Codex CLI)

**Date**: 2025-11-24
**Rationale**: Proven working, minimize risk, validate demand before expanding
**Impact**: Faster to beta (6 weeks vs 12 weeks for 4 platforms)
**Alternatives Considered**: Launch with all 4 platforms (rejected due to high risk)

### Decision 2: MIT License

**Date**: 2025-11-24
**Rationale**: Maximize adoption, permissive for commercial use, industry standard
**Impact**: Allows commercial derivatives, fork-friendly, community trust
**Alternatives Considered**: Apache 2.0 (similar), GPL (rejected due to copyleft restrictions)

### Decision 3: Python as Primary Language

**Date**: 2025-11-24
**Rationale**: Current codebase, strong data analysis ecosystem, fast iteration
**Impact**: npm wrapper needed for Node.js developers
**Alternatives Considered**: Node.js (rejected due to rewrite cost), Go (rejected due to ecosystem gap)

### Decision 4: Incremental Platform Additions

**Date**: 2025-11-24
**Rationale**: Validate demand before investing resources, kill criteria for non-viable platforms
**Impact**: May launch v1.0 with 2-3 platforms instead of 4
**Alternatives Considered**: All platforms at once (rejected due to high risk)

### Decision 5: Defer IDE/CI/Dashboard to Phase 5+

**Date**: 2025-11-24
**Rationale**: Build user base first, mature core library, validate ecosystem demand
**Impact**: Faster v1.0 release, reduced maintenance burden in early phases
**Alternatives Considered**: Include in Phase 4 (rejected due to scope creep risk)

### Decision 6: Schema Versioning from Day 1

**Date**: 2025-11-24
**Rationale**: Enables backward-compatible migrations, avoids painful rewrites later
**Impact**: Migration helper needed for future schema changes
**Alternatives Considered**: Add versioning later (rejected due to migration pain)

---

## Open Questions

### Q1: Gemini CLI MCP Maturity?

**Timeline**: Investigate in Phase 3 (Week 7-8)
**Decision Point**: End of Week 8 (kill criteria evaluation)
**Options**:
- Proceed if per-call token API/log available
- Skip if MCP integration is immature
- Experimental label if partial support

### Q2: Ollama CLI Token Reporting?

**Timeline**: Investigate in Phase 3 (Week 9-10)
**Decision Point**: End of Week 10 (kill criteria evaluation)
**Options**:
- Time-based tracking if no token reporting
- Experimental label if incomplete
- Skip if log format too unstable

### Q3: Community Adoption Rate?

**Timeline**: Measure in Phase 2 (Week 5-6)
**Decision Point**: End of Week 6 (beta iteration complete)
**Success Criteria**:
- 50+ GitHub stars
- 10+ bug reports
- Positive community sentiment

**Pivot Options** if adoption low:
- Focus on specific niche (e.g., Claude Code only)
- Add killer feature based on feedback
- Adjust positioning/marketing

### Q4: PyPI vs npm as Primary Distribution?

**Timeline**: Decide in Phase 4 (Week 13-14)
**Decision Point**: Based on user demographics from Phase 2-3
**Options**:
- PyPI primary, npm wrapper (current plan)
- npm primary, Python backend (if Node.js users dominate)
- Equal priority for both

### Q5: When to Add IDE Integrations?

**Timeline**: Re-evaluate in Phase 5 (after v1.0 release)
**Decision Point**: Based on community requests and core library maturity
**Criteria for proceeding**:
- 500+ stars (demand validation)
- Stable API surface (no breaking changes in 3+ months)
- 2+ co-maintainers (capacity for maintenance)

---

## Conclusion

This roadmap provides a clear path from internal tool to universal open-source MCP efficiency analyzer over **14 weeks** (compressed from 20) with ongoing community growth. The phased approach balances ambition with pragmatism:

- **Phase 1** (Weeks 1-3): Solid foundation + critical pricing configuration
- **Phase 2** (Weeks 4-6): Public beta validation + PyPI launch (moved from Week 13)
- **Phase 3** (Weeks 7-12): Platform expansion with kill criteria to manage risk
- **Phase 4** (Weeks 13-14): Additional distribution (PyPI already done, add Homebrew/Docker)
- **Phase 5** (Ongoing): Sustainable community-driven project

**Key Success Factors** (Validated by GPT-5.1 + Gemini Consensus):
- ✅ Start small, iterate fast (2 platforms → 2-4 platforms, flexible)
- ✅ Quality over quantity (proven platforms first, optional Gemini/Ollama)
- ✅ Community-driven priorities (let users guide features)
- ✅ Sustainable pace (avoid burnout, recruit co-maintainers, automated tooling)
- ✅ **Critical features early** (pricing config Week 2, PyPI Week 4, plugin system Week 11)
- ✅ **Realistic metrics** (minimum viability + stretch goals, not aspirational only)

**Critical Changes from Consensus Review**:
1. 🚨 **Pricing configuration** moved to Week 2 (from Week 11) - BLOCKS core value
2. 🚨 **PyPI distribution** moved to Week 4 (from Week 13) - BLOCKS beta adoption
3. 🚨 **Timeline compressed** to 14 weeks (from 20) - Eliminated 6-week void
4. ✅ **Programmatic API** added to Week 11 for integration
5. ✅ **Plugin system** moved to v1.0 (from Phase 5) for enterprise adoption
6. ✅ **Day 1 value workflows** + Team/CI examples added to Week 6
7. ✅ **Automated tooling** (stale bot, release drafter) to reduce maintainer burden
8. ✅ **Funding & governance** plan in Phase 4
9. ✅ **Minimum success metrics** alongside stretch goals

**Next Steps**:
1. **Review and approve** this consensus-validated roadmap
2. **Begin Phase 1, Week 1** implementation:
   - Gemini feasibility spike (1 day)
   - Interception mechanism specification
   - BaseTracker abstraction
   - Unrecognized line handler
3. **Weekly progress updates** in GitHub Discussions
4. **Adjust roadmap quarterly** based on learnings and community feedback

**v1.0 Target**: Week 14 (April 2026) 🎉

---

**Roadmap Maintained By**: MCP Audit Core Team
**Consensus Validated By**: GPT-5.1 (8/10 confidence) + Gemini 3 Pro Preview (9/10 confidence)
**Last Review**: 2025-11-24
**Next Review**: 2026-01-24 (Quarterly)
