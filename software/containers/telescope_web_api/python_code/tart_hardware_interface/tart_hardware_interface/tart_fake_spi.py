'''
    Inherit from tartspi and create fake data
    from a model sky, then return this data
'''
import json
import os
from datetime import datetime

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
from tart.operation import settings



'''
    Load the telescope configuration as well as the entenna positions. Then
    calculate the visibilities from some moving point sources.
'''
def forward_map(runtime_config):
    MODE = 'mini'
    SETTINGS = settings.from_dict(runtime_config['telescope_config'])
    loc = location.get_loc(SETTINGS)
    
    ANTS = [antennas.Antenna(loc, pos)
            for pos in runtime_config['antenna_positions']]
    ANT_MODELS = [antenna_model.GpsPatchAntenna() for i in range(SETTINGS.get_num_antenna())]
    NOISE_LVLS = 0.0 * np.ones(SETTINGS.get_num_antenna())
    RAD = radio.Max2769B(n_samples=2**12, noise_level=NOISE_LVLS)
    COR = correlator.Correlator()

    global msd_vis, sim_vis
    sim_vis = {}
    msd_vis = {}

    sim_sky= skymodel.Skymodel(0, location=loc, gps=0, thesun=0, known_cosmic=0)
    
    timestamp = datetime.utcnow()
    
    # The pattern rotates once per day
    hour_hand = timestamp.hour*30.0 + timestamp.minute/4.0

    sources = [ { 'el': el, 'az': hour_hand} for el in [85, 75, 65, 55] ]
    for m in sources:
        sim_sky.add_src(radio_source.ArtificialSource(loc, timestamp, r=100.0, el=m['el'], az=m['az']))

    minute_hand = timestamp.minute*6.0 + timestamp.second/10.0

    sources = [ { 'el': el, 'az': minute_hand} for el in [90, 80, 70, 60, 50, 40, 30] ]
    for m in sources:
        sim_sky.add_src(radio_source.ArtificialSource(loc, timestamp, r=100.0, el=m['el'], az=m['az']))
    
    v_sim = get_vis(sim_sky, COR, RAD, ANTS, ANT_MODELS, SETTINGS, timestamp, mode=MODE)
    # print(f"Simulated Vis: {v_sim.v.shape}")
    # sim_vis = calibration.CalibratedVisibility(v_sim)

    # Now convert to an array of bytes
    
    return v_sim

class TartFakeSPI(TartSPI):
    
    ##--------------------------------------------------------------------------
    ##  FAKE TART SPI interface.
    ##--------------------------------------------------------------------------
    def __init__(self, runtime_config, permute, speed=32000000):
        super().__init__(runtime_config, permute, speed, True)
    

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
        vis = forward_map(self.runtime_config)
        
        res = self.getbytes(self.VX_STREAM, 4*576)
        val = self.vis_convert(res)
        if noisy:
            tim = time.time()
            print(" Visibilities (@t = %g):\n%s (sum = %d)" % (tim, val[self.perm]-int(2**(self.blocksize-1)), sum(val)))
        return vis

    def vis_convert(self, viz):
        arr = np.zeros(576, dtype='int')
        for i in range(0,576):
            j = i*4
            x = viz[j] | (viz[j+1] << 8) | (viz[j+2] << 16) | ((viz[j+3] & 0x7f) << 24)
            if viz[j+3] > 0x7f:
                x = -x
            arr[i] = x
        return arr
