# Idea: Per-File Context Usage Tracking

**Status**: Proposed
**Priority**: Medium
**Phase**: v1.0+
**Related**: idea-context-bloat-sources.md, idea-compression-metrics.md

---

## Summary

Track which files are consuming the most context tokens, including how many times each file is read/summarized and the approximate token cost. This helps users identify files that need better documentation, splitting, or summary tools.

---

## Problem Statement

File content often dominates context usage, especially in coding sessions. Users don't know:

- Which files are repeatedly loaded into context
- How many tokens specific files consume
- Whether large files are worth splitting or summarizing
- The cumulative impact of reading the same file multiple times

---

## Proposed Solution

### File Context Tracking

Track file operations from telemetry:

```
File Context Usage (Session)
─────────────────────────────────────────────────────────────
File                                 Reads    Tokens    Share
─────────────────────────────────────────────────────────────
src/legacy/report_generator.rs          7    ~15,000    18%
docs/api/monolith.md                    3    ~11,200    14%
src/lib/parser.ts                       5     ~8,900    11%
src/components/Dashboard.tsx            4     ~6,200     8%
tests/integration/full_suite.py         2     ~5,400     7%
─────────────────────────────────────────────────────────────
Top 5 files: 58% of file context

Recommendations:
  → src/legacy/report_generator.rs: Read 7 times - consider summarization
  → docs/api/monolith.md: 11k tokens - consider splitting into modules
```

### Data Sources by Platform

**Gemini CLI** (most detailed):
- `gemini_cli.file_operation` events provide:
  - `tool_name`, `operation` (read/create/update)
  - `lines`, `mimetype`, `extension`, `language`
  - Diff stats for updates

**Claude Code**:
- Tool Result events for `Read` tool
- File paths from tool invocations
- Estimate tokens from content length

**Codex CLI**:
- `codex.tool_result` events for file operations
- Content length from tool outputs

---

## Implementation Details

### Data Structure

```python
from dataclasses import dataclass, field
from typing import Dict, List
from pathlib import Path

@dataclass
class FileUsage:
    path: str
    read_count: int = 0
    total_tokens: int = 0
    total_lines: int = 0
    operations: List[str] = field(default_factory=list)  # read, update, create

    @property
    def avg_tokens_per_read(self) -> float:
        if self.read_count == 0:
            return 0.0
        return self.total_tokens / self.read_count

    @property
    def extension(self) -> str:
        return Path(self.path).suffix

    @property
    def is_large(self) -> bool:
        return self.total_tokens > 5000

    @property
    def is_frequently_read(self) -> bool:
        return self.read_count >= 5


@dataclass
class FileContextReport:
    files: Dict[str, FileUsage]

    @property
    def total_tokens(self) -> int:
        return sum(f.total_tokens for f in self.files.values())

    @property
    def total_reads(self) -> int:
        return sum(f.read_count for f in self.files.values())

    def top_by_tokens(self, n: int = 10) -> List[FileUsage]:
        sorted_files = sorted(
            self.files.values(),
            key=lambda f: f.total_tokens,
            reverse=True
        )
        return sorted_files[:n]

    def top_by_reads(self, n: int = 10) -> List[FileUsage]:
        sorted_files = sorted(
            self.files.values(),
            key=lambda f: f.read_count,
            reverse=True
        )
        return sorted_files[:n]

    def large_files(self) -> List[FileUsage]:
        return [f for f in self.files.values() if f.is_large]

    def frequently_read(self) -> List[FileUsage]:
        return [f for f in self.files.values() if f.is_frequently_read]
```

### File Context Analyzer

```python
class FileContextAnalyzer:
    def __init__(self, encoding: str = "cl100k_base"):
        self.encoder = tiktoken.get_encoding(encoding)

    def analyze_session(self, session: Session) -> FileContextReport:
        files: Dict[str, FileUsage] = {}

        for call in session.all_calls:
            if self._is_file_operation(call):
                file_path = self._extract_file_path(call)
                if file_path:
                    if file_path not in files:
                        files[file_path] = FileUsage(path=file_path)

                    usage = files[file_path]
                    usage.read_count += 1
                    usage.operations.append(call.tool_name)

                    # Estimate tokens
                    tokens = self._estimate_tokens(call)
                    usage.total_tokens += tokens

                    # Track lines if available
                    if hasattr(call, 'lines'):
                        usage.total_lines += call.lines

        return FileContextReport(files=files)

    def _is_file_operation(self, call) -> bool:
        file_tools = ['Read', 'read_file', 'file_read', 'fs.read']
        return call.tool_name in file_tools

    def _extract_file_path(self, call) -> str | None:
        # Extract from tool arguments
        if hasattr(call, 'arguments'):
            return call.arguments.get('file_path') or call.arguments.get('path')
        return None

    def _estimate_tokens(self, call) -> int:
        # If token count available, use it
        if hasattr(call, 'output_tokens') and call.output_tokens:
            return call.output_tokens

        # Estimate from content length
        if hasattr(call, 'content_length'):
            return call.content_length // 4  # Rough approximation

        # Estimate from lines
        if hasattr(call, 'lines'):
            return call.lines * 10  # ~10 tokens per line average

        return 0
```

