from flask import jsonify, request
from flask_jwt_extended import jwt_required

import tart_web_api.database as db
from tart_web_api.app import app


@jwt_required()
@app.route(
    "/calibration/gain",
    methods=[
        "POST",
    ],
)
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
    content = request.get_json(silent=False)
    with db.connect_to_db() as con:
        c = con.cursor()
        db.insert_gain(c, content["gain"], content["phase_offset"])
    return jsonify({})


@jwt_required()
@app.route(
    "/calibration/antenna_positions",
    methods=[
        "POST",
    ],
)
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
    content = request.get_json(silent=False)
    runtime_config = app.config["CONFIG"]
    app.logger.info(content)
    runtime_config["antenna_positions"] = content
    return jsonify({})


@app.route(
    "/calibration/gain",
    methods=[
        "GET",
    ],
)
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
    runtime_config = app.config["CONFIG"]
    num_ant = runtime_config["telescope_config"]["num_antenna"]
    rows_dict = db.get_gain()
    ret_gain = [rows_dict[i][2] for i in range(num_ant)]
    ret_ph = [rows_dict[i][3] for i in range(num_ant)]
    ret_dict = {"gain": ret_gain, "phase_offset": ret_ph}
    return jsonify(ret_dict)
