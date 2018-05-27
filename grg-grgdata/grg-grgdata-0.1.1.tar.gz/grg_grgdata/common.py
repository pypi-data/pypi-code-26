from __future__ import print_function

import inspect
import re
import math
import logging
import sys

import os, pkg_resources

from functools import partial

# backport str to basestring for python 3 compat
try:
  basestring
except NameError:
  basestring = str

print_err = partial(print, file=sys.stderr)

def _get_resource(*resource_path):
    path = os.path.join(*resource_path)
    package = __name__  ## Could be any module/package name.
    return pkg_resources.resource_string(package, path).decode("utf-8")

grg_schema = _get_resource('schema', 'GRGv2.0_schema.json')
grg_version = 'v.2.0'

bus_name_template = u'bus_%s'
shunt_name_template = u'shunt_%s'
load_name_template = u'load_%s'
generator_name_template = u'gen_%s'
sync_cond_name_template = u'sync_cond_%s'
line_name_template = u'line_%s'
transformer_name_template = u'transformer_%s'
dcline_name_template = u'dc_line_%s'
switch_name_template = u'switch_%s'
area_name_template = u'area_%s'
zone_name_template = u'zone_%s'
voltage_level_name_template = u'voltage_level_%s'
substation_name_template = u'substation_%s'

bus_voltage_name_template = u'voltage_bus_id_%s'
switch_voltage_name_template = u'voltage_switch_id_%s'


default_float_precision = 11

# criteria for floating point equivalence testing
epsilon = 1e-10

grg_units = {
    'voltage': 'kilo_volt',
    'current': 'ampere',
    'angle': 'degree',
    'active_power': 'mega_watt',
    'reactive_power': 'mega_volt_ampre_reactive',
    'impedance': 'ohm',
    'resistance': 'ohm',
    'reactance': 'ohm',
    'conductance': 'siemens',
    'susceptance': 'siemens'
}

#grg_pointer = re.compile('(#|@|!)/.')
grg_pointer = re.compile('(#/.|@/.|.*/.*)')

logging.basicConfig(format='%(levelname)s: %(message)s', level=logging.DEBUG)
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

component_list_names = ['components', 'substation_components', 'voltage_level_components']
component_link_names = ['link', 'link_1', 'link_2']


# determines the number of leading zeros needed for component names
def calc_zeros(item_count):
    if item_count <= 0:
        return 0
    else:
        return int(math.ceil(math.log(item_count, 10)))


# checks that a given value k is not a grg 'variable'
def check_assignment(k):
    if type(k) is dict:
        # TODO make this a real exception
        raise 'not a value problem!'
    return k

def build_range_variable(lb, ub):
    assert(float(lb) <= float(ub))
    return {'var': {'lb':lb, 'ub':ub}}

def build_set_variable(*vals):
    return {'var': list(*vals)}

def build_status_variable():
    return {'var': ['off', 'on']}


def is_abstract(value):
    if isinstance(value, int) or isinstance(value, float) or isinstance(value, basestring):
        return False
    elif isinstance(value, list):
        return True
    elif isinstance(value, dict):
        if 'var' in value:
            return True
        else:
            return True
    else:
        assert(False) #should not happen

    return True


def min_value(value):
    if isinstance(value, int) or isinstance(value, float):
        return value
    elif isinstance(value, basestring):
        return float(value)
    elif isinstance(value, list):
        return min(min_value(v) for v in value)
    elif isinstance(value, dict):
        if 'var' in value:
            return min_value(value['var'])
        else:
            return min_value(value['lb'])
    else:
        assert(False) #should not happen

    return float('NaN')


def max_value(value):
    if isinstance(value, int) or isinstance(value, float):
        return value
    elif isinstance(value, basestring):
        return float(value)
    elif isinstance(value, list):
        return max(max_value(v) for v in value)
    elif isinstance(value, dict):
        if 'var' in value:
            return max_value(value['var'])
        else:
            return max_value(value['ub'])
    else:
        assert(False) #should not happen

    return float('NaN')


def ratio_less(value_a, value_b, ratio_limit, signless=False):
     # TODO extend this to work on abstract values
    assert(isinstance(value_a, int) or isinstance(value_b, float))
    assert(isinstance(value_b, int) or isinstance(value_b, float))
    ratio = value_a / float(value_b)
    if signless:
        ratio = abs(ratio)

    #print(value_a, value_b, ratio, ratio_limit)
    return ratio <= ratio_limit

def ratio_greater(value_a, value_b, ratio_limit, signless=False):
     # TODO extend this to work on abstract values
    assert(isinstance(value_a, int) or isinstance(value_b, float))
    assert(isinstance(value_b, int) or isinstance(value_b, float))
    ratio = value_a / float(value_b)
    if signless:
        ratio = abs(ratio)

    #print(value_a, value_b, ratio, ratio_limit)
    return ratio >= ratio_limit


def is_less(value_a, value_b):
    return min_value(value_a) <= min_value(value_b)

def is_positive(value):
    return min_value(value) >= 0

def is_negative(value):
    return max_value(value) <= 0

def is_in_range(value, lb, ub):
    return min_value(value) >= lb and max_value(value) <= ub

def isclose(a, b):
    return abs(a-b) <= epsilon


# changes the scope of a self pointer into a component list pointer
def component_list_pointer(component_id, self_pointer):
    return self_pointer.replace('@','!/'+component_id)


