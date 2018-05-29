import pandas
import numpy
from collections import Counter
from ipaddress import ip_network
from requests import get  # to make GET request
import os


def get_series_from_counters(counter1, counter2, name=None):
    """
    :param counter1:
    :param counter2:
    :param name:
    :return: Two Panda Series with sharex index
    """
    min_index = min([min(counter1.keys()), min(counter2.keys())])
    max_index = max([max(counter1.keys()), max(counter2.keys())])
    indexes = range(min_index, max_index + 1)
    values1 = []
    values2 = []
    for i in indexes:
        values1.append(counter1[i])
        values2.append(counter2[i])

    x_input = numpy.asarray(indexes)
    y_input1 = numpy.asarray(values1)
    y_input2 = numpy.asarray(values2)
    series1 = pandas.Series(y_input1, index=x_input, name=name)
    series2 = pandas.Series(y_input2, index=x_input, name=name)
    return series1, series2


def get_series_from_counter(counter, name=None):
    """
    :param counter: Counter()
    :param name: label for Series
    :return: Panda Series with counter values, index counter keys
    """
    if len(counter) == 0:
        return pandas.Series()
    min_index = 0
    max_index = max(counter.keys())
    indexes = range(min_index, max_index + 1)
    values = []
    for i in indexes:
        values.append(counter[i])

    x_input = numpy.asarray(indexes)
    y_input = numpy.asarray(values)
    series = pandas.Series(y_input, index=x_input, name=name)
    return series


def normalize_counter(counter, total):
    """
    Normalizes a counter by dividing each value by 'total'
    :param counter: Counter
    :param total: A number
    :return: Normalized Counter()
    """
    if len(counter) == 0:
        return counter
    new_counter = Counter()
    min_index = min(counter.keys())
    max_index = max(counter.keys())
    total_f = float(total)
    for i in range(min_index, max_index + 1):
        new_counter[i] = counter[i] / total_f
    return new_counter


def is_subprefix(pref1, pref2):
    """
    :param pref1: IP Prefix
    :param pref2: IP Prefix
    :return: True if pref1 is subprefix of pref2
    """
    pref2_network = ip_network(pref2)
    pref1_network = ip_network(pref1)
    if not pref2_network.overlaps(pref1_network):
        return False

    rtval = pref2_network.compare_networks(pref1_network)
    # If rtval is -1 it means pref2_network_contains
    if rtval < 0:
        return True
    return False


def make_dirs(directory):
    """
    Creates directory and all directories that lie on the path between working dir and directory
    :param directory:
    """
    if not os.path.exists(directory):
        os.makedirs(directory)


def init_dic_with(dic, key, default_value):
    """
    Inits dic[key] with default value, if key isn't in dic yet
    :param dic: A dictionary
    :param key: A key for dic
    :param default_value: Value to set dic[key] to if key isn't in dic
    :return: dic[key]
    """
    try:
        _ = dic[key]
    except KeyError:
        dic[key] = default_value

    return dic[key]


def download_file(url, out, verify_cert=True):
	with open(out, "wb") as file:
		response = get(url, verify=verify_cert)
		# write to file
		file.write(response.content)

def get_sum_of_values(counter):
    """
    Returns the sum of all values in a counter
    :param counter: Counter()
    :return: sum of values in counter
    """
    total = 0
    for key in counter:
        total += counter[key]
    return total
