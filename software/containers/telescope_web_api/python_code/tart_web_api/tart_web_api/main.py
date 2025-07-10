#
# TART web api main file.
#
# Maximilian Scheel (c) 2017 max@max.ac.nz
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


def tart_p(rt_config):
    tart_control = TartControl(rt_config)
    while True:
        tart_control.set_state(rt_config["mode"])
        tart_control.run(noisy=True)


app = Flask(__name__)

# Set up logging

with app.app_context():
    if not app.debug:
        # In production mode, add log handler to sys.stderr.
        app.logger.addHandler(logging.StreamHandler())
        app.logger.setLevel(logging.INFO)

CORS(app)

app.secret_key = os.environ.get("SECRET_KEY", "super-secret-123897219379179464asd13khk213")
app.config["JWT_HEADER_TYPE"] = "JWT"
jwt = JWTManager(app)


# import tart_web_api.views_log

# if __name__ == "__main__":
m = multiprocessing.Manager()
runtime_config = init_config(m)
runtime_config["sample_delay"] = db.get_sample_delay()
app.config["CONFIG"] = runtime_config
num_ant = runtime_config["telescope_config"]["num_antenna"]

db.setup_db(num_ant)

observation_cache_process = multiprocessing.Process(target=cleanup_observation_cache, args=())
observation_cache_process.start()

visibility_cache_process = multiprocessing.Process(target=cleanup_visibility_cache, args=())
visibility_cache_process.start()


tart_process = multiprocessing.Process(target=tart_p, args=(runtime_config,))
tart_process.start()

#    app.run(debug=True, use_reloader=False, port=5000, host='0.0.0.0')
