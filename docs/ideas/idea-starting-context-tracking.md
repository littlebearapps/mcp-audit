# Idea: Starting Context Tracking

**Status**: Proposed
**Priority**: Medium
**Phase**: v1.0+
**Related**: idea-context-bloat-sources.md, idea-compaction-tracking.md

---

## Summary

Track the "starting context" from instruction files (CLAUDE.md, AGENTS.md, GEMINI.md) and MCP metadata that exists before the first user message, providing visibility into the "floor cost" and "floor bloat" of each session.

---

## Problem Statement

Before any conversation begins, each AI assistant is already using context for:

- **Instruction files**: CLAUDE.md, AGENTS.md, GEMINI.md
- **MCP tool metadata**: Tool definitions, schemas, descriptions
- **System prompt**: Built-in safety and routing instructions

This "starting context" is:

- **Static per session**: Shows up on every API call
- **Invisible in the UI**: Users don't see it consuming space
- **Affects compaction**: Less headroom = more frequent compaction

Users need visibility into this baseline cost.

---

## Proposed Solution

### Starting Context Record

At session start, compute and record:

```python
@dataclass
class StartingContext:
    # Instruction files
    instruction_files: Dict[str, int]  # path -> tokens
    total_instructions_tokens: int

    # MCP metadata
    mcp_servers: Dict[str, int]  # server -> metadata tokens
    total_mcp_metadata_tokens: int

    # System (estimated)
    system_prompt_tokens: int

    # Totals
    total_static_tokens: int
    window_size: int

    @property
    def static_percentage(self) -> float:
        return (self.total_static_tokens / self.window_size) * 100

    @property
    def available_tokens(self) -> int:
        return self.window_size - self.total_static_tokens
```

### Data Sources by Platform

**Claude Code**:
- Auto-loads: CLAUDE.md, AGENTS.md (if referenced)
- Project-level CLAUDE files
- MCP tool definitions from configured servers
- `/context` command provides breakdown (if available)

**Codex CLI**:
- Auto-loads: AGENTS.md as instructions
- MCP tool definitions
- Workspace context

**Gemini CLI**:
- Auto-loads: GEMINI.md (global, project, subdir)
- Merges as persistent context
- MCP server tools from config

---

## Implementation Details

### Starting Context Analyzer

```python
from pathlib import Path
import tiktoken

class StartingContextAnalyzer:
    INSTRUCTION_FILES = {
        "claude_code": ["CLAUDE.md", "AGENTS.md", ".claude/settings.json"],
        "codex_cli": ["AGENTS.md", "codex.toml"],
        "gemini_cli": ["GEMINI.md", ".gemini/settings.json"],
    }

    WINDOW_SIZES = {
        "claude-sonnet-4-5": 200_000,
        "gpt-5-codex": 200_000,
        "gemini-2.5-pro": 1_000_000,
    }

    def __init__(self, project_root: Path, platform: str, model: str):
        self.project_root = project_root
        self.platform = platform
        self.model = model
        self.encoder = tiktoken.get_encoding("cl100k_base")

    def analyze(self, mcp_footprints: Dict[str, int]) -> StartingContext:
        instruction_files = self._analyze_instructions()

        return StartingContext(
            instruction_files=instruction_files,
            total_instructions_tokens=sum(instruction_files.values()),
            mcp_servers=mcp_footprints,
            total_mcp_metadata_tokens=sum(mcp_footprints.values()),
            system_prompt_tokens=self._estimate_system_prompt(),
            total_static_tokens=(
                sum(instruction_files.values()) +
                sum(mcp_footprints.values()) +
                self._estimate_system_prompt()
            ),
            window_size=self.WINDOW_SIZES.get(self.model, 200_000)
        )

    def _analyze_instructions(self) -> Dict[str, int]:
        """Tokenize instruction files for this platform."""
        files = {}

        for filename in self.INSTRUCTION_FILES.get(self.platform, []):
            # Check project root
            filepath = self.project_root / filename
            if filepath.exists():
                content = filepath.read_text()
                tokens = len(self.encoder.encode(content))
                files[str(filepath)] = tokens

            # Check home directory for global files
            global_path = Path.home() / filename
            if global_path.exists() and global_path != filepath:
                content = global_path.read_text()
                tokens = len(self.encoder.encode(content))
                files[str(global_path)] = tokens

        return files

    def _estimate_system_prompt(self) -> int:
        """Estimate system prompt size (platform-specific)."""
        estimates = {
            "claude_code": 3_000,
            "codex_cli": 2_500,
            "gemini_cli": 2_000,
        }
        return estimates.get(self.platform, 2_500)
```

