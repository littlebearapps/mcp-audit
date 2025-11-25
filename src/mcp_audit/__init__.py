"""
MCP Audit - Multi-platform MCP usage tracking and cost analysis.

Track token usage, costs, and efficiency across AI coding sessions
for Claude Code, Codex CLI, and other MCP-enabled tools.
"""

__version__ = "0.3.0"
__author__ = "Little Bear Apps"
__email__ = "contact@littlebearapps.com"

# Lazy imports to avoid circular dependencies
# Users can import directly: from mcp_audit import BaseTracker


def __getattr__(name: str):
    """Lazy import handler for package attributes."""
    if name in (
        "BaseTracker",
        "Session",
        "ServerSession",
        "Call",
        "ToolStats",
        "TokenUsage",
        "MCPToolCalls",
    ):
        from .base_tracker import (
            BaseTracker,
            Session,
            ServerSession,
            Call,
            ToolStats,
            TokenUsage,
            MCPToolCalls,
        )

        return locals()[name]

    if name in ("normalize_tool_name", "extract_server_name"):
        from .normalization import normalize_tool_name, extract_server_name

        return locals()[name]

    if name in ("PricingConfig", "get_default_pricing"):
        from .pricing_config import PricingConfig, get_default_pricing

        return locals()[name]

    if name in ("StorageManager", "SessionIndex"):
        from .storage import StorageManager, SessionIndex

        return locals()[name]

    if name in ("ClaudeCodeAdapter",):
        from .claude_code_adapter import ClaudeCodeAdapter

        return ClaudeCodeAdapter

    if name in ("CodexCLIAdapter",):
        from .codex_cli_adapter import CodexCLIAdapter

        return CodexCLIAdapter

    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


__all__ = [
    # Version info
    "__version__",
    "__author__",
    "__email__",
    # Core classes
    "BaseTracker",
    "Session",
    "ServerSession",
    "Call",
    "ToolStats",
    "TokenUsage",
    "MCPToolCalls",
    # Normalization
    "normalize_tool_name",
    "extract_server_name",
    # Pricing
    "PricingConfig",
    "get_default_pricing",
    # Storage
    "StorageManager",
    "SessionIndex",
    # Platform adapters
    "ClaudeCodeAdapter",
    "CodexCLIAdapter",
]
