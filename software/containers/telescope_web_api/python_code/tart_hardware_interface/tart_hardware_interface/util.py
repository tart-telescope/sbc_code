import os
import logging


import numpy as np


from .tartspi import TartSPI
from .tart_fake_spi import TartFakeSPI


PERMUTE_FILE='permute.txt'

def load_permute(filepath=PERMUTE_FILE, noisy=False):
  '''Load a permutation vector from the file at the given filepath.'''
  filepath = os.path.join(os.environ["CONFIG_DIR"], PERMUTE_FILE);
  pp = np.loadtxt(filepath, dtype='int')
  return pp


def create_spi_object(speed=32000000):
  perm = load_permute()
  try:
    return TartSPI(perm, speed)
  except Exception as e:
    logging.exception(e)
    logging.warn('USING DUMMY SPI MODULE.')
    return TartFakeSPI(perm, speed)
