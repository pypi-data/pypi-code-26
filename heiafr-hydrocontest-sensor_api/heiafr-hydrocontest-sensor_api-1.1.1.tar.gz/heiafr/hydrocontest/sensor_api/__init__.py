# Copyright 2018 Jacques Supcik, HEIA-FR
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
This program gives environmental data using a simple JSON Web Service
"""

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
