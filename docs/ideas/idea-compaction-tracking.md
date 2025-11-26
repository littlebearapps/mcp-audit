# Idea: Compaction Tracking

**Status**: Proposed
**Priority**: Medium
**Phase**: v1.0+
**Related**: idea-compression-metrics.md, idea-context-bloat-sources.md

---

## Summary

Track detailed compaction/compression events across all platforms, including what content was likely removed, the cost of removed content, and patterns that trigger frequent compaction.

---

## Problem Statement

All three AI coding assistants use context compaction:

- **Claude Code**: `/compact` command and automatic compaction
- **Codex CLI**: Native compaction in GPT-5.1-Codex-Max
- **Gemini CLI**: `chat_compression` with explicit metrics

Compaction means: "We paid for all this context and then threw most of it away." Users need to understand:

- How often compaction happens
- What content is being lost
- The cost of content that gets compacted away
- How to reduce compaction frequency

---

## Proposed Solution

### Per-Compaction Metrics

For each compaction event, track:

```python
@dataclass
class CompactionEvent:
    timestamp: datetime
    tokens_before: int
    tokens_after: int
    source: str  # gemini | claude | codex | inferred
    reason: str | None  # auto | manual | window_full

    # What was likely removed (estimated)
    removed_by_category: Dict[str, int]  # tool_outputs: 5000, history: 3000, etc.
    removed_by_server: Dict[str, int]    # mcp__docs: 4000, mcp__zen: 2000
    removed_by_tool: Dict[str, int]      # semantic_search: 3000, chat: 1500

    # Age of removed content
    oldest_content_age_minutes: int
    avg_content_age_minutes: int

    @property
    def tokens_trimmed(self) -> int:
        return self.tokens_before - self.tokens_after

    @property
    def trim_ratio(self) -> float:
        return self.tokens_trimmed / self.tokens_before if self.tokens_before > 0 else 0
```

### Session-Level Compaction Health

```python
@dataclass
class CompactionHealth:
    total_events: int
    total_tokens_trimmed: int
    events_per_hour: float
    avg_minutes_between_events: float
    waste_ratio: float  # trimmed / total_dynamic_tokens
    compaction_cost: float  # cost of compaction calls themselves

    # By category
    wasted_by_category: Dict[str, int]
    wasted_by_server: Dict[str, int]
    wasted_by_tool: Dict[str, int]
```

### Content Attribution (LRU Model)

When compaction trims `D` tokens, model removal as LRU (oldest first):

```python
class CompactionAttributor:
    """Attribute removed tokens to sources using LRU model."""

    def __init__(self):
        self.context_ledger: List[ContextEntry] = []

    def add_content(self, entry: ContextEntry):
        """Record content added to context."""
        self.context_ledger.append(entry)

    def attribute_removal(self, tokens_removed: int) -> Dict[str, int]:
        """
        Walk backwards through ledger (oldest → newest),
        subtracting tokens until we've removed `tokens_removed`.
        """
        removed_by_source = {}
        remaining = tokens_removed

        for entry in self.context_ledger:
            if remaining <= 0:
                break

            tokens_from_entry = min(entry.tokens, remaining)
            source = entry.source  # e.g., "mcp__docs__semantic_search"

            removed_by_source[source] = removed_by_source.get(source, 0) + tokens_from_entry
            remaining -= tokens_from_entry

        return removed_by_source
```

---

## Implementation Details

### Platform-Specific Detection

**Gemini CLI** (explicit):
```python
def detect_gemini_compaction(event: dict) -> CompactionEvent | None:
    if event.get("type") == "gemini_cli.chat_compression":
        return CompactionEvent(
            timestamp=parse_timestamp(event["timestamp"]),
            tokens_before=event["tokens_before"],
            tokens_after=event["tokens_after"],
            source="gemini",
            reason="auto"
        )
    return None
```

**Claude Code** (inferred):
```python
def detect_claude_compaction(calls: List[Call]) -> List[CompactionEvent]:
    events = []
    prev_tokens = None

    for i, call in enumerate(calls):
        # Look for /compact command
        if call.tool_name == "compact":
            # Next call shows result
            if i + 1 < len(calls):
                events.append(CompactionEvent(
                    timestamp=call.timestamp,
                    tokens_before=prev_tokens or call.input_tokens,
                    tokens_after=calls[i + 1].input_tokens,
                    source="claude",
                    reason="manual"
                ))

        # Detect auto-compaction: significant drop in input tokens
        elif prev_tokens and call.input_tokens < prev_tokens * 0.7:
            events.append(CompactionEvent(
                timestamp=call.timestamp,
                tokens_before=prev_tokens,
                tokens_after=call.input_tokens,
                source="inferred",
                reason="auto"
            ))

        prev_tokens = call.input_tokens

    return events
```

**Codex CLI** (inferred):
```python
def detect_codex_compaction(calls: List[Call]) -> List[CompactionEvent]:
    events = []
    prev_tokens = None

    for call in calls:
        # GPT-5.1-Codex-Max has native compaction
        # Detect via token drops
        if prev_tokens and call.input_tokens < prev_tokens * 0.6:
            events.append(CompactionEvent(
                timestamp=call.timestamp,
                tokens_before=prev_tokens,
                tokens_after=call.input_tokens,
                source="codex",
                reason="auto"
            ))

        prev_tokens = call.input_tokens

    return events
```

### Compaction Analyzer

