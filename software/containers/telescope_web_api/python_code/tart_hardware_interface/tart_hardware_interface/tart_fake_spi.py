'''
    Inherit from tartspi and create fake data
    from a model sky, then return this data
'''
import json

import logging
import numpy as np

from .tartspi import TartSPI

from tart.imaging import visibility
from tart.imaging import calibration
from tart.imaging import antenna_model
from tart.imaging import radio_source
from tart.imaging import correlator
from tart.imaging import location
from tart.simulation import skymodel
from tart.simulation import antennas
from tart.simulation import radio
from tart.simulation.simulator import get_vis_parallel, get_vis

# def load_permute(filepath=PERMUTE_FILE, noisy=False):
#   '''Load a permutation vector from the file at the given filepath.'''
#   filepath = os.path.join(os.environ["CONFIG_DIR"], PERMUTE_FILE);
#   pp = np.loadtxt(filepath, dtype='int')
#   return pp


'''
    Load the telescope configuration as well as the entenna positions. Then
    calculate the visibilities from some moving point sources.
'''
def forward_map():
    filepath = os.path.join(os.environ["CONFIG_DIR"], 'telescope_config.json');
    with open(filepath) as json_file:
        config = json.load(json_file)
    filepath = os.path.join(os.environ["CONFIG_DIR"], 'calibrated_antenna_positions.json');
    with open(filepath) as json_file:
        positions = json.load(json_file)
    
    
    n_ant = config['num_antenna']
    n_vis = (n_ant * (n_ant - 1)) // 2

    # Generate model visibilities according to specified point source positions
    sim_sky= skymodel.Skymodel(0, location=loc,
                               gps=0, thesun=0, known_cosmic=0)
    sim_sky.add_src(radio_source.ArtificialSource(loc, timestamp, r=100.0, el=m['el'], az=m['az']))
    v_sim = get_vis(sim_sky, COR, RAD, ANTS, ANT_MODELS, SETTINGS, timestamp, mode=MODE)
    sim_vis = calibration.CalibratedVisibility(v_sim)


    return np.ones(n_vis)

class TartFakeSPI(TartSPI):
    
    ##--------------------------------------------------------------------------
    ##  FAKE TART SPI interface.
    ##--------------------------------------------------------------------------
    def __init__(self, permute, speed=32000000):
        super().__init__(permute, speed, True)
    

    # Override reading of data
    
    def setbyte(self, reg, val, noisy=False):
        '''
            Ignore all write command
        '''
        return True


    def getbyte(self, reg, noisy=False):
        res = 0xFF
        return res

    def getbytes(self, reg, num, noisy=False):
        reg = int(reg) & 0x7f
        res = [0xFF for i in range(num)]
        if noisy:
            for val in res:
                print('%s' % self.show_status(reg, val))
            self.pause(duration=num/100000.0)
        return res

    def vis_ready(self, noisy=False):
        if np.random.uniform(0,100) < 10:
            return True
        return False


    def vis_read(self, noisy=False):
        while not self.vis_ready(noisy):
            self.pause()
        vis = self.read_visibilities(noisy)
        return vis

    def read_visibilities(self, noisy=True):
        '''
            Read back visibilities data.
            This should perform the ifft imaging...
        '''
        vis = forward_map()
        
        res = self.getbytes(self.VX_STREAM, 4*576)
        val = self.vis_convert(res)
        if noisy:
            tim = time.time()
            print(" Visibilities (@t = %g):\n%s (sum = %d)" % (tim, val[self.perm]-int(2**(self.blocksize-1)), sum(val)))
        return val

    def vis_convert(self, viz):
        arr = np.zeros(576, dtype='int')
        for i in range(0,576):
            j = i*4
            x = viz[j] | (viz[j+1] << 8) | (viz[j+2] << 16) | ((viz[j+3] & 0x7f) << 24)
            if viz[j+3] > 0x7f:
                x = -x
            arr[i] = x
        return arr
