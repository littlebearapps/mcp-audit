# MCP Audit

**Track and optimize your AI coding assistant costs.**

MCP Audit measures token usage and costs across AI coding sessions, helping you identify expensive MCP tools and optimize your workflow.

[![CI](https://github.com/littlebearapps/mcp-audit/actions/workflows/ci.yml/badge.svg)](https://github.com/littlebearapps/mcp-audit/actions/workflows/ci.yml)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

---

## Why MCP Audit?

AI coding assistants like Claude Code and Codex CLI use MCP (Model Context Protocol) servers that can significantly impact your token usage and costs. MCP Audit helps you:

- **Find expensive tools** - Identify which MCP tools consume the most tokens
- **Detect duplicates** - Spot redundant tool calls wasting tokens
- **Track trends** - Monitor usage patterns across sessions
- **Optimize costs** - Make data-driven decisions to reduce spending

---

## Installation

```bash
# Install from PyPI
pip install mcp-audit

# Or with optional analytics features
pip install mcp-audit[analytics]
```

**Requirements**: Python 3.8+

---

## Quick Start

### 1. Track a Session

```bash
# Track Claude Code session
mcp-analyze collect --platform claude_code

# Track Codex CLI session
mcp-analyze collect --platform codex_cli
```

Sessions are automatically saved to `~/.mcp-audit/sessions/`.

### 2. Generate a Report

```bash
# View summary of recent sessions
mcp-analyze report

# Export detailed CSV
mcp-analyze report --format csv --output report.csv

# Analyze specific date range
mcp-analyze report --start 2025-11-01 --end 2025-11-30
```

### 3. Review Results

```
Top 10 Most Expensive Tools (Total Tokens)
═══════════════════════════════════════════════════════════════
Tool                              Calls    Tokens    Avg/Call
mcp__zen__thinkdeep                  12   450,231      37,519
mcp__brave-search__web               45   123,456       2,743
mcp__zen__chat                       89    98,765       1,109

Estimated Total Cost: $2.34 (across 15 sessions)
```

---

## Platform Support

| Platform | Status | Token Tracking | Time Tracking |
|----------|--------|----------------|---------------|
| Claude Code | **Stable** | Yes | Yes |
| Codex CLI | **Stable** | Yes | Yes |
| Gemini CLI | Planned | TBD | TBD |
| Ollama CLI | Experimental | No* | Yes |

*Ollama runs locally without token costs; time-based tracking available.

---

## Features

### Real-Time Tracking

Monitor your session as you work:

```bash
mcp-analyze collect --platform claude_code
```

```
MCP Audit - Live Session
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Tokens:  45,231 input │ 12,543 output │ 125K cached
Cost:    $0.12 (estimated)
Tools:   42 calls │ 12 unique

Recent: mcp__zen__chat (3,421 tokens)
```

### Cross-Session Analysis

Aggregate insights across all your sessions:

```bash
mcp-analyze report --last 30
```

- Top expensive tools by total tokens
- Most frequently called tools
- Anomaly detection (high variance, duplicates)
- Trend analysis over time

### Duplicate Detection

Automatically identifies redundant tool calls:

```json
{
  "redundancy_analysis": {
    "duplicate_calls": 3,
    "potential_savings": 15234,
    "details": [
      {"tool": "mcp__brave-search__web", "count": 2, "tokens": 8765}
    ]
  }
}
```

### Privacy-First Design

- **No prompts stored** - Only token counts and tool names
- **Local-only** - All data stays on your machine
- **Redaction hooks** - Customize what gets logged

---

## Configuration

Create `~/.mcp-audit/config/mcp-analyze.toml`:

```toml
[pricing.claude]
"claude-sonnet-4" = { input = 3.00, output = 15.00 }
"claude-opus-4" = { input = 15.00, output = 75.00 }

[pricing.openai]
"gpt-4o" = { input = 2.50, output = 10.00 }
```

See [Pricing Configuration](docs/PRICING-CONFIGURATION.md) for details.

---

## Documentation

| Document | Description |
|----------|-------------|
| [Architecture](docs/architecture.md) | System design, data model, adapters |
| [Data Contract](docs/data-contract.md) | Backward compatibility guarantees |
| [Platforms: Claude Code](docs/platforms/claude-code.md) | Claude Code setup guide |
| [Platforms: Codex CLI](docs/platforms/codex-cli.md) | Codex CLI setup guide |
| [Contributing](docs/contributing.md) | How to add platform adapters |
| [Privacy & Security](docs/privacy-security.md) | Data handling policies |

---

## CLI Reference

```bash
mcp-analyze --help

Commands:
  collect   Track a live session
  report    Generate usage report
  migrate   Migrate from v0.x format

Options:
  --version  Show version
  --help     Show help
```

### collect

```bash
mcp-analyze collect [OPTIONS]

Options:
  --platform TEXT    Platform to track (claude_code, codex_cli)
  --project TEXT     Project name (auto-detected from directory)
  --output PATH      Output directory (default: ~/.mcp-audit/sessions/)
```

### report

```bash
mcp-analyze report [OPTIONS] [SESSION_DIR]

Options:
  --format TEXT      Output format: json, csv, markdown (default: markdown)
  --output PATH      Output file (default: stdout)
  --top INT          Number of top tools to show (default: 10)
  --start DATE       Start date filter (YYYY-MM-DD)
  --end DATE         End date filter (YYYY-MM-DD)
  --last INT         Analyze last N days
```

---

## Data Storage

Sessions are stored at `~/.mcp-audit/sessions/`:

```
~/.mcp-audit/sessions/
├── claude_code/
│   └── 2025-11-25/
│       └── session-20251125T103045-abc123.jsonl
└── codex_cli/
    └── 2025-11-25/
        └── session-20251125T143022-def456.jsonl
```

Each session is a JSONL file (one event per line) for efficient streaming.

---

## Contributing

We welcome contributions! See [CONTRIBUTING.md](docs/contributing.md) for:

- How to add new platform adapters
- Testing requirements
- PR workflow

### Development Setup

```bash
git clone https://github.com/littlebearapps/mcp-audit.git
cd mcp-audit
python -m venv venv
source venv/bin/activate
pip install -e ".[dev]"
pytest
```

---

## License

MIT License - see [LICENSE](LICENSE) for details.

---

## Links

- [GitHub Repository](https://github.com/littlebearapps/mcp-audit)
- [Issue Tracker](https://github.com/littlebearapps/mcp-audit/issues)
- [Discussions](https://github.com/littlebearapps/mcp-audit/discussions)
- [Changelog](CHANGELOG.md)

---

**Made with care by [Little Bear Apps](https://littlebearapps.com)**
