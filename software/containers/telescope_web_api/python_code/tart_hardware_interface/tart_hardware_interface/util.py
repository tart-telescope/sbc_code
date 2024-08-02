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

def load_config():
    filepath = os.path.join(os.environ["CONFIG_DIR"], 'telescope_config.json');
    with open(filepath) as json_file:
        config = json.load(json_file)
    filepath = os.path.join(os.environ["CONFIG_DIR"], 'calibrated_antenna_positions.json');
    with open(filepath) as json_file:
        positions = json.load(json_file)
    

def create_spi_object(runtime_config, speed=16000000):
  perm = load_permute()
  logging.info(f'create_spi_object(speed={speed}')
  try:
    return TartSPI(runtime_config, perm, speed)
  except Exception as e:
    logging.exception(e)
    logging.warn('USING DUMMY SPI MODULE.')
    return TartFakeSPI(runtime_config, perm, speed)
