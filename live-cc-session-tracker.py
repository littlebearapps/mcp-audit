#!/usr/bin/env python3
"""
Real-time session tracker for WP Navigator Pro
Monitors Claude Code usage ONLY for this project, starting from NOW
"""

import os
import sys
import time
import json
import subprocess
import atexit
import signal
import argparse
from pathlib import Path
from datetime import datetime
from collections import defaultdict


# Colors
class Colors:
    GREEN = "\033[0;32m"
    BLUE = "\033[0;34m"
    YELLOW = "\033[1;33m"
    CYAN = "\033[0;36m"
    RED = "\033[0;31m"
    BOLD = "\033[1m"
    NC = "\033[0m"  # No Color


def load_model_pricing():
    """Load pricing data from model-pricing.json"""
    pricing_file = Path(__file__).parent / "model-pricing.json"

    if not pricing_file.exists():
        print(
            f"{Colors.YELLOW}Warning: model-pricing.json not found, using fallback pricing{Colors.NC}"
        )
        return {
            "models": {
                "claude": {
                    "claude-sonnet-4-5-20250929": {
                        "name": "Claude Sonnet 4.5",
                        "input": 3.0,
                        "output": 15.0,
                        "cache_create": 3.75,
                        "cache_read": 0.30,
                    }
                }
            },
            "exchange_rates": {"USD_to_AUD": 1.54},
        }

    try:
        with open(pricing_file, "r") as f:
            return json.load(f)
    except Exception as e:
        print(f"{Colors.RED}Error loading pricing: {e}{Colors.NC}")
        return None


def get_model_pricing(pricing_data, model_id):
    """Get pricing for a specific model ID"""
    if not pricing_data or "models" not in pricing_data:
        return None

    # Try Claude models first
    for provider in ["claude", "openai"]:
        if provider in pricing_data["models"]:
            if model_id in pricing_data["models"][provider]:
                return pricing_data["models"][provider][model_id]

    return None


def extract_mcp_server(tool_name):
    """Extract MCP server name from tool name

    Args:
        tool_name: Tool name from Claude Code session (e.g., 'mcp__brave-search__brave_web_search')

    Returns:
        MCP server name (e.g., 'brave-search') or None if not an MCP tool
    """
    if tool_name and tool_name.startswith("mcp__"):
        # Format: mcp__server-name__tool-name
        parts = tool_name.split("__")
        if len(parts) >= 3:
            return parts[1]  # server-name
    return None


def get_git_metadata(working_dir):
    """Collect git metadata for the session

    Args:
        working_dir: Path to the working directory

    Returns:
        Dictionary with branch, commit hash, and status
    """
    metadata = {
        "branch": None,
        "commit": None,
        "commit_short": None,
        "status": "unknown",
        "has_changes": False,
    }

    try:
        # Get current branch
        result = subprocess.run(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            cwd=working_dir,
            capture_output=True,
            text=True,
            timeout=2,
        )
        if result.returncode == 0:
            metadata["branch"] = result.stdout.strip()

        # Get commit hash
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"], cwd=working_dir, capture_output=True, text=True, timeout=2
        )
        if result.returncode == 0:
            metadata["commit"] = result.stdout.strip()
            metadata["commit_short"] = metadata["commit"][:8]

        # Check for uncommitted changes
        result = subprocess.run(
            ["git", "status", "--porcelain"],
            cwd=working_dir,
            capture_output=True,
            text=True,
            timeout=2,
        )
        if result.returncode == 0:
            metadata["has_changes"] = len(result.stdout.strip()) > 0
            metadata["status"] = "clean" if not metadata["has_changes"] else "dirty"

    except (subprocess.TimeoutExpired, FileNotFoundError, Exception):
        # Git not available or not a git repo
        pass

    return metadata


