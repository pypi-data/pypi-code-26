import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from epidaurus.pid import PID
from pathlib import Path
from pelops import mypyyaml
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from tools.model_trivial_flat import TrivialFlat
from pelops.read_config import read_config


png_filename = 'test_pid_model.png'


def create_png(series, filename):
    list_key = []
    list_target_temperature = []
    list_heater_set_point = []
    list_temperature = []
    for key, entry in series.items():
        list_key.append(key)
        list_target_temperature.append(entry["target_temperature"])
        list_heater_set_point.append(entry["heater_set_point"])
        list_temperature.append(entry["temperature"])

    plt.plot(list_key, list_target_temperature, color="tab:red")
    plt.plot(list_key, list_heater_set_point, color="tab:blue")
    plt.plot(list_key, list_temperature, color="tab:green")
    fig = plt.gcf()
    fig.tight_layout()
    DPI = fig.get_dpi()
    fig.set_size_inches(1024.0 / float(DPI), 768.0 / float(DPI))
    plt.savefig(filename, bbox_inches='tight')


config = read_config()

flat = TrivialFlat(temperature=0, verbose=True, temp_decrease=0.01, heater_temp_inc=0.9, heater_max=1, heater_idle=0,
                 heater_safety=0)

pid = PID(config["controller"]["pid"], True)
pid.reset(0,0)

pid._p_gain = 1.025
pid._i_gain = 0.0035
pid._d_gain = 0.05
pid._windup_guard = 20
pid._update_interval = 30
pid._set_point = 0

series = {}
temperature = 0
target_temperature = 0
heater_set_point = 0
pid._set_point = target_temperature

for i in range(0,50):
    if i == 10:
        target_temperature = 1
        pid._set_point = target_temperature

    heater_set_point = pid.update(temperature)
    temperature = flat.update_temperature(min(1, heater_set_point / 1.2))

    series[i] = {
        "target_temperature": target_temperature,
        "heater_set_point": heater_set_point,
        "temperature": temperature
    }

create_png(series, png_filename)
