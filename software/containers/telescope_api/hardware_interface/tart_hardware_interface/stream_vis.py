"""Visibility Streaming Code"""

import logging.config
import multiprocessing
import time
import traceback

import numpy as np
from tart.imaging import visibility
from tart.operation import settings
from tart.util import utc

from tart_hardware_interface.highlevel_modes_api import get_status

logger = logging.getLogger(__name__)

"""
    This function performs the van_vleck_correction for two-level quantization.
    https://arxiv.org/pdf/1608.04367.pdf
"""


def van_vleck_correction(R):
    return np.sin(np.pi / 2.0 * R)


def get_corr(xnor_sum, n_samples):
    return 2 * xnor_sum / float(n_samples) - 1


"""
    The data is composed to 276 real:imag pairs, followed by the 24 means of the real components
"""


def get_vis_object(data, runtime_config):
    n_samples = 2 ** runtime_config["vis"]["N_samples_exp"]
    timestamp = utc.now()
    config = settings.from_file(runtime_config["telescope_config_path"])
    num_ant = config.get_num_antenna()
    v = []
    baselines = []
    xnor_cos = data[0:-num_ant:2]
    xnor_sin = data[1:-num_ant:2]
    corr_cos_i_cos_j = get_corr(xnor_cos, n_samples)
    corr_cos_i_sin_j = get_corr(xnor_sin, n_samples)
    means = (data[-num_ant:]) / float(n_samples) * 2.0 - 1
    for i in range(0, num_ant):
        for j in range(i + 1, num_ant):
            idx = len(baselines)
            baselines.append([i, j])
            v_real = van_vleck_correction((-means[i] * means[j]) + corr_cos_i_cos_j[idx])
            v_imag = van_vleck_correction((-means[i] * means[j]) + corr_cos_i_sin_j[idx])

            v_com = v_real - 1j * v_imag
            v.append(v_com)
    vis = visibility.Visibility.from_config(config, timestamp)
    vis.set_visibilities(v, baselines)
    return vis, means, timestamp


def get_data(tart_instance):
    viz = tart_instance.vis_read(noisy=False)
    if tart_instance.spi is None:
        return viz
    return viz[tart_instance.perm]


def capture_loop(
    tart_instance,
    process_queue,
    cmd_queue,
    runtime_config,
    logger=logger,
):
    logger.info("Capture Loop Start")
    tart_instance.reset()
    tart_instance.read_status(True)
    tart_instance.debug(on=False, shift=False, count=False, noisy=True)
    tart_instance.read_status(True)
    tart_instance.capture(on=True, noisy=False)
    tart_instance.set_sample_delay(runtime_config["sample_delay"])
    tart_instance.start(runtime_config["vis"]["N_samples_exp"], True)
    active = 1
    while active:
        try:
            if not cmd_queue.empty():
                cmd = cmd_queue.get()
                if cmd == "stop":
                    active = 0
            # Add the data to the process queue
            data = get_data(tart_instance)
            d = get_status(tart_instance)
            # Pass status data through the queue instead of updating runtime_config
            process_queue.put((data, d))
            logger.info(("Capture Loop: Vis Data Acquired"))
        except Exception as e:
            logger.error("Capture Loop Error %s" % str(e))
            logger.error(traceback.format_exc())
    logger.info("Done acquisition. Closing Capture Loop.")
    return 1


def update_means(means, ts, runtime_config):
    channels = []
    for i in range(runtime_config["telescope_config"]["num_antenna"]):
        channel = {}
        for key in runtime_config["channels"][i]:
            channel[key] = runtime_config["channels"][i][key]
        channel["radio_mean"] = means[i]
        channels.append(channel)
    runtime_config["channels"] = channels
    runtime_config["channels_timestamp"] = ts


def process_loop(process_queue, vis_queue, cmd_queue, runtime_config, logger=logger):
    active = 1
    logger.debug("process_loop start")
    while active:
        try:
            time.sleep(0.01)
            if not cmd_queue.empty():
                cmd = cmd_queue.get()
                if cmd == "stop":
                    active = 0
            if not process_queue.empty():
                queue_item = process_queue.get()

                # Handle both old format (data only) and new format (data, status)
                if isinstance(queue_item, tuple) and len(queue_item) == 2:
                    data, status = queue_item
                    # Update runtime_config with status in the main process
                    runtime_config["status"] = status
                else:
                    data = queue_item

                if hasattr(data, "v"):  # Test if the data contains a vis object.
                    vis = data
                    means = np.zeros(runtime_config["telescope_config"]["num_antenna"])
                    timestamp = vis.timestamp
                else:  # Otherwise the data is real.
                    vis, means, timestamp = get_vis_object(data, runtime_config)
                vis_queue.put((vis, means))
        except Exception as e:
            logger.error("Processing Error %s" % str(e))
            logger.error(traceback.format_exc())
            logger.error(f"Data: {data.shape}")
    logger.debug("process_loop finished")
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

    capture_process = multiprocessing.Process(
        target=capture_loop,
        args=(tart, raw_data_queue, capture_cmd_queue, runtime_config, logger),
    )
    vis_calc_process = multiprocessing.Process(
        target=process_loop,
        args=(raw_data_queue, vis_queue, vis_calc_cmd_queue, runtime_config, logger),
    )

    vis_calc_process.start()
    capture_process.start()
    return (
        vis_queue,
        vis_calc_process,
        capture_process,
        vis_calc_cmd_queue,
        capture_cmd_queue,
    )
