# MCP Audit Ideas - Assessment & Recommendations

**Created**: 2025-11-26
**Purpose**: Centralized assessment of all idea proposals against the Phase 2-5 roadmap

---

## Executive Summary

Assessed **13 ideas** against the MCP Audit roadmap (Phases 2-5, Weeks 4-14+).

**Recommendations**:
- **4 ideas**: Implement in Phase 3 (Weeks 7-12) - Core value enhancers
- **4 ideas**: Implement in Phase 5+ - Nice-to-have, post-v1.0
- **3 ideas**: Partially implement in Phase 3, full in Phase 5
- **2 ideas**: Defer or deprioritize - Low ROI or scope creep risk

---

## Rating System

| Rating | Meaning |
|--------|---------|
| **GREAT** | High-value, aligns perfectly with roadmap, implement soon |
| **GOOD** | Solid value, fits roadmap, implement when capacity allows |
| **CONDITIONAL** | Value depends on prerequisites or user demand |
| **DEFER** | Nice-to-have, doesn't fit current roadmap priorities |

---

## Idea Assessments

### 1. Context Bloat Sources Analysis (task-14)

**Rating**: **GREAT** - Core differentiator

**Roadmap Fit**: Phase 3 (Week 11) - Enhanced Analysis Features

**Assessment**:
This idea directly addresses MCP Audit's core value proposition. Scott Spence's analysis (14,214 tokens for 20 tools = 41% context) demonstrates the problem is real and measurable. Cross-platform bloat visibility is exactly what differentiates MCP Audit from generic token counters.

**Why Implement**:
- Solves the "where is my context going?" question users are asking
- Enables data-driven MCP server optimization
- Platform-specific recommendations add concrete value
- Aligns with "Day 1 Value Workflows" (Week 6) goal

**Implementation Recommendations**:
1. Start with Claude Code (best telemetry) in Week 7-8
2. Add shared bloat patterns (system, instructions, MCP metadata, dynamic)
3. Platform-specific analysis after Gemini/Codex adapters mature (Week 9-10)
4. Auto-generate recommendations based on thresholds

**Dependencies**: Context Slices Data Model (task-15), Starting Context Tracking (task-25)

---

### 2. Context Slices Data Model (task-15)

**Rating**: **GREAT** - Foundation for multiple features

**Roadmap Fit**: Phase 3 (Week 7) - Schema Enhancement

**Assessment**:
This is a prerequisite for several high-value ideas. The `token_breakdown` schema extension enables precise attribution, which powers bloat analysis, context categories, and compaction tracking. Gemini CLI's telemetry already provides much of this data directly.

**Why Implement**:
- Enables 5+ dependent features (bloat, categories, compaction, cache, file tracking)
- Minimal schema change (additive, backward compatible)
- Gemini CLI data sources make this low-risk to implement
- Aligns with Data Contract (Week 3) backward compatibility guarantees

