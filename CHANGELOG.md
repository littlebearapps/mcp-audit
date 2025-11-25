# Changelog

All notable changes to MCP Audit will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.3.0] - 2025-11-25

### Added
- **PyPI distribution** - Now installable via `pip install mcp-audit` or `pipx install mcp-audit`
- **CLI command** - `mcp-analyze` command with `collect` and `report` subcommands
- **Proper package structure** - Modern `src/` layout following Python packaging best practices
- **Type hints** - Full type annotations with `py.typed` marker for editor support
- **GitHub Actions** - Automated CI/CD pipeline with PyPI publishing on releases
- **JSONL storage system** - Efficient session storage with indexing for fast queries
- **Platform adapters** - Modular architecture for adding new platform support

### Changed
- Restructured project from flat files to `src/mcp_audit/` package
- Updated from Phase 1 (Foundation) to Phase 2 (Public Beta)
- Improved test organization with dedicated `tests/` directory
- Enhanced pyproject.toml with modern Python packaging standards

### Fixed
- License deprecation warnings in setuptools
- Test imports for new package structure

## [0.2.0] - 2025-11-24

### Added
- **BaseTracker abstraction** - Platform-agnostic tracker base class
- **Schema v1.0.0** - Locked data schema with backward compatibility guarantees
- **Pricing configuration** - TOML-based model pricing with Claude and OpenAI support
- **CI/CD pipeline** - GitHub Actions with pytest, mypy, ruff, and black
- **JSONL storage** - Session persistence with 57 comprehensive tests
- **Complete documentation** - Architecture docs, data contract, contributing guide

### Changed
- Migrated from single-file scripts to modular architecture
- Added strict mypy type checking
- Standardized code formatting with black

## [0.1.0] - 2025-11-18

### Added
- Initial implementation
- Claude Code session tracking
- Codex CLI session tracking
- Real-time token usage display
- Cross-session analysis
- Duplicate detection
- Anomaly detection
