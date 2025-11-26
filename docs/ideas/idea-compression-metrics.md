# Idea: Context Saturation & Compression Metrics

**Status**: Proposed
**Priority**: Medium
**Phase**: v1.0+
**Related**: idea-compaction-tracking.md, idea-context-bloat-sources.md

---

## Summary

Track context saturation levels and compression events to help users understand when they're approaching context limits and how much content is being automatically compacted away.

---

## Problem Statement

Users often don't realize they're hitting context limits until:

- Performance degrades
- The model "forgets" earlier context
- Automatic compression kicks in

Tracking saturation and compression provides early warning and quantifies waste.

---

## Proposed Solution

### Key Metrics to Track

1. **Context Utilization %**: How full is the context window?
2. **Compression Events**: When did auto-compression fire?
3. **Tokens Trimmed**: How many tokens were compacted?
4. **Saturation Timeline**: How utilization changed over session

### Data Sources

**Gemini CLI** (explicit):
- `gemini_cli.chat_compression` with `tokens_before`, `tokens_after`
- Direct measurement of compression impact

**Claude Code** (inferred):
- Monitor for `/compact` commands
- Detect sudden drops in input tokens between calls
- Track when context nears window limit

**Codex CLI** (inferred):
- Watch for compaction-related log messages
- Detect input token drops after compaction
- GPT-5.1-Codex-Max has native compaction support

---

## Implementation Details

### Data Structures

```python
from dataclasses import dataclass
from typing import List, Optional
from datetime import datetime

@dataclass
class CompressionEvent:
    timestamp: datetime
    tokens_before: int
    tokens_after: int
    source: str  # auto | manual | gemini | claude | codex
    reason: Optional[str] = None

    @property
    def tokens_trimmed(self) -> int:
        return self.tokens_before - self.tokens_after

    @property
    def trim_ratio(self) -> float:
        if self.tokens_before == 0:
            return 0.0
        return self.tokens_trimmed / self.tokens_before


@dataclass
class SaturationMetrics:
    context_window_size: int
    peak_utilization: int
    peak_utilization_percent: float
    compression_events: List[CompressionEvent]
    utilization_timeline: List[tuple]  # (timestamp, tokens, percent)

    @property
    def total_tokens_trimmed(self) -> int:
        return sum(e.tokens_trimmed for e in self.compression_events)

    @property
    def compression_count(self) -> int:
        return len(self.compression_events)

    @property
    def avg_trim_ratio(self) -> float:
        if not self.compression_events:
            return 0.0
        return sum(e.trim_ratio for e in self.compression_events) / len(self.compression_events)

    @property
    def time_above_80_percent(self) -> int:
        """Minutes spent above 80% utilization."""
        # Calculate from timeline
        high_util_points = [t for t in self.utilization_timeline if t[2] > 80]
        # Approximate duration based on point count
        return len(high_util_points)
```

### Saturation Analyzer

```python
class SaturationAnalyzer:
    WINDOW_SIZES = {
        "claude-sonnet-4-5": 200_000,
        "gpt-5-codex": 200_000,
        "gemini-2.5-pro": 1_000_000,
    }

    def __init__(self, session: Session):
        self.session = session
        self.window_size = self._detect_window_size()

    def analyze(self) -> SaturationMetrics:
        timeline = self._build_timeline()
        compressions = self._detect_compressions()
        peak = max(t[1] for t in timeline) if timeline else 0

        return SaturationMetrics(
            context_window_size=self.window_size,
            peak_utilization=peak,
            peak_utilization_percent=(peak / self.window_size) * 100,
            compression_events=compressions,
            utilization_timeline=timeline
        )

    def _detect_window_size(self) -> int:
        model = self.session.model or "claude-sonnet-4-5"
        return self.WINDOW_SIZES.get(model, 200_000)

    def _build_timeline(self) -> List[tuple]:
        """Build timeline of context utilization."""
        timeline = []
        for call in self.session.calls:
            tokens = call.input_tokens or 0
            percent = (tokens / self.window_size) * 100
            timeline.append((call.timestamp, tokens, percent))
        return timeline

    def _detect_compressions(self) -> List[CompressionEvent]:
        """Detect compression events from telemetry or inference."""
        compressions = []

        # For Gemini: direct from telemetry
        for event in self.session.raw_events:
            if event.get("type") == "gemini_cli.chat_compression":
                compressions.append(CompressionEvent(
                    timestamp=event["timestamp"],
                    tokens_before=event["tokens_before"],
                    tokens_after=event["tokens_after"],
                    source="gemini"
                ))

        # For Claude/Codex: infer from token drops
        prev_tokens = None
        for call in self.session.calls:
            if prev_tokens and call.input_tokens:
                # Significant drop (>30%) suggests compression
                if call.input_tokens < prev_tokens * 0.7:
                    compressions.append(CompressionEvent(
                        timestamp=call.timestamp,
                        tokens_before=prev_tokens,
                        tokens_after=call.input_tokens,
                        source="inferred"
                    ))
            prev_tokens = call.input_tokens

        return compressions
```

