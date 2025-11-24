#!/usr/bin/env python3
"""
CodexCLIAdapter - Platform adapter for Codex CLI tracking

Implements BaseTracker for Codex CLI's output format.
"""

import json
import subprocess
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

from base_tracker import BaseTracker


class CodexCLIAdapter(BaseTracker):
    """
    Codex CLI platform adapter.

    Wraps the `codex` command as a subprocess and monitors stdout/stderr
    for MCP tool usage events. Uses process wrapper approach.
    """

    def __init__(self, project: str, codex_args: list[str] | None = None):
        """
        Initialize Codex CLI adapter.

        Args:
            project: Project name (e.g., "mcp-audit")
            codex_args: Additional arguments to pass to codex command
        """
        super().__init__(project=project, platform="codex-cli")

        self.codex_args = codex_args or []
        self.detected_model: Optional[str] = None
        self.model_name: str = "Unknown Model"
        self.process: Optional[subprocess.Popen[str]] = None

    # ========================================================================
    # Abstract Method Implementations
    # ========================================================================

    def start_tracking(self) -> None:
        """
        Start tracking Codex CLI session.

        Launches codex as subprocess and monitors output.
        """
        print(f"[Codex CLI] Starting tracker for project: {self.project}")
        print(f"[Codex CLI] Launching codex with args: {self.codex_args}")

        # Launch codex as subprocess
        self.process = subprocess.Popen(
            ["codex"] + self.codex_args,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,  # Line buffered
            universal_newlines=True,
        )

        print("[Codex CLI] Process started. Monitoring output...")

        # Monitor output
        try:
            assert self.process.stdout is not None, "Process stdout is None"
            while True:
                # Read from stdout
                line = self.process.stdout.readline()
                if not line:
                    # Process ended
                    break

                # Parse event
                result = self.parse_event(line)
                if result:
                    tool_name, usage = result
                    self._process_tool_call(tool_name, usage)

        except KeyboardInterrupt:
            print("\n[Codex CLI] Stopping tracker...")
            if self.process:
                self.process.terminate()
                self.process.wait(timeout=5)

    def parse_event(self, event_data: Any) -> Optional[Tuple[str, Dict[str, Any]]]:
        """
        Parse Codex CLI output event.

        Args:
            event_data: Text line from codex stdout/stderr

        Returns:
            Tuple of (tool_name, usage_dict) if MCP tool call, None otherwise
        """
        try:
            # Codex CLI outputs JSON events
            line = str(event_data).strip()
            if not line:
                return None

            # Try to parse as JSON
            data = json.loads(line)

            # Look for conversation events
            if data.get("type") != "conversation":
                return None

            message = data.get("message", {})

            # Extract model information
            if not self.detected_model:
                model_id = message.get("model")
                if model_id:
                    self.detected_model = model_id
                    self.model_name = model_id

            # Extract token usage
            usage = message.get("usage", {})
            if not usage:
                return None

            # Codex CLI format field names
            usage_dict = {
                "input_tokens": usage.get("inputTokens", 0),
                "output_tokens": usage.get("outputTokens", 0),
                "cache_created_tokens": 0,  # Codex doesn't have cache creation
                "cache_read_tokens": usage.get("cacheReadInputTokens", 0),
            }

            # Extract tools used
            content = message.get("content", [])
            if isinstance(content, list):
                for content_block in content:
                    if isinstance(content_block, dict) and content_block.get("type") == "toolUse":
                        tool_name = content_block.get("name")
                        tool_params = content_block.get("input", {})

                        if tool_name and tool_name.startswith("mcp__"):
                            # Return MCP tool call data
                            usage_dict["tool_params"] = tool_params
                            return (tool_name, usage_dict)

            return None

        except (json.JSONDecodeError, KeyError, ValueError) as e:
            self.handle_unrecognized_line(f"Parse error: {e}")
            return None

    def get_platform_metadata(self) -> Dict[str, Any]:
        """
        Get Codex CLI platform metadata.

        Returns:
            Dictionary with platform-specific data
        """
        return {
            "model": self.detected_model,
            "model_name": self.model_name,
            "codex_args": self.codex_args,
            "process_id": self.process.pid if self.process else None,
        }

    # ========================================================================
    # Helper Methods
    # ========================================================================

    def _process_tool_call(self, tool_name: str, usage: Dict[str, Any]) -> None:
        """
        Process a single tool call using BaseTracker.

        Args:
            tool_name: MCP tool name (may have -mcp suffix in Codex format)
            usage: Token usage dictionary
        """
        # Extract tool parameters for duplicate detection
        tool_params = usage.get("tool_params", {})
        content_hash = None
        if tool_params:
            content_hash = self.compute_content_hash(tool_params)

        # Get platform metadata
        platform_data = {"model": self.detected_model, "model_name": self.model_name}

        # Record tool call using BaseTracker
        # BaseTracker will normalize the tool name (strip -mcp suffix)
        self.record_tool_call(
            tool_name=tool_name,
            input_tokens=usage["input_tokens"],
            output_tokens=usage["output_tokens"],
            cache_created_tokens=usage["cache_created_tokens"],
            cache_read_tokens=usage["cache_read_tokens"],
            duration_ms=0,  # Codex CLI doesn't provide duration
            content_hash=content_hash,
            platform_data=platform_data,
        )


# ============================================================================
# Standalone Execution
# ============================================================================


def main() -> int:
    """Main entry point for standalone execution"""
    import argparse

    parser = argparse.ArgumentParser(
        description="Codex CLI MCP Tracker (BaseTracker Adapter)",
        epilog="All arguments after -- are passed to codex command",
    )
    parser.add_argument("--project", default="mcp-audit", help="Project name")
    parser.add_argument(
        "--output", default="logs/sessions", help="Output directory for session logs"
    )

    # Parse known args, rest go to codex
    args, codex_args = parser.parse_known_args()

    # Create adapter
    print(f"Starting Codex CLI tracker for project: {args.project}")
    print(f"Codex arguments: {codex_args}")

    adapter = CodexCLIAdapter(project=args.project, codex_args=codex_args)

    try:
        # Start tracking
        adapter.start_tracking()
    except KeyboardInterrupt:
        print("\nStopping tracker...")
    finally:
        # Finalize session
        session = adapter.finalize_session()

        # Save session data
        output_dir = Path(args.output)
        adapter.save_session(output_dir)

        print(f"\nSession saved to: {adapter.session_dir}")
        print(f"Total tokens: {session.token_usage.total_tokens:,}")
        print(f"MCP calls: {session.mcp_tool_calls.total_calls}")
        print(f"Cache efficiency: {session.token_usage.cache_efficiency:.1%}")

    return 0


if __name__ == "__main__":
    import sys

    sys.exit(main())
