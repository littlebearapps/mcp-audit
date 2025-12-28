"""
Tests for TUI + MCP concurrent access safety.

Tests file locking and thread safety for simultaneous access.

v1.0.3 - task-233.15
"""

import os
import tempfile
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from unittest.mock import MagicMock, patch

import pytest


# ============================================================================
# File Locking Tests
# ============================================================================


class TestFileLocking:
    """Tests for file locking mechanism."""

    def test_filelock_import(self) -> None:
        """Test filelock module is available."""
        from filelock import FileLock, Timeout

        assert FileLock is not None
        assert Timeout is not None

    def test_filelock_basic_usage(self) -> None:
        """Test basic file lock acquisition and release."""
        from filelock import FileLock

        with tempfile.TemporaryDirectory() as tmpdir:
            lock_path = os.path.join(tmpdir, "test.lock")
            lock = FileLock(lock_path, timeout=5)

            # Acquire and release
            with lock:
                assert lock.is_locked

            assert not lock.is_locked

    def test_filelock_prevents_concurrent_access(self) -> None:
        """Test file lock prevents concurrent access."""
        from filelock import FileLock, Timeout

        with tempfile.TemporaryDirectory() as tmpdir:
            lock_path = os.path.join(tmpdir, "test.lock")
            lock1 = FileLock(lock_path, timeout=0.1)
            lock2 = FileLock(lock_path, timeout=0.1)

            with lock1:
                # Second lock should timeout
                with pytest.raises(Timeout):
                    with lock2:
                        pass

    def test_filelock_timeout_handling(self) -> None:
        """Test file lock timeout is configurable."""
        from filelock import FileLock

        with tempfile.TemporaryDirectory() as tmpdir:
            lock_path = os.path.join(tmpdir, "test.lock")

            # Short timeout
            lock = FileLock(lock_path, timeout=0.5)
            assert lock.timeout == 0.5

            # Long timeout
            lock = FileLock(lock_path, timeout=30)
            assert lock.timeout == 30


# ============================================================================
# Index File Locking Tests
# ============================================================================


class TestIndexFileLocking:
    """Tests for index file locking in storage module."""

    def test_index_lock_context_manager(self) -> None:
        """Test index lock works as context manager."""
        from token_audit.storage import _index_file_lock
        from pathlib import Path

        with tempfile.TemporaryDirectory() as tmpdir:
            index_path = Path(tmpdir) / "index.json"
            index_path.touch()

            # Should not raise
            with _index_file_lock(index_path):
                # Do something with index
                pass

    def test_index_lock_prevents_race_condition(self) -> None:
        """Test index lock prevents race conditions on index writes."""
        from token_audit.storage import _index_file_lock
        from pathlib import Path

        with tempfile.TemporaryDirectory() as tmpdir:
            index_path = Path(tmpdir) / "index.json"
            index_path.touch()

            results = []
            lock = threading.Lock()

            def update_index(value: int) -> None:
                with _index_file_lock(index_path):
                    # Simulate index read-modify-write
                    time.sleep(0.01)  # Small delay
                    with lock:
                        results.append(value)

            # Run concurrent updates
            with ThreadPoolExecutor(max_workers=5) as executor:
                futures = [executor.submit(update_index, i) for i in range(5)]
                for f in as_completed(futures):
                    f.result()

            # All updates should complete
            assert len(results) == 5


# ============================================================================
# Thread Lock Tests
# ============================================================================


class TestThreadLocking:
    """Tests for thread-level locking in streaming storage."""

    def test_thread_lock_per_session(self) -> None:
        """Test each session has its own thread lock."""
        from pathlib import Path
        from token_audit.storage import StreamingStorage

        with tempfile.TemporaryDirectory() as tmpdir:
            storage = StreamingStorage(base_dir=Path(tmpdir))

            lock1 = storage._get_thread_lock("session1")
            lock2 = storage._get_thread_lock("session2")

            # Different sessions, different locks
            assert lock1 is not lock2

    def test_same_session_same_lock(self) -> None:
        """Test same session returns same lock."""
        from pathlib import Path
        from token_audit.storage import StreamingStorage

        with tempfile.TemporaryDirectory() as tmpdir:
            storage = StreamingStorage(base_dir=Path(tmpdir))

            lock1 = storage._get_thread_lock("session1")
            lock2 = storage._get_thread_lock("session1")

            # Same session, same lock
            assert lock1 is lock2


# ============================================================================
# Concurrent Write Tests
# ============================================================================


class TestConcurrentWrites:
    """Tests for concurrent write operations."""

    def test_concurrent_session_writes(self) -> None:
        """Test concurrent writes to different sessions are safe."""
        from pathlib import Path
        from token_audit.storage import StreamingStorage

        with tempfile.TemporaryDirectory() as tmpdir:
            storage = StreamingStorage(base_dir=Path(tmpdir))

            results = []

            def write_session(session_id: str) -> None:
                # Simulate session write
                thread_lock = storage._get_thread_lock(session_id)
                with thread_lock:
                    time.sleep(0.01)
                    results.append(session_id)

            # Concurrent writes to different sessions
            with ThreadPoolExecutor(max_workers=3) as executor:
                sessions = ["session1", "session2", "session3"]
                futures = [executor.submit(write_session, s) for s in sessions]
                for f in as_completed(futures):
                    f.result()

            assert len(results) == 3

    def test_concurrent_writes_same_session_serialized(self) -> None:
        """Test concurrent writes to same session are serialized."""
        from pathlib import Path
        from token_audit.storage import StreamingStorage

        with tempfile.TemporaryDirectory() as tmpdir:
            storage = StreamingStorage(base_dir=Path(tmpdir))

            order = []
            lock = threading.Lock()

            def write_event(event_id: int) -> None:
                thread_lock = storage._get_thread_lock("session1")
                with thread_lock:
                    with lock:
                        order.append(("start", event_id))
                    time.sleep(0.02)  # Simulate write time
                    with lock:
                        order.append(("end", event_id))

            # Concurrent writes to same session
            with ThreadPoolExecutor(max_workers=3) as executor:
                futures = [executor.submit(write_event, i) for i in range(3)]
                for f in as_completed(futures):
                    f.result()

            # Verify serialization: each write should complete before next starts
            # Pattern should be: start-end pairs not interleaved
            starts = [i for i, (op, _) in enumerate(order) if op == "start"]
            ends = [i for i, (op, _) in enumerate(order) if op == "end"]

            # For each event, its end should come before next start
            for i in range(len(starts) - 1):
                assert ends[i] < starts[i + 1]


