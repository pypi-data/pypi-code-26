from flask import jsonify

from app import app

@app.route('/actuator/info', methods=['GET'])
def actuator_info():
    return jsonify({})


@app.route('/actuator/health', methods=['GET'])
def actuator_health():
    return jsonify({"status": "UP"})
