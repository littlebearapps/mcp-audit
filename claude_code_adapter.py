#!/usr/bin/env python3
"""
ClaudeCodeAdapter - Platform adapter for Claude Code tracking

Implements BaseTracker for Claude Code's debug.log format.
"""

import json
import time
from pathlib import Path
from typing import Optional, Tuple, Dict, Any, List
from datetime import datetime

from base_tracker import BaseTracker, SCHEMA_VERSION


class ClaudeCodeAdapter(BaseTracker):
    """
    Claude Code platform adapter.

    Monitors Claude Code debug.log files for MCP tool usage.
    Uses file watcher approach to tail debug logs in real-time.
    """

    def __init__(self, project: str, project_path: str = ""):
        """
        Initialize Claude Code adapter.

        Args:
            project: Project name (e.g., "mcp-audit")
            project_path: Relative project path (e.g., "wp-navigator-pro/main")
        """
        super().__init__(project=project, platform="claude-code")

        self.project_path = project_path or project
        self.file_positions: Dict[Path, int] = {}  # Track read positions
        self.claude_dir: Optional[Path] = None
        self.detected_model: Optional[str] = None
        self.model_name: str = "Unknown Model"

        # Find Claude Code directory
        self._find_claude_directory()

    def _find_claude_directory(self) -> None:
        """Find Claude Code data directory for this project"""
        # Try standard locations
        base_dir = Path.home() / ".config" / "claude" / "projects"
        if not base_dir.exists():
            base_dir = Path.home() / ".claude" / "projects"

        if not base_dir.exists():
            raise FileNotFoundError(
                "Claude Code data directory not found. "
                "Tried: ~/.config/claude/projects and ~/.claude/projects"
            )

        # Find project-specific directory
        # Format: -Users-username-path-to-project
        home_path = str(Path.home())[1:]  # Remove leading /
        project_dir_name = f"-{home_path}-claude-code-tools-lba-{self.project_path}".replace("/", "-")

        self.claude_dir = base_dir / project_dir_name

        # If not found, try searching
        if not self.claude_dir.exists():
            for d in base_dir.iterdir():
                if d.is_dir() and self.project_path.replace("/", "-") in d.name:
                    self.claude_dir = d
                    break

        # Fall back to scanning all directories
        if not self.claude_dir or not self.claude_dir.exists():
            self.claude_dir = base_dir

    def _find_jsonl_files(self) -> List[Path]:
        """Find all .jsonl files in Claude Code directory"""
        if not self.claude_dir or not self.claude_dir.exists():
            return []

        # Get all non-empty .jsonl files
        return [
            f for f in self.claude_dir.glob("*.jsonl")
            if f.stat().st_size > 0
        ]

    # ========================================================================
    # Abstract Method Implementations
    # ========================================================================

    def start_tracking(self) -> None:
        """
        Start tracking Claude Code session.

        Monitors .jsonl debug log files in real-time.
        """
        print(f"[Claude Code] Initializing tracker for: {self.project_path}")
        print(f"[Claude Code] Monitoring directory: {self.claude_dir}")

        # Initial file discovery
        files = self._find_jsonl_files()
        print(f"[Claude Code] Found {len(files)} .jsonl files")

        # Initialize file positions (start from end - track NEW content only)
        for file_path in files:
            try:
                self.file_positions[file_path] = file_path.stat().st_size
            except Exception:
                continue

        print("[Claude Code] Tracking started. Press Ctrl+C to stop.")

        # Main monitoring loop
        while True:
            try:
                files = self._find_jsonl_files()

                for file_path in files:
                    # Initialize position for new files
                    if file_path not in self.file_positions:
                        try:
                            self.file_positions[file_path] = file_path.stat().st_size
                        except Exception:
                            continue

                    # Read new content
                    try:
                        with open(file_path, 'r') as f:
                            # Seek to last position
                            f.seek(self.file_positions[file_path])

                            # Read new content
                            new_content = f.read()
                            if new_content:
                                # Process each new line
                                for line in new_content.split('\n'):
                                    if line.strip():
                                        result = self.parse_event(line)
                                        if result:
                                            tool_name, usage = result
                                            self._process_tool_call(tool_name, usage)

                            # Update position
                            self.file_positions[file_path] = f.tell()
                    except Exception as e:
                        self.handle_unrecognized_line(f"Error reading {file_path.name}: {e}")
                        continue

                # Sleep briefly
                time.sleep(0.5)

            except KeyboardInterrupt:
                print("\n[Claude Code] Stopping tracker...")
                break

    def parse_event(self, event_data: Any) -> Optional[Tuple[str, dict]]:
        """
        Parse Claude Code debug.log event.

        Args:
            event_data: JSONL line from debug.log

        Returns:
            Tuple of (tool_name, usage_dict) if MCP tool call, None otherwise
        """
        try:
            data = json.loads(event_data)

            # Only process assistant messages with usage data
            if data.get('type') != 'assistant':
                return None

            message = data.get('message', {})

            # Extract model information
            if not self.detected_model:
                model_id = message.get('model')
                if model_id:
                    self.detected_model = model_id
                    self.model_name = model_id

            # Extract token usage
            usage = message.get('usage', {})
            if not usage:
                return None

            # Claude Code format field names
            usage_dict = {
                'input_tokens': usage.get('input_tokens', 0),
                'output_tokens': usage.get('output_tokens', 0),
                'cache_created_tokens': usage.get('cache_creation_input_tokens', 0),
                'cache_read_tokens': usage.get('cache_read_input_tokens', 0)
            }

            # Extract tools used
            content = message.get('content', [])
            if isinstance(content, list):
                for content_block in content:
                    if isinstance(content_block, dict) and content_block.get('type') == 'tool_use':
                        tool_name = content_block.get('name')
                        tool_params = content_block.get('input', {})

                        if tool_name and tool_name.startswith('mcp__'):
                            # Return MCP tool call data
                            usage_dict['tool_params'] = tool_params
                            return (tool_name, usage_dict)

            return None

        except (json.JSONDecodeError, KeyError) as e:
            self.handle_unrecognized_line(f"Parse error: {e}")
            return None

    def get_platform_metadata(self) -> Dict[str, Any]:
        """
        Get Claude Code platform metadata.

        Returns:
            Dictionary with platform-specific data
        """
        return {
            'model': self.detected_model,
            'model_name': self.model_name,
            'claude_dir': str(self.claude_dir),
            'project_path': self.project_path,
            'files_monitored': len(self.file_positions)
        }

    # ========================================================================
    # Helper Methods
    # ========================================================================

    def _process_tool_call(self, tool_name: str, usage: dict) -> None:
        """
        Process a single tool call using BaseTracker.

        Args:
            tool_name: MCP tool name
            usage: Token usage dictionary
        """
        # Extract tool parameters for duplicate detection
        tool_params = usage.get('tool_params', {})
        content_hash = None
        if tool_params:
            content_hash = self.compute_content_hash(tool_params)

        # Get platform metadata
        platform_data = {
            'model': self.detected_model,
            'model_name': self.model_name
        }

        # Record tool call using BaseTracker
        self.record_tool_call(
            tool_name=tool_name,
            input_tokens=usage['input_tokens'],
            output_tokens=usage['output_tokens'],
            cache_created_tokens=usage['cache_created_tokens'],
            cache_read_tokens=usage['cache_read_tokens'],
            duration_ms=0,  # Claude Code doesn't provide duration
            content_hash=content_hash,
            platform_data=platform_data
        )


# ============================================================================
# Standalone Execution
# ============================================================================

def main():
    """Main entry point for standalone execution"""
    import argparse

    parser = argparse.ArgumentParser(description="Claude Code MCP Tracker (BaseTracker Adapter)")
    parser.add_argument('--project', default='mcp-audit', help='Project name')
    parser.add_argument('--path', default='', help='Project path (e.g., wp-navigator-pro/main)')
    parser.add_argument('--output', default='logs/sessions', help='Output directory for session logs')
    args = parser.parse_args()

    # Create adapter
    print(f"Starting Claude Code tracker for project: {args.project}")
    adapter = ClaudeCodeAdapter(project=args.project, project_path=args.path)

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


if __name__ == "__main__":
    main()