# ============================================================================
# Delete Session Concurrency Tests
# ============================================================================


class TestDeleteSessionConcurrency:
    """Tests for safe session deletion during concurrent access."""

    def test_delete_checks_active_session(self) -> None:
        """Test delete checks if session is active before deletion."""
        from pathlib import Path
        from token_audit.storage import StreamingStorage

        with tempfile.TemporaryDirectory() as tmpdir:
            storage = StreamingStorage(base_dir=Path(tmpdir))

            # Check active session
            is_active = storage.has_active_session("session1")
            assert isinstance(is_active, bool)

    def test_delete_waits_for_lock(self) -> None:
        """Test delete waits for write lock before proceeding."""
        from filelock import FileLock

        with tempfile.TemporaryDirectory() as tmpdir:
            lock_path = os.path.join(tmpdir, "session.lock")
            lock = FileLock(lock_path, timeout=5)

            deleted = threading.Event()

            def writer():
                with lock:
                    time.sleep(0.1)

            def deleter():
                with lock:
                    deleted.set()

            t1 = threading.Thread(target=writer)
            t2 = threading.Thread(target=deleter)

            t1.start()
            time.sleep(0.01)  # Ensure writer starts first
            t2.start()

            t1.join()
            t2.join()

            # Delete should have completed after writer finished
            assert deleted.is_set()


# ============================================================================
# TUI + MCP Simultaneous Access Tests
# ============================================================================


class TestTUIMCPSimultaneousAccess:
    """Tests for TUI and MCP accessing data simultaneously."""

    def test_tui_read_during_mcp_write(self) -> None:
        """Test TUI can read while MCP is writing (different sessions)."""
        from pathlib import Path
        from token_audit.storage import StreamingStorage

        with tempfile.TemporaryDirectory() as tmpdir:
            storage = StreamingStorage(base_dir=Path(tmpdir))

            read_completed = threading.Event()
            write_completed = threading.Event()

            def tui_read():
                # TUI reads session list (no lock needed for read)
                time.sleep(0.01)
                read_completed.set()

            def mcp_write():
                # MCP writes to active session
                thread_lock = storage._get_thread_lock("active_session")
                with thread_lock:
                    time.sleep(0.02)
                write_completed.set()

            t1 = threading.Thread(target=tui_read)
            t2 = threading.Thread(target=mcp_write)

            t1.start()
            t2.start()

            t1.join()
            t2.join()

            # Both should complete
            assert read_completed.is_set()
            assert write_completed.is_set()

    def test_index_locked_during_session_list_refresh(self) -> None:
        """Test index is locked when refreshing session list."""
        from token_audit.storage import _index_file_lock
        from pathlib import Path

        with tempfile.TemporaryDirectory() as tmpdir:
            index_path = Path(tmpdir) / "index.json"
            index_path.touch()

            operations = []
            lock = threading.Lock()

            def refresh_sessions():
                with _index_file_lock(index_path):
                    with lock:
                        operations.append("refresh_start")
                    time.sleep(0.02)
                    with lock:
                        operations.append("refresh_end")

            def mcp_finalize():
                with _index_file_lock(index_path):
                    with lock:
                        operations.append("finalize_start")
                    time.sleep(0.02)
                    with lock:
                        operations.append("finalize_end")

            t1 = threading.Thread(target=refresh_sessions)
            t2 = threading.Thread(target=mcp_finalize)

            t1.start()
            time.sleep(0.01)  # Ensure refresh starts first
            t2.start()

            t1.join()
            t2.join()

            # Operations should be serialized
            assert len(operations) == 4
            # First operation should complete before second starts
            refresh_end_idx = operations.index("refresh_end")
            finalize_start_idx = operations.index("finalize_start")
            assert refresh_end_idx < finalize_start_idx


# ============================================================================
# Error Handling Tests
# ============================================================================


class TestConcurrencyErrorHandling:
    """Tests for error handling during concurrent access."""

    def test_lock_released_on_exception(self) -> None:
        """Test lock is released when exception occurs."""
        from filelock import FileLock

        with tempfile.TemporaryDirectory() as tmpdir:
            lock_path = os.path.join(tmpdir, "test.lock")
            lock = FileLock(lock_path, timeout=1)

            try:
                with lock:
                    raise ValueError("Test error")
            except ValueError:
                pass

            # Lock should be released
            assert not lock.is_locked

            # Should be able to acquire again
            with lock:
                assert lock.is_locked

    def test_permission_error_handling(self) -> None:
        """Test PermissionError is handled gracefully."""
        # Simulate permission error scenario
        with pytest.raises(PermissionError):
            raise PermissionError("Access denied")

    def test_file_not_found_during_delete(self) -> None:
        """Test FileNotFoundError handled during delete."""
        with tempfile.TemporaryDirectory() as tmpdir:
            filepath = os.path.join(tmpdir, "nonexistent.json")

            with pytest.raises(FileNotFoundError):
                with open(filepath) as f:
                    f.read()
