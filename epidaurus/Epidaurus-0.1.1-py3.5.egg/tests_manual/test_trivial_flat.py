import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from tools.model_trivial_flat import TrivialFlat
from epidaurus.pid import PID
from pathlib import Path
from pelops import mypyyaml
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt


png_filename = 'test_trivial_flat.png'


def create_png(series, filename):
    plt.plot(series["key"], series["set-point"], color="tab:red")
    plt.plot(series["key"], series["reaction"], color="tab:blue")
    plt.plot(series["key"], series["temperature"], color="tab:green")
    fig = plt.gcf()
    fig.tight_layout()
    DPI = fig.get_dpi()
    fig.set_size_inches(1024.0 / float(DPI), 768.0 / float(DPI))
    plt.savefig(filename, bbox_inches='tight')


# inc. 22.15 -> 22.84 in 30 min -> 0.023/min
# dec. 23.34 -> 23.06 in 30 min -> 0.0093/min

flat = TrivialFlat(20, True, temp_decrease=0.0093, heater_temp_inc=0.023)
series = {}
series["key"] = []
series["set-point"] = []
series["reaction"] = []
series["temperature"] = []
counter = 0

volt = 3
for i in range(0,15):
    flat.update_temperature(volt)
    series["key"].append(counter)
    series["set-point"].append(flat.heater_set_point)
    series["reaction"].append(flat.heater_reaction*100)
    series["temperature"].append(flat.temperature)
    counter += 1

volt = 4.5
for i in range(0,15):
    flat.update_temperature(volt)
    series["key"].append(counter)
    series["set-point"].append(flat.heater_set_point)
    series["reaction"].append(flat.heater_reaction*100)
    series["temperature"].append(flat.temperature)
    counter += 1

volt = 22
for i in range(0,30):
    flat.update_temperature(volt)
    series["key"].append(counter)
    series["set-point"].append(flat.heater_set_point)
    series["reaction"].append(flat.heater_reaction*100)
    series["temperature"].append(flat.temperature)
    counter += 1

for volt in range(22, 0, -1):
    for i in range(0,10):
        flat.update_temperature(volt)
        series["key"].append(counter)
        series["set-point"].append(flat.heater_set_point)
        series["reaction"].append(flat.heater_reaction*100)
        series["temperature"].append(flat.temperature)
        counter += 1

volt = 4.5
for i in range(0,180):
    flat.update_temperature(volt)
    series["key"].append(counter)
    series["set-point"].append(flat.heater_set_point)
    series["reaction"].append(flat.heater_reaction*100)
    series["temperature"].append(flat.temperature)
    counter += 1


create_png(series, png_filename)
