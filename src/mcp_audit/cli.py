#!/usr/bin/env python3
"""
MCP Analyze CLI - Command-line interface for MCP Audit

Provides commands for collecting MCP session data and generating reports.
"""

import argparse
import sys
from pathlib import Path

from . import __version__


def main() -> int:
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        prog="mcp-audit",
        description="MCP Audit - Multi-platform MCP usage tracking and cost analysis",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Collect session data under Claude Code
  mcp-audit collect --platform claude-code --output ./session-data

  # Collect session data under Codex CLI
  mcp-audit collect --platform codex-cli --output ./session-data

  # Collect session data under Gemini CLI (requires telemetry enabled)
  mcp-audit collect --platform gemini-cli --output ./session-data

  # Generate report from session data
  mcp-audit report ./session-data --format markdown --output report.md

  # Generate JSON report
  mcp-audit report ./session-data --format json --output report.json

For more information, visit: https://github.com/littlebearapps/mcp-audit
        """,
    )

    parser.add_argument("--version", action="version", version=f"mcp-audit {__version__}")

    # Subcommands
    subparsers = parser.add_subparsers(
        title="commands",
        description="Available commands",
        dest="command",
        help="Command to execute",
    )

    # ========================================================================
    # collect command
    # ========================================================================
    collect_parser = subparsers.add_parser(
        "collect",
        help="Collect MCP session data from CLI tools",
        description="""
Collect MCP session data by monitoring CLI tool output.

This command runs under a Claude Code, Codex CLI, or Gemini CLI session
and captures MCP tool usage, token counts, and cost data in real-time.

The collected data is saved to the specified output directory and can be
analyzed later with the 'report' command.
        """,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    collect_parser.add_argument(
        "--platform",
        choices=["claude-code", "codex-cli", "gemini-cli", "auto"],
        default="auto",
        help="Platform to monitor (default: auto-detect)",
    )

    collect_parser.add_argument(
        "--output",
        type=Path,
        default=Path("logs/sessions"),
        help="Output directory for session data (default: logs/sessions)",
    )

    collect_parser.add_argument(
        "--project",
        type=str,
        default=None,
        help="Project name for session (default: auto-detect from directory)",
    )

    collect_parser.add_argument(
        "--no-logs", action="store_true", help="Skip writing logs to disk (real-time display only)"
    )

    collect_parser.add_argument(
        "--quiet", action="store_true", help="Suppress all display output (logs only)"
    )

    collect_parser.add_argument(
        "--tui",
        action="store_true",
        help="Use rich TUI display (default when TTY available)",
    )

    collect_parser.add_argument(
        "--plain",
        action="store_true",
        help="Use plain text output (for CI/logs)",
    )

    collect_parser.add_argument(
        "--refresh-rate",
        type=float,
        default=0.5,
        help="TUI refresh rate in seconds (default: 0.5)",
    )

    # ========================================================================
    # report command
    # ========================================================================
    report_parser = subparsers.add_parser(
        "report",
        help="Generate reports from collected session data",
        description="""
Generate reports from collected MCP session data.