### Recommendations Generator

```python
def generate_file_recommendations(report: FileContextReport) -> List[str]:
    recommendations = []

    # Large files
    for file in report.large_files():
        if file.total_tokens > 10000:
            recommendations.append(
                f"→ {file.path}: {file.total_tokens:,} tokens - "
                f"consider splitting into smaller modules"
            )
        elif file.total_tokens > 5000:
            recommendations.append(
                f"→ {file.path}: {file.total_tokens:,} tokens - "
                f"consider adding a summary or extracting key sections"
            )

    # Frequently read files
    for file in report.frequently_read():
        if file.read_count >= 5:
            recommendations.append(
                f"→ {file.path}: Read {file.read_count} times - "
                f"consider caching or using a summarization tool"
            )

    # Same file read multiple times in quick succession
    # (detected via timestamps, if available)

    return recommendations
```

---

## Report Output

```
File Context Usage
════════════════════════════════════════════════════════════════

Summary
────────────────────────────────────────────────────────────────
Total files accessed:         23
Total file reads:             47
Total file tokens:        82,400

By Token Usage (Top 10)
────────────────────────────────────────────────────────────────
File                                      Reads    Tokens    Share
────────────────────────────────────────────────────────────────
src/legacy/report_generator.rs               7    15,000    18.2%
docs/api/monolith.md                         3    11,200    13.6%
src/lib/parser.ts                            5     8,900    10.8%
src/components/Dashboard.tsx                 4     6,200     7.5%
tests/integration/full_suite.py              2     5,400     6.6%
src/utils/helpers.py                         6     4,800     5.8%
src/models/user.py                           3     4,200     5.1%
README.md                                    2     3,800     4.6%
src/api/endpoints.py                         4     3,500     4.2%
config/settings.toml                         8     2,100     2.5%
────────────────────────────────────────────────────────────────
Top 10:                                     44    65,100    79.0%

By Read Frequency (Top 5)
────────────────────────────────────────────────────────────────
config/settings.toml                         8 reads
src/legacy/report_generator.rs               7 reads
src/utils/helpers.py                         6 reads
src/lib/parser.ts                            5 reads
src/components/Dashboard.tsx                 4 reads

By File Type
────────────────────────────────────────────────────────────────
.rs (Rust)                               15,000 tokens (18%)
.md (Markdown)                           15,000 tokens (18%)
.ts (TypeScript)                         14,600 tokens (18%)
.tsx (React)                              6,200 tokens (8%)
.py (Python)                             14,400 tokens (17%)

Recommendations
────────────────────────────────────────────────────────────────
→ src/legacy/report_generator.rs: 15,000 tokens, read 7 times
  Consider: Split into modules or use summarization

→ docs/api/monolith.md: 11,200 tokens
  Consider: Split into per-endpoint documentation

→ config/settings.toml: Read 8 times
  Consider: Cache in memory or use config MCP server
```

---

## CLI Flags

```bash
# Include file analysis in report
mcp-analyze report --file-analysis

# Show only files above threshold
mcp-analyze report --file-analysis --min-tokens 1000

# Group by directory
mcp-analyze report --file-analysis --group-by-dir

# Export file data
mcp-analyze report --file-analysis --format csv > files.csv
```

---

## User Value

- **Identify bloat sources**: See which files dominate context
- **Optimize file structure**: Data to justify splitting large files
- **Reduce redundancy**: Spot files read multiple times
- **Guide documentation**: Know where better docs would help

---

## Dependencies

- File operation events from platform telemetry
- Token estimation (tiktoken or heuristics)
- Path normalization utilities

---

## Success Metrics

- File analysis available for 80%+ of sessions
- Top 10 files by tokens shown in reports
- Actionable recommendations for files >5k tokens

---

## References

- Gemini CLI `file_operation` telemetry
- Claude Code Read tool output
- Code file average token densities by language
