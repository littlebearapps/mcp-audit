# Roadmap

This document outlines the planned development direction for MCP Audit. For completed features, see the [Changelog](CHANGELOG.md).

## Current Status

**Version**: v0.4.x
**Stage**: Stable for daily use

MCP Audit provides stable support for Claude Code, Codex CLI, and Gemini CLI. The core tracking and reporting functionality is production-ready.

## Released (v0.4.0) - December 2025

- [x] **Token estimation for Codex/Gemini CLI** - Per-tool token estimation via tiktoken and sentencepiece (Task 69)
- [x] **Theme system** - Catppuccin Mocha/Latte, high-contrast themes, ASCII mode, `--theme` CLI option (Task 83)
- [x] **Schema v1.4.0** - Per-call estimation metadata (`is_estimated`, `estimation_method`, `estimation_encoding`)
- [x] **Optional Gemma tokenizer** - Package size reduced to <500KB, tokenizer downloaded from GitHub Releases (Task 96)

## Upcoming (v0.5.0)

Target: Q1 2026
**Theme:** "MCP Efficiency Intelligence"

- [ ] **Smell Engine** - Detect 5 efficiency patterns: HIGH_VARIANCE, TOP_CONSUMER, HIGH_MCP_SHARE, CHATTY, LOW_CACHE_HIT (Task 85)
- [ ] **AI Prompt Export** - `mcp-audit export ai-prompt` command for AI analysis integration (Task 86)
- [ ] **Data Quality System** - Session-level `data_quality` block with accuracy labels (exact/estimated/calls-only) (Task 87)
- [ ] **Zombie Tool Detection** - Identify MCP tools defined but never called (Task 88)
- [ ] **TUI: Enhanced Live Overview** - Smells panel, data quality indicator, keybindings (Task 89)
- [ ] **TUI: Session Browser** - New `mcp-audit ui` command for exploring past sessions (Task 90)
- [ ] **Dynamic Pricing via LiteLLM** - Fetch pricing from LiteLLM JSON with static TOML fallback and caching (Task 59.5, 59.6)
- [ ] **Schema v1.5.0** - `smells`, `data_quality`, `zombie_tools` blocks (Task 91)

## Future (v0.6.0)

Target: Q2 2026
**Theme:** "Deeper Analysis + Multi-Model Sessions"

- [ ] **Multi-Model Per-Session Support** - Track per-model tokens/costs when users switch models mid-session (Task 59.0, 59.2, 59.3, 59.4)
  - Per-call model tagging (`model` field on each tool call)
  - Session-level model summary (`models_used`, `model_usage` with per-model tokens/costs)
  - TUI "Models Used" block for multi-model sessions
  - AI Export model breakdown
  - Accuracy metadata (`models_mixed` flag)
- [ ] **Static Cost Tracking** - Measure MCP server schema token weight (context tax) (Task 92)
- [ ] **Ollama CLI Support** - Track local model sessions (calls-only mode for models without token counts) (Task 93)
- [ ] **Schema v1.6.0** - `static_cost` block, `models_used`, `model_usage`, Ollama platform support (Task 94)

## v1.0.0 (Stable Release)

Target: Q3-Q4 2026
**Theme:** "Production Ready"

- [ ] All v0.5.0 and v0.6.0 features stable
- [ ] Comprehensive documentation
- [ ] Performance optimization
- [ ] API stability guarantees

## v1.1+ (Post-v1 Expansion)

**v1.1 - Developer Insight**
- Context window tracking (per-turn token load)
- TUI: Tool Detail mode
- Platform capability warnings

**v1.2 - Payload Analysis**
- Dynamic payload heatmap
- Full schema tokenizer
- Description density scoring

**v1.3 - Cross-Model Analysis**
- Model behavior differences
- Tool families/categories
- Baseline session support

**v1.4 - Comparison Suite**
- Session drift detection
- Enhanced TUI comparison mode

## Long-Term Vision (v2.0+)

- **Cross-session trend engine** - Time-series analysis of MCP efficiency over time
- **Team/enterprise features** - Aggregate tracking across team members
- **Plugin architecture** - Dynamic adapters for new AI CLI platforms
- **Cross-platform unified tracking** - Single dashboard for all AI coding tools

## Contributing Ideas

We welcome community input on the roadmap!

- **Feature requests**: [Start a Discussion](https://github.com/littlebearapps/mcp-audit/discussions/new?category=ideas)
- **View all ideas**: [Ideas Board](https://github.com/littlebearapps/mcp-audit/discussions/categories/ideas)
- **Questions**: [Q&A Discussions](https://github.com/littlebearapps/mcp-audit/discussions/categories/q-a)

## Disclaimer

This roadmap represents our current development plans and is subject to change. Items may be added, removed, or reprioritized based on community feedback, technical constraints, and resource availability. This roadmap does not represent a commitment to deliver any specific feature by any particular date.

---

**Last Updated**: December 2025
