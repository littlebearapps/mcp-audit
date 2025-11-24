#!/usr/bin/env python3
"""
Cross-Session MCP Efficiency Analyzer
Analyzes MCP tool usage across multiple sessions to identify patterns and inefficiencies
"""

import os
import sys
import json
import csv
import argparse
from pathlib import Path
from datetime import datetime
from collections import defaultdict
from statistics import mean, median, stdev


# Colors for terminal output
class Colors:
    GREEN = "\033[0;32m"
    BLUE = "\033[0;34m"
    YELLOW = "\033[1;33m"
    CYAN = "\033[0;36m"
    RED = "\033[0;31m"
    BOLD = "\033[1m"
    NC = "\033[0m"  # No Color


class MCPEfficiencyAnalyzer:
    """Analyze MCP tool efficiency across multiple sessions"""

    def __init__(self, sessions_dir="scripts/ai-mcp-audit/logs/sessions"):
        self.sessions_dir = Path(sessions_dir)
        self.sessions = []
        self.tool_stats = defaultdict(
            lambda: {
                "total_calls": 0,
                "total_tokens": 0,
                "session_count": 0,
                "token_values": [],  # Track all token values for variance
                "servers": set(),  # Which servers provide this tool
                "sessions_used": [],  # Which sessions used this tool
            }
        )

        # Thresholds for outlier detection
        self.HIGH_AVG_THRESHOLD = 100000  # 100K avg tokens
        self.HIGH_FREQ_THRESHOLD = 10  # >10 calls per session average
        self.HIGH_VARIANCE_RATIO = 5.0  # Max/min > 5x

    def load_sessions(self):
        """Load all session data from logs directory"""
        if not self.sessions_dir.exists():
            print(
                f"{Colors.RED}Error: Sessions directory not found: {self.sessions_dir}{Colors.NC}"
            )
            return False

        # Find all session folders
        session_folders = [f for f in self.sessions_dir.iterdir() if f.is_dir()]

        if not session_folders:
            print(
                f"{Colors.YELLOW}Warning: No session folders found in {self.sessions_dir}{Colors.NC}"
            )
            return False

        print(f"{Colors.CYAN}Found {len(session_folders)} session folders{Colors.NC}")

        # Load each session
        for session_folder in session_folders:
            session_data = self._load_session(session_folder)
            if session_data:
                self.sessions.append(session_data)

        print(f"{Colors.GREEN}Loaded {len(self.sessions)} sessions successfully{Colors.NC}")
        return len(self.sessions) > 0

    def _load_session(self, session_folder):
        """Load a single session's data"""
        session_data = {"folder": session_folder.name, "summary": None, "mcp_servers": {}}

        # Load summary.json
        summary_file = session_folder / "summary.json"
        if summary_file.exists():
            try:
                with open(summary_file, "r") as f:
                    session_data["summary"] = json.load(f)
            except Exception as e:
                print(f"{Colors.YELLOW}Warning: Failed to load {summary_file}: {e}{Colors.NC}")
                return None
        else:
            # Try to recover from events.jsonl if summary is missing
            events_file = session_folder / "events.jsonl"
            if events_file.exists():
                print(
                    f"{Colors.CYAN}Attempting recovery for {session_folder.name} from events.jsonl{Colors.NC}"
                )
                session_data = self._recover_from_events(session_folder, session_data)
                if session_data is None:
                    return None
            else:
                # No summary and no events - skip this session
                return None

        # Load all mcp-*.json files
        for mcp_file in session_folder.glob("mcp-*.json"):
            server_name = mcp_file.stem.replace("mcp-", "")
            try:
                with open(mcp_file, "r") as f:
                    session_data["mcp_servers"][server_name] = json.load(f)
            except Exception as e:
                print(f"{Colors.YELLOW}Warning: Failed to load {mcp_file}: {e}{Colors.NC}")

        return session_data

    def _recover_from_events(self, session_folder, session_data):
        """Recover session data from events.jsonl when summary.json is missing"""
        events_file = session_folder / "events.jsonl"

        try:
            # Track MCP tools used
            mcp_tools = defaultdict(lambda: defaultdict(lambda: {"calls": 0, "tokens": 0}))

            with open(events_file, "r") as f:
                for line in f:
                    try:
                        event = json.loads(line.strip())
                        tools_used = event.get("tools_used", [])
                        tokens = event.get("tokens", {})

                        # Calculate total tokens for this event
                        event_tokens = (
                            tokens.get("input", 0)
                            + tokens.get("output", 0)
                            + tokens.get("cache_create", 0)
                            + tokens.get("cache_read", 0)
                        )

                        # Process each tool
                        for tool in tools_used:
                            # Check if it's an MCP tool (starts with mcp__)
                            if tool.startswith("mcp__"):
                                # Extract server name (e.g., mcp__zen__ -> zen)
                                parts = tool.split("__")
                                if len(parts) >= 3:
                                    server_name = parts[1].replace("-mcp", "")  # Handle -mcp suffix
                                    tool_name = "__".join(parts[2:])
                                    full_name = tool

                                    mcp_tools[server_name][full_name]["calls"] += 1
                                    mcp_tools[server_name][full_name]["tokens"] += event_tokens

                    except json.JSONDecodeError:
                        continue  # Skip malformed lines

            # Convert to mcp_servers format
            if mcp_tools:
                for server_name, tools in mcp_tools.items():
                    session_data["mcp_servers"][server_name] = {
                        "tools": [
                            {
                                "full_name": tool_name,
                                "calls": stats["calls"],
                                "tokens": stats["tokens"],
                            }
                            for tool_name, stats in tools.items()
                        ]
                    }
                print(
                    f"{Colors.GREEN}✓ Recovered {len(mcp_tools)} MCP server(s) from events{Colors.NC}"
                )
            else:
                print(
                    f"{Colors.YELLOW}⚠ No MCP tools found in events (session used built-in tools only){Colors.NC}"
                )

            return session_data

        except Exception as e:
            print(f"{Colors.RED}Error recovering from events: {e}{Colors.NC}")
            return None

    def aggregate_tool_stats(self):
        """Aggregate statistics per tool across all sessions"""
        print(f"\n{Colors.CYAN}Aggregating tool statistics...{Colors.NC}")

        for session in self.sessions:
            for server_name, server_data in session["mcp_servers"].items():
                tools = server_data.get("tools", [])

                for tool in tools:
                    tool_name = tool["full_name"]
                    calls = tool["calls"]
                    tokens = tool["tokens"]

                    # Aggregate stats
                    self.tool_stats[tool_name]["total_calls"] += calls
                    self.tool_stats[tool_name]["total_tokens"] += tokens
                    self.tool_stats[tool_name]["session_count"] += 1
                    self.tool_stats[tool_name]["servers"].add(server_name)
                    self.tool_stats[tool_name]["sessions_used"].append(session["folder"])

                    # Track individual token values for variance calculation
                    # Approximate: divide total tokens by calls to get per-call average
                    avg_per_call = tokens // calls if calls > 0 else 0
                    for _ in range(calls):
                        self.tool_stats[tool_name]["token_values"].append(avg_per_call)

        print(f"{Colors.GREEN}Aggregated {len(self.tool_stats)} unique tools{Colors.NC}")

    def calculate_derived_stats(self):
        """Calculate averages, variance, etc."""
        for tool_name, stats in self.tool_stats.items():
            # Average tokens per call
            stats["avg_tokens_per_call"] = (
                stats["total_tokens"] // stats["total_calls"] if stats["total_calls"] > 0 else 0
            )

            # Average calls per session
            stats["avg_calls_per_session"] = (
                stats["total_calls"] / stats["session_count"] if stats["session_count"] > 0 else 0
            )

            # Variance (if we have enough data)
            if len(stats["token_values"]) >= 3:
                stats["min_tokens"] = min(stats["token_values"])
                stats["max_tokens"] = max(stats["token_values"])
                stats["median_tokens"] = median(stats["token_values"])
                stats["variance_ratio"] = (
                    stats["max_tokens"] / stats["min_tokens"] if stats["min_tokens"] > 0 else 0
                )

                # Standard deviation (if enough variance)
                if len(stats["token_values"]) > 1:
                    try:
                        stats["stdev_tokens"] = stdev(stats["token_values"])
                    except:
                        stats["stdev_tokens"] = 0
                else:
                    stats["stdev_tokens"] = 0
            else:
                stats["min_tokens"] = 0
                stats["max_tokens"] = 0
                stats["median_tokens"] = 0
                stats["variance_ratio"] = 0
                stats["stdev_tokens"] = 0

    def identify_outliers(self):
        """Identify outlier tools based on thresholds"""
        outliers = {
            "high_avg_tokens": [],
            "high_frequency": [],
            "high_variance": [],
            "top_expensive": [],
            "top_frequent": [],
        }

        for tool_name, stats in self.tool_stats.items():
            # High average tokens
            if stats["avg_tokens_per_call"] > self.HIGH_AVG_THRESHOLD:
                outliers["high_avg_tokens"].append((tool_name, stats))

            # High call frequency
            if stats["avg_calls_per_session"] > self.HIGH_FREQ_THRESHOLD:
                outliers["high_frequency"].append((tool_name, stats))

            # High variance
            if stats["variance_ratio"] > self.HIGH_VARIANCE_RATIO:
                outliers["high_variance"].append((tool_name, stats))

        # Top 10 most expensive (by total tokens)
        sorted_by_tokens = sorted(
            self.tool_stats.items(), key=lambda x: x[1]["total_tokens"], reverse=True
        )
        outliers["top_expensive"] = sorted_by_tokens[:10]

        # Top 10 most frequent (by total calls)
        sorted_by_calls = sorted(
            self.tool_stats.items(), key=lambda x: x[1]["total_calls"], reverse=True
        )
        outliers["top_frequent"] = sorted_by_calls[:10]

        return outliers

    def display_report(self):
        """Display analysis report to terminal"""
        print(f"\n{Colors.BLUE}{'═' * 80}{Colors.NC}")
        print(f"{Colors.BOLD}MCP Efficiency Analysis Report{Colors.NC}")
        print(f"{Colors.BLUE}{'═' * 80}{Colors.NC}\n")

        print(f"{Colors.CYAN}Sessions Analyzed:{Colors.NC} {len(self.sessions)}")
        print(f"{Colors.CYAN}Unique Tools:{Colors.NC} {len(self.tool_stats)}")
        print(
            f"{Colors.CYAN}Total Tool Calls:{Colors.NC} {sum(s['total_calls'] for s in self.tool_stats.values()):,}"
        )
        print(
            f"{Colors.CYAN}Total Tokens:{Colors.NC} {sum(s['total_tokens'] for s in self.tool_stats.values()):,}"
        )

        # Get outliers
        outliers = self.identify_outliers()

        # 1. Top 10 Most Expensive Tools (by total tokens)
        print(f"\n{Colors.YELLOW}{'─' * 80}{Colors.NC}")
        print(f"{Colors.BOLD}Top 10 Most Expensive Tools (Total Tokens){Colors.NC}")
        print(f"{Colors.YELLOW}{'─' * 80}{Colors.NC}")
        print(f"{'Tool':<50} {'Calls':>8} {'Tokens':>12} {'Avg/Call':>12}")
        print(f"{Colors.YELLOW}{'─' * 80}{Colors.NC}")

        for tool_name, stats in outliers["top_expensive"]:
            short_name = tool_name.split("__")[-1] if "__" in tool_name else tool_name
            print(
                f"{short_name[:50]:<50} {stats['total_calls']:>8,} {stats['total_tokens']:>12,} {stats['avg_tokens_per_call']:>12,}"
            )

        # 2. Top 10 Most Frequent Tools (by total calls)
        print(f"\n{Colors.YELLOW}{'─' * 80}{Colors.NC}")
        print(f"{Colors.BOLD}Top 10 Most Frequent Tools (Total Calls){Colors.NC}")
        print(f"{Colors.YELLOW}{'─' * 80}{Colors.NC}")
        print(f"{'Tool':<50} {'Calls':>8} {'Sessions':>10} {'Avg/Session':>12}")
        print(f"{Colors.YELLOW}{'─' * 80}{Colors.NC}")

        for tool_name, stats in outliers["top_frequent"]:
            short_name = tool_name.split("__")[-1] if "__" in tool_name else tool_name
            print(
                f"{short_name[:50]:<50} {stats['total_calls']:>8,} {stats['session_count']:>10} {stats['avg_calls_per_session']:>12.1f}"
            )

        # 3. High Average Tokens (>100K)
        if outliers["high_avg_tokens"]:
            print(f"\n{Colors.RED}{'─' * 80}{Colors.NC}")
            print(
                f"{Colors.BOLD}{Colors.RED}⚠️  Tools with High Average Tokens (>{self.HIGH_AVG_THRESHOLD:,}){Colors.NC}"
            )
            print(f"{Colors.RED}{'─' * 80}{Colors.NC}")
            print(f"{'Tool':<50} {'Avg Tokens/Call':>15}")
            print(f"{Colors.RED}{'─' * 80}{Colors.NC}")

            for tool_name, stats in outliers["high_avg_tokens"]:
                short_name = tool_name.split("__")[-1] if "__" in tool_name else tool_name
                print(f"{short_name[:50]:<50} {stats['avg_tokens_per_call']:>15,}")
        else:
            print(
                f"\n{Colors.GREEN}✓ No tools with high average tokens (all <{self.HIGH_AVG_THRESHOLD:,}){Colors.NC}"
            )

        # 4. High Frequency (>10 calls/session)
        if outliers["high_frequency"]:
            print(f"\n{Colors.RED}{'─' * 80}{Colors.NC}")
            print(
                f"{Colors.BOLD}{Colors.RED}⚠️  Tools with High Call Frequency (>{self.HIGH_FREQ_THRESHOLD} calls/session){Colors.NC}"
            )
            print(f"{Colors.RED}{'─' * 80}{Colors.NC}")
            print(f"{'Tool':<50} {'Avg Calls/Session':>17}")
            print(f"{Colors.RED}{'─' * 80}{Colors.NC}")

            for tool_name, stats in outliers["high_frequency"]:
                short_name = tool_name.split("__")[-1] if "__" in tool_name else tool_name
                print(f"{short_name[:50]:<50} {stats['avg_calls_per_session']:>17.1f}")
        else:
            print(
                f"\n{Colors.GREEN}✓ No tools with high call frequency (all <{self.HIGH_FREQ_THRESHOLD} calls/session){Colors.NC}"
            )

        # 5. High Variance (>5x difference)
        if outliers["high_variance"]:
            print(f"\n{Colors.YELLOW}{'─' * 80}{Colors.NC}")
            print(
                f"{Colors.BOLD}Tools with High Token Variance ({self.HIGH_VARIANCE_RATIO}x+ difference){Colors.NC}"
            )
            print(f"{Colors.YELLOW}{'─' * 80}{Colors.NC}")
            print(f"{'Tool':<40} {'Min':>10} {'Max':>10} {'Ratio':>8}")
            print(f"{Colors.YELLOW}{'─' * 80}{Colors.NC}")

            for tool_name, stats in outliers["high_variance"]:
                short_name = tool_name.split("__")[-1] if "__" in tool_name else tool_name
                print(
                    f"{short_name[:40]:<40} {stats['min_tokens']:>10,} {stats['max_tokens']:>10,} {stats['variance_ratio']:>8.1f}x"
                )
        else:
            print(
                f"\n{Colors.GREEN}✓ No tools with high variance (all <{self.HIGH_VARIANCE_RATIO}x){Colors.NC}"
            )

        print(f"\n{Colors.BLUE}{'═' * 80}{Colors.NC}\n")

    def export_csv(self, output_file="mcp-efficiency-report.csv"):
        """Export full analysis to CSV"""
        output_path = Path(output_file)

        # Prepare data for export
        rows = []
        for tool_name, stats in sorted(
            self.tool_stats.items(), key=lambda x: x[1]["total_tokens"], reverse=True
        ):
            rows.append(
                {
                    "tool_name": tool_name,
                    "short_name": tool_name.split("__")[-1] if "__" in tool_name else tool_name,
                    "servers": ",".join(sorted(stats["servers"])),
                    "total_calls": stats["total_calls"],
                    "total_tokens": stats["total_tokens"],
                    "session_count": stats["session_count"],
                    "avg_tokens_per_call": stats["avg_tokens_per_call"],
                    "avg_calls_per_session": round(stats["avg_calls_per_session"], 2),
                    "min_tokens": stats["min_tokens"],
                    "max_tokens": stats["max_tokens"],
                    "median_tokens": stats["median_tokens"],
                    "variance_ratio": round(stats["variance_ratio"], 2),
                    "stdev_tokens": round(stats["stdev_tokens"], 2),
                    "high_avg_outlier": (
                        "YES" if stats["avg_tokens_per_call"] > self.HIGH_AVG_THRESHOLD else "NO"
                    ),
                    "high_freq_outlier": (
                        "YES" if stats["avg_calls_per_session"] > self.HIGH_FREQ_THRESHOLD else "NO"
                    ),
                    "high_variance_outlier": (
                        "YES" if stats["variance_ratio"] > self.HIGH_VARIANCE_RATIO else "NO"
                    ),
                    "sessions_used": ";".join(stats["sessions_used"]),
                }
            )

        # Write CSV
        with open(output_path, "w", newline="") as f:
            fieldnames = [
                "tool_name",
                "short_name",
                "servers",
                "total_calls",
                "total_tokens",
                "session_count",
                "avg_tokens_per_call",
                "avg_calls_per_session",
                "min_tokens",
                "max_tokens",
                "median_tokens",
                "variance_ratio",
                "stdev_tokens",
                "high_avg_outlier",
                "high_freq_outlier",
                "high_variance_outlier",
                "sessions_used",
            ]
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)

        print(f"{Colors.GREEN}✓ Exported detailed report to: {output_path}{Colors.NC}")

        return str(output_path)


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        prog="mcp:analyze",
        description="MCP Efficiency Analyzer - Cross-session tool usage analysis",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  npm run mcp:analyze                           # Analyze all sessions
  npm run mcp:help                              # Show this help
  python3 scripts/ai-mcp-audit/analyze-mcp-efficiency.py /custom/path

