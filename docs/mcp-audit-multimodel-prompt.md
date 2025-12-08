# MCP Audit – Multi-Model Per Session Support (Prompt for Claude Code)

Paste the entire contents of this file into Claude Code.  
The goal is to update the MCP Audit roadmap and specs to explicitly support **multi-model usage within a single session**.

---

```markdown
I want to update our MCP Audit roadmap, v1 architecture, and all relevant spec documents to explicitly support **multi-model usage within a single session**.

This is essential because Codex CLI, Claude Code, Gemini CLI, and Ollama CLI all allow the user to switch models mid-session. MCP Audit must continue to treat the session as ONE logical unit, while correctly tracking token usage and costs per model.

Please carefully read the full specification below and then produce:

1. an updated roadmap (v0.4.0 → v1.0.0),  
2. an updated v1 session JSON schema,  
3. an updated AI export summary schema,  
4. and updated TUI design notes,  
all with multi-model support incorporated cleanly and consistently.

──────────────────────────────────────────────────────────────
# 1. Core Behavioural Requirement

A single MCP Audit session may now involve **multiple model identities**, e.g.:

- Codex CLI:
  - Start using `gpt-5.1-codex-max`
  - Switch to `gpt-5.1` later in the session

- Claude Code:
  - Start on Claude Opus
  - Switch to Claude Sonnet

- Gemini CLI:
  - Switch between model variants

- Ollama:
  - Load and run multiple local models (deepseek, qwen, mistral, llama, etc.)

A “session” in MCP Audit is still ONE session, even if the **model changes multiple times**.

──────────────────────────────────────────────────────────────
# 2. Logging Requirements — Session JSON Updates

Please update the v1 JSON schema design to include:

## 2.1 Per-call model tagging
Every logged tool or model call includes a `model` field:

```json
{
  "platform": "codex-cli",
  "model": "gpt-5.1-codex-max",
  "tool": "mcp__zen__thinkdeep",
  "tokens": 19526,
  "timestamp": "..."
}
```

If the model is unknown, use:
```json
"model": null
```
and ensure this is represented in accuracy metadata.

## 2.2 Session-level model summary

Add these fields:

```json
"models_used": ["gpt-5.1-codex-max", "gpt-5.1"],
"model_usage": {
  "gpt-5.1-codex-max": {
    "calls": 12,
    "input_tokens": 64000,
    "output_tokens": 8000,
    "total_tokens": 72000,
    "est_cost_usd": 0.90
  },
  "gpt-5.1": {
    "calls": 7,
    "input_tokens": 32000,
    "output_tokens": 6000,
    "total_tokens": 38000,
    "est_cost_usd": 0.45
  }
}
```

## 2.3 Session totals remain simple

```json
"total_tokens": 110000,
"total_est_cost_usd": 1.35
```

Where platform-reported totals exist, those override.

## 2.4 Accuracy metadata should incorporate multi-model complexity

Extend:

```json
"token_accounting": {
  "mode": "exact" | "estimated" | "calls-only",
  "session_relative_error": 0.061,
  "models_mixed": true
}
```

──────────────────────────────────────────────────────────────
# 3. Cost & Pricing Computation Requirements

MCP Audit must:

- compute **per-model** cost using a local price table (input/output costs per model),  
- sum these into **session-level cost**,  
- compare to platform-reported cost when available,  
- update the accuracy score accordingly.

No in-tool recommendations — just telemetry.

──────────────────────────────────────────────────────────────
# 4. TUI Requirements — v0.5.0 Minimal Design

### Live Overview Header

If only one model used:
\`\`\`
Model: gpt-5.1-codex-max
\`\`\`

If multiple:
\`\`\`
Models: gpt-5.1-codex-max, gpt-5.1 (multi)
\`\`\`

### Optional Models Block

Below Token Usage:

\`\`\`
Models Used
  gpt-5.1-codex-max  72K tokens   $0.90
  gpt-5.1            38K tokens   $0.45
\`\`\`

This MUST be minimal and ASCII-first.

### Session Browser

Either:

- a \`MODELS\` column (e.g. \`gpt-5.1-codex-max,+1\`), or
- rely on AI export for deeper details.

Do NOT add a third TUI mode; Browser + Live Overview is sufficient for v0.5.0.

──────────────────────────────────────────────────────────────
# 5. AI Export Summary Schema Requirements

Please update the export schema to include:

```json
{
  "project": "zen-mcp",
  "platform": "codex-cli",
  "session_id": "...",
  "total_tokens": 110000,
  "total_est_cost_usd": 1.35,

  "models_used": ["gpt-5.1-codex-max", "gpt-5.1"],
  "model_usage": { ... as specified above ... },

  "mcp": {
    "servers": [...],
    "tools": [...]
  },

  "smells": [...],
  "token_accounting": {
    "mode": "...",
    "session_relative_error": 0.061,
    "models_mixed": true
  }
}
```

AI agents must receive all model-level context for cost and efficiency analysis.

──────────────────────────────────────────────────────────────
# 6. Updated Roadmap Requirements

Please update the roadmap to include multi-model support explicitly:

- **v0.4.0** → Smells, AI Export (single-model OK), Session Index  
- **v0.5.0** → TUI Browser, Accuracy Metadata, Zombie Tools  
- **v0.6.0** → Ollama CLI, Static/Dynamic telemetry, **multi-model-per-session support (logging + schema + TUI integration + AI export)**  
- **v1.0.0** → Polish, docs, tests (including docs explaining mixed-model sessions)  

If you believe it is cleaner to split logging and UI integration across two versions, propose an adjustment.

──────────────────────────────────────────────────────────────
# 7. Questions for You — Please Answer Explicitly

1. Do you see any technical risks with multi-model-per-session support given the current architecture?  
2. For Claude/Codex/Gemini, are there cases where the model identity is *not* available? How should we handle \`model: null\` cases?  
3. Is the small “Models Used” block in Live Overview adequate for v0.5.0?  
4. Should the Session Browser attempt to show a compact \`MODELS\` column, or is that unnecessary in v0.5.0?  
5. How would you modify the AI prompt export templates so the AI agent properly understands mixed-model cost tradeoffs without overwhelming the user?

──────────────────────────────────────────────────────────────

Now please:

- update the roadmap,
- update the v1 session JSON schema,
- update the AI export summary schema,
- update the TUI design notes,

to incorporate **multi-model support per session** in a clean, telemetry-first way.
```
