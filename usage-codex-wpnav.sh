#!/bin/bash
# Codex CLI usage tracking helper for WP Navigator Pro project only
# This filters @ccusage/codex output to show only wp-navigator-pro sessions

set -e

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

echo -e "${BLUE}═══════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}  WP Navigator Pro - Codex CLI Usage Report${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════${NC}"
echo ""

# Check if any sessions exist
SESSION_COUNT=$(npx @ccusage/codex@latest session --json 2>/dev/null | jq '[.sessions[] | select(.directory | contains("wp-navigator-pro"))] | length')

if [ "$SESSION_COUNT" -eq 0 ]; then
  echo -e "${YELLOW}No Codex CLI sessions found for WP Navigator Pro yet.${NC}"
  echo ""
  echo "This script will show usage data once you start using Codex CLI"
  echo "in the wp-navigator-pro directory."
  echo ""
  echo -e "${CYAN}To use Codex CLI:${NC}"
  echo "  codex exec 'your task here'"
  echo ""
  exit 0
fi

# Get session data for wp-navigator-pro only
npx @ccusage/codex@latest session --json 2>/dev/null | jq -r '
  .sessions[] |
  select(.directory | contains("wp-navigator-pro")) |
  {
    session_id: .sessionId,
    directory: .directory,
    last_active: .lastActivity,
    input_tokens: .inputTokens,
    output_tokens: .outputTokens,
    reasoning_tokens: .reasoningOutputTokens,
    cache_tokens: .cachedInputTokens,
    total_tokens: .totalTokens,
    cost: .costUSD,
    models: .models
  } |
  "
Session ID: \(.session_id)
Directory:  \(.directory)
Last Active: \(.last_active)

Tokens:
  Input:     \(.input_tokens | tostring | gsub(\"(?<a>\\\\d)(?<b>(\\\\d{3})+$)\"; \"\\(.a),\\(.b)\"))
  Output:    \(.output_tokens | tostring | gsub(\"(?<a>\\\\d)(?<b>(\\\\d{3})+$)\"; \"\\(.a),\\(.b)\"))
  Reasoning: \(.reasoning_tokens | tostring | gsub(\"(?<a>\\\\d)(?<b>(\\\\d{3})+$)\"; \"\\(.a),\\(.b)\"))
  Cached:    \(.cache_tokens | tostring | gsub(\"(?<a>\\\\d)(?<b>(\\\\d{3})+$)\"; \"\\(.a),\\(.b)\"))
  Total:     \(.total_tokens | tostring | gsub(\"(?<a>\\\\d)(?<b>(\\\\d{3})+$)\"; \"\\(.a),\\(.b)\"))

Cost: $\(.cost)

Models: \(.models | join(\", \"))
---------------------------------------------------
"
' || echo "Error: Unable to fetch Codex usage data."

echo ""
echo -e "${GREEN}Total for WP Navigator Pro (Codex):${NC}"
npx @ccusage/codex@latest session --json 2>/dev/null | jq -r '
  [.sessions[] | select(.directory | contains("wp-navigator-pro"))] |
  {
    total_sessions: length,
    total_input: ([.[].inputTokens] | add),
    total_output: ([.[].outputTokens] | add),
    total_reasoning: ([.[].reasoningOutputTokens] | add),
    total_cached: ([.[].cachedInputTokens] | add),
    total_tokens: ([.[].totalTokens] | add),
    total_cost: ([.[].costUSD] | add)
  } |
  "
  Sessions: \(.total_sessions)
  Total Input:     \(.total_input) tokens
  Total Output:    \(.total_output) tokens
  Total Reasoning: \(.total_reasoning) tokens
  Total Cached:    \(.total_cached) tokens
  Total Tokens:    \(.total_tokens) tokens
  Total Cost:      $\(.total_cost)
  "
'

echo ""
echo -e "${CYAN}Cache Efficiency:${NC}"
npx @ccusage/codex@latest session --json 2>/dev/null | jq -r '
  [.sessions[] | select(.directory | contains("wp-navigator-pro"))] |
  {
    total_input: ([.[].inputTokens] | add),
    total_cached: ([.[].cachedInputTokens] | add)
  } |
  if .total_input > 0 then
    {
      cache_ratio: ((.total_cached / .total_input) * 100 | floor)
    } |
    "  \(.cache_ratio)% of input tokens were cached (cost savings!)"
  else
    "  No cache data available"
  end
'

echo ""
echo -e "${YELLOW}Note: Codex CLI tracks full timestamps (date + time) in sessions.${NC}"
echo -e "${YELLOW}For real-time monitoring, use: npm run codex:live${NC}"