### Session Integration

```python
class SessionTracker:
    def start_session(self, project_root: Path) -> Session:
        # Analyze starting context
        footprints = self.footprint_cache.get_all()
        starting = StartingContextAnalyzer(
            project_root=project_root,
            platform=self.platform,
            model=self.model
        ).analyze(footprints)

        session = Session(
            id=generate_id(),
            platform=self.platform,
            started_at=datetime.utcnow(),
            starting_context=starting,
            # ...
        )

        return session
```

### Dynamic Token Calculation

With starting context known, every API call can show:

```python
def analyze_call(call: Call, starting: StartingContext) -> dict:
    """Break down call tokens into static vs dynamic."""
    return {
        "input_total": call.input_tokens,
        "static_baseline": starting.total_static_tokens,
        "dynamic_tokens": call.input_tokens - starting.total_static_tokens,
        "dynamic_percentage": (
            (call.input_tokens - starting.total_static_tokens) /
            call.input_tokens * 100
        )
    }
```

---

## Report Output

```
Starting Context Analysis
════════════════════════════════════════════════════════════════

Session Baseline (before first prompt)
────────────────────────────────────────────────────────────────
Context window:           200,000 tokens (claude-sonnet-4-5)
Static baseline:           31,500 tokens (15.8%)
Available for work:       168,500 tokens (84.2%)

Instruction Files
────────────────────────────────────────────────────────────────
File                                              Tokens    Share
────────────────────────────────────────────────────────────────
~/claude-code-tools/CLAUDE.md                      3,200     1.6%
~/claude-code-tools/lba/project/CLAUDE.md          1,800     0.9%
~/claude-code-tools/.claude-instructions           1,500     0.8%
────────────────────────────────────────────────────────────────
Subtotal:                                          6,500     3.3%

MCP Tool Metadata
────────────────────────────────────────────────────────────────
Server                                            Tokens    Share
────────────────────────────────────────────────────────────────
mcp__zen (12 tools)                                8,340     4.2%
mcp__brave-search (4 tools)                        2,100     1.1%
mcp__omnisearch (20 tools)                        14,214     7.1%
────────────────────────────────────────────────────────────────
Subtotal:                                         24,654    12.3%

System Prompt (estimated)
────────────────────────────────────────────────────────────────
Built-in instructions:                             3,000     1.5%

Summary
────────────────────────────────────────────────────────────────
Every API call starts with 31,500 tokens of overhead.
With 200k window, you have 168,500 tokens for actual work.

⚠️  mcp__omnisearch alone uses 14,214 tokens (7.1%)
    → Consider: Disable if not frequently used, or trim descriptions

Trend (last 7 days)
────────────────────────────────────────────────────────────────
Date        Static      Delta    Note
────────────────────────────────────────────────────────────────
Nov 20      28,100         -     Baseline
Nov 22      31,500     +3,400    Added mcp__omnisearch
Nov 24      31,500         0     No change
Nov 26      31,500         0     Current
────────────────────────────────────────────────────────────────
```

### What-If Integration

```
What-If: Remove mcp__omnisearch
────────────────────────────────────────────────────────────────
Current static:           31,500 tokens (15.8%)
After removal:            17,286 tokens (8.6%)
Freed up:                 14,214 tokens (7.1%)

Impact:
  → Compaction threshold pushed back by ~14k tokens
  → Estimated 20% fewer compaction events
  → Per-call cost reduced by $0.004
```

---

## CLI Interface

```bash
# Show starting context for current session
mcp-analyze starting-context

# Compare starting context over time
mcp-analyze starting-context --history

# Show what-if scenarios
mcp-analyze starting-context --what-if remove=mcp__omnisearch

# Export for tracking
mcp-analyze starting-context --format json >> context-history.jsonl
```

---

## User Value

- **Floor cost visibility**: Know baseline before any work
- **Pathological file detection**: Catch bloated CLAUDE.md files
- **MCP optimization**: See which servers dominate static overhead
- **Compaction prediction**: Understand why compaction triggers early

---

## Dependencies

- Instruction file discovery per platform
- MCP footprint analyzer (existing)
- Token counting (tiktoken)

---

## Success Metrics

- Starting context calculated for 100% of sessions
- Instruction files detected with 95%+ accuracy
- Static percentage shown in session headers

---

## References

- Claude Code CLAUDE.md and AGENTS.md auto-loading
- Codex CLI AGENTS.md documentation
- Gemini CLI GEMINI.md specification
- Scott Spence MCP metadata analysis
