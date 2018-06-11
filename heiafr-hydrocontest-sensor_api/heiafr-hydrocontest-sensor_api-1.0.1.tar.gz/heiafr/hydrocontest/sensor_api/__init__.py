from flask import Flask, jsonify
from sense_hat import SenseHat

app = Flask(__name__)

@app.route("/")
def sensors():
    sense = SenseHat()
    sense.clear()
    data = {
        "H": sense.get_humidity(),
        "T": sense.get_temperature_from_humidity(),
        "P": sense.get_pressure(),
    }
    f = open("/sys/class/thermal/thermal_zone0/temp")
    cpu_temp = f.readline()
    f.close()
    data["C"] = int(cpu_temp)/1000
    
    return jsonify(data)
