"""
Pytest configuration for token-audit tests.

This conftest.py ensures the package can be imported during testing
by installing it in editable mode or adding src to the path.
"""

import sys
from pathlib import Path

import pytest

# Add src directory to path for imports during development
src_path = Path(__file__).parent.parent / "src"
if src_path.exists() and str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))


# Check if MCP server dependencies are available
def _mcp_available() -> bool:
    """Check if MCP server dependencies are installed."""
    try:
        import mcp  # noqa: F401

        return True
    except ImportError:
        return False


MCP_AVAILABLE = _mcp_available()


def pytest_ignore_collect(collection_path: Path, config: pytest.Config) -> bool | None:
    """Skip server test files if MCP dependencies are not installed.

    This prevents ImportError during test collection when the optional
    'server' dependencies (mcp, pydantic, filelock) are not installed.

    Install with: pip install token-audit[server]
    """
    if not MCP_AVAILABLE:
        # Skip server-related test files that require optional dependencies
        # (mcp, pydantic, filelock from pip install token-audit[server])
        server_test_patterns = [
            "test_server",
            "test_live_tracker",
            "test_tui_concurrency",  # requires filelock
            "benchmarks",  # benchmarks may also use server components
        ]
        for pattern in server_test_patterns:
            if pattern in collection_path.name:
                return True
    return None


def pytest_configure(config: pytest.Config) -> None:
    """Register custom markers."""
    config.addinivalue_line(
        "markers",
        "requires_server: mark test as requiring MCP server dependencies",
    )


def pytest_collection_modifyitems(config: pytest.Config, items: list[pytest.Item]) -> None:
    """Skip tests marked with requires_server if MCP is not available."""
    if MCP_AVAILABLE:
        return

    skip_server = pytest.mark.skip(
        reason="MCP server dependencies not installed. Install with: pip install token-audit[server]"
    )
    for item in items:
        if "requires_server" in item.keywords:
            item.add_marker(skip_server)