This command analyzes session data and produces reports in various formats
(JSON, Markdown, CSV) showing token usage, costs, and MCP tool efficiency.
        """,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    report_parser.add_argument(
        "session_dir", type=Path, help="Session directory or parent directory containing sessions"
    )

    report_parser.add_argument(
        "--format",
        choices=["json", "markdown", "csv"],
        default="markdown",
        help="Report format (default: markdown)",
    )

    report_parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="Output file path (default: stdout or auto-generated filename)",
    )

    report_parser.add_argument(
        "--aggregate", action="store_true", help="Aggregate data across multiple sessions"
    )

    report_parser.add_argument(
        "--top-n", type=int, default=10, help="Number of top tools to show (default: 10)"
    )

    # Parse arguments
    args = parser.parse_args()

    # Execute command
    if args.command == "collect":
        return cmd_collect(args)
    elif args.command == "report":
        return cmd_report(args)
    else:
        parser.print_help()
        return 1


# ============================================================================
# Command Implementations
# ============================================================================


def get_display_mode(args) -> str:
    """Determine display mode from CLI args."""
    if args.quiet:
        return "quiet"
    if args.plain:
        return "plain"
    if args.tui:
        return "tui"
    return "auto"  # Will use TUI if TTY, else plain


def cmd_collect(args) -> int:
    """Execute collect command."""
    from datetime import datetime

    from .display import DisplaySnapshot, create_display

    # Determine display mode
    display_mode = get_display_mode(args)

    # Create display adapter
    try:
        display = create_display(mode=display_mode, refresh_rate=args.refresh_rate)
    except ImportError as e:
        print(f"Error: {e}")
        return 1

    # Detect platform
    platform = args.platform
    if platform == "auto":
        platform = detect_platform()

    # Determine project name
    project = args.project or detect_project_name()

    # Create initial snapshot for display start
    start_time = datetime.now()
    initial_snapshot = DisplaySnapshot.create(
        project=project,
        platform=platform,
        start_time=start_time,
        duration_seconds=0.0,
    )

    # Start display
    display.start(initial_snapshot)

    # Import appropriate tracker
    if platform == "claude-code":
        from .claude_code_adapter import ClaudeCodeAdapter

        tracker_class = ClaudeCodeAdapter
    elif platform == "codex-cli":
        from .codex_cli_adapter import CodexCLIAdapter

        tracker_class = CodexCLIAdapter
    elif platform == "gemini-cli":
        from .gemini_cli_adapter import GeminiCLIAdapter

        tracker_class = GeminiCLIAdapter
    else:
        display.stop(initial_snapshot)
        print(f"Error: Platform '{platform}' not yet implemented")
        print("Supported platforms: claude-code, codex-cli, gemini-cli")
        return 1

    # Create tracker instance
    try:
        tracker = tracker_class(
            project=project,
        )

        # Start tracking
        tracker.start()

        # Monitor until interrupted
        try:
            tracker.monitor(display=display)
        except KeyboardInterrupt:
            pass  # Display will show summary

        # Stop tracking (saves session)
        session = tracker.stop()

        # Build final snapshot
        if session:
            final_snapshot = _build_snapshot_from_session(session, start_time)
        else:
            final_snapshot = initial_snapshot

        # Stop display and show summary
        display.stop(final_snapshot)

        if session and not args.no_logs:
            print(f"Session saved to: {tracker.session_dir}")

        return 0

    except Exception as e:
        display.stop(initial_snapshot)
        print(f"Error: {e}")
        import traceback

        traceback.print_exc()
        return 1


def _build_snapshot_from_session(session, start_time) -> "DisplaySnapshot":
    """Build DisplaySnapshot from a Session object."""
    from datetime import datetime

    from .display import DisplaySnapshot

    # Calculate duration
    duration_seconds = (datetime.now() - start_time).total_seconds()

    # Calculate cache tokens
    cache_tokens = session.token_usage.cache_read_tokens + session.token_usage.cache_created_tokens

    # Calculate cache efficiency
    total = session.token_usage.total_tokens
    cache_efficiency = cache_tokens / total if total > 0 else 0.0

    # Build top tools list
    top_tools = []
    for server_name, server_session in session.server_sessions.items():
        for tool_name, tool_stats in server_session.tools.items():
            avg_tokens = tool_stats.total_tokens // tool_stats.calls if tool_stats.calls > 0 else 0
            top_tools.append((tool_name, tool_stats.calls, tool_stats.total_tokens, avg_tokens))

    # Sort by total tokens descending
    top_tools.sort(key=lambda x: x[2], reverse=True)

    return DisplaySnapshot.create(
        project=session.project,
        platform=session.platform,
        start_time=start_time,
        duration_seconds=duration_seconds,
        input_tokens=session.token_usage.input_tokens,
        output_tokens=session.token_usage.output_tokens,
        cache_tokens=cache_tokens,
        total_tokens=session.token_usage.total_tokens,
        cache_efficiency=cache_efficiency,
        cost_estimate=session.cost_estimate,
        total_tool_calls=session.mcp_tool_calls.total_calls,
        unique_tools=session.mcp_tool_calls.unique_tools,
        top_tools=top_tools,
    )


def cmd_report(args) -> int:
    """Execute report command."""
    print("=" * 70)
    print("MCP Analyze - Generate Report")
    print("=" * 70)
    print()

    session_dir = args.session_dir

    # Check if session directory exists
    if not session_dir.exists():
        print(f"Error: Session directory not found: {session_dir}")
        return 1

    # Import session manager
    from .session_manager import SessionManager

    manager = SessionManager()

    # Determine if single session or multiple sessions
    if (session_dir / "summary.json").exists():
        # Single session
        print(f"Loading session from: {session_dir}")
        session = manager.load_session(session_dir)

        if not session:
            print("Error: Failed to load session")
            return 1

        sessions = [session]
    else:
        # Multiple sessions (parent directory)
        print(f"Loading sessions from: {session_dir}")
        session_dirs = [d for d in session_dir.iterdir() if d.is_dir()]
        sessions = []

        for s_dir in session_dirs:
            session = manager.load_session(s_dir)
            if session:
                sessions.append(session)

        if not sessions:
            print("Error: No valid sessions found")
            return 1

        print(f"Loaded {len(sessions)} session(s)")

    print()

    # Generate report
    if args.format == "json":
        return generate_json_report(sessions, args)
    elif args.format == "markdown":
        return generate_markdown_report(sessions, args)
    elif args.format == "csv":
        return generate_csv_report(sessions, args)
    else:
        print(f"Error: Unknown format: {args.format}")
        return 1


# ============================================================================
# Report Generators
# ============================================================================


def generate_json_report(sessions, args) -> int:
    """Generate JSON report."""
    import json
    from datetime import datetime

    from . import __version__

    # Build report data
    report = {"generated": datetime.now().isoformat(), "version": __version__, "sessions": []}

    for session in sessions:
        report["sessions"].append(session.to_dict())

    # Output to file or stdout
    output_path = args.output
    if output_path:
        with open(output_path, "w") as f:
            json.dump(report, f, indent=2, default=str)
        print(f"JSON report written to: {output_path}")
    else:
        print(json.dumps(report, indent=2, default=str))

    return 0


def generate_markdown_report(sessions, args) -> int:
    """Generate Markdown report."""
    from datetime import datetime

    # Build markdown content
    lines = []
    lines.append("# MCP Audit Report")
    lines.append("")
    lines.append(f"**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append(f"**Sessions**: {len(sessions)}")
    lines.append("")

    # Per-session summaries
    for i, session in enumerate(sessions, 1):
        lines.append(f"## Session {i}: {session.project}")
        lines.append("")
        lines.append(f"**Timestamp**: {session.timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append(f"**Platform**: {session.platform}")
        lines.append("")

        lines.append("### Token Usage")
        lines.append("")
        lines.append(f"- **Input tokens**: {session.token_usage.input_tokens:,}")
        lines.append(f"- **Output tokens**: {session.token_usage.output_tokens:,}")
        lines.append(f"- **Cache created**: {session.token_usage.cache_created_tokens:,}")
        lines.append(f"- **Cache read**: {session.token_usage.cache_read_tokens:,}")
        lines.append(f"- **Total tokens**: {session.token_usage.total_tokens:,}")
        lines.append("")

        lines.append(f"**Cost Estimate**: ${session.cost_estimate:.4f}")
        lines.append("")

        lines.append("### MCP Tool Calls")
        lines.append("")
        lines.append(f"- **Total calls**: {session.mcp_tool_calls.total_calls}")
        lines.append(f"- **Unique tools**: {session.mcp_tool_calls.unique_tools}")
        lines.append("")

        # Top tools
        if session.server_sessions:
            lines.append("#### Top MCP Tools")
            lines.append("")

            # Collect all tools
            all_tools = []
            for _server_name, server_session in session.server_sessions.items():
                for tool_name, tool_stats in server_session.tools.items():
                    all_tools.append((tool_name, tool_stats.calls, tool_stats.total_tokens))

            # Sort by total tokens
            all_tools.sort(key=lambda x: x[2], reverse=True)

            # Show top N
            for tool_name, calls, total_tokens in all_tools[: args.top_n]:
                lines.append(f"- **{tool_name}**: {calls} calls, {total_tokens:,} tokens")

            lines.append("")

    # Output to file or stdout
    content = "\n".join(lines)
    output_path = args.output
    if output_path:
        with open(output_path, "w") as f:
            f.write(content)
        print(f"Markdown report written to: {output_path}")
    else:
        print(content)

    return 0


def generate_csv_report(sessions, args) -> int:
    """Generate CSV report."""
    import csv

    # Collect tool statistics across all sessions
    tool_stats = {}

    for session in sessions:
        for _server_name, server_session in session.server_sessions.items():
            for tool_name, stats in server_session.tools.items():
                if tool_name not in tool_stats:
                    tool_stats[tool_name] = {"calls": 0, "total_tokens": 0}

                tool_stats[tool_name]["calls"] += stats.calls
                tool_stats[tool_name]["total_tokens"] += stats.total_tokens

    # Build CSV rows
    rows = []
    for tool_name, stats in sorted(
        tool_stats.items(), key=lambda x: x[1]["total_tokens"], reverse=True
    ):
        rows.append(
            {
                "tool_name": tool_name,
                "total_calls": stats["calls"],
                "total_tokens": stats["total_tokens"],
                "avg_tokens": stats["total_tokens"] // stats["calls"] if stats["calls"] > 0 else 0,
            }
        )

    # Output to file or stdout
    output_path = args.output or Path("mcp-audit-report.csv")

    with open(output_path, "w", newline="") as f:
        if rows:
            writer = csv.DictWriter(
                f, fieldnames=["tool_name", "total_calls", "total_tokens", "avg_tokens"]
            )
            writer.writeheader()
            writer.writerows(rows)

    print(f"CSV report written to: {output_path}")
    return 0


# ============================================================================
# Utility Functions
# ============================================================================


def detect_platform() -> str:
    """Auto-detect platform from environment."""
    # Check for Claude Code debug log
    claude_log = Path.home() / ".claude" / "cache"
    if claude_log.exists():
        return "claude-code"

    # Check for Codex CLI indicators
    # (Would need to check for codex-specific environment variables)

    # Default to Claude Code
    return "claude-code"


def detect_project_name() -> str:
    """Detect project name from current directory."""
    cwd = Path.cwd()
    return cwd.name


if __name__ == "__main__":
    sys.exit(main())
