import os
import logging

import numpy as np

from .tartspi import TartSPI
from .tart_fake_spi import TartFakeSPI


def load_permute(noisy=False):
    '''Load a permutation vector from the file at the given filepath.'''
    filepath = os.path.join(os.environ["PERMUTE_DIR"], 'permute.txt')
    pp = np.loadtxt(filepath, dtype='int')
    return pp


def create_spi_object(runtime_config, speed=16000000):
    perm = load_permute()
    logging.info(f'create_spi_object(speed={speed}')
    try:
        return TartSPI(runtime_config, perm, speed)
    except Exception as e:
        logging.exception(e)
        logging.warn('USING DUMMY SPI MODULE.')
    return TartFakeSPI(runtime_config, perm, speed)
