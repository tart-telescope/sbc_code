"""
Telescope control service for TART FastAPI application.

This module provides the background state machine that controls the telescope
hardware, reusing the existing TartControl logic from the Flask application.
"""

import asyncio
import logging
import multiprocessing
from typing import Any

from .tart_control import (
    TartControl,
    cleanup_observation_cache,
    cleanup_visibility_cache,
)

logger = logging.getLogger(__name__)

# Global shared config manager
_config_manager = None
_shared_config = None


def get_shared_config():
    """Get the shared configuration dict."""
    global _shared_config
    return _shared_config


def init_shared_config(config_dict: dict[str, Any]):
    """Initialize the shared configuration."""
    global _config_manager, _shared_config
    _config_manager = multiprocessing.Manager()
    _shared_config = _config_manager.dict(config_dict)
    return _shared_config


class TelescopeControlService:
    """
    Background service that runs the telescope state machine.

    This service maintains compatibility with the Flask implementation while
    providing async integration for FastAPI.
    """

    def __init__(self, runtime_config: dict[str, Any]):
        # Initialize shared config
        self.shared_config = init_shared_config(runtime_config)
        self.tart_process: multiprocessing.Process | None = None
        self.observation_cache_process: multiprocessing.Process | None = None
        self.visibility_cache_process: multiprocessing.Process | None = None
        self.running = False

    async def start(self) -> None:
        """Start all background processes."""
        if self.running:
            logger.warning("Telescope control service already running")
            return

        logger.info("Starting telescope control service...")

        try:
            # Start cache cleanup processes
            self.observation_cache_process = multiprocessing.Process(
                target=cleanup_observation_cache, args=()
            )
            self.observation_cache_process.start()
            logger.info("Started observation cache cleanup process")

            self.visibility_cache_process = multiprocessing.Process(
                target=cleanup_visibility_cache, args=()
            )
            self.visibility_cache_process.start()
            logger.info("Started visibility cache cleanup process")

            # Start main telescope control process
            # Pass no arguments - the process will access shared config via global
            self.tart_process = multiprocessing.Process(target=self._tart_control_loop)
            self.tart_process.start()
            logger.info("Started telescope control state machine")

            self.running = True
            logger.info("Telescope control service started successfully")

        except Exception as e:
            logger.error(f"Failed to start telescope control service: {e}")
            await self.stop()
            raise

    async def stop(self) -> None:
        """Stop all background processes gracefully."""
        if not self.running:
            return

        logger.info("Stopping telescope control service...")

        try:
            # Stop main telescope control process
            if self.tart_process and self.tart_process.is_alive():
                self.tart_process.terminate()
                self.tart_process.join(timeout=5)
                if self.tart_process.is_alive():
                    logger.warning("Force killing telescope control process")
                    self.tart_process.kill()
                    self.tart_process.join()
                logger.info("Stopped telescope control process")

            # Stop cache cleanup processes
            if (
                self.observation_cache_process
                and self.observation_cache_process.is_alive()
            ):
                self.observation_cache_process.terminate()
                self.observation_cache_process.join(timeout=5)
                if self.observation_cache_process.is_alive():
                    self.observation_cache_process.kill()
                    self.observation_cache_process.join()
                logger.info("Stopped observation cache process")

            if (
                self.visibility_cache_process
                and self.visibility_cache_process.is_alive()
            ):
                self.visibility_cache_process.terminate()
                self.visibility_cache_process.join(timeout=5)
                if self.visibility_cache_process.is_alive():
                    self.visibility_cache_process.kill()
                    self.visibility_cache_process.join()
                logger.info("Stopped visibility cache process")

            self.running = False
            logger.info("Telescope control service stopped")

        except Exception as e:
            logger.error(f"Error stopping telescope control service: {e}")

    def _tart_control_loop(self) -> None:
        """
        Main telescope control loop (runs in separate process).

        This reuses the exact same logic as the Flask application.
        """
        try:
            # Get shared config in the child process
            shared_config = get_shared_config()
            if shared_config is None:
                logger.error("Shared config not available in child process")
                return

            # Convert to regular dict for TartControl initialization
            config_dict = dict(shared_config)
            tart_control = TartControl(config_dict)
            logger.info("TartControl initialized, starting control loop")

            while True:
                # Read current mode from shared config
                current_mode = shared_config.get("mode", "off")

                # Update TartControl config with current shared config values
                # to preserve API changes before executing hardware interface
                api_updatable_fields = [
                    "raw",
                    "vis",
                    "antenna_positions",
                    "mode",
                    "loop_mode",
                    "loop_n",
                ]
                for field in api_updatable_fields:
                    if field in shared_config:
                        tart_control.config[field] = shared_config[field]

                # Update state machine
                tart_control.set_state(current_mode)

                # Execute current state
                tart_control.run()

                # Sync hardware interface updates back to shared config
                # (but don't overwrite API changes)
                hardware_updatable_fields = [
                    "vis_current",
                    "vis_timestamp",
                    "status",
                    "channels",
                    "channels_timestamp",
                    "sample_delay",
                    "acquire",
                ]

                for field in hardware_updatable_fields:
                    if field in tart_control.config:
                        shared_config[field] = tart_control.config[field]

        except KeyboardInterrupt:
            logger.info("Telescope control loop interrupted")
        except Exception as e:
            logger.error(f"Error in telescope control loop: {e}")
            logger.exception(e)

    def get_status(self) -> dict[str, Any]:
        """Get status of all background processes."""
        return {
            "service_running": self.running,
            "tart_process_alive": (
                self.tart_process.is_alive() if self.tart_process else False
            ),
            "observation_cache_alive": (
                self.observation_cache_process.is_alive()
                if self.observation_cache_process
                else False
            ),
            "visibility_cache_alive": (
                self.visibility_cache_process.is_alive()
                if self.visibility_cache_process
                else False
            ),
            "current_mode": self.shared_config.get("mode", "unknown"),
        }

    async def restart(self) -> None:
        """Restart the telescope control service."""
        logger.info("Restarting telescope control service...")
        await self.stop()
        await asyncio.sleep(1)  # Brief pause
        await self.start()


# Global service instance
_telescope_service: TelescopeControlService | None = None


async def get_telescope_service() -> TelescopeControlService:
    """Get the global telescope control service instance."""
    global _telescope_service
    if _telescope_service is None:
        raise RuntimeError("Telescope control service not initialized")
    return _telescope_service


async def init_telescope_service(
    runtime_config: dict[str, Any],
) -> TelescopeControlService:
    """Initialize the global telescope control service."""
    global _telescope_service
    if _telescope_service is not None:
        await _telescope_service.stop()

    _telescope_service = TelescopeControlService(runtime_config)
    await _telescope_service.start()
    return _telescope_service


def update_config(key: str, value: Any) -> None:
    """Update a configuration value in the shared config."""
    shared_config = get_shared_config()
    if shared_config is not None:
        shared_config[key] = value


async def cleanup_telescope_service() -> None:
    """Cleanup the global telescope control service."""
    global _telescope_service
    if _telescope_service is not None:
        await _telescope_service.stop()
        _telescope_service = None
