# Idea: Static MCP Server Footprint Analyzer

**Status**: Proposed
**Priority**: High
**Phase**: v1.0
**Related**: idea-context-bloat-sources.md, idea-mcp-authoring-hints.md

---

## Summary

Promote the existing `analyze-mcp-efficiency.py` to a first-class CLI subcommand that analyzes MCP server metadata token costs, caches results, and surfaces findings in session reports automatically.

---

## Problem Statement

MCP tool definitions consume significant context before any conversation begins. Scott Spence's analysis showed 20 tools = 14,214 tokens (41% of context). With 50-60 tools, this becomes critical. Users need to:

- Know their "floor cost" before any prompt
- Identify which servers/tools are most expensive
- Make informed decisions about which tools to enable

---

## Proposed Solution

### CLI Subcommand

```bash
# Analyze all configured MCP servers
mcp-audit footprint

# Analyze specific server
mcp-audit footprint --server mcp__omnisearch

# Analyze from config file
mcp-audit footprint --config ~/.claude.json

# Output formats
mcp-audit footprint --format json
mcp-audit footprint --format table
```

### Cached Results

Store analysis results to avoid re-tokenizing on every session:

```
~/.mcp-audit/footprint-cache/
├── mcp__zen.json
├── mcp__brave-search.json
└── mcp__omnisearch.json
```

Cache structure:
```json
{
  "server": "mcp__omnisearch",
  "version": "1.2.3",
  "analyzed_at": "2025-11-26T10:00:00Z",
  "total_tokens": 14214,
  "tools": {
    "web_search": {
      "description_tokens": 520,
      "schema_tokens": 180,
      "total": 700
    },
    "ai_search": {
      "description_tokens": 380,
      "schema_tokens": 180,
      "total": 560
    }
  }
}
```

### Session Report Integration

Automatically include in session reports:

```
Static MCP Footprint (before first prompt)
──────────────────────────────────────────
Server                    Tools    Tokens
──────────────────────────────────────────
mcp__omnisearch            20     14,214
mcp__zen                   12      8,340
mcp__brave-search           4      2,100
mcp__github                 8      3,890
──────────────────────────────────────────
TOTAL                      44     28,544

⚠️  28,544 tokens (14%) consumed before your first prompt
```

---

## Implementation Details

### Footprint Analyzer Module

```python
# src/mcp_audit/analyzers/footprint.py

from dataclasses import dataclass
from typing import Dict, List
import tiktoken

@dataclass
class ToolFootprint:
    name: str
    description_tokens: int
    schema_tokens: int
    examples_tokens: int = 0

    @property
    def total(self) -> int:
        return self.description_tokens + self.schema_tokens + self.examples_tokens

@dataclass
class ServerFootprint:
    server: str
    version: str | None
    analyzed_at: str
    tools: Dict[str, ToolFootprint]

    @property
    def total_tokens(self) -> int:
        return sum(t.total for t in self.tools.values())

    @property
    def tool_count(self) -> int:
        return len(self.tools)

class FootprintAnalyzer:
    def __init__(self, encoding: str = "cl100k_base"):
        self.encoder = tiktoken.get_encoding(encoding)

    def analyze_server(self, server_name: str, tools: List[dict]) -> ServerFootprint:
        """Analyze all tools from an MCP server."""
        tool_footprints = {}
        for tool in tools:
            footprint = self._analyze_tool(tool)
            tool_footprints[tool["name"]] = footprint

        return ServerFootprint(
            server=server_name,
            version=None,  # TODO: Get from MCP handshake
            analyzed_at=datetime.utcnow().isoformat(),
            tools=tool_footprints
        )

    def _analyze_tool(self, tool: dict) -> ToolFootprint:
        """Tokenize a single tool definition."""
        desc_tokens = len(self.encoder.encode(tool.get("description", "")))
        schema_tokens = len(self.encoder.encode(json.dumps(tool.get("inputSchema", {}))))
        examples_tokens = len(self.encoder.encode(json.dumps(tool.get("examples", []))))

        return ToolFootprint(
            name=tool["name"],
            description_tokens=desc_tokens,
            schema_tokens=schema_tokens,
            examples_tokens=examples_tokens
        )
```

### Cache Manager

```python
class FootprintCache:
    def __init__(self, cache_dir: Path = None):
        self.cache_dir = cache_dir or Path.home() / ".mcp-audit" / "footprint-cache"
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def get(self, server: str) -> ServerFootprint | None:
        """Load cached footprint if fresh."""
        cache_file = self.cache_dir / f"{server}.json"
        if not cache_file.exists():
            return None

        data = json.loads(cache_file.read_text())
        # Check if cache is still valid (e.g., < 24 hours old)
        analyzed_at = datetime.fromisoformat(data["analyzed_at"])
        if datetime.utcnow() - analyzed_at > timedelta(hours=24):
            return None

        return ServerFootprint(**data)

    def set(self, footprint: ServerFootprint) -> None:
        """Cache a footprint analysis."""
        cache_file = self.cache_dir / f"{footprint.server}.json"
        cache_file.write_text(json.dumps(asdict(footprint), indent=2))
```

### CLI Integration

```python
# In mcp_analyze_cli.py

@app.command()
def footprint(
    server: str = typer.Option(None, help="Specific server to analyze"),
    config: Path = typer.Option(None, help="Path to MCP config file"),
    format: str = typer.Option("table", help="Output format: table, json"),
    no_cache: bool = typer.Option(False, help="Skip cache, re-analyze"),
):
    """Analyze static MCP server footprint (token costs)."""
    analyzer = FootprintAnalyzer()
    cache = FootprintCache()

    servers = discover_mcp_servers(config)

    results = []
    for srv in servers:
        if server and srv.name != server:
            continue

        cached = None if no_cache else cache.get(srv.name)
        if cached:
            results.append(cached)
        else:
            footprint = analyzer.analyze_server(srv.name, srv.tools)
            cache.set(footprint)
            results.append(footprint)

    if format == "json":
        print(json.dumps([asdict(r) for r in results], indent=2))
    else:
        print_footprint_table(results)
```

---

## User Value

- **Pre-session awareness**: Know context cost before starting
- **Server comparison**: Identify which servers are expensive
- **Tool-level detail**: See which specific tools are bloated
- **Optimization guidance**: Data to justify trimming descriptions
- **Automatic integration**: Shows up in session reports without extra work

---

## Dependencies

- `tiktoken` library for accurate tokenization
- MCP server discovery (from config files)
- Cache storage (~/.mcp-audit/footprint-cache/)

---

## Success Metrics

- Footprint analysis runs in <5 seconds for 10 servers
- Cache hit rate >80% for repeated analyses
- Users can identify servers consuming >10k tokens

---

## References

- Scott Spence MCP metadata analysis
- Claude `/context` command output
- Existing `analyze-mcp-efficiency.py` script
