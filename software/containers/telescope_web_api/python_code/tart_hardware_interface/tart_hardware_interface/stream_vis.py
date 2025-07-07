'''  Visibility Streaming Code

'''
import numpy as np

import os
import stat

import multiprocessing
import traceback
import logging.config
import time

logger = logging.getLogger(__name__)

from tart.operation import settings
from tart.imaging import visibility
from tart.util import angle
from tart.util import utc

from tart_hardware_interface.highlevel_modes_api import get_status_json

'''
    This function performs the van_vleck_correction for two-level quantization.

    https://arxiv.org/pdf/1608.04367.pdf
'''
def van_vleck_correction(R):
    return np.sin(np.pi / 2.0 * R)

def get_corr(xnor_sum, n_samples):
    return 2*xnor_sum/float(n_samples)-1


'''
    The data is composed to 276 real:imag pairs, followed by the 24 means of the real components
'''
def get_vis_object(data, runtime_config):
    n_samples = 2**runtime_config['vis']['N_samples_exp']
    timestamp = utc.now()
    config = settings.from_file(runtime_config['telescope_config_path'])
    num_ant = config.get_num_antenna()
    v = []
    baselines = []
    xnor_cos = data[0:-num_ant:2]
    xnor_sin = data[1:-num_ant:2]
    corr_cos_i_cos_j = get_corr(xnor_cos, n_samples)
    corr_cos_i_sin_j = get_corr(xnor_sin, n_samples)
    means = (data[-num_ant:])/float(n_samples)*2.-1
    #print(means)
    for i in range(0, num_ant):
        for j in range(i+1, num_ant):
            idx = len(baselines)
            baselines.append([i, j])
            v_real = van_vleck_correction((-means[i]*means[j]) + corr_cos_i_cos_j[idx])
            v_imag = van_vleck_correction((-means[i]*means[j]) + corr_cos_i_sin_j[idx])

            v_com = v_real - 1j * v_imag
            v.append(v_com)
    vis = visibility.from_config(config, timestamp)
    vis.set_visibilities(v, baselines)
    return vis, means, timestamp

def get_data(tart):
    viz = tart.vis_read(noisy=False)
    if tart.spi is None:
        return viz
    return viz[tart.perm]

def capture_loop(tart, process_queue, cmd_queue, runtime_config, logger=None,):
    print('Capture Loop Start')
    tart.reset()
    tart.read_status(True)
    tart.debug(on=False, shift=False, count=False, noisy=True)
    tart.read_status(True)
    tart.capture(on=True, noisy=False)
    tart.set_sample_delay(runtime_config['sample_delay'])
    tart.start(runtime_config['vis']['N_samples_exp'], True)
    active = 1
    while active:
        try:
            if cmd_queue.empty() == False:
                cmd = cmd_queue.get()
                if cmd == 'stop':
                    active = 0
            # Add the data to the process queue
            data = get_data(tart)
            d, d_json = get_status_json(tart)
            runtime_config['status'] = d
            process_queue.put(data)
            logger.info((f"Capture Loop: Acquired"))
        except Exception as e:
            logger.error("Capture Loop Error %s" % str(e))
            logger.error(traceback.format_exc())
    print('Done acquisition. Closing Capture Loop.')
    return 1

def update_means(means, ts, runtime_config):
    channels = []
    for i in range(runtime_config['telescope_config']['num_antenna']):
        channel = {}
        for key in runtime_config['channels'][i]:
            channel[key] = runtime_config['channels'][i][key]
        channel['radio_mean'] = means[i]
        channels.append(channel)
    runtime_config['channels'] = channels
    runtime_config['channels_timestamp'] = ts

def process_loop(process_queue, vis_queue, cmd_queue, runtime_config, logger=None):
    active = 1
    print('process_loop start')
    while active:
        try:
            time.sleep(0.01)
            if cmd_queue.empty() == False:
                cmd = cmd_queue.get()
                if cmd == 'stop':
                    active = 0
            if process_queue.empty() == False:
                data = process_queue.get()
                if hasattr(data, 'v'): # Test if the data contains a vis object.
                    vis = data
                    means = np.zeros(runtime_config['telescope_config']["num_antenna"])
                    timestamp = vis.timestamp
                else:  # Otherwise the data is real.
                    vis, means, timestamp = get_vis_object(data, runtime_config)
                #print(vis, means, timestamp)
                #update_means(means, timestamp, runtime_config)
                #print(means)
                #print( 'Process Loop:', # vis)
                vis_queue.put((vis, means))
        except Exception as e:
            logger.error("Processing Error %s" % str(e))
            logger.error(traceback.format_exc())
            logger.error(f"Data: {data.shape}")
    print('process_loop finished')
    return 1

def stream_vis_to_queue(tart, runtime_config):
    # tart
    # >> [2x visibility and mean readout]
    # >> raw_data_queue >> [visibility assembly]
    # >> vis_queue

    # Send data to each process
    raw_data_queue = multiprocessing.Queue()
    vis_queue = multiprocessing.Queue()

    # Send commands to each process
    capture_cmd_queue = multiprocessing.Queue()
    vis_calc_cmd_queue = multiprocessing.Queue()

    capture_process = multiprocessing.Process(target=capture_loop,\
      args=(tart, raw_data_queue, capture_cmd_queue, runtime_config, logger))
    vis_calc_process = multiprocessing.Process(target=process_loop,\
      args=(raw_data_queue, vis_queue, vis_calc_cmd_queue, runtime_config, logger))

    vis_calc_process.start()
    capture_process.start()
    return vis_queue, vis_calc_process, capture_process, vis_calc_cmd_queue, capture_cmd_queue
