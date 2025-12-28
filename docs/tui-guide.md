# TUI Navigation Guide

Complete guide to the Token Audit Terminal User Interface (v1.0.3).

---

## Table of Contents

- [Quick Start](#quick-start)
- [Views Overview](#views-overview)
- [Keybinding Reference](#keybinding-reference)
- [Workflow Diagram](#workflow-diagram)
- [Modal System](#modal-system)
- [Date Filtering](#date-filtering)
- [Export Formats](#export-formats)
- [Themes](#themes)

---

## Quick Start

```bash
# Launch the TUI
token-audit ui

# Start in a specific view
token-audit ui --view analytics

# Use a specific theme
token-audit ui --theme mocha
```

Navigate with `j/k` or arrow keys, press `Enter` to select, `1-7` to switch views, `q` to quit.

---

## Views Overview

The TUI provides 7 integrated views accessible via number keys:

### 1. Dashboard (key `1`)

The default landing page showing today's summary:

```
Token Audit v1.0.3                               [Last 7d] Last refresh: 2m ago
================================================================================

Today's Summary                    │  Weekly Trends
--------------------------------   │  --------------------------------
Sessions: 5                        │  Mon  ████████████ 45K
Tokens: 125,000                    │  Tue  ██████████   38K
Cost: $0.42                        │  Wed  ████████████████ 62K
                                   │  Thu  ██████████   40K
Top Smells                         │  Fri  ████████     32K
--------------------------------   │
1. CHATTY (45%)                    │  Recent Sessions
2. REDUNDANT_CALLS (30%)           │  --------------------------------
3. HIGH_VARIANCE (25%)             │  12:30 token-audit   $0.12
                                   │  11:15 wp-navigator  $0.08
[1] Dashboard  [2] Sessions  [3] Recommendations  [4] Live  ...
```

### 2. Sessions (key `2`)

Browse all sessions with filtering, search, and delete:

```
Sessions (45)                                    [claude-code] [Last 7d]
================================================================================
Date       Project           Tokens    Cost    Smells
────────────────────────────────────────────────────────────────────────────────
> 12:30   token-audit        45,231   $0.15   CHATTY, HIGH_VARIANCE
  11:15   wp-navigator       28,450   $0.08   LOW_CACHE_HIT
  10:00   illustrations      92,100   $0.31   BURST_PATTERN
  09:30   token-audit        15,200   $0.05   -
  08:45   brand-copilot      67,300   $0.22   CHATTY

[j/k] Navigate  [Enter] View  [/] Search  [d] Date  [Delete] Remove
```

### 3. Recommendations (key `3`)

Actionable optimization suggestions grouped by confidence:

```
Recommendations
================================================================================

High Confidence (3)
────────────────────────────────────────────────────────────────────────────────
> REMOVE_UNUSED_SERVER
  Server 'unused-mcp' has 0 calls across 5 sessions
  Impact: ~450 tokens saved per session

  ENABLE_CACHING
  Tool 'mcp__search__web' called 15x with same params
  Impact: Could cache 80% of calls

Medium Confidence (2)
────────────────────────────────────────────────────────────────────────────────
  BATCH_OPERATIONS
  25 sequential file reads could be batched
```

### 4. Live (key `4`)

Real-time session monitoring with burn rate:

```
Live Session Monitor                              Active: token-audit
================================================================================

Token Usage                        │  MCP Servers (4 servers, 8 calls)
--------------------------------   │  --------------------------------
Input:       45,231                │  zen ............. 5 calls
Output:      12,345                │  brave-search .... 2 calls
Cached:     125,000                │  backlog ......... 1 call
                                   │
Rate: 15.2K tokens/min             │  Cost: $0.42
                                   │  Cache Efficiency: 68.4%

Recent Tool Calls
────────────────────────────────────────────────────────────────────────────────
12:30:45  mcp__zen__chat          1,234 tokens
12:30:42  Read                      456 tokens
12:30:40  mcp__zen__thinkdeep     2,100 tokens
```

### 5. Analytics (key `5`)

Usage trends by period with project grouping:

```
Analytics                                         [Daily] [Group by Project]
================================================================================

Period      Sessions   Tokens      Cost     Trend    Smells
────────────────────────────────────────────────────────────────────────────────
Dec 27      5          125,000     $0.42    ▲ +15%   3
Dec 26      8          180,000     $0.60    → 0%     5
Dec 25      3          45,000      $0.15    ▼ -25%   1
Dec 24      6          150,000     $0.50    ▲ +10%   4

Top Models                         │  Project Breakdown
--------------------------------   │  --------------------------------
claude-3-5-sonnet   60%            │  token-audit    45%  $1.50
claude-3-5-haiku    25%            │  wp-navigator   30%  $1.00
claude-3-opus       15%            │  illustrations  25%  $0.83

[p] Period: Daily/Weekly/Monthly  [g] Toggle project grouping
```

### 6. Smell Trends (key `6`)

Pattern frequency over time with severity indicators:

```
Smell Trends                                     [Last 30 days]
================================================================================

Pattern                 Frequency   Trend    Severity   Top Tool
────────────────────────────────────────────────────────────────────────────────
CHATTY                  45%         ▲        ●●○        mcp__zen__chat
REDUNDANT_CALLS         30%         →        ●●○        mcp__search__web
HIGH_VARIANCE           25%         ▼        ●○○        mcp__jina__read
LOW_CACHE_HIT           20%         ▲        ●●●        mcp__context7__search
BURST_PATTERN           15%         →        ●●○        mcp__brave__search

Summary
────────────────────────────────────────────────────────────────────────────────
Total sessions: 45 | Sessions with smells: 32 (71%) | Unique patterns: 8

[7/14/30/90] Change analysis period
```

### 7. Pinned Servers (key `7`)

Frequently-used MCP servers with usage stats:

```
Pinned Servers
================================================================================

Server          Source      Calls    Tokens    Cost     Last Used
────────────────────────────────────────────────────────────────────────────────
> zen           explicit    150      450,000   $1.50    Today
  brave-search  auto        45       135,000   $0.45    Today
  backlog       auto        30       90,000    $0.30    Yesterday
  jina          explicit    25       75,000    $0.25    2 days ago

Legend: explicit = manually pinned | auto = high-frequency detection

[Enter] View server details  [p] Pin/Unpin  [r] Refresh
```

---

## Keybinding Reference

### Global Keys

| Key | Action | Available |
|-----|--------|-----------|
| `1-7` | Switch to view | All views |
| `q` | Quit | All views |
| `Esc` | Back / Close modal | All views |
| `?` | Show help | All views |
| `r` | Refresh data | All views |
| `:` | Command palette | All views |

### Navigation

| Key | Action |
|-----|--------|
| `j` / `↓` | Move down |
| `k` / `↑` | Move up |
| `Enter` | Select / View details |
| `g` | Go to top |
| `G` | Go to bottom |

### Filtering & Sorting

| Key | Action | Views |
|-----|--------|-------|
| `/` | Search | Sessions |
| `f` | Cycle platform filter | Sessions, Analytics |
| `s` | Cycle sort order | Sessions |
| `d` | Open date filter modal | All views |
| `p` | Toggle period (D/W/M) | Analytics |
| `g` | Toggle project grouping | Analytics |

### Actions

| Key | Action | Views |
|-----|--------|-------|
| `e` | Export as CSV | All views |
| `x` | Export as JSON | All views |
| `a` | Export for AI analysis | All views |
| `Delete` | Delete session | Sessions |
| `p` | Pin/Unpin | Sessions, Pinned Servers |

### Modal Keys

| Key | Action | Modal Type |
|-----|--------|------------|
| `j/k`, `↑/↓` | Navigate options | Select |
| `1-9` | Quick select option | Select |
| `Enter` | Confirm selection | All |
| `y` | Yes / Confirm | Confirm |
| `n` | No / Cancel | Confirm |
| `h/l`, `←/→` | Toggle Yes/No | Confirm |
| `Backspace` | Delete character | Input |
| `Ctrl+U` | Clear input | Input |
| `Esc` | Cancel / Close | All |

---

## Workflow Diagram

```
                              ┌──────────────────┐
                              │    token-audit   │
                              │        ui        │
                              └────────┬─────────┘
                                       │
                    ┌──────────────────┼──────────────────┐
                    │                  │                  │
              ┌─────▼─────┐      ┌─────▼─────┐      ┌─────▼─────┐
              │ Dashboard │◀────▶│ Sessions  │◀────▶│   Live    │
              │    (1)    │      │    (2)    │      │    (4)    │
              └─────┬─────┘      └─────┬─────┘      └───────────┘
                    │                  │
                    │            ┌─────▼─────┐
                    │            │  Session  │
                    │            │  Details  │
                    │            └─────┬─────┘
                    │                  │
              ┌─────▼─────┐            │         ┌───────────────┐
              │Recommend- │◀───────────┴────────▶│   Analytics   │
              │ations (3) │                      │      (5)      │
              └───────────┘                      └───────────────┘
                                                        │
                                         ┌──────────────┼──────────────┐
                                         │              │              │
                                   ┌─────▼─────┐  ┌─────▼─────┐  ┌─────▼─────┐
                                   │   Smell   │  │  Pinned   │  │  Export   │
                                   │ Trends(6) │  │Servers(7) │  │   Modal   │
                                   └───────────┘  └───────────┘  └───────────┘
```

### Typical Workflows

**Daily check:**
1. Open TUI → Dashboard (key `1`)
2. Review today's summary and smells
3. If issues found → Recommendations (key `3`)
4. Take action based on suggestions

**Session analysis:**
1. Sessions view (key `2`)
2. Filter by date (key `d`) → Last 7 days
3. Navigate to session → Enter
4. Export for AI analysis (key `a`)

**Cost tracking:**
1. Analytics view (key `5`)
2. Set period (key `p`) → Monthly
3. Toggle project grouping (key `g`)
4. Export as CSV (key `e`) for spreadsheet

---

## Modal System

### SelectModal

Used for choosing from a list of options:

```
┌─────────────────────────────────────┐
│  Select Platform                    │
│─────────────────────────────────────│
│  > claude-code                      │
│    codex-cli                        │
│    gemini-cli                       │
│    All platforms                    │
│─────────────────────────────────────│
│  [j/k] Navigate  [Enter] Select     │
│  [1-4] Quick select  [Esc] Cancel   │
└─────────────────────────────────────┘
```

### ConfirmModal

Used for yes/no confirmations:

```
┌─────────────────────────────────────┐
│  Delete Session?                    │
│─────────────────────────────────────│
│  Session: token-audit               │
│  Date: 2025-12-27 12:30             │
│  Tokens: 45,231                     │
│                                     │
│  This action cannot be undone.      │
│─────────────────────────────────────│
│     [ Cancel ]     [ Delete ]       │
│─────────────────────────────────────│
│  [y] Yes  [n] No  [Enter] Confirm   │
└─────────────────────────────────────┘
```

### InputModal

Used for text input with validation:

```
┌─────────────────────────────────────┐
│  Enter Date Range                   │
│─────────────────────────────────────│
│  Format: YYYY-MM-DD                 │
│                                     │
│  Start: [2025-12-20          ]      │
│                                     │
│  ⚠ Invalid date format              │
│─────────────────────────────────────│
│  [Enter] Submit  [Esc] Cancel       │
└─────────────────────────────────────┘
```

---

## Date Filtering

Press `d` to open the date filter modal. Use number keys for instant selection:

| Key | Preset | Date Range |
|-----|--------|------------|
| `1` | Today | Start of today → Now |
| `2` | Yesterday | Yesterday 00:00 → 23:59 |
| `3` | Last 7 days | 7 days ago → Now |
| `4` | Last 14 days | 14 days ago → Now |
| `5` | Last 30 days | 30 days ago → Now |
| `6` | Last 60 days | 60 days ago → Now |
| `7` | This month | First of month → Now |
| `8` | Last month | First of prev month → End of prev month |
| `0` | All time | Clear filter |

Active filter displays as badge: `[Last 7d]` or `[Dec 01-Dec 15]`

---

## Export Formats

### CSV Export (key `e`)

Standard comma-separated values:

```csv
session_id,date,platform,project,tokens,cost,smells
abc123,2025-12-27T12:30:00,claude-code,token-audit,45231,0.15,"CHATTY,HIGH_VARIANCE"
def456,2025-12-27T11:15:00,claude-code,wp-navigator,28450,0.08,LOW_CACHE_HIT
```

### JSON Export (key `x`)

Full structured data with metadata:

```json
{
  "view": "sessions",
  "exported_at": "2025-12-27T14:00:00Z",
  "filter_applied": "Last 7 days",
  "record_count": 45,
  "records": [
    {
      "session_id": "abc123",
      "date": "2025-12-27T12:30:00",
      "platform": "claude-code",
      "project": "token-audit",
      "tokens": 45231,
      "cost": 0.15,
      "smells": ["CHATTY", "HIGH_VARIANCE"]
    }
  ]
}
```

### AI Export (key `a`)

Markdown format optimized for LLM analysis:

```markdown
# Token Audit Analysis

## View: Sessions
**Date Range:** Last 7 days
**Total Sessions:** 45
**Total Cost:** $3.25

## Summary
- Average session: 15,000 tokens, $0.07
- Most active project: token-audit (45%)
- Top smell: CHATTY (45% of sessions)

## Sessions

| Date | Project | Tokens | Cost | Smells |
|------|---------|--------|------|--------|
| Dec 27 12:30 | token-audit | 45,231 | $0.15 | CHATTY, HIGH_VARIANCE |
| Dec 27 11:15 | wp-navigator | 28,450 | $0.08 | LOW_CACHE_HIT |

## Recommendations Requested

1. Identify inefficiencies
2. Suggest optimizations
3. Prioritize by impact
```

---

## Themes

Select theme with `--theme` flag:

```bash
token-audit ui --theme mocha
```

| Theme | Description | Best For |
|-------|-------------|----------|
| `auto` | Detect terminal preference | Default |
| `dark` | Standard dark theme | Dark terminals |
| `light` | Standard light theme | Light terminals |
| `mocha` | Catppuccin Mocha (warm dark) | Aesthetic preference |
| `latte` | Catppuccin Latte (warm light) | Aesthetic preference |
| `hc-dark` | High contrast dark | Accessibility (WCAG AAA) |
| `hc-light` | High contrast light | Accessibility (WCAG AAA) |

---

*For more details on specific features, see [Features Reference](features.md). For troubleshooting, see [Troubleshooting](troubleshooting.md).*
