import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from epidaurus.pid import PID
import datetime
import collections
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from pelops.read_config import read_config


csv_filename = '../tools/LivingRoom_T_avg_1min_gVolt_1803151630-1803152330.csv'
png_filename = 'test_pid_csv.png'


def create_png(series, filename):
    list_count = []
    list_time = []
    list_input = []
    list_output = []
    list_set_point = []
    list_pid_result = []
    i = 0
    for key, entry in series.items():
        list_count.append(i)
        i = i + 1
        list_time.append(key)
        list_input.append(entry["input"])
        list_output.append(entry["output"])
        list_set_point.append(entry["set-point"])
        list_pid_result.append(entry["pid-result"])

    fig, ax1 = plt.subplots()
    ax1.plot(list_count, list_input, color="tab:red")
    ax1.plot(list_count, list_set_point, color="tab:blue")
    ax1.tick_params(axis='C')
    ax2 = ax1.twinx()
    ax2.plot(list_count, list_output, color="tab:gray")
    ax2.plot(list_count, list_pid_result, color="tab:orange")
    ax2.tick_params(axis='V')
    fig.tight_layout()

    fig = plt.gcf()
    DPI = fig.get_dpi()
    fig.set_size_inches(3000.0 / float(DPI), 800.0 / float(DPI))
    plt.savefig(filename, bbox_inches='tight')


def read_csv(filename):
    result = collections.OrderedDict()
    with open(filename, 'r') as f:
        lines = f.readlines()
        _ = lines.pop(0)
        for line in lines:
            columns = line.split(";")
            key = datetime.datetime.strptime(columns[0], "%Y-%m-%dT%H:%M:%S.%fZ")
            value_input = float(columns[1])
            set_point = float(columns[2])
            value_output = float(columns[3])
            result[key] = {
                "input": value_input,
                "output": value_output,
                "set-point": set_point,
                "pid-result": None,
            }
    return result


# get configuration
config = read_config('config.yaml')

pid = PID(config["controller"]["pid"], True)
series = read_csv(csv_filename)

#init
first = series[next(iter(series.keys()))]
pid.reset(first["input"], first["set-point"])

e_min = 9999999
e_max = -9999999
for entry in series.values():
    result = pid.update(entry["input"])
    entry["pid-result"] = result
    e_min = min(e_min, result)
    e_max = max(e_max, result)

e_diff = abs(e_max - e_min)
e_scale = 11
e_shift = 5
print(e_min, e_max, e_diff, e_scale)

for entry in series.values():
    e = entry["pid-result"]
    e = e + abs(e_min)
    e = e / e_diff
    e = e * e_scale
    e = e + e_shift
    #entry["pid-result"] = e

create_png(series, png_filename)
