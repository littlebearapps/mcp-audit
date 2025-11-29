# Messaging - MCP Audit

Target audiences, value propositions, and key messaging for consistent communication.

---

## Target Audiences

### Primary: MCP Tool Developers
- Built MCP servers (hand-coded or via AI CLI agents like Claude Code, Codex)
- Need per-tool token metrics to optimize their implementations
- Want to know: "How efficient are my tools? Which ones bloat context?"
- **Key value**: Optimize before shipping, data-driven tool development

### Primary: Session Users (Power Users)
- Use Claude Code, Codex CLI, or Gemini CLI daily
- Hit context limits or see unexpected costs
- Want to know: "What's eating my context? Which MCP tools are expensive?"
- **Key value**: Understand usage patterns, make informed tool choices

---

## Value Proposition

### One-Liner
> MCP token tracking for tool builders and power users.

### Hook (Problem-Focused)
> MCP tools eating context and you don't know which ones—or why?

### Expanded Hook
> Whether you're building MCP servers or just using them, mcp-audit shows you exactly where tokens go.

---

## Three-Column Value Prop

| Track | Break Down | Optimize |
|-------|------------|----------|
| Watch tokens flow in real-time | See it by server, then by tool | Tune your tools—or pick better ones |

**Alternative (problem/solution framing):**

| See It | Understand It | Fix It |
|--------|---------------|--------|
| Real-time session monitoring | Per-server, per-tool breakdown | Find what's eating your context |

---

## Key Messages

### For MCP Tool Developers
- "See exactly how your MCP tools consume tokens"
- "Per-tool metrics to optimize before shipping"
- "Build more efficient MCP servers with real usage data"
- "Find the tools bloating context—fix them"

### For Session Users
- "Understand what's eating your context"
- "Per-session breakdown by MCP server and tool"
- "Spot expensive tools, make informed choices"
- "Stop hitting context limits blindly"

### Universal
- "It starts with the data"
- "Local-only, privacy-first"
- "Free, open-source"
- "Works with Claude Code, Codex CLI, Gemini CLI"

---

## Tone & Voice

- **Direct**: No fluff, developers appreciate brevity
- **Problem-aware**: Lead with pain points, not features
- **Technical but accessible**: Assume MCP familiarity, explain metrics
- **Confident but not salesy**: Let the tool speak for itself

---

## Platform-Specific Angles

### Claude Code Users
- Context limits are the pain (not direct costs)
- "Stop wondering why you hit the context limit"
- Cache efficiency tracking is valuable

### Codex CLI / API Users
- Direct token costs matter
- "Know exactly what you're paying for"
- Cost estimation features highlight

### Gemini CLI Users
- Newer platform, early adopters
- "Full telemetry support via OpenTelemetry"
- Latency tracking available

---

## Competitive Positioning

**vs. ccusage**: ccusage tracks long-term trends across all sessions. mcp-audit goes deeper: per-tool, per-server granularity within sessions.

**vs. manual tracking**: mcp-audit automates what you'd otherwise do with grep and spreadsheets.

**Unique angle**: MCP tool developers optimizing their own implementations—underserved niche.

---

## Sample Copy

### README Intro
```
MCP tools eating context and you don't know which ones?

Whether you're building MCP servers or using them daily, mcp-audit shows you exactly where tokens go—per server, per tool, in real-time.
```

### Tweet/X Thread Opener
```
Built an MCP server? Using Claude Code or Codex daily?

You probably have no idea which tools are eating your context.

mcp-audit fixes that. Per-tool token tracking, real-time monitoring, completely free.

pip install mcp-audit
```

### Reddit Post Intro
```
I built mcp-audit to solve my own problem: MCP tools were eating my context and I had no visibility into which ones.

Now I can see exactly how many tokens each tool consumes, per server, per session. Helps whether you're building MCP servers or just using them.
```
