import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from epidaurus.controller import Controller
from pathlib import Path
from pelops import mqttclient
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from tools.model_trivial_flat import TrivialFlat
from pelops.read_config import read_config
import threading
import time


png_filename = 'test_controller_model_nomqtt.png'


def create_png(series, filename):
    plt.xlabel('Hours')
    plt.ylabel('Volt/Celsius')
    plt.title('Thermostat')
    plt.plot(series["key"], series["target_temperature"], label="target_temperature", color="tab:red")
#    plt.plot(series["key"], series["output"], label="output", color="tab:orange")
#    plt.plot(series["key"], series["output_raw"], label="output_raw", color="tab:purple")
    plt.plot(series["key"], series["heater_set_point"], label="heater_set_point", color="tab:blue")
    plt.plot(series["key"], series["temperature"], label="temperature", color="tab:green")
    plt.legend()
    fig = plt.gcf()
    fig.tight_layout()
    DPI = fig.get_dpi()
    fig.set_size_inches(1024.0 / float(DPI), 768.0 / float(DPI))
    plt.savefig(filename, bbox_inches='tight')


config = read_config()

current_temperature = 20

series = {}
series["target_temperature"] = []
series["heater_set_point"] = []
series["output"] = []
series["output_raw"] = []
series["temperature"] = []
series["key"] =[]

flat = TrivialFlat(temperature=current_temperature, verbose=False, temp_decrease=0.005, heater_temp_inc=0.03,
                   heater_max=config["controller"]["value-max"], heater_idle=config["controller"]["value-idle"],
                   heater_safety=4)

print("---------------------------------------------------------------------")
print("init")

controller = Controller(config, True)
controller.start()
target_temperature = 17
controller._sub_set_point_handler(target_temperature)

print("---------------------------------------------------------------------")
print("start")

for i in range(0, 1000):
    print(" - {}".format(i))
    if i == 10:
        print(" - update target temperature")
        target_temperature = 23.5
        controller._sub_set_point_handler(target_temperature)
    elif i == 800:
        print(" - update target temperature")
        target_temperature = 17
        controller._sub_set_point_handler(target_temperature)
    controller._sub_input_handler(current_temperature)
    flat.update_temperature(controller._output)
    current_temperature = flat.temperature
    print(" - current temperature: {}.".format(current_temperature))

    series["key"].append(i*0.5/60)  # interval is 30 seconds - or half a minute
    series["output_raw"].append(max(0, controller._output_raw/150))
    series["output"].append(controller._output)
    series["target_temperature"].append(target_temperature)
    series["heater_set_point"].append(flat.heater_set_point)
    series["temperature"].append(flat.temperature)

print("end")
print("---------------------------------------------------------------------")
print("stopping controller")
controller.stop()
print("---------------------------------------------------------------------")
print("creating png")
create_png(series, png_filename)
print("---------------------------------------------------------------------")
print("done")