### Warning Thresholds

```python
class SaturationWarnings:
    THRESHOLDS = {
        "approaching": 70,   # 70% utilization
        "high": 85,          # 85% utilization
        "critical": 95,      # 95% utilization
    }

    @classmethod
    def check(cls, metrics: SaturationMetrics) -> List[str]:
        warnings = []

        if metrics.peak_utilization_percent >= cls.THRESHOLDS["critical"]:
            warnings.append(
                f"⚠️  CRITICAL: Context hit {metrics.peak_utilization_percent:.1f}% "
                f"({metrics.peak_utilization:,} / {metrics.context_window_size:,} tokens)"
            )
        elif metrics.peak_utilization_percent >= cls.THRESHOLDS["high"]:
            warnings.append(
                f"⚠️  HIGH: Context reached {metrics.peak_utilization_percent:.1f}% utilization"
            )
        elif metrics.peak_utilization_percent >= cls.THRESHOLDS["approaching"]:
            warnings.append(
                f"ℹ️  Context approached {metrics.peak_utilization_percent:.1f}% utilization"
            )

        if metrics.compression_count > 3:
            warnings.append(
                f"⚠️  Compressed {metrics.compression_count} times - "
                f"consider shorter sessions or fewer tools"
            )

        if metrics.total_tokens_trimmed > 100_000:
            warnings.append(
                f"⚠️  {metrics.total_tokens_trimmed:,} tokens trimmed - "
                f"significant context loss"
            )

        return warnings
```

---

## Report Output

```
Context Saturation Analysis
════════════════════════════════════════════════════════════════

Window Configuration
────────────────────────────────────────────────────────────────
Model:              gemini-2.5-pro
Context window:     1,000,000 tokens
Peak utilization:   847,000 tokens (84.7%)

⚠️  HIGH: Context reached 84.7% utilization

Compression Events
────────────────────────────────────────────────────────────────
Time        Before      After       Trimmed     Ratio
────────────────────────────────────────────────────────────────
10:08:23    892,000     412,000     480,000     54%
10:24:15    756,000     298,000     458,000     61%
10:41:02    823,000     345,000     478,000     58%
────────────────────────────────────────────────────────────────
Total:                            1,416,000 tokens trimmed

Compression Summary
────────────────────────────────────────────────────────────────
Events:                 3
Total trimmed:          1,416,000 tokens
Avg trim ratio:         57%
Est. cost of trimmed:   $4.25 (tokens we paid for, then lost)

Utilization Timeline
────────────────────────────────────────────────────────────────
10:00  ░░░░░░░░░░░░░░░░░░░░  12%   Session start
10:05  ████████░░░░░░░░░░░░  38%   First big file read
10:08  █████████████████░░░  84%   Multiple tool calls
       ↓ COMPRESSION ↓
10:09  ████████░░░░░░░░░░░░  41%   After compression
10:15  ████████████░░░░░░░░  58%   Building back up
10:24  ███████████████░░░░░  76%   Approaching limit
       ↓ COMPRESSION ↓
10:25  ██████░░░░░░░░░░░░░░  30%   After compression
...

Recommendations
────────────────────────────────────────────────────────────────
→ Session hit compression 3 times - context lost information each time
→ Consider using `/clear` to start fresh for new topics
→ Large tool outputs (mcp__docs) are major contributors - use summaries
→ File reads account for 45% of context - consider caching
```

---

## CLI Flags

```bash
# Include saturation analysis
mcp-analyze report --saturation

# Show compression timeline
mcp-analyze report --saturation --timeline

# Warn when approaching threshold
mcp-analyze report --saturation --warn-at 70

# Export timeline data
mcp-analyze report --saturation --format json > saturation.json
```

---

## User Value

- **Early warning**: Know when approaching context limits
- **Waste visibility**: See tokens paid for then lost
- **Session planning**: Data to decide when to clear/restart
- **Tool optimization**: Identify tools causing saturation

---

## Dependencies

- Platform telemetry (compression events)
- Model context window sizes
- Token tracking per call (existing)

---

## Success Metrics

- Saturation metrics available for all sessions
- Compression events detected within 5 seconds
- Users warned before hitting 90% utilization

---

## References

- Gemini CLI `chat_compression` telemetry
- Claude Code `/compact` command behavior
- Codex CLI native compaction (GPT-5.1-Codex-Max)
