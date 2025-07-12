"""
Async database connection wrapper for TART telescope API.

This module provides async wrappers around the existing SQLite database
operations while maintaining compatibility with the Flask codebase.
"""

import asyncio
import os

# Import existing database functions to reuse logic
import sys
from contextlib import asynccontextmanager
from typing import Any

import aiosqlite

sys.path.append(os.path.join(os.path.dirname(__file__), "../tart_web_api"))
import tart_web_api.database as flask_db


class AsyncDatabase:
    """Async wrapper for existing SQLite database operations."""

    def __init__(self, db_path: str = "tart_web_api_database_v2.db"):
        self.db_path = db_path

    @asynccontextmanager
    async def get_connection(self):
        """Get async database connection."""
        async with aiosqlite.connect(self.db_path) as conn:
            yield conn

    async def setup_db(self, num_ant: int) -> None:
        """Async wrapper for setup_db - reuses existing logic."""
        # Run the existing setup_db function in thread pool
        await asyncio.get_event_loop().run_in_executor(None, flask_db.setup_db, num_ant)

    async def get_manual_channel_status(self) -> list[dict[str, Any]]:
        """Async wrapper for get_manual_channel_status."""
        return await asyncio.get_event_loop().run_in_executor(
            None, flask_db.get_manual_channel_status
        )

    async def update_manual_channel_status(self, channel_idx: int, enable: bool) -> None:
        """Async wrapper for update_manual_channel_status."""
        await asyncio.get_event_loop().run_in_executor(
            None, flask_db.update_manual_channel_status, channel_idx, enable
        )

    async def get_sample_delay(self) -> float:
        """Async wrapper for get_sample_delay."""
        return await asyncio.get_event_loop().run_in_executor(None, flask_db.get_sample_delay)

    async def insert_sample_delay(self, timestamp: Any, sample_delay: float) -> int:
        """Async wrapper for insert_sample_delay."""
        return await asyncio.get_event_loop().run_in_executor(
            None, flask_db.insert_sample_delay, timestamp, sample_delay
        )

    async def get_gain(self) -> dict[int, tuple]:
        """Async wrapper for get_gain."""
        return await asyncio.get_event_loop().run_in_executor(None, flask_db.get_gain)

    async def insert_gain(self, gain: list[float], phase: list[float]) -> None:
        """Async wrapper for insert_gain."""

        def _insert_gain():
            with flask_db.connect_to_db() as con:
                c = con.cursor()
                flask_db.insert_gain(c, gain, phase)

        await asyncio.get_event_loop().run_in_executor(None, _insert_gain)

    async def insert_raw_file_handle(self, filename: str, checksum: str) -> None:
        """Async wrapper for insert_raw_file_handle."""
        await asyncio.get_event_loop().run_in_executor(
            None, flask_db.insert_raw_file_handle, filename, checksum
        )

    async def remove_raw_file_handle_by_id(self, file_id: int) -> None:
        """Async wrapper for remove_raw_file_handle_by_Id."""
        await asyncio.get_event_loop().run_in_executor(
            None, flask_db.remove_raw_file_handle_by_Id, file_id
        )

    async def get_raw_file_handle(self) -> list[dict[str, Any]]:
        """Async wrapper for get_raw_file_handle."""
        return await asyncio.get_event_loop().run_in_executor(None, flask_db.get_raw_file_handle)

    async def update_observation_cache_process_state(self, state: str) -> None:
        """Async wrapper for update_observation_cache_process_state."""
        await asyncio.get_event_loop().run_in_executor(
            None, flask_db.update_observation_cache_process_state, state
        )

    async def get_observation_cache_process_state(self) -> dict[str, Any]:
        """Async wrapper for get_observation_cache_process_state."""
        return await asyncio.get_event_loop().run_in_executor(
            None, flask_db.get_observation_cache_process_state
        )

    async def insert_vis_file_handle(self, filename: str, checksum: str) -> None:
        """Async wrapper for insert_vis_file_handle."""
        await asyncio.get_event_loop().run_in_executor(
            None, flask_db.insert_vis_file_handle, filename, checksum
        )

    async def remove_vis_file_handle_by_id(self, file_id: int) -> None:
        """Async wrapper for remove_vis_file_handle_by_Id."""
        await asyncio.get_event_loop().run_in_executor(
            None, flask_db.remove_vis_file_handle_by_Id, file_id
        )

    async def get_vis_file_handle(self) -> list[dict[str, Any]]:
        """Async wrapper for get_vis_file_handle."""
        return await asyncio.get_event_loop().run_in_executor(None, flask_db.get_vis_file_handle)

    async def update_vis_cache_process_state(self, state: str) -> None:
        """Async wrapper for update_vis_cache_process_state."""
        await asyncio.get_event_loop().run_in_executor(
            None, flask_db.update_vis_cache_process_state, state
        )

    async def get_vis_cache_process_state(self) -> dict[str, Any]:
        """Async wrapper for get_vis_cache_process_state."""
        return await asyncio.get_event_loop().run_in_executor(
            None, flask_db.get_vis_cache_process_state
        )


# Global database instance
_db_instance: AsyncDatabase | None = None


def get_database() -> AsyncDatabase:
    """Get the global database instance."""
    global _db_instance
    if _db_instance is None:
        _db_instance = AsyncDatabase()
    return _db_instance


async def init_database(num_ant: int = 24) -> AsyncDatabase:
    """Initialize the database with the given number of antennas."""
    db = get_database()
    await db.setup_db(num_ant)
    return db