What it analyzes:
  • Tool usage patterns across all sessions
  • Token consumption per tool (total, average, variance)
  • Call frequency per tool
  • Outlier detection:
    - High average tokens (>100K per call)
    - High call frequency (>10 calls/session)
    - High variance (>5x difference min/max)

Output:
  • Terminal report with formatted tables
  • CSV export: mcp-efficiency-report.csv
    - Complete statistics for all tools
    - Sortable in spreadsheet applications
    - Outlier flags for easy filtering

Input:
  Reads from: scripts/ai-mcp-audit/logs/sessions/
  Each session folder contains:
    - summary.json (session totals, redundancy, anomalies)
    - mcp-{server}.json (per-server tool stats)

Requirements:
  • At least 1 completed session (run npm run cc:live first)
  • Session must have finished (Ctrl+C to stop tracker)
        """,
    )

    parser.add_argument(
        "sessions_dir",
        nargs="?",
        default="scripts/ai-mcp-audit/logs/sessions",
        help="Directory containing session folders (default: scripts/ai-mcp-audit/logs/sessions)",
    )

    args = parser.parse_args()

    print(f"{Colors.BOLD}MCP Efficiency Analyzer{Colors.NC}")
    print(f"{Colors.CYAN}Analyzing cross-session MCP tool usage...{Colors.NC}\n")

    # Create analyzer
    analyzer = MCPEfficiencyAnalyzer(args.sessions_dir)

    # Load sessions
    if not analyzer.load_sessions():
        print(f"{Colors.RED}No sessions to analyze. Exiting.{Colors.NC}")
        sys.exit(1)

    # Aggregate stats
    analyzer.aggregate_tool_stats()

    # Calculate derived stats
    analyzer.calculate_derived_stats()

    # Display report
    analyzer.display_report()

    # Export to CSV
    csv_file = analyzer.export_csv()

    print(f"\n{Colors.BOLD}Analysis Complete!{Colors.NC}")
    print(f"{Colors.CYAN}View full data in: {csv_file}{Colors.NC}\n")


if __name__ == "__main__":
    main()
