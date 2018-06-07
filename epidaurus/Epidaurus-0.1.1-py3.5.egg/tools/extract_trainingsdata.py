from pelops.myinfluxdbclient import MyInfluxDBClient
from pelops import mypyyaml
import os
from pathlib import Path
import collections
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt


def create_png(series, filename):
    list_count = []
    list_time = []
    list_input = []
    list_output = []
    list_set_point = []
    i = 0
    for key, entry in series.items():
        list_count.append(i)
        i = i + 1
        list_time.append(key)
        list_input.append(entry["input"])
        list_output.append(entry["output"])
        list_set_point.append(entry["set-point"])

    fig, ax1 = plt.subplots()
    ax1.plot(list_count, list_input, color="tab:red")
    ax1.plot(list_count, list_set_point, color="tab:blue")
    ax1.tick_params(axis='°C')
    ax2 = ax1.twinx()
    ax2.plot(list_count, list_output, color="tab:gray")
    ax2.tick_params(axis='V')
    fig.tight_layout()

    fig = plt.gcf()
    DPI = fig.get_dpi()
    fig.set_size_inches(3000.0 / float(DPI), 800.0 / float(DPI))
    plt.savefig(filename, bbox_inches='tight')


print("start")

# get configuration
config_filename = 'extract_trainingsdata.yaml'
config_file = Path(config_filename)
if not config_file.is_file():
    raise FileNotFoundError("config file '{}' not found.".format(config_filename))

config = mypyyaml.load(open(config_filename, 'r'), Loader=mypyyaml.Loader)
credentials = mypyyaml.load(open(os.path.expanduser(config["influx"]["influx-credentials"]), 'r'),
                            Loader=mypyyaml.Loader)
config["influx"].update(credentials["influx"])
#credentials = mypyyaml.load(open(os.path.expanduser(config["mqtt"]["mqtt-credentials"]), 'r'),
#                            Loader=mypyyaml.Loader)
#config["mqtt"].update(credentials["mqtt"])

input_series = config["trainingsdata"]["input-series"]
output_series = config["trainingsdata"]["output-series"]
setpoint_low = config["trainingsdata"]["setpoint-low"]
setpoint_high = config["trainingsdata"]["setpoint-high"]
setpoint_threshold = config["trainingsdata"]["setpoint-threshold"]
datetime_from = config["trainingsdata"]["from"]
datetime_to = config["trainingsdata"]["to"]

filename_base = "{}_{}_{:%y%m%d%H%M}-{:%y%m%d%H%M}.".format(input_series, output_series, datetime_from, datetime_to)

# fetch data from influx
influx = MyInfluxDBClient(config["influx"], False)
query = "select * from {} where time>='{}' and time<='{}'".format(input_series, datetime_from, datetime_to)
result_input = influx.client.query(query).get_points()
print("fetched input points")
query = "select * from {} where time>='{}' and time<='{}'".format(output_series, datetime_from, datetime_to)
result_output = influx.client.query(query).get_points()
print("fetched output points")



series = collections.OrderedDict()

# create map entries for all input values
print("fill map")
for entry in result_input:
    key = entry["time"]
    input_value = entry["value"]
    series[key] = {
        "input": input_value,
        "output": None,
        "set-point": None,
    }

# update map entries for received output values
print("add output value")
prev_time = None
prev_value = None
series_iterator = iter(series.keys())
input_time = next(series_iterator)

for entry in result_output:
    output_time = entry["time"]
    value = entry["value"]

    if prev_time is not None:
        while True:
            if input_time < output_time:
                series_entry = series[input_time]
                series_entry["output"] = prev_value
            else:
                break

            try:
                input_time = next(series_iterator)
            except StopIteration:
                break

    prev_time = output_time
    prev_value = value

# fill last segment (last output time until last input time)
if prev_time is not None:
    while True:
        series_entry = series[input_time]
        series_entry["output"] = prev_value
        try:
            input_time = next(series_iterator)
        except StopIteration:
            break

# guess set-point value according to output value
print("guess set-point")
for key,entry in series.items():
    if entry["output"] <= setpoint_threshold:
        entry["set-point"] = setpoint_low
    else:
        entry["set-point"] = setpoint_high

# output to csv
filename = filename_base + "csv"
print("write {} lines to '{}'.".format(len(series), filename))
with open(filename, "w") as f:
    header = "time;input;set-point;output\n"
    f.write(header)
    for key, entry in series.items():
        line = "{};{};{};{}\n".format(key, entry["input"], entry["set-point"], entry["output"])
        f.write(line)

# output to plot
filename = filename_base + "png"
print("create plots for series ('{}').".format(filename))
create_png(series, filename)

print("done.")