'''
    Inherit from tartspi and create fake data
    from a model sky, then return this data
'''
import logging
import numpy as np

from .tartspi import TartSPI

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
