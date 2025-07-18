import json
import multiprocessing

from flask import request
from flask import jsonify
from flask_jwt_extended import jwt_required

from tart_web_api.app import app
from tart_web_api import service
import tart_web_api.database as db

from tart.util import utc

minimize_process = None


@jwt_required()
@app.route('/calibration/gain', methods=['POST',])
def set_gain():
    """
    @api {POST} /calibration/gain Set channel based complex gains.
    @apiName set_gain
    @apiGroup Calibration

    @apiHeader (Authorization) {String} Authorization JWT authorization value.

    @apiParam {Object}   body
    @apiParam {Number[]} body.gain List of channel gains
    @apiParam {Number[]} body.phase_offset List of channel phase offset (rad)
    """
    utc_date = utc.now()
    content = request.get_json(silent=False)
    g = content['gain']
    ph = content['phase_offset']
    con = db.connect_to_db()
    with con:
        c = con.cursor()
        db.insert_gain(c, utc_date, g, ph)
    return jsonify({})


@jwt_required()
@app.route('/calibration/antenna_positions', methods=['POST',])
def set_calibration_antenna_positions():
    """
    @api {POST} /calibration/antenna_positions Set antenna positions .
    @apiName set_calibration_antenna_positions
    @apiGroup Calibration

    @apiHeader (Authorization) {String} Authorization JWT authorization value.

    @apiParam {Object}   body
    @apiParam {Object[]} body.antenna_positions Array of antenna positions in
                        East-North-Up Coordinate system [[e,n,u],[e,n,u],..]].
    """
    utc_date = utc.now()
    content = request.get_json(silent=False)
    runtime_config = app.config['CONFIG']
    app.logger.info(content)
    runtime_config['antenna_positions'] = content
    return jsonify({})


@app.route('/calibration/gain', methods=['GET',])
def get_gain():
    """
    @api {GET} /calibration/gain Get channel based complex gains.
    @apiName get_gain
    @apiGroup Calibration

    @apiSuccess {Object}  body
    @apiSuccess {Number[]} body.gain List of channel gains
    @apiSuccess {Number[]} body.phase_offset List of channel phase offset (rad)

    @apiSampleRequest /calibration/gain
    """
    runtime_config = app.config['CONFIG']
    num_ant = runtime_config['telescope_config']['num_antenna']
    rows_dict = db.get_gain()
    ret_gain = [rows_dict[i][2] for i in range(num_ant)]
    ret_ph = [rows_dict[i][3] for i in range(num_ant)]
    ret_dict = {"gain": ret_gain,
                "phase_offset": ret_ph}
    return jsonify(ret_dict)


@jwt_required()
@app.route('/calibrate', methods=['POST',])
def post_calibration_from_vis():
    """
    @api {POST} /calibrate Start minimisation process by providing calibration measurements.
    @apiName post_calibration_from_vis
    @apiGroup Calibration

    @apiHeader (Authorization) {String} Authorization JWT authorization value.

    @apiParam {Object[]} body
    @apiParam {Number} body.el Elevation in decimal degree.
    @apiParam {Number} body.az Azimuth in decimal degree.
    @apiParam {Object[]} body.data Calibration data.
    @apiParam {Object[]} body.data.vis Visibilities from point source at specified elevation and azimuth.
    @apiParam {Object[]} body.data.timestamp Timestamp of measurement.
    @apiSuccess {String} status Status of optimisation process.
    """
    state = db.get_calibration_process_state()
    runtime_config = app.config['CONFIG']
    if state in ['idle', 'preparing']:
        db.update_calibration_process_state('preparing')
        cal_measurements = request.get_json(silent=False)
        t = utc.now()
        cal_request_file_name = t.strftime('Cal_%Y-%m-%d_%H-%M.json')
        with open(cal_request_file_name, 'w') as outfile:
            json.dump(cal_measurements, outfile)
            app.logger.info('saved to: %s ', cal_request_file_name)
        global minimize_process
        minimize_process = multiprocessing.Process(target=service.calibrate_from_vis, args=(cal_measurements, runtime_config))
        minimize_process.start()
        state = db.get_calibration_process_state()
    return jsonify({'status': state})


@app.route('/calibrate', methods=['GET',])
def get_calibrate_status():
    """
    @api {GET} /calibrate Get optimisation status.
    @apiName get_calibrate_status
    @apiGroup Calibration

    @apiSuccess {String} status Status of optimisation process.
    """
    state = db.get_calibration_process_state()
    return jsonify({'status': state})