# these functions help encode dictionaries with default class parameters
# they are used for translating other data formats into grg
def kwargs_defaults_dict(func):
    spec = inspect.getargspec(func)
    defaults_count = 0
    defaults_list = []
    if spec.defaults != None:
        defaults_count = len(spec.defaults)
        defaults_list = list(spec.defaults)
    kwargs_start_index = len(spec.args) - defaults_count
    return dict(zip([key for key in spec.args[kwargs_start_index:]], defaults_list))

def is_default_value(obj, from_name):
    defaults = kwargs_defaults_dict(obj.__init__)
    value = getattr(obj, from_name)
    return value == defaults[from_name]

def add_extra_data(obj, arg_from_names, data, scale=None):
    return add_extra_data_remap(obj, arg_from_names, data, arg_from_names, scale)

        #_add_extra_data_remap(self, ['br_b'], data, ['charge'])
def add_extra_data_remap(obj, arg_from_names, data, arg_to_names, scale=None):
    assert(len(arg_from_names) == len(arg_to_names))

    defaults = kwargs_defaults_dict(obj.__init__)
    for index, from_name in enumerate(arg_from_names):
        value = getattr(obj, from_name)
        if not from_name in defaults or defaults[from_name] != value:
            to_name = arg_to_names[index]
            assert(not to_name in data)
            if scale != None:
                data[to_name] = value*scale
            else:
                data[to_name] = value


# these functions help build key-word-arguments dictionaries from data dictionaries
# they are used for translating grg into class arguments lists of other data formats
def map_to_dict(arg_dict, obj_dict, name, scale=None, float_precision=None):
    remap_to_dict(arg_dict, obj_dict, name, name, scale, float_precision)

def remap_to_dict(arg_dict, obj_dict, arg_name, obj_name, scale=None, float_precision=None):
    if obj_name in obj_dict:
        assert(not arg_name in arg_dict) # don't want to clobber other data
        if scale != None:
            if float_precision != None:
                arg_dict[arg_name] = round(obj_dict[obj_name]*scale, float_precision)
            else:
                arg_dict[arg_name] = obj_dict[obj_name]*scale
        else:
            arg_dict[arg_name] = obj_dict[obj_name]


# given a limit table and a time threshold (seconds?), 
# returns the largest limit value that meets that time threshold
def max_limit(limit_table, threshold):

    for value in sorted(limit_table['values'], key=lambda x: float(x[0])):
        if float(value[0]) >= threshold:
            return float(value[2])

    return 0.0


def has_current_limits(component):
    return 'current_limits_1' in component and 'current_limits_2' in component

def get_current_rates(component, time_a=float('Inf'), time_b=14400, time_c=900):
    rate_a = 0.0
    rate_b = 0.0
    rate_c = 0.0

    if 'current_limits_1' in component:
        grg_limits = component['current_limits_1']
        rate_c = max_limit(grg_limits, time_c)
        rate_b = max_limit(grg_limits, time_b)
        rate_a = max_limit(grg_limits, float('Inf'))

    if 'current_limits_2' in component:
        grg_limits = component['current_limits_2']
        rate_c_2 = max_limit(grg_limits, time_c)
        if rate_c_2 != rate_c:
            print_err('warning: asymmetrical current limits on ac_line, using the smaller one')
            rate_c = min(rate_c, rate_c_2)
        rate_b_2 = max_limit(grg_limits, time_b)
        if rate_b_2 != rate_b:
            print_err('warning: asymmetrical current limits on ac_line, using the smaller one')
            rate_b = min(rate_b, rate_b_2)
        rate_a_2 = max_limit(grg_limits, float('Inf'))
        if rate_a_2 != rate_a:
            print_err('warning: asymmetrical current limits on ac_line, using the smaller one')
            rate_a = min(rate_a, rate_a_2)

    return rate_a, rate_b, rate_c


def has_thermal_limits(component):
    return 'thermal_limits_1' in component and 'thermal_limits_2' in component

def get_thermal_rates(component, time_a=float('Inf'), time_b=14400, time_c=900):
    rate_a = 0.0
    rate_b = 0.0
    rate_c = 0.0

    if 'thermal_limits_1' in component:
        grg_limits = component['thermal_limits_1']
        rate_c = max_limit(grg_limits, time_c)
        rate_b = max_limit(grg_limits, time_b)
        rate_a = max_limit(grg_limits, float('Inf'))

    if 'thermal_limits_2' in component:
        grg_limits = component['thermal_limits_2']
        rate_c_2 = max_limit(grg_limits, time_c)
        if rate_c_2 != rate_c:
            print_err('warning: asymmetrical thermal limits on ac_line, using the smaller one')
            rate_c = min(rate_c, rate_c_2)
        rate_b_2 = max_limit(grg_limits, time_b)
        if rate_b_2 != rate_b:
            print_err('warning: asymmetrical thermal limits on ac_line, using the smaller one')
            rate_b = min(rate_b, rate_b_2)
        rate_a_2 = max_limit(grg_limits, float('Inf'))
        if rate_a_2 != rate_a:
            print_err('warning: asymmetrical thermal limits on ac_line, using the smaller one')
            rate_a = min(rate_a, rate_a_2)

    # needed for idempotent translation
    if 'rates' in component:
        rates = component['rates']
        if rates < 3:
            rate_c = 0.0
        if rates < 2:
            rate_b = 0.0
        if rates < 1:
            rate_a = 0.0

    return rate_a, rate_b, rate_c


# given a tap_changer and a tap position, 
# returns the tap values
def tap_setting(tap_changer, position):

    for step in tap_changer['steps']['values']:
        if step[0] == position:
            return {
                'position': step[0],
                'impedance': step[1],
                'shunt': step[2],
                'tap_ratio': step[3],
                'angle_shift': step[4]
            }

    return None