```python
class CompactionAnalyzer:
    def __init__(self, session: Session):
        self.session = session
        self.attributor = CompactionAttributor()

    def analyze(self) -> CompactionHealth:
        # Build context ledger from session
        self._build_ledger()

        # Detect compaction events
        events = self._detect_events()

        # Attribute removed content
        for event in events:
            event.removed_by_source = self.attributor.attribute_removal(
                event.tokens_trimmed
            )

        # Calculate health metrics
        return self._calculate_health(events)

    def _build_ledger(self):
        """Build chronological record of context additions."""
        for call in self.session.calls:
            # User prompts
            if call.type == "user_prompt":
                self.attributor.add_content(ContextEntry(
                    timestamp=call.timestamp,
                    source="user_prompt",
                    tokens=call.input_tokens,
                    category="prompts"
                ))

            # Tool results
            elif call.type == "tool_result":
                self.attributor.add_content(ContextEntry(
                    timestamp=call.timestamp,
                    source=f"{call.server}__{call.tool_name}",
                    tokens=call.output_tokens,
                    category="tool_outputs"
                ))

    def _calculate_health(self, events: List[CompactionEvent]) -> CompactionHealth:
        if not events:
            return CompactionHealth(
                total_events=0,
                total_tokens_trimmed=0,
                events_per_hour=0,
                avg_minutes_between_events=0,
                waste_ratio=0,
                compaction_cost=0,
                wasted_by_category={},
                wasted_by_server={},
                wasted_by_tool={}
            )

        total_trimmed = sum(e.tokens_trimmed for e in events)
        duration_hours = (
            self.session.ended_at - self.session.started_at
        ).total_seconds() / 3600

        # Aggregate waste by source
        wasted_by_server = {}
        wasted_by_tool = {}
        for event in events:
            for source, tokens in event.removed_by_source.items():
                server = source.split("__")[0] if "__" in source else "other"
                wasted_by_server[server] = wasted_by_server.get(server, 0) + tokens
                wasted_by_tool[source] = wasted_by_tool.get(source, 0) + tokens

        return CompactionHealth(
            total_events=len(events),
            total_tokens_trimmed=total_trimmed,
            events_per_hour=len(events) / duration_hours if duration_hours > 0 else 0,
            avg_minutes_between_events=self._avg_time_between(events),
            waste_ratio=total_trimmed / self.session.total_dynamic_tokens,
            compaction_cost=self._estimate_compaction_cost(events),
            wasted_by_category={},  # TODO: implement
            wasted_by_server=wasted_by_server,
            wasted_by_tool=wasted_by_tool
        )
```

---

## Report Output

```
Compaction Analysis
════════════════════════════════════════════════════════════════

Summary
────────────────────────────────────────────────────────────────
Compaction events:          3
Total tokens trimmed:       1,416,000
Events per hour:            1.2
Waste ratio:                42% (of dynamic tokens paid for, then lost)
Compaction overhead:        $0.18 (cost of compaction calls)

Per-Event Details
────────────────────────────────────────────────────────────────
#   Time      Before      After       Trimmed    Ratio   Trigger
────────────────────────────────────────────────────────────────
1   10:08     892,000     412,000     480,000    54%     auto
2   10:24     756,000     298,000     458,000    61%     auto
3   10:41     823,000     345,000     478,000    58%     auto

What Was Lost (Top Sources)
────────────────────────────────────────────────────────────────
mcp__docs__semantic_search      520,000 tokens (37%)
  → Produced 800k tokens, 65% later compacted
  → Consider: Use summarizing tool instead of raw pages

mcp__zen__thinkdeep             280,000 tokens (20%)
  → Large reasoning outputs getting aged out
  → Consider: Extract key insights before they're lost

Conversation history            340,000 tokens (24%)
  → Normal aging, no action needed

File reads (src/legacy/*)       180,000 tokens (13%)
  → Same files read multiple times, then compacted
  → Consider: Cache file summaries

Recommendations
────────────────────────────────────────────────────────────────
⚠️  High compaction frequency (1.2/hour)
    → Static context may be too large, leaving less room for dynamic
    → Current static: 82k tokens (41% of window)

⚠️  mcp__docs outputs dominate waste
    → 37% of all trimmed tokens came from this server
    → Consider: Use mcp__docs__summarize instead of full content

ℹ️  Consider /clear for topic changes
    → 3 compactions suggest continuous context pressure
    → Fresh start may be more efficient than incremental compaction
```

---

## CLI Interface

```bash
# Include compaction analysis
mcp-analyze report --compaction

# Detailed per-event breakdown
mcp-analyze report --compaction --detail

# Focus on specific server's waste
mcp-analyze report --compaction --server mcp__docs

# Export for analysis
mcp-analyze report --compaction --format json
```

---

## User Value

- **Cost awareness**: See tokens paid for then lost
- **Pattern identification**: Understand what triggers compaction
- **Tool optimization**: Know which tools produce "wasted" output
- **Session planning**: Data to decide when to clear vs continue

---

## Dependencies

- Platform-specific compaction detection
- Context ledger tracking
- Token attribution logic

---

## Success Metrics

- Detect 90%+ of compaction events
- Attribute 80%+ of removed tokens to sources
- Generate actionable recommendations

---

## References

- Claude Code `/compact` command behavior
- Codex CLI native compaction (GPT-5.1-Codex-Max)
- Gemini CLI `chat_compression` telemetry
