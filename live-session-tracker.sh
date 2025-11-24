#!/bin/bash
# Real-time session tracker for MCP Audit
# Wrapper script that provides colored output for Python trackers

set -e

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
RED='\033[0;31m'
BOLD='\033[1m'
NC='\033[0m' # No Color

# Claude Code data directory
CLAUDE_DIR="${HOME}/.config/claude/projects"
if [ ! -d "$CLAUDE_DIR" ]; then
  CLAUDE_DIR="${HOME}/.claude/projects"
fi

if [ ! -d "$CLAUDE_DIR" ]; then
  echo -e "${RED}Error: Claude Code data directory not found${NC}"
  echo "Expected: ~/.config/claude/projects or ~/.claude/projects"
  exit 1
fi

# Project path detection (auto-detected by Python tracker)
# No longer needed - Python trackers handle project detection

# Session tracking variables
TOTAL_INPUT=0
TOTAL_OUTPUT=0
TOTAL_CACHE_CREATE=0
TOTAL_CACHE_READ=0
TOTAL_COST=0
MESSAGE_COUNT=0
START_TIME=$(date +%s)

# Pricing (approximate, adjust as needed)
# Claude Sonnet 4.5 pricing per million tokens
INPUT_PRICE=3.0
OUTPUT_PRICE=15.0
CACHE_CREATE_PRICE=3.75
CACHE_READ_PRICE=0.30

# Function to format numbers with commas
format_number() {
  printf "%'d" "$1" 2>/dev/null || echo "$1"
}

# Function to calculate cost
calculate_cost() {
  local input=$1
  local output=$2
  local cache_create=$3
  local cache_read=$4

  bc -l <<< "scale=4; ($input * $INPUT_PRICE + $output * $OUTPUT_PRICE + $cache_create * $CACHE_CREATE_PRICE + $cache_read * $CACHE_READ_PRICE) / 1000000"
}

# Function to display stats
display_stats() {
  local elapsed=$(($(date +%s) - START_TIME))
  local minutes=$((elapsed / 60))
  local seconds=$((elapsed % 60))

  # Clear screen and show header
  clear
  echo -e "${BLUE}╔════════════════════════════════════════════════════════════════╗${NC}"
  echo -e "${BLUE}║${NC} ${BOLD}MCP Audit - Live Session Tracker${NC}                             ${BLUE}║${NC}"
  echo -e "${BLUE}╚════════════════════════════════════════════════════════════════╝${NC}"
  echo ""
  echo -e "${CYAN}Started:${NC} $(date -r $START_TIME '+%Y-%m-%d %H:%M:%S')"
  echo -e "${CYAN}Elapsed:${NC} ${minutes}m ${seconds}s"
  echo -e "${CYAN}Messages:${NC} $MESSAGE_COUNT"
  echo ""

  echo -e "${YELLOW}═══════════════════════════════════════════════════════════════${NC}"
  echo -e "${BOLD}Token Usage (This Session)${NC}"
  echo -e "${YELLOW}═══════════════════════════════════════════════════════════════${NC}"

  printf "  %-20s %15s\n" "Input tokens:" "$(format_number $TOTAL_INPUT)"
  printf "  %-20s %15s\n" "Output tokens:" "$(format_number $TOTAL_OUTPUT)"
  printf "  %-20s %15s\n" "Cache created:" "$(format_number $TOTAL_CACHE_CREATE)"
  printf "  %-20s %15s\n" "Cache read:" "$(format_number $TOTAL_CACHE_READ)"

  echo ""
  echo -e "${YELLOW}───────────────────────────────────────────────────────────────${NC}"

  local total_tokens=$((TOTAL_INPUT + TOTAL_OUTPUT + TOTAL_CACHE_CREATE + TOTAL_CACHE_READ))
  printf "  %-20s %15s\n" "${BOLD}Total tokens:${NC}" "$(format_number $total_tokens)"

  if [ $total_tokens -gt 0 ]; then
    local cache_ratio=$((TOTAL_CACHE_READ * 100 / (TOTAL_CACHE_READ + TOTAL_CACHE_CREATE + 1)))
    printf "  %-20s %14s%%\n" "Cache efficiency:" "$cache_ratio"
  fi

  echo ""
  echo -e "${GREEN}═══════════════════════════════════════════════════════════════${NC}"
  printf "  ${BOLD}Estimated Cost:${NC}  ${GREEN}\$%.4f${NC}\n" "$TOTAL_COST"
  echo -e "${GREEN}═══════════════════════════════════════════════════════════════${NC}"

  echo ""
  echo -e "${CYAN}Monitoring: $PROJECT_PATH${NC}"
  echo -e "${YELLOW}Press Ctrl+C to stop tracking${NC}"
}

# Trap Ctrl+C for clean exit
trap 'echo -e "\n\n${GREEN}Session tracking stopped.${NC}\n"; exit 0' INT TERM

# Display initial state
display_stats

# Find the most recent JSONL file for this project
# Claude Code creates files like: project-name-SESSIONID.jsonl
find_project_files() {
  find "$CLAUDE_DIR" -type f -name "*.jsonl" 2>/dev/null | sort -t- -k3 -r | head -20
}

# Get initial file list
PROJECT_FILES=$(find_project_files)

if [ -z "$PROJECT_FILES" ]; then
  echo ""
  echo -e "${YELLOW}Waiting for Claude Code session to start...${NC}"
  echo ""
fi

# Monitor for new files and changes
while true; do
  # Re-scan for new files every iteration
  CURRENT_FILES=$(find_project_files)

  # Process any new or updated files
  for file in $CURRENT_FILES; do
    # Use tail to get only new lines since last check
    # We'll process line-by-line looking for message objects
    tail -n 100 "$file" 2>/dev/null | while IFS= read -r line; do
      # Process all lines (no project-specific filtering)
      if echo "$line" | grep -q "usage"; then

        # Try to extract token usage from the line
        # Claude Code JSONL format includes usage data in message objects
        input=$(echo "$line" | jq -r '.message.usage.inputTokens // 0' 2>/dev/null || echo 0)
        output=$(echo "$line" | jq -r '.message.usage.outputTokens // 0' 2>/dev/null || echo 0)
        cache_create=$(echo "$line" | jq -r '.message.usage.cacheCreationInputTokens // 0' 2>/dev/null || echo 0)
        cache_read=$(echo "$line" | jq -r '.message.usage.cacheReadInputTokens // 0' 2>/dev/null || echo 0)

        # If we got valid token counts, update totals
        if [ "$input" -gt 0 ] || [ "$output" -gt 0 ] || [ "$cache_create" -gt 0 ] || [ "$cache_read" -gt 0 ]; then
          TOTAL_INPUT=$((TOTAL_INPUT + input))
          TOTAL_OUTPUT=$((TOTAL_OUTPUT + output))
          TOTAL_CACHE_CREATE=$((TOTAL_CACHE_CREATE + cache_create))
          TOTAL_CACHE_READ=$((TOTAL_CACHE_READ + cache_read))
          MESSAGE_COUNT=$((MESSAGE_COUNT + 1))

          # Calculate cost
          TOTAL_COST=$(calculate_cost $TOTAL_INPUT $TOTAL_OUTPUT $TOTAL_CACHE_CREATE $TOTAL_CACHE_READ)

          # Update display
          display_stats
        fi
      fi
    done
  done

  # Check every 2 seconds
  sleep 2
done
