#!/usr/bin/env python3
"""
Real-time Codex CLI session tracker for WP Navigator Pro
Monitors Codex CLI usage ONLY for this project, starting from NOW
"""

import os
import sys
import time
import json
import argparse
import atexit
import signal
import subprocess
import hashlib
from pathlib import Path
from datetime import datetime
from collections import defaultdict

# Colors
class Colors:
    GREEN = '\033[0;32m'
    BLUE = '\033[0;34m'
    YELLOW = '\033[1;33m'
    CYAN = '\033[0;36m'
    RED = '\033[0;31m'
    BOLD = '\033[1m'
    NC = '\033[0m'  # No Color

def load_model_pricing():
    """Load pricing data from model-pricing.json"""
    pricing_file = Path(__file__).parent / "model-pricing.json"

    if not pricing_file.exists():
        print(f"{Colors.YELLOW}Warning: model-pricing.json not found, using fallback pricing{Colors.NC}")
        return {
            'models': {
                'openai': {
                    'gpt-4o': {
                        'name': 'GPT-4o',
                        'input': 2.5,
                        'output': 10.0,
                        'cache_read': 1.25
                    }
                }
            },
            'exchange_rates': {
                'USD_to_AUD': 1.54
            }
        }

    try:
        with open(pricing_file, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"{Colors.RED}Error loading pricing: {e}{Colors.NC}")
        return None

def get_model_pricing(pricing_data, model_id):
    """Get pricing for a specific model ID"""
    if not pricing_data or 'models' not in pricing_data:
        return None

    # Try OpenAI models first (Codex uses OpenAI), then Claude
    for provider in ['openai', 'claude']:
        if provider in pricing_data['models']:
            if model_id in pricing_data['models'][provider]:
                return pricing_data['models'][provider][model_id]

    return None

def extract_mcp_server(tool_name):
    """Extract MCP server name from tool name

    Args:
        tool_name: Tool name from Codex session (e.g., 'mcp__fs-mcp__fs_read')

    Returns:
        MCP server name (e.g., 'fs-mcp') or None if not an MCP tool
    """
    if tool_name and tool_name.startswith('mcp__'):
        # Format: mcp__server-name__tool-name
        parts = tool_name.split('__')
        if len(parts) >= 3:
            return parts[1]  # server-name (may include -mcp suffix)
    return None

def normalize_mcp_server(server_name):
    """Normalize MCP server name across platforms

    Codex CLI uses format: mcp__fs-mcp__tool
    Claude Code uses format: mcp__fs__tool

    This normalizes both to: fs (for cross-platform compatibility)

    Args:
        server_name: Raw server name from tool call

    Returns:
        Normalized server name (without -mcp suffix)
    """
    if server_name and server_name.endswith('-mcp'):
        return server_name[:-4]
    return server_name

