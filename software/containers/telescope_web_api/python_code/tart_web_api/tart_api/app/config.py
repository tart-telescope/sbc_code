"""
Configuration management for FastAPI TART telescope API.

This module wraps the existing Flask configuration system to maintain
compatibility while providing FastAPI-compatible configuration.
"""

import json
import os
import socket
from typing import Any

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings using Pydantic for validation."""

    secret_key: str = "super-secret-123897219379179464asd13khk213"
    jwt_header_type: str = "JWT"
    login_password: str = "password"
    config_dir: str = "/config"
    data_root: str = "/telescope_data"

    class Config:
        env_file = ".env"
        env_prefix = ""
        case_sensitive = False


class RuntimeConfig:
    """Runtime configuration manager that wraps the Flask multiprocessing config."""

    def __init__(self, flask_config: dict[str, Any]):
        """Initialize with existing Flask runtime config."""
        self._config = flask_config
        self.settings = Settings()

    def __getitem__(self, key: str) -> Any:
        """Get config value."""
        return self._config[key]

    def __setitem__(self, key: str, value: Any) -> None:
        """Set config value."""
        self._config[key] = value

    def __contains__(self, key: str) -> bool:
        """Check if key exists in config."""
        return key in self._config

    def get(self, key: str, default: Any = None) -> Any:
        """Get config value with default."""
        return self._config.get(key, default)

    def update(self, updates: dict[str, Any]) -> None:
        """Update config with dictionary."""
        self._config.update(updates)


def create_runtime_config() -> RuntimeConfig:
    """
    Create runtime configuration compatible with existing Flask config.

    This function reuses the existing init_config logic but adapts it
    for FastAPI without multiprocessing.Manager().
    """
    # Use regular dict instead of manager.dict()
    config_dict = {}

    # Copy all the existing config initialization logic
    data_root = "/telescope_data"
    config_root = os.environ.get("CONFIG_DIR", "/config")

    config_dict["spi_speed"] = 32000000
    config_dict["acquire"] = False
    config_dict["shifter"] = False
    config_dict["counter"] = False
    config_dict["verbose"] = False
    config_dict["centre"] = True
    config_dict["modes_available"] = [
        "off",
        "diag",
        "raw",
        "vis",
        "vis_save",
        "cal",
        "rt_syn_img",
    ]
    config_dict["mode"] = "vis"
    config_dict["loop_mode"] = "loop"
    config_dict["loop_mode_available"] = ["loop", "single", "loop_n"]
    config_dict["loop_n"] = 5
    config_dict["loop_idx"] = 0

    config_dict["optimisation"] = "idle"
    config_dict["data_root"] = data_root

    config_dict["raw"] = {
        "save": 1,
        "N_samples_exp": 20,
        "base_path": os.path.join(data_root, "raw"),
    }
    config_dict["diagnostic"] = {
        "num_ant": 24,
        "N_samples": 15,
        "stable_threshold": 0.95,
        "N_samples_exp": 20,
        "spectre": {"NFFT": 4096, "N_samples_exp": 18},
    }
    config_dict["vis"] = {
        "save": 1,
        "chunksize": 60,
        "N_samples_exp": 24,
        "base_path": os.path.join(data_root, "vis"),
    }

    config_dict["telescope_config_path"] = os.path.join(
        config_root, "telescope_config.json"
    )

    # Load telescope config if file exists
    try:
        with open(config_dict["telescope_config_path"]) as t_c:
            config_dict["telescope_config"] = json.load(t_c)
    except (FileNotFoundError, json.JSONDecodeError):
        # Fallback config for development
        config_dict["telescope_config"] = {
            "name": "TART",
            "frequency": 1575.42e6,
            "L0_frequency": 1575.42e6,
            "baseband_frequency": 0.0,
            "sampling_frequency": 16.368e6,
            "bandwidth": 2.5e6,
            "num_antenna": 24,
            "lon": 170.0,
            "lat": -45.0,
            "alt": 100.0,
        }

    # Load antenna positions if file exists
    antenna_positions_path = os.path.join(
        config_root, "calibrated_antenna_positions.json"
    )
    try:
        with open(antenna_positions_path) as a_c:
            config_dict["antenna_positions"] = json.load(a_c)
    except (FileNotFoundError, json.JSONDecodeError):
        # Fallback antenna positions
        config_dict["antenna_positions"] = [[0.0, 0.0, 0.0] for _ in range(24)]

    config_dict["calibration_dir"] = f"/{config_root}/"
    config_dict["realtime_image_path"] = f"{data_root}/assets/img/image.png"
    config_dict["hostname"] = socket.gethostname()

    return RuntimeConfig(config_dict)


# Global config instance - will be set during app startup
runtime_config: RuntimeConfig = None


def get_config() -> RuntimeConfig:
    """Get the global runtime configuration."""
    global runtime_config
    if runtime_config is None:
        runtime_config = create_runtime_config()
    return runtime_config


def init_config() -> RuntimeConfig:
    """Initialize and return the global configuration."""
    global runtime_config
    runtime_config = create_runtime_config()
    return runtime_config
