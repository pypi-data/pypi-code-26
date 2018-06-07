import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from epidaurus.pid import PID
from pathlib import Path
from pelops import mypyyaml
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt


png_filename = 'test_pid_simple.png'


def create_png(series, filename):
    list_key = []
    list_feedback = []
    list_set_point = []
    for key, entry in series.items():
        list_key.append(key)
        list_feedback.append(entry["feedback"])
        list_set_point.append(entry["set-point"])

    plt.plot(list_key, list_feedback, color="tab:red")
    plt.plot(list_key, list_set_point, color="tab:blue")
    fig = plt.gcf()
    fig.tight_layout()
    DPI = fig.get_dpi()
    fig.set_size_inches(1024.0 / float(DPI), 768.0 / float(DPI))
    plt.savefig(filename, bbox_inches='tight')


# get configuration
config_filename = 'config.yaml'
config_file = Path(config_filename)
if not config_file.is_file():
    raise FileNotFoundError("config file '{}' not found.".format(config_filename))

config = mypyyaml.load(open(config_filename, 'r'), Loader=mypyyaml.Loader)

pid = PID(config["controller"]["pid"], True)
pid.reset(0,0)

pid._p_gain = 1.025
pid._i_gain = 0.0035
pid._d_gain = 0.05
pid._windup_guard = 20
pid._update_interval = 30
pid._set_point = 0

series = {}
feedback = 0

for i in range(0,50):
    output = pid.update(feedback)
    if pid._set_point > 0:
        feedback += (output - (1 / i))
    if i > 9:
        pid._set_point = 1
    series[i] = {
        "set-point": pid._set_point,
        "feedback": feedback,
    }

create_png(series, png_filename)