class CodexTracker:
    def __init__(self, project_path="wp-navigator-pro/main"):
        print(f"{Colors.CYAN}[INIT] Initializing Codex tracker for: {project_path}{Colors.NC}")

        self.project_path = project_path
        # Convert to absolute path for matching
        self.project_abs_path = os.path.abspath(os.path.expanduser(f"~/claude-code-tools/lba/plugins/{project_path}"))
        print(f"{Colors.CYAN}[INIT] Watching for directory: {self.project_abs_path}{Colors.NC}")

        self.start_time = time.time()
        self.total_input = 0
        self.total_output = 0
        self.total_cache_create = 0
        self.total_cache_read = 0
        self.message_count = 0
        self.file_positions = {}
        self.debug_messages = []
        self.max_debug_messages = 5
        self.detected_model = None  # Track detected model ID
        self.model_name = "Unknown Model"  # Human-readable model name

        # MCP server usage tracking
        self.mcp_stats = defaultdict(lambda: {
            'calls': 0,
            'input_tokens': 0,
            'output_tokens': 0,
            'cache_create_tokens': 0,
            'cache_read_tokens': 0,
            'total_tokens': 0
        })
        self.builtin_tool_calls = 0
        self.builtin_tool_tokens = 0

        # Tool-level tracking (within each MCP server)
        # Format: self.mcp_tool_stats[server_name][tool_full_name] = {...}
        self.mcp_tool_stats = defaultdict(lambda: defaultdict(lambda: {
            'calls': 0,
            'input_tokens': 0,
            'output_tokens': 0,
            'cache_create_tokens': 0,
            'cache_read_tokens': 0,
            'total_tokens': 0
        }))

        # Tool call buffering (for correlating with token counts)
        # Stores recent tool calls waiting for token attribution
        self.tool_call_buffer = []
        self.last_token_attribution = None

        # Duplicate call detection
        self.tool_call_signatures = {}  # Track tool calls by signature
        self.duplicate_calls = []  # Store duplicate call details

        # Anomaly tracking
        self.anomalies = {
            'high_token_operations': [],
            'high_call_frequency': [],
            'high_variance': [],
            'unusual_patterns': []
        }
        self.tool_token_history = defaultdict(list)  # Track token history per tool

        # Anomaly detection thresholds
        self.HIGH_TOKEN_THRESHOLD = 100000
        self.HIGH_FREQUENCY_THRESHOLD = 5
        self.HIGH_VARIANCE_RATIO = 5.0

        # Parse CLI flags
        self.quiet_mode = '--quiet' in sys.argv
        self.enable_logging = '--no-logs' not in sys.argv

        # Session logging setup
        if self.enable_logging:
            # Create session folder
            session_timestamp = datetime.now().strftime('%Y-%m-%d-%H%M%S')
            project_slug = project_path.replace('/', '-')
            session_folder_name = f"{project_slug}-codex-{session_timestamp}"

            self.log_dir = Path('scripts/ai-mcp-audit/logs/sessions') / session_folder_name
            self.log_dir.mkdir(parents=True, exist_ok=True)

            self.summary_file = self.log_dir / 'summary.json'
            self.events_file = self.log_dir / 'events.jsonl'

            print(f"{Colors.GREEN}[INIT] Logging enabled: {self.log_dir}{Colors.NC}")

            # Register cleanup handlers
            atexit.register(self.write_summary)
            atexit.register(self.write_mcp_breakdowns)
            signal.signal(signal.SIGINT, self._signal_handler)
            signal.signal(signal.SIGTERM, self._signal_handler)
        else:
            self.log_dir = None
            print(f"{Colors.YELLOW}[INIT] Logging disabled (--no-logs flag){Colors.NC}")

        # Load pricing data
        print(f"{Colors.CYAN}[INIT] Loading model pricing data...{Colors.NC}")
        self.pricing_data = load_model_pricing()
        if self.pricing_data:
            print(f"{Colors.GREEN}[INIT] Pricing data loaded successfully{Colors.NC}")
        else:
            print(f"{Colors.RED}[INIT] Failed to load pricing data{Colors.NC}")

        # Track session working directory
        self.session_cwd = None

        # Find Codex sessions directory
        codex_home = Path.home() / ".codex"
        self.sessions_dir = codex_home / "sessions"

        print(f"{Colors.CYAN}[INIT] Checking for Codex directory: {self.sessions_dir}{Colors.NC}")

        if not self.sessions_dir.exists():
            print(f"{Colors.RED}Error: Codex sessions directory not found{Colors.NC}")
            print(f"Tried: {self.sessions_dir}")
            sys.exit(1)

        print(f"{Colors.GREEN}[INIT] Found Codex sessions directory{Colors.NC}")

    def add_debug(self, message):
        """Add a debug message to the buffer"""
        timestamp = datetime.now().strftime('%H:%M:%S')
        self.debug_messages.append(f"[{timestamp}] {message}")
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

        # Fall back to default GPT-4o pricing if no model detected
        if not model_pricing:
            model_pricing = {
                'input': 2.5,
                'output': 10.0,
                'cache_read': 1.25
            }

        # Note: OpenAI doesn't have separate cache_create pricing (treated as input)
        # and cache_read is typically counted as cached_input_tokens
        # Calculate actual cost (with caching)
        cost_usd = (
            (self.total_input * model_pricing['input']) +
            (self.total_output * model_pricing['output']) +
            (self.total_cache_create * model_pricing.get('input', model_pricing['input'])) +  # Treat cache_create as input
            (self.total_cache_read * model_pricing.get('cache_read', model_pricing['input'] * 0.5))  # Cache read is cheaper
        ) / 1_000_000

        # Calculate no-cache cost (what it would cost without caching)
        # All tokens would be charged at regular rates
        no_cache_cost_usd = (
            (self.total_input + self.total_cache_create + self.total_cache_read) * model_pricing['input'] +
            (self.total_output * model_pricing['output'])
        ) / 1_000_000

        # Calculate savings
        savings_usd = no_cache_cost_usd - cost_usd
        efficiency_percent = (savings_usd / no_cache_cost_usd * 100) if no_cache_cost_usd > 0 else 0

        # Convert to AUD
        usd_to_aud = 1.54  # Default
        if self.pricing_data and 'exchange_rates' in self.pricing_data:
            usd_to_aud = self.pricing_data['exchange_rates'].get('USD_to_AUD', 1.54)

        cost_aud = cost_usd * usd_to_aud
        no_cache_cost_aud = no_cache_cost_usd * usd_to_aud
        savings_aud = savings_usd * usd_to_aud

        return {
            'actual': (cost_usd, cost_aud),
            'no_cache': (no_cache_cost_usd, no_cache_cost_aud),
            'savings': (savings_usd, savings_aud, efficiency_percent)
        }

    def display_stats(self):
        """Display current statistics"""
        elapsed = int(time.time() - self.start_time)
        minutes = elapsed // 60
        seconds = elapsed % 60

        # Clear screen (ANSI escape codes - fast, no subprocess)
        print('\033[2J\033[H', end='')

        # Header
        print(f"{Colors.BLUE}╔════════════════════════════════════════════════════════════════╗{Colors.NC}")
        print(f"{Colors.BLUE}║{Colors.NC} {Colors.BOLD}WP Navigator Pro - Live Codex CLI Tracker{Colors.NC}                  {Colors.BLUE}║{Colors.NC}")
        print(f"{Colors.BLUE}╚════════════════════════════════════════════════════════════════╝{Colors.NC}")
        print()

        start_str = datetime.fromtimestamp(self.start_time).strftime('%Y-%m-%d %H:%M:%S')
        print(f"{Colors.CYAN}Started:{Colors.NC} {start_str}")
        print(f"{Colors.CYAN}Elapsed:{Colors.NC} {minutes}m {seconds}s")
        print(f"{Colors.CYAN}Messages:{Colors.NC} {self.message_count}")
        print()

        print(f"{Colors.YELLOW}═══════════════════════════════════════════════════════════════{Colors.NC}")
        print(f"{Colors.BOLD}Token Usage (This Session){Colors.NC}")
        print(f"{Colors.YELLOW}═══════════════════════════════════════════════════════════════{Colors.NC}")

        print(f"  {'Input tokens:':<20} {self.format_number(self.total_input):>15}")
        print(f"  {'Output tokens:':<20} {self.format_number(self.total_output):>15}")
        print(f"  {'Cache created:':<20} {self.format_number(self.total_cache_create):>15}")
        print(f"  {'Cache read:':<20} {self.format_number(self.total_cache_read):>15}")

        print()
        print(f"{Colors.YELLOW}───────────────────────────────────────────────────────────────{Colors.NC}")

        total_tokens = self.total_input + self.total_output + self.total_cache_create + self.total_cache_read
        print(f"  {Colors.BOLD}{'Total tokens:':<20}{Colors.NC} {self.format_number(total_tokens):>15}")

        if total_tokens > 0 and (self.total_cache_read + self.total_cache_create) > 0:
            cache_ratio = int((self.total_cache_read / (self.total_cache_read + self.total_cache_create)) * 100)
            print(f"  {'Cache efficiency:':<20} {cache_ratio:>14}%")

        print()
        costs = self.calculate_cost()
        actual_usd, actual_aud = costs['actual']
        no_cache_usd, no_cache_aud = costs['no_cache']
        savings_usd, savings_aud, efficiency = costs['savings']

        print(f"{Colors.GREEN}═══════════════════════════════════════════════════════════════{Colors.NC}")
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
            print(f"    {Colors.BOLD}Efficiency:{Colors.NC} {Colors.YELLOW}{efficiency:.1f}% saved{Colors.NC}")

        print(f"{Colors.GREEN}═══════════════════════════════════════════════════════════════{Colors.NC}")

        # MCP breakdown
        print()
        print(f"{Colors.YELLOW}═══════════════════════════════════════════════════════════════{Colors.NC}")
        print(f"{Colors.BOLD}MCP Server Breakdown{Colors.NC}")
        print(f"{Colors.YELLOW}═══════════════════════════════════════════════════════════════{Colors.NC}")

        if self.mcp_stats:
            # Sort by total tokens (descending)
            sorted_servers = sorted(
                self.mcp_stats.items(),
                key=lambda x: x[1]['total_tokens'],
                reverse=True
            )

            for server, stats in sorted_servers:
                calls = stats['calls']
                server_tokens = stats['total_tokens']
                percentage = (server_tokens / total_tokens * 100) if total_tokens > 0 else 0

                print(f"  {Colors.CYAN}{server}:{Colors.NC}")
                print(f"    Calls: {calls:>5}  |  Tokens: {self.format_number(server_tokens):>10}  ({percentage:.1f}%)")

            # Built-in tools summary
            if self.builtin_tool_calls > 0:
                builtin_percentage = (self.builtin_tool_tokens / total_tokens * 100) if total_tokens > 0 else 0
                print()
                print(f"  {Colors.CYAN}built-in tools:{Colors.NC}")
                print(f"    Calls: {self.builtin_tool_calls:>5}  |  Tokens: {self.format_number(self.builtin_tool_tokens):>10}  ({builtin_percentage:.1f}%)")
        else:
            print(f"  {Colors.YELLOW}No MCP tools used yet{Colors.NC}")

        print(f"{Colors.YELLOW}═══════════════════════════════════════════════════════════════{Colors.NC}")

        print()
        print(f"{Colors.CYAN}Monitoring: {self.project_path}{Colors.NC}")
        print(f"{Colors.YELLOW}Press Ctrl+C to stop tracking{Colors.NC}")

        # Show recent debug messages
        if self.debug_messages:
            print()
            print(f"{Colors.YELLOW}═══════════════════════════════════════════════════════════════{Colors.NC}")
            print(f"{Colors.BOLD}Recent Activity{Colors.NC}")
            print(f"{Colors.YELLOW}═══════════════════════════════════════════════════════════════{Colors.NC}")
            for msg in self.debug_messages:
                print(f"  {msg}")
            print(f"{Colors.YELLOW}═══════════════════════════════════════════════════════════════{Colors.NC}")

    def find_recent_session_files(self):
        """Find recent session files (today + yesterday)"""
        files = []

        # Look in year/month/day structure
        for year_dir in sorted(self.sessions_dir.iterdir(), reverse=True):
            if not year_dir.is_dir():
                continue

            for month_dir in sorted(year_dir.iterdir(), reverse=True):
                if not month_dir.is_dir():
                    continue

                for day_dir in sorted(month_dir.iterdir(), reverse=True):
                    if not day_dir.is_dir():
                        continue

                    # Get all .jsonl files in this day
                    for file_path in day_dir.glob("*.jsonl"):
                        if file_path.stat().st_size > 0:
                            files.append(file_path)

            # Only check most recent 2 days
            if len(files) > 0:
                break

        return files

    def process_line(self, line, debug=False):
        """Process a single JSONL line"""
        try:
            data = json.loads(line)
            entry_type = data.get('type')
            timestamp = data.get('timestamp', '')

            # Check for session_meta to get working directory
            if entry_type == 'session_meta':
                cwd = data.get('payload', {}).get('cwd', '')
                if cwd and self.project_abs_path in cwd:
                    self.session_cwd = cwd
                    if debug:
                        self.add_debug(f"✓ Found matching session: {os.path.basename(cwd)}")
                return False

            # Process response_item entries (function calls)
            if entry_type == 'response_item':
                payload = data.get('payload', {})
                payload_type = payload.get('type')

                # Extract function calls
                if payload_type == 'function_call':
                    tool_name = payload.get('name', '')
                    call_id = payload.get('call_id', '')
                    arguments = payload.get('arguments', '{}')

                    if tool_name:
                        # Determine if MCP or built-in
                        mcp_server = extract_mcp_server(tool_name)
                        normalized_server = normalize_mcp_server(mcp_server) if mcp_server else None

                        # Buffer for correlation with upcoming token count
                        tool_call = {
                            'timestamp': timestamp,
                            'tool_name': tool_name,
                            'call_id': call_id,
                            'mcp_server': normalized_server,  # None for built-in tools
                            'is_mcp': bool(mcp_server),
                            'arguments': arguments
                        }
                        self.tool_call_buffer.append(tool_call)

                        # Keep buffer size reasonable (last 10 calls)
                        if len(self.tool_call_buffer) > 10:
                            self.tool_call_buffer.pop(0)

                        if debug:
                            tool_type = f"MCP ({normalized_server})" if mcp_server else "built-in"
                            self.add_debug(f"✓ Buffered {tool_type} call: {tool_name[:30]}")

                return False

            # Only process event_msg entries with token data
            if entry_type != 'event_msg':
                return False

            # Extract token usage from event_msg
            payload = data.get('payload')
            if not payload or not isinstance(payload, dict):
                if debug:
                    self.add_debug(f"No payload or wrong type: {type(payload)}")
                return False

            info = payload.get('info')
            if not info or not isinstance(info, dict):
                if debug:
                    # Show what keys are available in payload
                    keys = list(payload.keys()) if isinstance(payload, dict) else []
                    self.add_debug(f"No info in payload. Keys: {keys}")
                return False

            # Extract model information (if not already detected)
            if not self.detected_model:
                model_id = info.get('model')
                if model_id:
                    self.detected_model = model_id
                    # Get human-readable name
                    if self.pricing_data:
                        model_pricing = get_model_pricing(self.pricing_data, model_id)
                        if model_pricing and 'name' in model_pricing:
                            self.model_name = model_pricing['name']
                        else:
                            self.model_name = model_id
                    else:
                        self.model_name = model_id

                    if debug:
                        self.add_debug(f"✓ Detected model: {self.model_name} ({model_id})")

            # Try last_token_usage first (most recent operation)
            last_usage = info.get('last_token_usage')
            if not last_usage:
                # Try total_token_usage as fallback
                last_usage = info.get('total_token_usage')

            if last_usage and isinstance(last_usage, dict):
                input_tokens = last_usage.get('input_tokens', 0)
                output_tokens = last_usage.get('output_tokens', 0)
                cached_input = last_usage.get('cached_input_tokens', 0)

                if debug:
                    self.add_debug(f"✓ Tokens: in={input_tokens}, out={output_tokens}, cache={cached_input}")

                # Attribute tokens to buffered tool calls
                if self.tool_call_buffer:
                    self._attribute_tokens_to_tools(
                        input_tokens, output_tokens, 0, cached_input,
                        timestamp
                    )

                # Update totals
                if any([input_tokens, output_tokens, cached_input]):
                    self.total_input += input_tokens
                    self.total_output += output_tokens
                    self.total_cache_read += cached_input
                    self.message_count += 1
                    return True
            else:
                if debug:
                    # Show what's in info
                    info_keys = list(info.keys()) if isinstance(info, dict) else []
                    self.add_debug(f"No token usage. Info keys: {info_keys}")

        except (json.JSONDecodeError, KeyError, AttributeError, TypeError) as e:
            if debug:
                self.add_debug(f"⚠ Error: {type(e).__name__}: {str(e)[:60]}")

        return False

    def _attribute_tokens_to_tools(self, input_tokens, output_tokens, cache_create, cache_read, timestamp):
        """Attribute token usage to buffered tool calls"""
        if not self.tool_call_buffer:
            return

        # Attribute tokens to all buffered tools (sequential buffering approach)
        for tool_call in self.tool_call_buffer:
            tool_name = tool_call['tool_name']
            mcp_server = tool_call['mcp_server']
            is_mcp = tool_call['is_mcp']

            total_tokens = input_tokens + output_tokens + cache_create + cache_read

            if is_mcp and mcp_server:
                # MCP tool - attribute to server and tool
                self.mcp_stats[mcp_server]['calls'] += 1
                self.mcp_stats[mcp_server]['input_tokens'] += input_tokens
                self.mcp_stats[mcp_server]['output_tokens'] += output_tokens
                self.mcp_stats[mcp_server]['cache_create_tokens'] += cache_create
                self.mcp_stats[mcp_server]['cache_read_tokens'] += cache_read
                self.mcp_stats[mcp_server]['total_tokens'] += total_tokens

                # Tool-level tracking
                self.mcp_tool_stats[mcp_server][tool_name]['calls'] += 1
                self.mcp_tool_stats[mcp_server][tool_name]['input_tokens'] += input_tokens
                self.mcp_tool_stats[mcp_server][tool_name]['output_tokens'] += output_tokens
                self.mcp_tool_stats[mcp_server][tool_name]['cache_create_tokens'] += cache_create
                self.mcp_tool_stats[mcp_server][tool_name]['cache_read_tokens'] += cache_read
                self.mcp_tool_stats[mcp_server][tool_name]['total_tokens'] += total_tokens
            else:
                # Built-in tool
                self.builtin_tool_calls += 1
                self.builtin_tool_tokens += total_tokens

        # Clear buffer after attribution
        self.tool_call_buffer = []

    def _signal_handler(self, signum, frame):
        """Handle Ctrl+C gracefully"""
        print(f"\n\n{Colors.YELLOW}Stopping tracker and writing session logs...{Colors.NC}")
        self.write_summary()
        self.write_mcp_breakdowns()
        print(f"{Colors.GREEN}Session logs saved to: {self.log_dir}{Colors.NC}\n")
        sys.exit(0)

    def write_summary(self):
        """Write session summary to summary.json"""
        if not self.enable_logging or not self.log_dir:
            return

        elapsed = int(time.time() - self.start_time)
        total_tokens = self.total_input + self.total_output + self.total_cache_create + self.total_cache_read

        # Calculate cost
        costs = self.calculate_cost()
        actual_usd, actual_aud = costs['actual']

        summary = {
            'session': {
                'project': self.project_path,
                'start_time': datetime.fromtimestamp(self.start_time).isoformat(),
                'end_time': datetime.now().isoformat(),
                'duration_seconds': elapsed,
                'model': self.model_name,
                'model_id': self.detected_model
            },
            'tokens': {
                'input': self.total_input,
                'output': self.total_output,
                'cache_create': self.total_cache_create,
                'cache_read': self.total_cache_read,
                'total': total_tokens
            },
            'cost': {
                'usd': round(actual_usd, 4),
                'aud': round(actual_aud, 4)
            },
            'messages': self.message_count,
            'mcp_servers': {
                server: {
                    'calls': stats['calls'],
                    'total_tokens': stats['total_tokens'],
                    'percentage': round((stats['total_tokens'] / total_tokens * 100), 2) if total_tokens > 0 else 0
                }
                for server, stats in self.mcp_stats.items()
            },
            'builtin_tools': {
                'calls': self.builtin_tool_calls,
                'total_tokens': self.builtin_tool_tokens,
                'percentage': round((self.builtin_tool_tokens / total_tokens * 100), 2) if total_tokens > 0 else 0
            }
        }

        try:
            with open(self.summary_file, 'w') as f:
                json.dump(summary, f, indent=2)
        except Exception as e:
            print(f"{Colors.RED}Error writing summary: {e}{Colors.NC}")

    def write_mcp_breakdowns(self):
        """Write per-MCP-server breakdown files"""
        if not self.enable_logging or not self.log_dir:
            return

        for server, stats in self.mcp_stats.items():
            # Get tool-level stats for this server
            tools = {}
            if server in self.mcp_tool_stats:
                for tool_name, tool_stats in self.mcp_tool_stats[server].items():
                    tools[tool_name] = {
                        'calls': tool_stats['calls'],
                        'input_tokens': tool_stats['input_tokens'],
                        'output_tokens': tool_stats['output_tokens'],
                        'cache_read_tokens': tool_stats['cache_read_tokens'],
                        'total_tokens': tool_stats['total_tokens'],
                        'percentage': round((tool_stats['total_tokens'] / stats['total_tokens'] * 100), 2) if stats['total_tokens'] > 0 else 0
                    }

            breakdown = {
                'server': server,
                'summary': stats,
                'tools': tools
            }

            filename = self.log_dir / f'mcp-{server}.json'
            try:
                with open(filename, 'w') as f:
                    json.dump(breakdown, f, indent=2)
            except Exception as e:
                print(f"{Colors.RED}Error writing {server} breakdown: {e}{Colors.NC}")

    def monitor_files(self):
        """Monitor files for new content"""
        print(f"{Colors.YELLOW}Initializing Codex session tracker...{Colors.NC}")
        print(f"{Colors.CYAN}Looking for Codex sessions in: {self.project_path}{Colors.NC}")
        print()

        # Initial file discovery
        print(f"{Colors.CYAN}[STARTUP] Scanning for session files...{Colors.NC}")
        initial_files = self.find_recent_session_files()
        print(f"{Colors.GREEN}Found {len(initial_files)} recent session files{Colors.NC}")
        print()

        # Initial display
        self.display_stats()

        last_update = time.time()
        update_interval = 1
        debug_counter = 0
        first_iteration = True

        while True:
            try:
                # Find files to monitor
                files = self.find_recent_session_files()

                # Show file count on first iteration
                if first_iteration:
                    self.add_debug(f"Started monitoring {len(files)} files")
                    for f in files[:3]:  # Show first 3
                        self.add_debug(f"  → {f.name[:40]}...")
                    self.display_stats()
                    first_iteration = False

                # Status update every 10 iterations (~5 seconds)
                debug_counter += 1
                if debug_counter >= 10:
                    status_parts = []
                    for file_path in files:
                        if file_path in self.file_positions:
                            current_size = file_path.stat().st_size
                            tracked_pos = self.file_positions[file_path]
                            if current_size > tracked_pos:
                                unread = current_size - tracked_pos
                                status_parts.append(f"{file_path.name[:20]}... (+{unread}B)")

                    if status_parts:
                        self.add_debug(f"Unread: {', '.join(status_parts[:2])}")
                    else:
                        self.add_debug(f"Monitoring {len(files)} files, all up-to-date")
                    debug_counter = 0

                for file_path in files:
                    # Initialize position at END (only track NEW content)
                    if file_path not in self.file_positions:
                        try:
                            self.file_positions[file_path] = file_path.stat().st_size
                        except Exception:
                            continue

                    # Read new content
                    try:
                        with open(file_path, 'r') as f:
                            f.seek(self.file_positions[file_path])
                            new_content = f.read()

                            if new_content:
                                lines = [l for l in new_content.split('\n') if l.strip()]
                                self.add_debug(f"Found {len(lines)} new lines in {file_path.name[:20]}...")

                                processed_count = 0
                                for idx, line in enumerate(lines):
                                    enable_debug = (idx == 0 and len(lines) <= 5)
                                    if self.process_line(line, debug=enable_debug):
                                        processed_count += 1

                                if processed_count > 0:
                                    total = self.total_input + self.total_output
                                    self.add_debug(f"✓ Processed {processed_count} messages (+{self.format_number(total)} tokens)")
                                    # Update display once after batch (throttled by time check below)
                                    last_update = time.time()

                            self.file_positions[file_path] = f.tell()
                    except Exception as e:
                        self.add_debug(f"⚠ Error reading {file_path.name[:20]}: {type(e).__name__}: {str(e)[:40]}")
                        continue

                # Periodic display update
                if time.time() - last_update > update_interval:
                    self.display_stats()
                    last_update = time.time()

                time.sleep(0.5)

            except KeyboardInterrupt:
                print(f"\n\n{Colors.GREEN}Codex session tracking stopped.{Colors.NC}\n")
                sys.exit(0)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog='codex:live',
        description='Live Session Tracker for Codex CLI - Real-time token usage monitoring',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  npm run codex:live           # Start live tracking for Codex CLI
  npm run codex:help           # Show this help

What it tracks:
  • Input/output tokens per message
  • Reasoning tokens (o1/o3 models)
  • Cached input tokens
  • Cost estimates (current model pricing)

Output location:
  scripts/ai-mcp-audit/logs/sessions/{project}-{timestamp}/
  └── summary.json          # Session totals and statistics

Press Ctrl+C to stop tracking and save session data.
        """
    )

    args = parser.parse_args()

    tracker = CodexTracker("wp-navigator-pro/main")
    tracker.monitor_files()
