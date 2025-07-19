import logging
import os

import numpy as np

from .tartspi import TartSPI


def load_permute(noisy=False):
    """Load a permutation vector from the file at the given filepath."""
    filepath = os.environ.get("PERMUTE_PATH", "/permute/permute.txt")
    pp = np.loadtxt(filepath, dtype="int")
    return pp


def create_spi_object(runtime_config, speed=16000000):
    perm = load_permute()
    logging.info(f"create_spi_object(speed={speed}")
    try:
        return TartSPI(runtime_config, perm, speed)
    except Exception as e:
        logging.exception(e)
        logging.warn("USING DUMMY SPI MODULE.")
    from .tart_fake_spi import TartFakeSPI

    return TartFakeSPI(runtime_config, perm, speed)