**Implementation Recommendations**:
1. Add `token_breakdown: Optional[TokenBreakdown]` to Call schema in Week 7
2. Populate from Gemini CLI directly (most complete data)
3. Use heuristics for Claude Code and Codex CLI
4. Leave `None` for fields not available (don't guess)

**Dependencies**: None (foundational)

---

### 3. Static MCP Server Footprint Analyzer (task-16)

**Rating**: **GREAT** - Quick win, high visibility

**Roadmap Fit**: Phase 2 (Week 6) or Phase 3 (Week 7)

**Assessment**:
This is a quick win that can ship early. The existing `analyze-mcp-efficiency.py` has most of the logic. Promoting to `mcp-analyze footprint` subcommand provides immediate "Day 1 Value" - users can see their floor cost before any session.

**Why Implement**:
- ~50% of the code already exists
- Answers "what's my starting overhead?" instantly
- Complements session tracking with pre-session analysis
- Low effort, high visibility

**Implementation Recommendations**:
1. Implement in Week 6 as part of "Day 1 Value Workflows"
2. Add tiktoken dependency for accurate tokenization
3. Cache results in `~/.mcp-audit/footprint-cache/`
4. Auto-include summary in session reports

**Dependencies**: tiktoken library

---

### 4. Context Categories in Reports (task-17)

**Rating**: **GREAT** - Standard feature for v1.0

**Roadmap Fit**: Phase 3 (Week 11) - Enhanced Reports

**Assessment**:
Standardized categories (user_prompts, tool_outputs, mcp_metadata, etc.) make reports actionable. Users can immediately see "45% of context is tool outputs" and know where to optimize. ASCII bar charts add visual appeal without requiring a web UI.

**Why Implement**:
- Makes reports immediately understandable
- Cross-platform consistency is key differentiator
- ASCII visualization works in terminal (no web UI needed)
- Aligns with `--format` flags already planned for Week 6

**Implementation Recommendations**:
1. Implement in Week 11 alongside Programmatic API
2. Use 7 standard categories across all platforms
3. Show percentages and absolute tokens
4. Add `--context-breakdown` flag to report command

**Dependencies**: Context Slices Data Model (task-15)

---

### 5. What-If Simulations (task-18)

**Rating**: **GOOD** - Valuable but not essential for v1.0

**Roadmap Fit**: Phase 5+ (Post-v1.0)

**Assessment**:
Simulations are valuable for MCP optimization decisions, but they're a "power user" feature. The core v1.0 value is measurement and visibility; simulations are optimization guidance. Risk of scope creep if included in Phase 3.

**Why Defer**:
- Requires complete footprint + session data first
- "Nice to have" not "must have" for v1.0
- Accuracy requirements (within 10%) need extensive validation
- Can be added post-v1.0 based on user demand

**Implementation Recommendations (Phase 5)**:
1. Start with `--what-if disable=server` (simplest)
2. Add `trim-descriptions` simulation second
3. Use cached footprint data for static calculations
4. Keep accuracy expectations modest (±20% initially)

**Dependencies**: Static Footprint Analyzer (task-16), Context Categories (task-17)

---

### 6. Cache Efficiency Drilldown (task-19)

**Rating**: **GOOD** - Aligns with existing cache tracking

**Roadmap Fit**: Phase 3 (Week 11) - Enhanced Analysis

**Assessment**:
MCP Audit already tracks cache tokens. Drilling down to per-model, per-server, per-tool cache rates adds clear value. The "potential savings" calculation is compelling for cost-conscious users.

**Why Implement**:
- Builds on existing cache_read_tokens tracking
- Per-tool cache analysis identifies optimization targets
- "Cost saved" messaging resonates with users
- Moderate complexity, fits in Week 11

**Implementation Recommendations**:
1. Add per-server cache aggregation in Week 11
2. Show "best performers" and "worst performers" tables
3. Calculate potential savings if low-cache tools matched average
4. Add `--cache-analysis` flag to report command

**Dependencies**: Per-server session data (existing)

---

### 7. Per-File Context Usage Tracking (task-20)

**Rating**: **CONDITIONAL** - Depends on telemetry quality

**Roadmap Fit**: Phase 5+ (Post-v1.0)

**Assessment**:
File tracking is valuable but depends heavily on telemetry. Gemini CLI has explicit `file_operation` events; Claude Code and Codex have less detail. Without consistent cross-platform data, this feature risks being Gemini-only.

**Why Conditional**:
- Gemini CLI: Excellent data (`file_operation` events)
- Claude Code: Limited (must infer from Read tool calls)
- Codex CLI: Moderate (file paths in tool results)
- Risk of inconsistent experience across platforms

**Implementation Recommendations (Phase 5)**:
1. Ship as "experimental" for Gemini CLI first
2. Add Claude Code/Codex support when telemetry improves
3. Focus on "files read >3 times" detection (universal)
4. Keep expectations modest for non-Gemini platforms

**Dependencies**: Platform telemetry improvements

---

### 8. Context Saturation & Compression Metrics (task-21)

**Rating**: **GOOD** - Strong fit for Phase 3

**Roadmap Fit**: Phase 3 (Week 9-10) alongside Gemini/Ollama work

**Assessment**:
Saturation tracking directly addresses "why did the model forget?" questions. Gemini CLI's `chat_compression` events make this easy to implement. Inference-based detection for Claude/Codex adds cross-platform value.

**Why Implement**:
- Gemini CLI provides explicit compression events
- Claude Code `/compact` can be detected
- Warning thresholds (70%, 85%, 95%) add proactive value
- "Tokens paid for then lost" messaging is compelling

**Implementation Recommendations**:
1. Implement Gemini compression tracking in Week 9-10
2. Add inference-based detection for Claude/Codex (>30% token drop)
3. Show utilization timeline in reports
4. Add warning thresholds with recommendations

**Dependencies**: None for basic implementation

---

### 9. Cross-Platform Comparison (task-22)

**Rating**: **CONDITIONAL** - Needs 3+ platforms first

**Roadmap Fit**: Phase 3 (Week 12) or Phase 5

**Assessment**:
Cross-platform comparison is compelling but requires multiple platforms to be stable. With 2 platforms (Claude + Codex), comparison is limited. With Gemini CLI added (Phase 3), comparison becomes meaningful.

**Why Conditional**:
- Most valuable with 3+ platforms
- Gemini CLI kill criteria (Week 8) could reduce this to 2 platforms
- Normalization (tokens/hour) requires accurate duration tracking
- Risk of "apples to oranges" comparisons confusing users

**Implementation Recommendations**:
1. Implement after Gemini CLI integration (Week 10+)
2. Start with cost comparison (most concrete)
3. Add normalized metrics (tokens/hour) second
4. Include caveats about different context windows

**Dependencies**: Gemini CLI integration (Phase 3), Duration tracking

---

### 10. MCP Authoring Hints (task-23)

**Rating**: **GOOD** - High value for MCP ecosystem

**Roadmap Fit**: Phase 5+ (Post-v1.0)

**Assessment**:
Authoring hints help MCP server authors optimize their servers, which benefits all users. The 60% reduction case study is compelling. However, this is a "give back to ecosystem" feature, not core user value.

**Why Defer to Phase 5**:
- Server authors are a secondary audience (primary: AI developers)
- Requires robust footprint analysis first
- "Lint-style" suggestions need careful UX design
- Risk of false positives annoying users

**Implementation Recommendations (Phase 5)**:
1. Start with "similar tools" detection (highest impact)
2. Add "verbose description" warnings second
3. Keep recommendations actionable and specific
4. Consider separate `mcp-analyze hints` subcommand

**Dependencies**: Static Footprint Analyzer (task-16), Usage tracking

---

### 11. Compaction Tracking (task-24)

**Rating**: **GOOD** - Complements Saturation Metrics

**Roadmap Fit**: Phase 3 (Week 11) with Saturation Metrics

**Assessment**:
Compaction tracking extends saturation metrics to answer "what was lost?" The LRU attribution model is elegant. However, accuracy depends on maintaining a context ledger throughout the session.

**Why Implement**:
- Directly answers "what got thrown away?"
- Quantifies "wasted" tokens (paid for, then lost)
- Per-server waste attribution guides optimization
- Gemini CLI has explicit data; others need inference

**Implementation Recommendations**:
1. Implement alongside Saturation Metrics (Week 11)
2. Start with Gemini CLI (explicit events)
3. Use LRU model for Claude/Codex attribution
4. Show "wasted by server" breakdown in reports

**Dependencies**: Context Saturation Metrics (task-21)

---

### 12. Starting Context Tracking (task-25)

**Rating**: **GREAT** - Foundational for multiple features

**Roadmap Fit**: Phase 3 (Week 7) - Early implementation

**Assessment**:
Starting context tracking answers "what's my floor cost?" before any work. This is foundational for bloat analysis, saturation warnings, and what-if simulations. Relatively simple to implement with existing footprint analyzer.

**Why Implement**:
- Answers most basic question: "what's already in context?"
- Enables "available tokens" calculation per session
- Trend tracking shows configuration drift over time
- Low complexity, high visibility

**Implementation Recommendations**:
1. Implement in Week 7 alongside Context Slices
2. Detect CLAUDE.md, AGENTS.md, GEMINI.md automatically
3. Combine with footprint analyzer for MCP metadata
4. Show in session header: "31,500 tokens static (15.8%)"

**Dependencies**: Static Footprint Analyzer (task-16)

---

### 13. Focus Server Mode (task-26)

**Rating**: **DEFER** - Low priority filtering feature

**Roadmap Fit**: Phase 5+ (Post-v1.0)

**Assessment**:
Focus mode is a presentation/filtering enhancement, not new functionality. The same data is available in aggregate reports. Useful for server authors but not essential for v1.0.

**Why Defer**:
- Pure filtering, no new data collection
- Server authors are secondary audience
- Risk of feature creep in CLI flags
- Can be added post-v1.0 based on demand

**Implementation Recommendations (Phase 5)**:
1. Add `--focus-server` flag to existing report command
2. Add `--exclude-server` for inverse filtering
3. Keep report format consistent with standard reports
4. Consider as part of broader "filtering" feature set

**Dependencies**: None (filtering only)

---

## Implementation Priority Matrix

### Tier 1: Implement in Phase 3 (Weeks 7-11) - Core Value

| Idea | Week | Rationale |
|------|------|-----------|
| **Context Slices Data Model** (task-15) | 7 | Foundation for 5+ features |
| **Starting Context Tracking** (task-25) | 7 | Answers "floor cost" question |
| **Static MCP Footprint Analyzer** (task-16) | 6-7 | Quick win, 50% code exists |
| **Context Bloat Sources Analysis** (task-14) | 11 | Core differentiator |
| **Context Categories in Reports** (task-17) | 11 | Makes reports actionable |
| **Cache Efficiency Drilldown** (task-19) | 11 | Builds on existing tracking |
| **Context Saturation Metrics** (task-21) | 9-10 | Proactive warnings |
| **Compaction Tracking** (task-24) | 11 | Complements saturation |

### Tier 2: Implement in Phase 5+ - Post-v1.0 Enhancements

| Idea | Rationale |
|------|-----------|
| **What-If Simulations** (task-18) | Power user feature, not essential for v1.0 |
| **Cross-Platform Comparison** (task-22) | Needs 3+ stable platforms first |
| **MCP Authoring Hints** (task-23) | Secondary audience (server authors) |
| **Per-File Context Usage** (task-20) | Telemetry-dependent, Gemini-only initially |
| **Focus Server Mode** (task-26) | Pure filtering, can add later |

---

## Dependency Graph

```
Context Slices Data Model (task-15)
├── Context Bloat Sources Analysis (task-14)
├── Context Categories in Reports (task-17)
├── Per-File Context Usage (task-20)
└── Compaction Tracking (task-24)

Static MCP Footprint Analyzer (task-16)
├── Starting Context Tracking (task-25)
├── What-If Simulations (task-18)
└── MCP Authoring Hints (task-23)

Context Saturation Metrics (task-21)
└── Compaction Tracking (task-24)

Platform Adapters (existing)
├── Cross-Platform Comparison (task-22) [needs 3+ platforms]
└── Per-File Context Usage (task-20) [Gemini-first]
```

---

## Risk Assessment

### Implementation Risks

| Risk | Mitigation |
|------|------------|
| **Scope creep** from 13 ideas | Strict tier enforcement, defer Tier 2 |
| **Dependencies creating delays** | Implement Context Slices first (Week 7) |
| **Cross-platform inconsistency** | Accept "best effort" for non-Gemini platforms |
| **Solo maintainer burden** | Focus on Tier 1 only for v1.0 |

### Quality Risks

| Risk | Mitigation |
|------|------------|
| **Inaccurate token attribution** | Use "unknown" category, don't guess |
| **False positive hints** | Start conservative, tune thresholds |
| **Compression detection errors** | Use >30% drop threshold, accept some misses |

---

## Recommended Phase 3 Timeline Update

Based on this assessment, suggest updating Phase 3 (Weeks 7-12):

**Week 7**: Context Slices Data Model + Starting Context Tracking
**Week 8**: Static Footprint Analyzer promotion + Gemini CLI research
**Week 9-10**: Context Saturation Metrics (alongside Gemini/Ollama work)
**Week 11**: Context Categories + Cache Drilldown + Compaction Tracking + Bloat Analysis
**Week 12**: v1.0 polish, defer remaining ideas to Phase 5

This adds **~6 ideas** to Phase 3 scope. Evaluate bandwidth against solo maintainer risk.

---

## Conclusion

Of the 13 ideas assessed:

- **4 ideas are GREAT**: Implement in Phase 3 (Context Slices, Starting Context, Footprint Analyzer, Bloat Sources)
- **5 ideas are GOOD**: Implement partially in Phase 3, fully in Phase 5
- **2 ideas are CONDITIONAL**: Depend on prerequisites or telemetry
- **2 ideas to DEFER**: Low priority or risk of scope creep

The ideas collectively enhance MCP Audit's core value proposition: **helping users understand and optimize their context usage**. The Context Slices data model (task-15) should be prioritized as it enables 5+ dependent features.

---

**Next Steps**:
1. Review this assessment with user
2. Update ROADMAP.md with accepted ideas
3. Create implementation tasks for Tier 1 ideas
4. Add dependencies to backlog task files
