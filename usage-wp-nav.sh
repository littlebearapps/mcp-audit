#!/bin/bash
# Usage tracking helper for WP Navigator Pro project only
# This filters ccusage output to show only wp-navigator-pro sessions

set -e

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${BLUE}═══════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}  WP Navigator Pro - Usage Report${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════${NC}"
echo ""

# Get session data for wp-navigator-pro only
npx ccusage session --json 2>/dev/null | jq -r '
  .sessions[] |
  select(.sessionId | contains("wp-navigator-pro")) |
  {
    session: (.sessionId | split("/")[-1] | split("-")[-1]),
    last_active: .lastActivity,
    input_tokens: .inputTokens,
    output_tokens: .outputTokens,
    cache_create: .cacheCreationTokens,
    cache_read: .cacheReadTokens,
    total_cost: .totalCost,
    cache_ratio: ((.cacheReadTokens / (.cacheReadTokens + .cacheCreationTokens)) * 100 | floor),
    models: .modelsUsed
  } |
  "
Session: \(.session)
Last Active: \(.last_active)

Tokens:
  Input:  \(.input_tokens | tostring | gsub("(?<a>\\d)(?<b>(\\d{3})+$)"; "\(.a),\(.b)"))
  Output: \(.output_tokens | tostring | gsub("(?<a>\\d)(?<b>(\\d{3})+$)"; "\(.a),\(.b)"))

Cache:
  Created: \(.cache_create | tostring | gsub("(?<a>\\d)(?<b>(\\d{3})+$)"; "\(.a),\(.b)")) tokens
  Read:    \(.cache_read | tostring | gsub("(?<a>\\d)(?<b>(\\d{3})+$)"; "\(.a),\(.b)")) tokens
  Ratio:   \(.cache_ratio)% (cache read efficiency)

Cost: $\(.total_cost)

Models: \(.models | join(", "))
---------------------------------------------------
"
' || echo "Error: Unable to fetch usage data. Make sure ccusage is installed."

echo ""
echo -e "${GREEN}Total for WP Navigator Pro:${NC}"
npx ccusage session --json 2>/dev/null | jq -r '
  [.sessions[] | select(.sessionId | contains("wp-navigator-pro"))] |
  {
    total_sessions: length,
    total_input: ([.[].inputTokens] | add),
    total_output: ([.[].outputTokens] | add),
    total_cache_create: ([.[].cacheCreationTokens] | add),
    total_cache_read: ([.[].cacheReadTokens] | add),
    total_cost: ([.[].totalCost] | add),
    cache_ratio: ((([.[].cacheReadTokens] | add) / (([.[].cacheReadTokens] | add) + ([.[].cacheCreationTokens] | add))) * 100 | floor)
  } |
  "
  Sessions: \(.total_sessions)
  Total Input:  \(.total_input) tokens
  Total Output: \(.total_output) tokens
  Total Cache:  \(.total_cache_read) read / \(.total_cache_create) create (\(.cache_ratio)% efficiency)
  Total Cost:   $\(.total_cost)
  "
'

echo ""
echo -e "${YELLOW}Note: ccusage only tracks 'last active' date, not specific times.${NC}"
echo -e "${YELLOW}For real-time monitoring, use: npm run usage:live${NC}"
