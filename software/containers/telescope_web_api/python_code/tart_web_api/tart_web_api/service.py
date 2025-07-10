"""
Services for the TART web api. These are background processes that
capture visibilities e.t.c.

Author. Max Scheel 2017
        Tim Molteno 2018-2021

"""

import logging
import os
import time

logging.basicConfig(level=os.environ.get("LOGLEVEL", "INFO"))

from tart.imaging import visibility
from tart.util import utc

# prepare to replace with utility
save_vis_list = visibility.list_save

from tart_hardware_interface.highlevel_modes_api import (
    run_acquire_raw,
    run_diagnostic,
    sha256_checksum,
)
from tart_hardware_interface.stream_vis import stream_vis_to_queue
from tart_hardware_interface.util import create_spi_object

import tart_web_api.database as db

N_IT = 0


def cleanup_observation_cache():
    while True:
        resp = db.get_raw_file_handle()
        if len(resp) > 10:
            for entry in resp[10:]:
                try:
                    db.remove_raw_file_handle_by_Id(entry["Id"])
                    print("removed", entry["Id"], entry["filename"], entry["checksum"])
                except Exception as e:
                    print("couldnt remove handle from database", e)
                    pass
                try:
                    os.remove(entry["filename"])
                except Exception as e:
                    print("couldnt remove file", e)
                    pass
        else:
            db.update_observation_cache_process_state("OK")
        time.sleep(60)


def cleanup_visibility_cache():
    while True:
        resp = db.get_vis_file_handle()
        if len(resp) > 10:
            for entry in resp[10:]:
                try:
                    db.remove_vis_file_handle_by_Id(entry["Id"])
                    print("removed", entry["Id"], entry["filename"], entry["checksum"])
                except Exception as e:
                    print("couldnt remove handle from database", e)
                    pass
                try:
                    os.remove(entry["filename"])
                except Exception as e:
                    print("couldnt remove file", e)
                    pass

        else:
            db.update_vis_cache_process_state("OK")
        time.sleep(60)


def create_direct_vis_dict(vis):
    vis_dict = {}
    vis_list = []
    for b, v in zip(vis.baselines, vis.v, strict=False):
        i, j = b
        vis_el = {"i": i, "j": j, "re": v.real, "im": v.imag}
        vis_list.append(vis_el)
    vis_dict = {"data": vis_list, "timestamp": utc.to_string(vis.timestamp)}
    return vis_dict


class TartControl:
    """High Level TART Interface"""

    def __init__(self, runtime_config):
        self.TartSPI = create_spi_object(runtime_config)

        self.config = runtime_config
        self.state = "off"
        self.queue_vis = None
        self.process_vis_calc = None
        self.cmd_queue_vis_calc = None
        self.process_capture = None
        self.cmd_queue_capture = None
        self.vislist = []
        os.makedirs(self.config["vis"]["base_path"], exist_ok=True)
        os.makedirs(self.config["raw"]["base_path"], exist_ok=True)

    def run(self):
        try:
            if self.state == "diag":
                run_diagnostic(self.TartSPI, self.config)
                db.insert_sample_delay(
                    self.config["channels_timestamp"], self.config["sample_delay"]
                )

            elif self.state == "raw":
                ret = run_acquire_raw(self.TartSPI, self.config)
                if "filename" in ret:
                    db.insert_raw_file_handle(ret["filename"], ret["sha256"])

            elif self.state == "vis":
                if self.queue_vis is None:
                    logging.info("vis_stream_setup")
                    self.vis_stream_setup()
                else:
                    ret = self.vis_stream_acquire()
                    if "filename" in ret:
                        logging.debug(f"vis_stream_acquire = {ret}")
                        db.insert_vis_file_handle(ret["filename"], ret["sha256"])
                    time.sleep(0.005)
            elif self.state == "off":
                time.sleep(0.5)
            else:
                logging.error(f"unknown state: {self.state}")
        except Exception as err:
            logging.error(f"Error: {self.state}")
            logging.exception(err)

    def set_state(self, new_state):
        if new_state == self.state:
            return
        else:
            """ State Transition """
            if self.state == "vis":
                """Cleanup vis acquisition queues and processes"""
                self.vis_stream_finish()
            self.state = new_state

    def vis_stream_setup(self):
        (
            self.queue_vis,
            self.process_vis_calc,
            self.process_capture,
            self.cmd_queue_vis_calc,
            self.cmd_queue_capture,
        ) = stream_vis_to_queue(self.TartSPI, self.config)

    def vis_stream_acquire(self):
        """Get all available visibities"""
        ret = {}

        while self.queue_vis.qsize() > 0:
            vis, means = self.queue_vis.get()
            if vis is not None:
                self.config["vis_current"] = create_direct_vis_dict(vis)
                self.vislist.append(vis)
                logging.debug(f"Updated vis list N={len(self.vislist)}")

                chunksize = self.config["vis"]["chunksize"]
                if len(self.vislist) >= chunksize:
                    logging.info(f"reached chunksize of {chunksize}")
                    if self.config["vis"]["save"] == 1:
                        fname = "{}/vis_{}.hdf".format(
                            self.config["vis"]["base_path"],
                            vis.timestamp.strftime("%Y-%m-%d_%H_%M_%S.%f"),
                        )

                        # Get the gains and phases and save them with the visibilities
                        rows_dict = db.get_gain()
                        gain = [rows_dict[i][2] for i in range(24)]
                        phases = [rows_dict[i][3] for i in range(24)]

                        ant_pos = self.config["antenna_positions"]
                        save_vis_list(self.vislist, ant_pos, gain, phases, fname)

                        logging.info(f"saved to {vis}")
                        ret["filename"] = fname
                        ret["sha256"] = sha256_checksum(fname)
                    self.vislist = []
        return ret

    def vis_stream_finish(self):
        self.cmd_queue_capture.put("stop")
        self.cmd_queue_vis_calc.put("stop")
        self.process_capture.join()
        self.process_vis_calc.join()
        self.queue_vis = None
        self.vislist = []
        print("Stop visibility acquisition processes.")

    def vis_stream_reconfigure(self):
        self.vis_stream_finish()