class SessionTracker:
    def __init__(self, project_path="wp-navigator-pro/main"):
        print(f"{Colors.CYAN}[INIT] Initializing tracker for: {project_path}{Colors.NC}")

        self.project_path = project_path
        self.start_time = time.time()
        self.total_input = 0
        self.total_output = 0
        self.total_cache_create = 0
        self.total_cache_read = 0
        self.message_count = 0
        self.file_positions = {}  # Track where we are in each file
        self.debug_messages = []  # Store last 5 debug messages
        self.max_debug_messages = 5
        self.detected_model = None  # Track detected model ID
        self.model_name = "Unknown Model"  # Human-readable model name

        # MCP server usage tracking
        self.mcp_stats = defaultdict(
            lambda: {
                "calls": 0,
                "input_tokens": 0,
                "output_tokens": 0,
                "cache_create_tokens": 0,
                "cache_read_tokens": 0,
                "total_tokens": 0,
            }
        )
        self.builtin_tool_calls = 0
        self.builtin_tool_tokens = 0

        # Tool-level tracking (within each MCP server)
        # Format: self.mcp_tool_stats[server_name][tool_full_name] = {...}
        self.mcp_tool_stats = defaultdict(
            lambda: defaultdict(
                lambda: {
                    "calls": 0,
                    "input_tokens": 0,
                    "output_tokens": 0,
                    "cache_create_tokens": 0,
                    "cache_read_tokens": 0,
                    "total_tokens": 0,
                }
            )
        )

        # Error, warning, and anomaly tracking (Gap 1 & 3)
        self.errors = []
        self.warnings = []
        self.anomalies = {
            "high_token_operations": [],
            "high_call_frequency": [],  # Tools called >5x
            "high_variance": [],  # Tools with inconsistent token usage
            "unusual_patterns": [],
        }

        # Anomaly detection thresholds
        self.HIGH_TOKEN_THRESHOLD = 100000  # 100K tokens in single message
        self.HIGH_AVG_THRESHOLD = 50000  # 50K avg tokens per tool call
        self.HIGH_FREQUENCY_THRESHOLD = 5  # >5 calls per session
        self.HIGH_VARIANCE_RATIO = 5.0  # Max/min tokens ratio > 5x

        # Per-tool variance tracking
        self.tool_token_history = defaultdict(list)  # Track all token values per tool

        # Session comparison data (Gap 4)
        self.previous_session_data = None

        # Duplicate call detection (Efficiency Measurement)
        self.tool_call_signatures = {}  # Track tool calls by signature
        self.duplicate_calls = []  # Store duplicate call details

        # Parse CLI flags
        self.quiet_mode = "--quiet" in sys.argv
        self.enable_logging = "--no-logs" not in sys.argv

        # Session logging setup
        if self.enable_logging:
            # Create session folder: {project}-{YYYY-MM-DD-HHMMSS}
            session_timestamp = datetime.now().strftime("%Y-%m-%d-%H%M%S")
            project_slug = project_path.replace("/", "-")
            session_folder_name = f"{project_slug}-{session_timestamp}"

            self.log_dir = Path("scripts/ai-mcp-audit/logs/sessions") / session_folder_name
            self.log_dir.mkdir(parents=True, exist_ok=True)

            # Log file paths
            self.summary_file = self.log_dir / "summary.json"
            self.events_file = self.log_dir / "events.jsonl"

            print(f"{Colors.GREEN}[INIT] Logging enabled: {self.log_dir}{Colors.NC}")
        else:
            self.log_dir = None
            print(f"{Colors.YELLOW}[INIT] Logging disabled (--no-logs flag){Colors.NC}")

        # Collect git metadata
        working_dir = Path.cwd()
        self.git_metadata = get_git_metadata(working_dir)
        if self.git_metadata["branch"]:
            print(
                f"{Colors.CYAN}[INIT] Git branch: {self.git_metadata['branch']} ({self.git_metadata['commit_short']}){Colors.NC}"
            )

        # Register cleanup handler
        atexit.register(self.cleanup)
        signal.signal(signal.SIGINT, self._signal_handler)

        # Load pricing data
        print(f"{Colors.CYAN}[INIT] Loading model pricing data...{Colors.NC}")
        self.pricing_data = load_model_pricing()
        if self.pricing_data:
            print(f"{Colors.GREEN}[INIT] Pricing data loaded successfully{Colors.NC}")
        else:
            print(f"{Colors.RED}[INIT] Failed to load pricing data{Colors.NC}")

        # Find Claude Code projects directory
        base_dir = Path.home() / ".config" / "claude" / "projects"
        print(f"{Colors.CYAN}[INIT] Checking for Claude Code directory: {base_dir}{Colors.NC}")

        if not base_dir.exists():
            base_dir = Path.home() / ".claude" / "projects"
            print(f"{Colors.CYAN}[INIT] Trying alternate location: {base_dir}{Colors.NC}")

        if not base_dir.exists():
            print(f"{Colors.RED}Error: Claude Code data directory not found{Colors.NC}")
            print(f"Tried: ~/.config/claude/projects and ~/.claude/projects")
            sys.exit(1)

        print(f"{Colors.GREEN}[INIT] Found Claude Code directory: {base_dir}{Colors.NC}")

        # Find the project-specific directory
        # Format: -Users-username-path-to-project
        home_path = os.path.expanduser("~")[1:]  # Remove leading /
        project_dir_name = f"-{home_path}-claude-code-tools-lba-plugins-{project_path}".replace(
            "/", "-"
        )
        print(f"{Colors.CYAN}[INIT] Looking for project directory: {project_dir_name}{Colors.NC}")

        self.claude_dir = base_dir / project_dir_name

        if not self.claude_dir.exists():
            print(f"{Colors.YELLOW}[INIT] Project directory not found, searching...{Colors.NC}")
            # Try to find it by searching
            found = False
            for d in base_dir.iterdir():
                if d.is_dir() and project_path.replace("/", "-") in d.name:
                    self.claude_dir = d
                    found = True
                    print(f"{Colors.GREEN}[INIT] Found matching directory: {d.name}{Colors.NC}")
                    break

            if not found:
                print(
                    f"{Colors.YELLOW}Warning: Project directory not found: {project_dir_name}{Colors.NC}"
                )
                print(f"{Colors.YELLOW}Looking in: {base_dir}{Colors.NC}")
                print(
                    f"{Colors.YELLOW}This may mean no Claude Code sessions exist for this project yet.{Colors.NC}"
                )
                print(f"{Colors.YELLOW}Will scan all directories...{Colors.NC}")
                self.claude_dir = base_dir  # Fall back to scanning all
        else:
            print(f"{Colors.GREEN}[INIT] Using project directory: {self.claude_dir}{Colors.NC}")

        # Load previous session for comparison (Gap 4)
        if self.enable_logging:
            self.load_previous_session()

    def load_previous_session(self):
        """Load the most recent previous session for comparison"""
        try:
            sessions_dir = Path("scripts/ai-mcp-audit/logs/sessions")
            if not sessions_dir.exists():
                return

            # Get all session folders except current one
            session_folders = [
                f for f in sessions_dir.iterdir() if f.is_dir() and f.name != self.log_dir.name
            ]

            if not session_folders:
                return

            # Sort by name (which includes timestamp) and get most recent
            session_folders.sort(reverse=True)
            prev_session = session_folders[0]

            # Load summary from previous session
            prev_summary = prev_session / "summary.json"
            if prev_summary.exists():
                with open(prev_summary, "r") as f:
                    self.previous_session_data = json.load(f)
                print(
                    f"{Colors.CYAN}[INIT] Loaded previous session for comparison: {prev_session.name}{Colors.NC}"
                )
        except Exception as e:
            # Silently fail - previous session data is optional
            pass

    def detect_anomaly(self, tool_name, tokens, message_tokens=None):
        """Detect anomalies in tool usage (Gap 3 + Enhanced)

        Args:
            tool_name: Name of tool used
            tokens: Tokens used by this tool
            message_tokens: Optional total message tokens
        """
        # Track token history for variance detection
        if message_tokens:
            self.tool_token_history[tool_name].append(message_tokens)

        # 1. High token usage in single operation
        if message_tokens and message_tokens > self.HIGH_TOKEN_THRESHOLD:
            anomaly = {
                "timestamp": datetime.now().isoformat() + "Z",
                "type": "high_token_operation",
                "tool": tool_name,
                "tokens": message_tokens,
                "threshold": self.HIGH_TOKEN_THRESHOLD,
                "severity": "warning",
            }
            self.anomalies["high_token_operations"].append(anomaly)

            # Also add to warnings list
            self.warnings.append(
                {
                    "timestamp": anomaly["timestamp"],
                    "type": "high_token_usage",
                    "tool": tool_name,
                    "message": f"{tool_name} used {message_tokens:,} tokens in single call (>{self.HIGH_TOKEN_THRESHOLD:,})",
                    "severity": "warning",
                }
            )

        # 2. High variance detection (if we have multiple calls)
        token_history = self.tool_token_history[tool_name]
        if len(token_history) >= 3:  # Need at least 3 calls to detect variance
            min_tokens = min(token_history)
            max_tokens = max(token_history)

            if min_tokens > 0:  # Avoid division by zero
                variance_ratio = max_tokens / min_tokens

                if variance_ratio > self.HIGH_VARIANCE_RATIO:
                    # Check if we haven't already recorded this tool
                    existing = [
                        a for a in self.anomalies["high_variance"] if a["tool"] == tool_name
                    ]
                    if not existing:
                        anomaly = {
                            "timestamp": datetime.now().isoformat() + "Z",
                            "type": "high_variance",
                            "tool": tool_name,
                            "min_tokens": min_tokens,
                            "max_tokens": max_tokens,
                            "variance_ratio": round(variance_ratio, 1),
                            "threshold_ratio": self.HIGH_VARIANCE_RATIO,
                            "severity": "info",
                        }
                        self.anomalies["high_variance"].append(anomaly)

                        self.warnings.append(
                            {
                                "timestamp": anomaly["timestamp"],
                                "type": "high_variance",
                                "tool": tool_name,
                                "message": f"{tool_name} has high variance: {min_tokens:,}-{max_tokens:,} tokens ({variance_ratio:.1f}x difference)",
                                "severity": "info",
                            }
                        )

    def detect_duplicate_call(self, tool_name, params, tokens):
        """Detect duplicate tool calls within a session (Efficiency Measurement)

        Args:
            tool_name: Name of tool used
            params: Tool parameters (dict)
            tokens: Tokens used by this message

        Returns:
            True if this is a duplicate call, False otherwise
        """
        # Generate dedup key (simple string approach, not SHA-256)
        dedup_key = json.dumps({"tool": tool_name, "params": params}, sort_keys=True)

        if dedup_key in self.tool_call_signatures:
            # This is a duplicate call
            self.tool_call_signatures[dedup_key] += 1
            occurrences = self.tool_call_signatures[dedup_key]

            # Record duplicate
            duplicate_entry = {
                "timestamp": datetime.now().isoformat() + "Z",
                "tool": tool_name,
                "params": params,
                "occurrences": occurrences,
                "tokens_wasted": tokens,
            }
            self.duplicate_calls.append(duplicate_entry)

            # Also add to warnings
            self.warnings.append(
                {
                    "timestamp": duplicate_entry["timestamp"],
                    "type": "duplicate_call",
                    "tool": tool_name,
                    "message": f"{tool_name} called {occurrences} times with identical params (wasted {tokens:,} tokens)",
                    "severity": "info",
                }
            )

            return True
        else:
            # First time seeing this call
            self.tool_call_signatures[dedup_key] = 1
            return False

    def add_debug(self, message):
        """Add a debug message to the buffer"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.debug_messages.append(f"[{timestamp}] {message}")
        # Keep only last N messages
        if len(self.debug_messages) > self.max_debug_messages:
            self.debug_messages.pop(0)

    def format_number(self, num):
        """Format number with commas"""
        return f"{num:,}"

    def calculate_cost(self):
        """Calculate total cost based on token usage and detected model"""
        # Get pricing for detected model
        model_pricing = None
        if self.detected_model and self.pricing_data:
            model_pricing = get_model_pricing(self.pricing_data, self.detected_model)

        # Fall back to default Sonnet 4.5 pricing if no model detected
        if not model_pricing:
            model_pricing = {"input": 3.0, "output": 15.0, "cache_create": 3.75, "cache_read": 0.30}

        # Calculate actual cost (with caching)
        cost_usd = (
            (self.total_input * model_pricing["input"])
            + (self.total_output * model_pricing["output"])
            + (self.total_cache_create * model_pricing["cache_create"])
            + (self.total_cache_read * model_pricing["cache_read"])
        ) / 1_000_000

        # Calculate no-cache cost (what it would cost without caching)
        # All cache tokens would be charged at regular input rate
        no_cache_cost_usd = (
            (self.total_input + self.total_cache_create + self.total_cache_read)
            * model_pricing["input"]
            + (self.total_output * model_pricing["output"])
        ) / 1_000_000

        # Calculate savings
        savings_usd = no_cache_cost_usd - cost_usd
        efficiency_percent = (savings_usd / no_cache_cost_usd * 100) if no_cache_cost_usd > 0 else 0

        # Convert to AUD
        usd_to_aud = 1.54  # Default
        if self.pricing_data and "exchange_rates" in self.pricing_data:
            usd_to_aud = self.pricing_data["exchange_rates"].get("USD_to_AUD", 1.54)

        cost_aud = cost_usd * usd_to_aud
        no_cache_cost_aud = no_cache_cost_usd * usd_to_aud
        savings_aud = savings_usd * usd_to_aud

        return {
            "actual": (cost_usd, cost_aud),
            "no_cache": (no_cache_cost_usd, no_cache_cost_aud),
            "savings": (savings_usd, savings_aud, efficiency_percent),
        }

    def display_mcp_breakdown(self):
        """Display MCP server usage breakdown (top 5 by tokens)"""
        # Only display if we have MCP usage
        if not self.mcp_stats:
            return

        print()
        print(
            f"{Colors.YELLOW}═══════════════════════════════════════════════════════════════{Colors.NC}"
        )
        print(f"{Colors.BOLD}MCP Server Breakdown (Top 5){Colors.NC}")
        print(
            f"{Colors.YELLOW}═══════════════════════════════════════════════════════════════{Colors.NC}"
        )

        # Sort servers by total tokens (descending) and take top 5
        sorted_servers = sorted(
            self.mcp_stats.items(), key=lambda x: x[1]["total_tokens"], reverse=True
        )[:5]

        # Calculate totals
        total_mcp_calls = sum(stats["calls"] for _, stats in self.mcp_stats.items())
        total_mcp_tokens = sum(stats["total_tokens"] for _, stats in self.mcp_stats.items())
        total_session_tokens = (
            self.total_input + self.total_output + self.total_cache_create + self.total_cache_read
        )

        # Display each server with tool breakdown
        for server_name, stats in sorted_servers:
            calls = stats["calls"]
            tokens = stats["total_tokens"]
            avg_tokens = tokens // calls if calls > 0 else 0

            # Format tokens with K/M suffix
            if tokens >= 1_000_000:
                tokens_str = f"{tokens / 1_000_000:.1f}M"
            elif tokens >= 1_000:
                tokens_str = f"{tokens / 1_000:.0f}K"
            else:
                tokens_str = str(tokens)

            # Format average with K suffix
            if avg_tokens >= 1_000:
                avg_str = f"{avg_tokens / 1_000:.0f}K"
            else:
                avg_str = str(avg_tokens)

            print(
                f"  {server_name:<20} {calls:>3} calls  {tokens_str:>8} tokens  (avg {avg_str}/call)"
            )

            # Show per-tool breakdown (indented)
            if server_name in self.mcp_tool_stats:
                # Sort tools by tokens (descending)
                sorted_tools = sorted(
                    self.mcp_tool_stats[server_name].items(),
                    key=lambda x: x[1]["total_tokens"],
                    reverse=True,
                )

                for tool_full_name, tool_stats in sorted_tools:
                    # Extract short tool name (last part after __)
                    tool_short = (
                        tool_full_name.split("__")[-1] if "__" in tool_full_name else tool_full_name
                    )

                    tool_calls = tool_stats["calls"]
                    tool_tokens = tool_stats["total_tokens"]
                    pct_of_server = (tool_tokens / tokens * 100) if tokens > 0 else 0

                    # Format tool tokens
                    if tool_tokens >= 1_000_000:
                        tool_tokens_str = f"{tool_tokens / 1_000_000:.1f}M"
                    elif tool_tokens >= 1_000:
                        tool_tokens_str = f"{tool_tokens / 1_000:.0f}K"
                    else:
                        tool_tokens_str = str(tool_tokens)

                    print(
                        f"    └─ {tool_short:<17} {tool_calls:>3} calls  {tool_tokens_str:>8} tokens  ({pct_of_server:.0f}% of server)"
                    )

        # Summary line
        print(
            f"{Colors.YELLOW}───────────────────────────────────────────────────────────────{Colors.NC}"
        )

        # Calculate percentage
        mcp_percentage = (
            (total_mcp_tokens / total_session_tokens * 100) if total_session_tokens > 0 else 0
        )

        # Format total tokens
        if total_mcp_tokens >= 1_000_000:
            total_str = f"{total_mcp_tokens / 1_000_000:.1f}M"
        elif total_mcp_tokens >= 1_000:
            total_str = f"{total_mcp_tokens / 1_000:.0f}K"
        else:
            total_str = str(total_mcp_tokens)

        print(
            f"  {Colors.BOLD}Total MCP usage:{Colors.NC}    {total_mcp_calls:>3} calls  {total_str:>8} tokens  ({mcp_percentage:.0f}% of session)"
        )

        # Built-in tools summary (if any)
        if self.builtin_tool_calls > 0:
            builtin_percentage = (
                (self.builtin_tool_tokens / total_session_tokens * 100)
                if total_session_tokens > 0
                else 0
            )

            # Format built-in tokens
            if self.builtin_tool_tokens >= 1_000_000:
                builtin_str = f"{self.builtin_tool_tokens / 1_000_000:.1f}M"
            elif self.builtin_tool_tokens >= 1_000:
                builtin_str = f"{self.builtin_tool_tokens / 1_000:.0f}K"
            else:
                builtin_str = str(self.builtin_tool_tokens)

            print(
                f"  Built-in tools:      {self.builtin_tool_calls:>3} calls  {builtin_str:>8} tokens  ({builtin_percentage:.0f}% of session)"
            )

        print(
            f"{Colors.YELLOW}═══════════════════════════════════════════════════════════════{Colors.NC}"
        )

    def display_stats(self):
        """Display current statistics"""
        # Skip display in quiet mode
        if self.quiet_mode:
            return

        elapsed = int(time.time() - self.start_time)
        minutes = elapsed // 60
        seconds = elapsed % 60

        # Clear screen (ANSI escape codes - fast, no subprocess)
        print("\033[2J\033[H", end="")

        # Header
        print(
            f"{Colors.BLUE}╔════════════════════════════════════════════════════════════════╗{Colors.NC}"
        )
        print(
            f"{Colors.BLUE}║{Colors.NC} {Colors.BOLD}WP Navigator Pro - Live Session Tracker{Colors.NC}                       {Colors.BLUE}║{Colors.NC}"
        )
        print(
            f"{Colors.BLUE}╚════════════════════════════════════════════════════════════════╝{Colors.NC}"
        )
        print()

        start_str = datetime.fromtimestamp(self.start_time).strftime("%Y-%m-%d %H:%M:%S")
        print(f"{Colors.CYAN}Started:{Colors.NC} {start_str}")
        print(f"{Colors.CYAN}Elapsed:{Colors.NC} {minutes}m {seconds}s")
        print(f"{Colors.CYAN}Messages:{Colors.NC} {self.message_count}")
        print()

        print(
            f"{Colors.YELLOW}═══════════════════════════════════════════════════════════════{Colors.NC}"
        )
        print(f"{Colors.BOLD}Token Usage (This Session){Colors.NC}")
        print(
            f"{Colors.YELLOW}═══════════════════════════════════════════════════════════════{Colors.NC}"
        )

        print(f"  {'Input tokens:':<20} {self.format_number(self.total_input):>15}")
        print(f"  {'Output tokens:':<20} {self.format_number(self.total_output):>15}")
        print(f"  {'Cache created:':<20} {self.format_number(self.total_cache_create):>15}")
        print(f"  {'Cache read:':<20} {self.format_number(self.total_cache_read):>15}")

        print()
        print(
            f"{Colors.YELLOW}───────────────────────────────────────────────────────────────{Colors.NC}"
        )

        total_tokens = (
            self.total_input + self.total_output + self.total_cache_create + self.total_cache_read
        )
        print(
            f"  {Colors.BOLD}{'Total tokens:':<20}{Colors.NC} {self.format_number(total_tokens):>15}"
        )

        if total_tokens > 0 and (self.total_cache_read + self.total_cache_create) > 0:
            cache_ratio = int(
                (self.total_cache_read / (self.total_cache_read + self.total_cache_create)) * 100
            )
            print(f"  {'Cache efficiency:':<20} {cache_ratio:>14}%")

        print()
        costs = self.calculate_cost()
        actual_usd, actual_aud = costs["actual"]
        no_cache_usd, no_cache_aud = costs["no_cache"]
        savings_usd, savings_aud, efficiency = costs["savings"]

        print(
            f"{Colors.GREEN}═══════════════════════════════════════════════════════════════{Colors.NC}"
        )
        print(f"  {Colors.BOLD}Model:{Colors.NC} {self.model_name}")
        print()
        print(f"  {Colors.BOLD}Cost (with cache):{Colors.NC}")
        print(f"    USD: {Colors.GREEN}${actual_usd:.4f}{Colors.NC}")
        print(f"    AUD: {Colors.GREEN}${actual_aud:.4f}{Colors.NC}")

        # Only show savings if we have cache usage
        if (self.total_cache_create + self.total_cache_read) > 0:
            print()
            print(f"  {Colors.BOLD}Cost (no cache):{Colors.NC}")
            print(f"    USD: ${no_cache_usd:.4f}")
            print(f"    AUD: ${no_cache_aud:.4f}")
            print()
            print(f"  {Colors.BOLD}💰 Cache Savings:{Colors.NC}")
            print(f"    USD: {Colors.YELLOW}${savings_usd:.4f}{Colors.NC}")
            print(f"    AUD: {Colors.YELLOW}${savings_aud:.4f}{Colors.NC}")
            print(
                f"    {Colors.BOLD}Efficiency:{Colors.NC} {Colors.YELLOW}{efficiency:.1f}% saved{Colors.NC}"
            )

        print(
            f"{Colors.GREEN}═══════════════════════════════════════════════════════════════{Colors.NC}"
        )

        # Display MCP breakdown (if any MCP usage)
        self.display_mcp_breakdown()

        print()
        print(f"{Colors.CYAN}Monitoring: {self.project_path}{Colors.NC}")
        print(f"{Colors.YELLOW}Press Ctrl+C to stop tracking{Colors.NC}")

        # Show recent debug messages
        if self.debug_messages:
            print()
            print(
                f"{Colors.YELLOW}═══════════════════════════════════════════════════════════════{Colors.NC}"
            )
            print(f"{Colors.BOLD}Recent Activity{Colors.NC}")
            print(
                f"{Colors.YELLOW}═══════════════════════════════════════════════════════════════{Colors.NC}"
            )
            for msg in self.debug_messages:
                print(f"  {msg}")
            print(
                f"{Colors.YELLOW}═══════════════════════════════════════════════════════════════{Colors.NC}"
            )

    def find_project_files(self, verbose=False):
        """Find all JSONL files related to this project"""
        project_files = []
        if not self.claude_dir.exists():
            if verbose:
                print(
                    f"{Colors.RED}[FILES] Claude directory does not exist: {self.claude_dir}{Colors.NC}"
                )
            return project_files

        # Get all .jsonl files in the project directory
        for file_path in self.claude_dir.glob("*.jsonl"):
            if file_path.stat().st_size > 0:  # Only include non-empty files
                project_files.append(file_path)

        if verbose:
            print(
                f"{Colors.CYAN}[FILES] Found {len(project_files)} non-empty .jsonl files{Colors.NC}"
            )
            if len(project_files) > 0 and len(project_files) <= 3:
                for f in project_files:
                    print(f"  - {f.name} ({f.stat().st_size} bytes)")

        return project_files

    def process_line(self, line, debug=False):
        """Process a single JSONL line"""
        try:
            data = json.loads(line)

            # Only process assistant messages with usage data
            if data.get("type") != "assistant":
                if debug:
                    print(f"  [DEBUG] Skipping non-assistant message (type: {data.get('type')})")
                return False

            # Extract model information (if not already detected)
            message = data.get("message", {})
            if not self.detected_model:
                model_id = message.get("model")
                if model_id:
                    self.detected_model = model_id
                    # Get human-readable name
                    if self.pricing_data:
                        model_pricing = get_model_pricing(self.pricing_data, model_id)
                        if model_pricing and "name" in model_pricing:
                            self.model_name = model_pricing["name"]
                        else:
                            self.model_name = model_id
                    else:
                        self.model_name = model_id

                    if debug:
                        print(f"  [DEBUG] Detected model: {self.model_name} ({model_id})")

            # Extract token usage from message
            usage = message.get("usage", {})
            if not usage:
                if debug:
                    print(f"  [DEBUG] Assistant message has no usage data")
                return False

            # Claude Code format uses these field names
            input_tokens = usage.get("input_tokens", 0)
            output_tokens = usage.get("output_tokens", 0)
            cache_create = usage.get("cache_creation_input_tokens", 0)
            cache_read = usage.get("cache_read_input_tokens", 0)

            if debug:
                print(
                    f"  [DEBUG] Tokens: input={input_tokens}, output={output_tokens}, "
                    f"cache_create={cache_create}, cache_read={cache_read}"
                )

            # Extract tools used in this message
            mcp_servers_used = []
            mcp_tools_used = []  # Track full tool names for tool-level stats
            builtin_tools_used = []

            content = message.get("content", [])
            if isinstance(content, list):
                for content_block in content:
                    if isinstance(content_block, dict) and content_block.get("type") == "tool_use":
                        tool_name = content_block.get("name")
                        tool_params = content_block.get("input", {})  # Extract parameters

                        if tool_name:
                            # Calculate message tokens for duplicate detection
                            message_total = input_tokens + output_tokens + cache_create + cache_read

                            # Check for duplicate calls (all tools, MCP and built-in)
                            self.detect_duplicate_call(tool_name, tool_params, message_total)

                            # Check if it's an MCP tool
                            mcp_server = extract_mcp_server(tool_name)
                            if mcp_server:
                                mcp_servers_used.append(mcp_server)
                                mcp_tools_used.append(
                                    (mcp_server, tool_name)
                                )  # Store (server, tool) pair
                                if debug:
                                    print(
                                        f"  [DEBUG] MCP tool found: {tool_name} (server: {mcp_server})"
                                    )
                            else:
                                builtin_tools_used.append(tool_name)
                                if debug:
                                    print(f"  [DEBUG] Built-in tool found: {tool_name}")

            # If we got valid counts, update totals
            if any([input_tokens, output_tokens, cache_create, cache_read]):
                self.total_input += input_tokens
                self.total_output += output_tokens
                self.total_cache_create += cache_create
                self.total_cache_read += cache_read
                self.message_count += 1

                # Attribute tokens to MCP servers (hybrid approach)
                # Each MCP server used in this message gets the full message tokens attributed
                for server in mcp_servers_used:
                    self.mcp_stats[server]["calls"] += 1
                    self.mcp_stats[server]["input_tokens"] += input_tokens
                    self.mcp_stats[server]["output_tokens"] += output_tokens
                    self.mcp_stats[server]["cache_create_tokens"] += cache_create
                    self.mcp_stats[server]["cache_read_tokens"] += cache_read
                    self.mcp_stats[server]["total_tokens"] += (
                        input_tokens + output_tokens + cache_create + cache_read
                    )

                # Track tool-level stats (NEW)
                for server, tool_name in mcp_tools_used:
                    self.mcp_tool_stats[server][tool_name]["calls"] += 1
                    self.mcp_tool_stats[server][tool_name]["input_tokens"] += input_tokens
                    self.mcp_tool_stats[server][tool_name]["output_tokens"] += output_tokens
                    self.mcp_tool_stats[server][tool_name]["cache_create_tokens"] += cache_create
                    self.mcp_tool_stats[server][tool_name]["cache_read_tokens"] += cache_read
                    self.mcp_tool_stats[server][tool_name]["total_tokens"] += (
                        input_tokens + output_tokens + cache_create + cache_read
                    )

                # Track built-in tool usage
                if builtin_tools_used:
                    self.builtin_tool_calls += len(builtin_tools_used)
                    self.builtin_tool_tokens += (
                        input_tokens + output_tokens + cache_create + cache_read
                    )

                # Detect anomalies (Gap 3)
                message_total = input_tokens + output_tokens + cache_create + cache_read
                for server, tool_name in mcp_tools_used:
                    self.detect_anomaly(tool_name, message_total, message_total)

                # Write event log
                if self.enable_logging:
                    event_data = {
                        "timestamp": datetime.now().isoformat() + "Z",
                        "type": "message",
                        "tokens": {
                            "input": input_tokens,
                            "output": output_tokens,
                            "cache_create": cache_create,
                            "cache_read": cache_read,
                        },
                        "tools_used": [tool for _, tool in mcp_tools_used] + builtin_tools_used,
                    }
                    self.write_event_log(event_data)

                return True

        except (json.JSONDecodeError, KeyError) as e:
            if debug:
                print(f"  [DEBUG] Error parsing line: {e}")
            pass

        return False

    def write_event_log(self, event_data):
        """Append event to events.jsonl"""
        if not self.enable_logging:
            return

        try:
            with open(self.events_file, "a") as f:
                f.write(json.dumps(event_data) + "\n")
        except Exception as e:
            # Silently fail - don't interrupt session tracking
            pass

    def _build_session_comparison(self, current_tokens, current_cost_usd):
        """Build session comparison data (Gap 4)

        Args:
            current_tokens: Total tokens for current session
            current_cost_usd: Total cost in USD for current session

        Returns:
            Dictionary with comparison data
        """
        comparison = {"vs_last_session": None, "vs_avg_session": None}

        if not self.previous_session_data:
            return comparison

        # Compare to previous session
        try:
            prev_tokens = self.previous_session_data["tokens"]["total"]
            prev_cost = self.previous_session_data["costs"]["with_cache"]["usd"]
            prev_duration = self.previous_session_data["session"].get("duration_seconds", 0)
            current_duration = int(time.time() - self.start_time)

            token_delta = current_tokens - prev_tokens
            token_pct = round((token_delta / prev_tokens) * 100, 1) if prev_tokens > 0 else 0

            cost_delta = current_cost_usd - prev_cost
            cost_pct = round((cost_delta / prev_cost) * 100, 1) if prev_cost > 0 else 0

            duration_delta = current_duration - prev_duration
            duration_pct = (
                round((duration_delta / prev_duration) * 100, 1) if prev_duration > 0 else 0
            )

            comparison["vs_last_session"] = {
                "tokens": {
                    "delta": token_delta,
                    "percent_change": token_pct,
                    "direction": (
                        "increase"
                        if token_delta > 0
                        else ("decrease" if token_delta < 0 else "same")
                    ),
                },
                "cost": {
                    "delta_usd": round(cost_delta, 4),
                    "percent_change": cost_pct,
                    "direction": (
                        "increase" if cost_delta > 0 else ("decrease" if cost_delta < 0 else "same")
                    ),
                },
                "duration": {
                    "delta_seconds": duration_delta,
                    "percent_change": duration_pct,
                    "direction": (
                        "longer"
                        if duration_delta > 0
                        else ("shorter" if duration_delta < 0 else "same")
                    ),
                },
            }
        except (KeyError, TypeError):
            # Previous session data incomplete
            pass

        return comparison

    def _detect_high_frequency(self):
        """Detect tools called more than HIGH_FREQUENCY_THRESHOLD times (Enhanced Anomaly Detection)"""
        # Check MCP tools
        for server_name, tools in self.mcp_tool_stats.items():
            for tool_full_name, stats in tools.items():
                if stats["calls"] > self.HIGH_FREQUENCY_THRESHOLD:
                    # Extract short tool name
                    tool_short = (
                        tool_full_name.split("__")[-1] if "__" in tool_full_name else tool_full_name
                    )

                    anomaly = {
                        "timestamp": datetime.now().isoformat() + "Z",
                        "type": "high_call_frequency",
                        "tool": tool_full_name,
                        "calls": stats["calls"],
                        "threshold": self.HIGH_FREQUENCY_THRESHOLD,
                        "severity": "info",
                    }
                    self.anomalies["high_call_frequency"].append(anomaly)

                    self.warnings.append(
                        {
                            "timestamp": anomaly["timestamp"],
                            "type": "high_call_frequency",
                            "tool": tool_full_name,
                            "message": f"{tool_full_name} called {stats['calls']} times (>{self.HIGH_FREQUENCY_THRESHOLD} threshold)",
                            "severity": "info",
                        }
                    )

    def write_summary(self):
        """Write final summary.json on exit"""
        if not self.enable_logging:
            return

        try:
            # Detect high call frequency before writing summary
            self._detect_high_frequency()

            # Calculate final costs
            costs = self.calculate_cost()
            actual_usd, actual_aud = costs["actual"]
            no_cache_usd, no_cache_aud = costs["no_cache"]
            savings_usd, savings_aud, efficiency = costs["savings"]

            # Calculate totals
            total_tokens = (
                self.total_input
                + self.total_output
                + self.total_cache_create
                + self.total_cache_read
            )

            # Build MCP summary
            mcp_summary = {
                "total_calls": sum(stats["calls"] for stats in self.mcp_stats.values()),
                "total_tokens": sum(stats["total_tokens"] for stats in self.mcp_stats.values()),
                "percentage_of_session": 0,
                "top_5_servers": [],
            }

            if total_tokens > 0:
                mcp_summary["percentage_of_session"] = round(
                    (mcp_summary["total_tokens"] / total_tokens) * 100, 1
                )

            # Get top 5 servers
            sorted_servers = sorted(
                self.mcp_stats.items(), key=lambda x: x[1]["total_tokens"], reverse=True
            )[:5]

            for server_name, stats in sorted_servers:
                avg_per_call = stats["total_tokens"] // stats["calls"] if stats["calls"] > 0 else 0
                mcp_summary["top_5_servers"].append(
                    {
                        "name": server_name,
                        "calls": stats["calls"],
                        "tokens": stats["total_tokens"],
                        "avg_per_call": avg_per_call,
                    }
                )

            # Build summary
            summary = {
                "session": {
                    "start_time": datetime.fromtimestamp(self.start_time).isoformat() + "Z",
                    "end_time": datetime.now().isoformat() + "Z",
                    "duration_seconds": int(time.time() - self.start_time),
                    "directory": self.project_path,
                    "git_branch": self.git_metadata.get("branch"),
                    "git_commit": self.git_metadata.get("commit_short"),
                    "git_status": self.git_metadata.get("status"),
                },
                "model": {"id": self.detected_model, "name": self.model_name},
                "tokens": {
                    "input": self.total_input,
                    "output": self.total_output,
                    "cache_create": self.total_cache_create,
                    "cache_read": self.total_cache_read,
                    "total": total_tokens,
                },
                "costs": {
                    "with_cache": {"usd": round(actual_usd, 4), "aud": round(actual_aud, 4)},
                    "without_cache": {"usd": round(no_cache_usd, 4), "aud": round(no_cache_aud, 4)},
                    "savings": {
                        "usd": round(savings_usd, 4),
                        "aud": round(savings_aud, 4),
                        "efficiency_percent": round(efficiency, 1),
                    },
                },
                "mcp_summary": mcp_summary,
                "builtin_tools": {
                    "total_calls": self.builtin_tool_calls,
                    "total_tokens": self.builtin_tool_tokens,
                    "percentage_of_session": (
                        round((self.builtin_tool_tokens / total_tokens) * 100, 1)
                        if total_tokens > 0
                        else 0
                    ),
                },
                # Gap 1: Error and warning tracking
                "errors": self.errors,
                "warnings": self.warnings,
                "health_status": (
                    "healthy"
                    if not self.warnings and not self.errors
                    else ("warnings_present" if self.warnings else "errors_present")
                ),
                # Gap 3: Anomaly detection
                "anomalies": self.anomalies,
                # Gap 4: Session comparison
                "session_comparison": self._build_session_comparison(total_tokens, actual_usd),
                # Efficiency Measurement: Duplicate detection
                "redundancy_analysis": {
                    "duplicate_calls": self.duplicate_calls,
                    "unique_calls": len(self.tool_call_signatures),
                    "redundant_calls": len(self.duplicate_calls),
                    "redundancy_ratio": (
                        round(len(self.duplicate_calls) / len(self.tool_call_signatures), 3)
                        if len(self.tool_call_signatures) > 0
                        else 0
                    ),
                    "total_tokens_wasted": sum(d["tokens_wasted"] for d in self.duplicate_calls),
                },
            }

            with open(self.summary_file, "w") as f:
                json.dump(summary, f, indent=2)

        except Exception as e:
            print(f"{Colors.RED}[ERROR] Failed to write summary: {e}{Colors.NC}")

    def write_mcp_breakdowns(self):
        """Write per-MCP breakdown files"""
        if not self.enable_logging:
            return

        try:
            total_tokens = (
                self.total_input
                + self.total_output
                + self.total_cache_create
                + self.total_cache_read
            )
            total_mcp_tokens = sum(stats["total_tokens"] for stats in self.mcp_stats.values())

            for server_name, server_stats in self.mcp_stats.items():
                # Build tool breakdown for this server
                tools = []
                for tool_full_name, tool_stats in self.mcp_tool_stats[server_name].items():
                    # Extract short tool name (last part after __)
                    tool_short = (
                        tool_full_name.split("__")[-1] if "__" in tool_full_name else tool_full_name
                    )

                    avg_per_call = (
                        tool_stats["total_tokens"] // tool_stats["calls"]
                        if tool_stats["calls"] > 0
                        else 0
                    )
                    pct_of_server = (
                        round((tool_stats["total_tokens"] / server_stats["total_tokens"]) * 100, 1)
                        if server_stats["total_tokens"] > 0
                        else 0
                    )

                    tools.append(
                        {
                            "tool_name": tool_short,
                            "full_name": tool_full_name,
                            "calls": tool_stats["calls"],
                            "tokens": tool_stats["total_tokens"],
                            "avg_per_call": avg_per_call,
                            "percentage_of_server": pct_of_server,
                        }
                    )

                # Sort tools by tokens (descending)
                tools.sort(key=lambda x: x["tokens"], reverse=True)

                # Calculate pre-calculated stats (Gap 2)
                avg_tokens_per_call = (
                    server_stats["total_tokens"] // server_stats["calls"]
                    if server_stats["calls"] > 0
                    else 0
                )
                num_tools = len(tools)
                avg_tokens_per_tool = (
                    server_stats["total_tokens"] // num_tools if num_tools > 0 else 0
                )

                # Find most/least expensive tools
                most_expensive = tools[0] if tools else None
                least_expensive = tools[-1] if tools else None

                # Build server breakdown
                breakdown = {
                    "server_name": server_name,
                    "session_totals": {
                        "total_calls": server_stats["calls"],
                        "total_tokens": server_stats["total_tokens"],
                        "percentage_of_session": (
                            round((server_stats["total_tokens"] / total_tokens) * 100, 1)
                            if total_tokens > 0
                            else 0
                        ),
                        "percentage_of_mcp_usage": (
                            round((server_stats["total_tokens"] / total_mcp_tokens) * 100, 1)
                            if total_mcp_tokens > 0
                            else 0
                        ),
                    },
                    "tools": tools,
                    # Gap 2: Pre-calculated statistics
                    "statistics": {
                        "avg_tokens_per_call": avg_tokens_per_call,
                        "avg_tokens_per_tool": avg_tokens_per_tool,
                        "num_tools_used": num_tools,
                        "most_expensive_tool": (
                            most_expensive["tool_name"] if most_expensive else None
                        ),
                        "least_expensive_tool": (
                            least_expensive["tool_name"] if least_expensive else None
                        ),
                        "token_distribution": {
                            "input_tokens": server_stats["input_tokens"],
                            "output_tokens": server_stats["output_tokens"],
                            "cache_create_tokens": server_stats["cache_create_tokens"],
                            "cache_read_tokens": server_stats["cache_read_tokens"],
                        },
                    },
                }

                # Write to file
                mcp_file = self.log_dir / f"mcp-{server_name}.json"
                with open(mcp_file, "w") as f:
                    json.dump(breakdown, f, indent=2)

        except Exception as e:
            print(f"{Colors.RED}[ERROR] Failed to write MCP breakdowns: {e}{Colors.NC}")

    def _signal_handler(self, signum, frame):
        """Handle Ctrl+C gracefully"""
        print(f"\n{Colors.YELLOW}[SHUTDOWN] Received interrupt signal, cleaning up...{Colors.NC}")
        self.cleanup()
        sys.exit(0)

    def _validate_mcp_files(self):
        """Validate that all MCP servers with tool calls have corresponding files"""
        if not self.enable_logging:
            return

        # Check if we have MCP stats but missing files
        if self.mcp_stats:
            missing_files = []

            for server_name in self.mcp_stats.keys():
                mcp_file = self.log_dir / f"mcp-{server_name}.json"
                if not mcp_file.exists():
                    missing_files.append(server_name)

            if missing_files:
                print(
                    f"\n{Colors.YELLOW}[WARNING] MCP tools were used but files are missing:{Colors.NC}"
                )
                for server in missing_files:
                    calls = self.mcp_stats[server]["calls"]
                    tokens = self.mcp_stats[server]["total_tokens"]
                    print(
                        f"{Colors.YELLOW}  • mcp-{server}.json (lost {calls} calls, {tokens:,} tokens){Colors.NC}"
                    )
                print(
                    f"{Colors.YELLOW}[WARNING] This may indicate the session was interrupted during cleanup.{Colors.NC}"
                )
                print(
                    f"{Colors.CYAN}[INFO] Run the analyzer to recover data from events.jsonl{Colors.NC}"
                )
            else:
                # All MCP files written successfully
                print(
                    f"{Colors.GREEN}[VALIDATION] ✓ All MCP server files written successfully{Colors.NC}"
                )

    def cleanup(self):
        """Write final logs before exit"""
        if self.enable_logging:
            print(f"\n{Colors.CYAN}[CLEANUP] Writing session logs...{Colors.NC}")
            self.write_summary()
            self.write_mcp_breakdowns()
            self._validate_mcp_files()
            print(f"{Colors.GREEN}[CLEANUP] Session logs saved to: {self.log_dir}{Colors.NC}")

    def monitor_files(self):
        """Monitor files for new content"""
        print(f"{Colors.YELLOW}Initializing session tracker...{Colors.NC}")
        print(f"{Colors.CYAN}Looking for Claude Code sessions in: {self.project_path}{Colors.NC}")
        print()

        # Initial file discovery with verbose output
        print(f"{Colors.CYAN}[STARTUP] Scanning for session files...{Colors.NC}")
        initial_files = self.find_project_files(verbose=True)
        print()

        # Initial display
        self.display_stats()

        last_update = time.time()
        update_interval = 1  # Update display every 1 second
        debug_counter = 0  # For periodic debug output
        first_iteration = True  # Track first loop iteration

        while True:
            try:
                # Find files to monitor
                files = self.find_project_files()

                # Show file count on first iteration
                if first_iteration:
                    self.add_debug(f"Started monitoring {len(files)} files:")
                    for f in files:
                        self.add_debug(f"  → {f.name[:30]}... ({f.stat().st_size} bytes)")
                    self.display_stats()  # Refresh to show the debug message
                    first_iteration = False

                # Debug output every 10 iterations (~5 seconds)
                debug_counter += 1
                if debug_counter >= 10:
                    # Show file sizes vs tracked positions
                    status_parts = []
                    for file_path in files:
                        if file_path in self.file_positions:
                            current_size = file_path.stat().st_size
                            tracked_pos = self.file_positions[file_path]
                            if current_size > tracked_pos:
                                unread = current_size - tracked_pos
                                status_parts.append(f"{file_path.name[:20]}... (+{unread}B)")

                    if status_parts:
                        self.add_debug(f"Unread data: {', '.join(status_parts[:2])}")
                    else:
                        self.add_debug(f"Monitoring {len(files)} files, all up-to-date")
                    debug_counter = 0

                for file_path in files:
                    # Initialize position for new files
                    if file_path not in self.file_positions:
                        # Start from end of file (only track NEW content)
                        try:
                            self.file_positions[file_path] = file_path.stat().st_size
                        except Exception:
                            continue

                    # Read new content
                    try:
                        with open(file_path, "r") as f:
                            # Seek to last position
                            f.seek(self.file_positions[file_path])

                            # Read new lines
                            new_content = f.read()
                            if new_content:
                                # Debug: show we found new content
                                lines = [l for l in new_content.split("\n") if l.strip()]
                                self.add_debug(f"Found {len(lines)} new lines in {file_path.name}")

                                # Process each new line
                                processed_count = 0
                                for idx, line in enumerate(lines):
                                    # Enable debug for first line in batch
                                    enable_debug = idx == 0 and len(lines) <= 5
                                    if self.process_line(line, debug=enable_debug):
                                        processed_count += 1

                                if processed_count > 0:
                                    self.add_debug(
                                        f"✓ Processed {processed_count} messages (+{self.format_number(self.total_input + self.total_output)} tokens)"
                                    )
                                    # Update display once after batch (throttled by time check below)
                                    last_update = time.time()

                            # Update position
                            self.file_positions[file_path] = f.tell()
                    except Exception as e:
                        self.add_debug(f"⚠ Error reading {file_path.name}: {str(e)[:50]}")
                        continue

                # Periodic display update even if no new data
                if time.time() - last_update > update_interval:
                    self.display_stats()
                    last_update = time.time()

                # Sleep briefly
                time.sleep(0.5)

            except KeyboardInterrupt:
                print(f"\n\n{Colors.GREEN}Session tracking stopped.{Colors.NC}\n")
                sys.exit(0)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog="cc:live",
        description="Live Session Tracker for Claude Code - Real-time token usage monitoring",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  npm run cc:live              # Start live tracking
  npm run cc:live:quiet        # Quiet mode (less output)
  npm run cc:live:no-logs      # Skip session logging
  npm run cc:help              # Show this help

Available flags:
  --quiet                      Suppress verbose output
  --no-logs                    Don't save session logs to disk
  -h, --help                   Show this help message

What it tracks:
  • Input/output tokens per message
  • Cache creation/read tokens
  • Per-MCP-server tool usage breakdown
  • Duplicate call detection (same tool + params)
  • Anomaly detection (high token usage, high variance)
  • Cost estimates (Claude Sonnet 4.5 pricing)

Output location:
  scripts/ai-mcp-audit/logs/sessions/{project}-{timestamp}/
  └── summary.json          # Session totals, redundancy analysis, anomalies
  └── mcp-{server}.json     # Per-server tool statistics
  └── events.jsonl          # Event stream (optional)

Press Ctrl+C to stop tracking and save session data.
        """,
    )

    parser.add_argument("--quiet", action="store_true", help="Suppress verbose output")
    parser.add_argument("--no-logs", action="store_true", help="Don't save session logs to disk")

    args = parser.parse_args()

    tracker = SessionTracker("wp-navigator-pro/main")
    tracker.monitor_files()
