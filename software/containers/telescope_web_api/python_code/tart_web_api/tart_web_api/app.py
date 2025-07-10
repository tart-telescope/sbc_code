#
# TART web api main file.
#
# Maximilian Scheel (c) 2017, 2025. max@max.ac.nz
# Tim Molteno 2018-2019. tim@elec.ac.nz
#
import logging
import multiprocessing
import os

from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager

import tart_web_api.database as db
from tart_web_api.config import init_config
from tart_web_api.service import (
    TartControl,
    cleanup_observation_cache,
    cleanup_visibility_cache,
)


def setup():
    app = Flask(__name__)
    CORS(app)
    with app.app_context():
        if not app.debug:
            # In production mode, add log handler to sys.stderr.
            app.logger.addHandler(logging.StreamHandler())
            app.logger.setLevel(logging.INFO)

    app.secret_key = os.environ.get(
        "SECRET_KEY", "super-secret-123897219379179464asd13khk213"
    )  # Change this!
    app.config["JWT_HEADER_TYPE"] = "JWT"
    jwt = JWTManager(app)

    m = multiprocessing.Manager()
    runtime_config = init_config(m)
    app.config["CONFIG"] = runtime_config
    num_ant = runtime_config["telescope_config"]["num_antenna"]
    db.setup_db(num_ant)
    runtime_config["sample_delay"] = db.get_sample_delay()

    observation_cache_process = multiprocessing.Process(target=cleanup_observation_cache, args=())
    observation_cache_process.start()

    visibility_cache_process = multiprocessing.Process(target=cleanup_visibility_cache, args=())
    visibility_cache_process.start()

    def tart_p(rt_config):
        tart_control = TartControl(rt_config)
        while True:
            tart_control.set_state(rt_config["mode"])
            tart_control.run()

    tart_process = multiprocessing.Process(target=tart_p, args=(runtime_config,))
    tart_process.start()
    return app


app = setup()
