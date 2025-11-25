# MCP Audit Data Contract

**Version**: 1.0.0
**Last Updated**: 2025-11-25
**Status**: Active

This document defines the data contract for MCP Audit, including backward compatibility guarantees, versioning policy, and migration guidelines.

---

## Table of Contents

1. [Backward Compatibility Guarantee](#backward-compatibility-guarantee)
2. [Versioning Policy](#versioning-policy)
3. [Schema Stability](#schema-stability)
4. [Migration Support](#migration-support)
5. [Breaking Changes](#breaking-changes)
6. [Deprecation Policy](#deprecation-policy)

---

## Backward Compatibility Guarantee

### Our Promise

**We guarantee backward compatibility for the on-disk session format within major versions.**

This means:

- ✅ **v1.0 sessions will always be readable by v1.x**
- ✅ **v1.5 can read sessions created by v1.0, v1.1, v1.2, etc.**
- ✅ **Index files remain compatible within major versions**
- ⚠️ **v2.0 may require migration from v1.x format**

### What This Covers

| Component | Guarantee |
|-----------|-----------|
| Session JSONL files | Read compatibility within major version |
| Daily index files | Read compatibility within major version |
| Platform index files | Read compatibility within major version |
| Event schema | Additive changes only within major version |
| Storage directory structure | Stable within major version |

### What This Does NOT Cover

| Component | Note |
|-----------|------|
| CLI arguments | May change between minor versions |
| Python API signatures | May add optional parameters |
| Report output format | May improve between versions |
| Configuration file format | May add new options |

---

## Versioning Policy

MCP Audit follows [Semantic Versioning 2.0.0](https://semver.org/):

```
MAJOR.MINOR.PATCH
```

### Version Bump Rules

#### Major Version (1.x.x → 2.x.x)

Bump major version when making **breaking changes**:

- Removing required fields from schema
- Changing field types (e.g., `int` → `string`)
- Renaming fields
- Changing directory structure
- Removing support for old session formats

**User Impact**: May require data migration

#### Minor Version (x.1.x → x.2.x)

Bump minor version for **additive changes**:

- Adding new optional fields to schema
- Adding new event types
- Adding new platforms
- Adding new CLI commands
- Adding new configuration options

**User Impact**: No action required, new features available

#### Patch Version (x.x.1 → x.x.2)

Bump patch version for **bug fixes**:

- Fixing parsing errors
- Fixing calculation bugs
- Documentation corrections
- Performance improvements (no behavior change)

**User Impact**: Safe to upgrade immediately

### Examples

| Change | Version Bump |
|--------|--------------|
| Add `duration_ms` field to Call | Minor (additive) |
| Remove `legacy_field` from Session | **Major** (breaking) |
| Fix token calculation bug | Patch |
| Add Gemini CLI support | Minor |
| Change `total_tokens: int` to `total_tokens: str` | **Major** (type change) |
| Add `[analytics]` optional dependency | Minor |

---

## Schema Stability

### Schema Version Field

All data structures include a `schema_version` field:

```json
{
  "schema_version": "1.0.0",
  "session_id": "session-20251125T103045-abc123",
  ...
}
```

This enables:

- Version detection when loading old sessions
- Graceful handling of unknown fields
- Migration path identification

### Field Categories

#### Required Fields (Stable)

These fields will always be present and maintain their type:

```python
# Session
schema_version: str    # Always present
session_id: str        # Always present
platform: str          # Always present
timestamp: str         # ISO 8601 format
token_usage: dict      # Structure defined below

# Token Usage
input_tokens: int
output_tokens: int
total_tokens: int
```

#### Optional Fields (May be absent in older versions)

```python
# Added in v1.0.0
duration_ms: Optional[int]         # For time-based tracking
content_hash: Optional[str]        # For duplicate detection
cache_created_tokens: Optional[int]
cache_read_tokens: Optional[int]
```

#### Extension Fields (Platform-specific)

```python
# May vary by platform
platform_data: Optional[dict]  # Platform-specific metadata
metadata: Optional[dict]       # Additional context
```

### Handling Unknown Fields

When loading sessions, unknown fields are **preserved but ignored**:

```python
# Session created by v1.5.0, loaded by v1.2.0
{
  "schema_version": "1.5.0",
  "session_id": "...",
  "new_field_in_1_5": "value",  # Unknown to v1.2.0, preserved
  ...
}
```

This ensures forward compatibility within major versions.

---

## Migration Support

### Automatic Migration

MCP Audit provides migration helpers for upgrading between versions:

```bash
# Check for sessions needing migration
mcp-analyze migrate --check

# Migrate from v0.x format to v1.x
mcp-analyze migrate --from logs/sessions/

# Dry run (preview without changes)
mcp-analyze migrate --from logs/sessions/ --dry-run
```

### Programmatic Migration

```python
from storage import StorageManager, migrate_all_v0_sessions
from pathlib import Path

# Migrate v0.x sessions to v1.x format
storage = StorageManager()
results = migrate_all_v0_sessions(
    v0_base_dir=Path("logs/sessions"),
    storage=storage,
    platform="claude_code"
)

print(f"Migrated: {results['migrated']}")
print(f"Skipped: {results['skipped']}")
print(f"Failed: {results['failed']}")
```

### Migration Matrix

| From | To | Migration Path |
|------|-----|----------------|
| v0.x | v1.x | `migrate_all_v0_sessions()` |
| v1.0 | v1.5 | Automatic (no migration needed) |
| v1.x | v2.x | Future: `migrate_v1_to_v2()` |

### What Gets Migrated

When migrating from v0.x to v1.x:

| v0.x File | v1.x Destination | Notes |
|-----------|------------------|-------|
| `events.jsonl` | `<session-id>.jsonl` | Copied directly |
| `summary.json` | Index entries | Metadata extracted |
| `mcp-*.json` | Embedded in JSONL | Data merged |

### Migration Safety

- **Non-destructive**: Original files are never deleted
- **Idempotent**: Running twice won't create duplicates
- **Reversible**: Keep v0.x files until confident

---

## Breaking Changes

### Definition

A **breaking change** is any modification that:

1. Prevents reading existing session files
2. Changes the meaning of existing fields
3. Removes functionality users depend on

### Breaking Change Process

When a breaking change is necessary:

1. **Announce** in release notes (minimum 1 minor version notice)
2. **Provide** migration tooling
3. **Document** upgrade path
4. **Support** previous major version for 6 months
5. **Bump** major version

### Example Timeline

```
v1.8.0 - Announce: "field_x will be removed in v2.0"
v1.9.0 - Deprecation warning when field_x is used
v2.0.0 - field_x removed, migration tool available
v2.0.0+6mo - v1.x support ends
```

### Breaking Changes History

| Version | Change | Migration |
|---------|--------|-----------|
| v1.0.0 | Initial release | N/A |
| (future) | | |

---

## Deprecation Policy

### Deprecation Warnings

Deprecated features generate warnings:

```python
# Example deprecation warning
import warnings
warnings.warn(
    "field_x is deprecated and will be removed in v2.0. "
    "Use field_y instead.",
    DeprecationWarning
)
```

### Deprecation Timeline

1. **Announcement**: Feature marked deprecated in release notes
2. **Warning Period**: Minimum 2 minor versions with warnings
3. **Removal**: Feature removed in next major version

### Currently Deprecated

| Feature | Deprecated In | Removed In | Replacement |
|---------|---------------|------------|-------------|
| (none currently) | | | |

---

## Stability Tiers

Different parts of MCP Audit have different stability guarantees:

### Tier 1: Stable (Data Format)

- Session JSONL format
- Index file format
- Directory structure
- Core schema fields

**Guarantee**: Backward compatible within major version

### Tier 2: Stable (Core API)

- `StorageManager` class
- `BaseTracker` abstract class
- CLI commands (`collect`, `report`)

**Guarantee**: API stable, may add optional parameters

### Tier 3: Evolving (Extensions)

- Platform adapters (may add new ones)
- Report formats (may improve)
- Optional dependencies (may change)

**Guarantee**: Functionality stable, implementation may change

### Tier 4: Experimental

- Features marked `[experimental]`
- New platform integrations
- Preview features

**Guarantee**: May change without notice

---

## Testing Compatibility

### Automated Tests

Our CI pipeline includes:

- **Schema validation tests**: Verify all fields match spec
- **Migration tests**: Test v0.x → v1.x migration
- **Round-trip tests**: Write → Read → Compare
- **Forward compatibility tests**: Old reader, new data

### Manual Verification

Before each release:

1. Load sessions from all previous minor versions
2. Verify index files remain readable
3. Test migration from v0.x format
4. Confirm no data loss

---

## Questions?

If you have questions about the data contract:

1. Check [GitHub Discussions](https://github.com/littlebearapps/mcp-audit/discussions)
2. Open an issue for clarification
3. Review the [CORE-SCHEMA-SPEC.md](CORE-SCHEMA-SPEC.md) for technical details

---

## Summary

| Aspect | Guarantee |
|--------|-----------|
| Session files | Readable within major version |
| Schema version | Always present |
| Unknown fields | Preserved on load |
| Migration | Tools provided for major upgrades |
| Deprecation | 2+ minor version warning period |
| Breaking changes | Major version bump required |
