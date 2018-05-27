from __future__ import print_function

# this import has a significant overhead in python 2 (2-6 sec.)
import json
import copy
import itertools
import sys
import math
import argparse


from collections import defaultdict

from functools import partial

# this import has a significant overhead in python 2  (7 sec.)
from jsonschema import ValidationError
from jsonschema import validate

import grg_grgdata
from grg_grgdata import common
from grg_grgdata.common import logger
from grg_grgdata.common import isclose

print_err = partial(print, file=sys.stderr)

def _dict_size(dictionary):
    count = 0
    for k,v in dictionary.items():
        if isinstance(v, dict):
            count += _dict_size(v)
        else:
            count += 1
    return count


def _get_items(dictionary, key):
    if key in dictionary:
        return dictionary[key].items()
    else:
        return {}.items()


def validate_grg(grg_data):
    schema = json.loads(grg_grgdata.common.grg_schema)

    try:
        validate(grg_data, schema)
    except ValidationError as e:
        print(e.message)
        print(e.path)
        # TODO needs to support integers in cueue, to support lists in the format
        #print('@ '+' -> '.join(e.path))
        #print(e)
        return False

    valid_versions = ['v.1.6', 'v.2.0',' v.3.0', 'v.4.0']
    if all(vv != grg_data['grg_version'] for vv in valid_versions):
        print('given a file in grg version %s but only versions v.1.6, v.2.0, v.3.0, and v.4.0 are supported' % (grg_data['grg_version']))
        return False

    component_lookup = {}
    for comp_path_id, comp_data in walk_components(grg_data):
        if comp_data['id'] in component_lookup:
            print('component name {} is not unique'.format(comp_data['id']))
            return False
        #print('{} - {}'.format(comp_id, comp_data['id']))
        component_lookup[comp_data['id']] = comp_data

    vl_lookup = votlage_level_lookup(grg_data)

    for comp, link_id in walk_voltage_links(grg_data):
        voltage_id = comp[link_id]
        if not voltage_id in vl_lookup:
            print('voltage id {} in component {} is not defined'.format(voltage_id, comp['id']))
            return False

    pointers = itertools.chain(
        walk_pointers(grg_data),
        #walk_fault_lists(grg_data)
    )

    #for pointer in pointers:
    #    print(pointer)

    for pointer in pointers:
        if not validate_pointer(pointer, grg_data, component_lookup):
            print('Invalid component pointer: %s' % pointer)
            #print(context)
            return False

    assignment_pointers = itertools.chain(
        walk_assignments(grg_data),
        walk_operation_constraints(grg_data)
        #walk_time_series_assignments(grg_data),
    )

    #for pointer in assignment_pointers:
    #    print(pointer)

    for pointer, val in assignment_pointers:
        if not validate_pointer(pointer, grg_data, component_lookup, assignment=True):
            print('Invalid assignment pointer: %s' % pointer)
            return False

    return True


def validate_grg_parameters(grg_data):

    per_unit = grg_data['network']['per_unit']

    # for key, value in walk_components(grg_data['network']['components']):
    #     print('{} - {}'.format(key, value['id']))
    vl_lookup = votlage_level_lookup(grg_data)


    ad_lookup = {}
    if 'operation_constraints' in grg_data:
        for key, value in grg_data['operation_constraints'].items():
            comp_id = key.split('/')[0]
            if key.endswith('angle_difference'):
                assert(not comp_id in ad_lookup)
                ad_lookup[comp_id] = value


    for identifier, component in walk_components(grg_data):
        if component['type'] == 'bus':
            validate_grg_bus(identifier, component, per_unit)
        elif component['type'] == 'shunt':
            validate_grg_shunt(identifier, component)
        elif component['type'] == 'load':
            validate_grg_load(identifier, component)
        elif component['type'] == 'generator':
            validate_grg_generator(identifier, component)
        elif component['type'] == 'synchronous_condenser':
            validate_grg_synchronous_condenser(identifier, component)
        elif component['type'] == 'switch':
            validate_grg_switch(identifier, component)
        elif component['type'] == 'ac_line':
            validate_grg_ac_line(identifier, component, per_unit)
            check_voltage_level(identifier, component, vl_lookup)
            check_flow_limit_bound(identifier, component, ad_lookup, vl_lookup, per_unit)
        elif component['type'] == 'two_winding_transformer':
            validate_grg_two_winding_transformer(identifier, component, per_unit)
            #check_flow_limit_bound(identifier, component, ad_lookup, vl_lookup, per_unit)
        elif component['type'] == 'three_winding_transformer':
            validate_grg_three_winding_transformer(identifier, component, per_unit)
        elif component['type'] == 'dc_line':
            validate_grg_dc_line(identifier, component)
        elif component['type'] == 'intertie':
            validate_grg_intertie(identifier, component)
        elif component['type'] == 'substation':
            #validate_grg_TBD
            pass
        elif component['type'] == 'voltage_level':
            #validate_grg_TBD
            pass
        else:
            print_err('unknown component type: %s' % component['type'])


    if 'operation_constraints' in grg_data:
        for key, value in grg_data['operation_constraints'].items():
            if key.endswith('angle_difference') and per_unit:
                min_value = common.min_value(value)
                max_value = common.max_value(value)
                if min_value < -0.5236 or max_value > 0.5236:
                    print('angle limit operational constraint are outside +/- 30 degrees on {}'.format(key))


    return True


def check_property(status, feedback):
    if not status:
        logger.warning(feedback)


def validate_grg_bus(identifier, bus_data, per_unit):
    subtype = bus_data.get('subtype', None)

    # if bus_data != None and per_unit:
    #     check_property(
    #         common.is_in_range(bus_data['voltage']['magnitude'], 0.8499, 1.1501), 
    #         'voltage magnitude is outside +/- 20% of nominal {}'.format(identifier)
    #     )

    if subtype == None:
        pass
    elif subtype == 'bus':
        pass
    elif subtype == 'busbar':
        pass
    elif subtype == 'voltage_point':
        pass
    else:
        print_err('unknown component subtype {} on {}'.format(subtype, identifier))


def validate_grg_shunt(identifier, shunt_data):
    subtype = shunt_data.get('subtype', None)
    if subtype == None:
        pass
    elif subtype == 'inductor':
        check_property(common.is_negative(shunt_data['shunt']['conductance']), 'positive shunt conductance on {}'.format(identifier))
        check_property(common.is_positive(shunt_data['shunt']['susceptance']), 'negative shunt susceptance on {}'.format(identifier))
    elif subtype == 'capacitor':
        check_property(common.is_positive(shunt_data['shunt']['conductance']), 'negative shunt conductance on {}'.format(identifier))
        check_property(common.is_negative(shunt_data['shunt']['susceptance']), 'positive shunt susceptance on {}'.format(identifier))
    else:
        print_err('unknown component subtype {} on {}'.format(subtype, identifier))

    return True


def validate_grg_load(identifier, load_data):
    subtype = load_data.get('subtype', None)
    if subtype == None:
        pass
    elif subtype == 'withdrawal':
        check_property(common.is_positive(load_data['demand']['active']), 'negative active demand on {}'.format(identifier))
        check_property(common.is_positive(load_data['demand']['reactive']), 'negative reactive demand on {}'.format(identifier))
    else:
        print_err('unknown component subtype {} on {}'.format(subtype, identifier))

    return True


def validate_grg_generator(identifier, gen_data):
    subtype = gen_data.get('subtype', None)

    if subtype != None:
        max_active_output = max(abs(common.max_value(gen_data['output']['active'])), abs(common.min_value(gen_data['output']['active'])))
        max_reactive_output = common.max_value(gen_data['output']['reactive'])
        min_reactive_output = common.min_value(gen_data['output']['reactive'])

        check_property(min_reactive_output <= 0, 'no negative reactive capabilities on {}'.format(identifier))
        check_property(max_reactive_output >= 0, 'no positive reactive capabilities on {}'.format(identifier))

        check_property(max_reactive_output <=  max_active_output, 'reactive capabilities larger than active capabilities on {}'.format(identifier))
        check_property(min_reactive_output >= -max_active_output, 'reactive capabilities larger than active capabilities on {}'.format(identifier))

        check_property(max_reactive_output >=  max_active_output/4.0, 'maximum reactive capabilities four times smaller than active capabilities on {}'.format(identifier))
        check_property(min_reactive_output <= -max_active_output/12.0, 'minimum reactive capabilities twelve times smaller than active capabilities on {}'.format(identifier))

        if 'cost_models' in gen_data:
            for cm_name, cm_data in gen_data['cost_models'].items():
                if cm_data['type'] == 'polynomial_1d' and cm_data['argument'] == "@/output/active":
                    for i, val in enumerate(cm_data['coefficients']):
                         check_property(val >= 0, 'negative coefficient for cost active power on {}'.format(identifier))

    if subtype == None:
        pass
    elif subtype == 'injection':
        check_property(common.is_positive(gen_data['output']['active']), 'negative active output on {}'.format(identifier))
    else:
        print_err('unknown component subtype {} on {}'.format(subtype, identifier))

    return True


def validate_grg_synchronous_condenser(identifier, sync_cond_data):
    return True


def validate_grg_switch(identifier, switch_data):
    return True

def validate_grg_flow_limit(identifier, limit_name, comp_data):
    if limit_name in comp_data:
        limit_data = comp_data[limit_name]
        values = []
        for value_data in limit_data['values']:
            value_data = [x for x in value_data]
            value_data[0] = float(value_data[0])
            values.append(value_data)
        values.sort(key=lambda x: x[0], reverse=True)
        for i, value_data in enumerate(values):
            if i > 0:
                if value_data[2] < values[i-1][2]:
                    check_property(False, 'flow limits are not increasing in {} on {}'.format(limit_name, identifier))
                    return False
                if value_data[0] >= values[i-1][0]:
                    check_property(False, 'flow limit times are not decreasing in {} on {}'.format(limit_name, identifier))
                    return False
    return True


def validate_grg_ac_line(identifier, ac_line_data, per_unit):
    subtype = ac_line_data.get('subtype', None)

    if subtype != None:
            # previously these checks were in validate_grg_pi_model
            check_property(common.is_positive(ac_line_data['impedance']['resistance']), 'negative resistance on {}'.format(identifier))
            check_property(common.is_positive(ac_line_data['impedance']['reactance']), 'negative reactance on {}'.format(identifier))

            if 'shunt_1' in ac_line_data:
                check_property(common.is_negative(ac_line_data['shunt_1']['conductance']), 'positive shunt_1 conductance on {}'.format(identifier))
                check_property(common.is_positive(ac_line_data['shunt_1']['susceptance']), 'negative shunt_1 susceptance on {}'.format(identifier))

            if 'shunt_2' in ac_line_data:
                check_property(common.is_negative(ac_line_data['shunt_2']['conductance']), 'positive shunt_2 conductance on {}'.format(identifier))
                check_property(common.is_positive(ac_line_data['shunt_2']['susceptance']), 'negative shunt_2 susceptance on {}'.format(identifier))

            validate_grg_flow_limit(identifier, 'current_limits_1', ac_line_data)
            validate_grg_flow_limit(identifier, 'current_limits_2', ac_line_data)
            validate_grg_flow_limit(identifier, 'thermal_limits_1', ac_line_data)
            validate_grg_flow_limit(identifier, 'thermal_limits_2', ac_line_data)

    if subtype == None:
        pass
    elif subtype == 'overhead':
        check_property(
            common.ratio_less(ac_line_data['impedance']['resistance'], ac_line_data['impedance']['reactance'], 0.5),
            'high resistance/impedance ratio on {}'.format(identifier)
        )

        if 'shunt_1' in ac_line_data and not isclose(ac_line_data['shunt_1']['susceptance'], 0.0):
            check_property(
                common.ratio_less(ac_line_data['shunt_1']['susceptance'], ac_line_data['impedance']['reactance'], 0.50, signless=True),
                'large shunt_1 susceptance on {}'.format(identifier)
            )
            check_property(
                common.ratio_greater(ac_line_data['shunt_1']['susceptance'], ac_line_data['impedance']['reactance'], 0.04, signless=True),
                'small shunt_1 susceptance on {}'.format(identifier)
            )

        if 'shunt_2' in ac_line_data and not isclose(ac_line_data['shunt_2']['susceptance'], 0.0):
            check_property(
                common.ratio_less(ac_line_data['shunt_2']['susceptance'], ac_line_data['impedance']['reactance'], 0.50, signless=True),
                'large shunt_2 susceptance on {}'.format(identifier)
            )
            check_property(
                common.ratio_greater(ac_line_data['shunt_2']['susceptance'], ac_line_data['impedance']['reactance'], 0.04, signless=True),
                'small shunt_2 susceptance on {}'.format(identifier)
            )
    elif subtype == 'underground':
        pass
    else:
        print_err('unknown component subtype {} on {}'.format(subtype, identifier))

    return True


def validate_grg_two_winding_transformer(identifier, twt_data, per_unit):
    subtype = twt_data.get('subtype', None)

    validate_grg_flow_limit(identifier, 'current_limits_1', twt_data)
    validate_grg_flow_limit(identifier, 'current_limits_2', twt_data)
    validate_grg_flow_limit(identifier, 'thermal_limits_1', twt_data)
    validate_grg_flow_limit(identifier, 'thermal_limits_2', twt_data)

    if subtype != None and per_unit:
        check_property(
            common.is_in_range(twt_data['tap_changer']['tap_ratio'], 0.8999, 1.1001), 
            'tap ratio is outside +/- 10% of nominal {}'.format(identifier)
        )

        # TODO how to extend this reasoning needs over ranges?
        # check_property(
        #     common.ratio_less(twt_data['tap_changer']['impedance']['resistance'], twt_data['tap_changer']['impedance']['reactance'], 0.05),
        #     'high resistance/impedance ratio on {}'.format(identifier)
        # )

        if not isclose(common.min_value(twt_data['tap_changer']['impedance']['resistance']), 0.0):
            # TODO how to extend this reasoning needs over ranges?
            # check_property(
            #     common.ratio_greater(twt_data['tap_changer']['impedance']['resistance'], twt_data['tap_changer']['impedance']['reactance'], 0.01),
            #     'low resistance/impedance ratio on {}'.format(identifier)
            # )
            pass

    if subtype == None:
        pass
    elif subtype == 'T_model':
        pass
    elif subtype == 'PI_model':
        pass
    else:
        print_err('unknown component subtype {} on {}'.format(subtype, identifier))

    return True


def validate_grg_three_winding_transformer(identifier, thwt_data):
    return True


def validate_grg_dc_line(identifier, dc_line_data):
    return True


def validate_grg_intertie(identifier, intertie_data):
    return True


def check_flow_limit_bound(identifier, ac_line_data, ad_lookup, vl_lookup, per_unit):
    if per_unit:
        if identifier in ad_lookup:
            min_ad = common.min_value(ad_lookup[identifier])
            max_ad = common.max_value(ad_lookup[identifier])
            theta_max = max(abs(min_ad), abs(max_ad))

            voltage_level_from = vl_lookup[ac_line_data['link_1']]
            voltage_level_to = vl_lookup[ac_line_data['link_2']]

            max_vm_from = voltage_level_from['voltage']['upper_limit']/voltage_level_from['voltage']['nominal_value']
            max_vm_to = voltage_level_to['voltage']['upper_limit']/voltage_level_to['voltage']['nominal_value']

            r = ac_line_data['impedance']['resistance']
            x = ac_line_data['impedance']['reactance']
            g =  r / (r**2 + x**2)
            b = -x / (r**2 + x**2)

            y_mag = math.sqrt(g**2 + b**2)
            max_vm = max(max_vm_from, max_vm_to)
            c_max = math.sqrt(max_vm_from**2 + max_vm_to**2 - 2*max_vm_from*max_vm_to*math.cos(theta_max))
            mva_max = y_mag*max_vm*c_max

            validate_grg_flow_limit_bound(identifier, 'current_limits_1', ac_line_data, c_max)
            validate_grg_flow_limit_bound(identifier, 'current_limits_2', ac_line_data, c_max)
            validate_grg_flow_limit_bound(identifier, 'thermal_limits_1', ac_line_data, mva_max)
            validate_grg_flow_limit_bound(identifier, 'thermal_limits_2', ac_line_data, mva_max)

    return True

def validate_grg_flow_limit_bound(identifier, limit_name, comp_data, limit_bound):
    if limit_name in comp_data:
        limit_data = comp_data[limit_name]
        for value_data in limit_data['values']:
            limit_value = value_data[2]
            if limit_value > limit_bound:
                check_property(False, 'the flow limit of {} in {} on {} is redundant (max value {})'.format(limit_value, limit_name, identifier, limit_bound))
    return True


def check_voltage_level(identifier, ac_line_data, votlage_level_lookup):
    # we know this works, if it is a valid grg file
    voltage_level_from = votlage_level_lookup[ac_line_data['link_1']]
    voltage_level_to = votlage_level_lookup[ac_line_data['link_2']]

    nom_kv_from = voltage_level_from['voltage']['nominal_value']
    nom_kv_to = voltage_level_from['voltage']['nominal_value']

    ratio = nom_kv_from/nom_kv_to

    check_property(ratio >= 0.9, 'ac_line nominal voltage levels differ by more than 10% on {}'.format(identifier))
    check_property(ratio <= 1.1, 'ac_line nominal voltage levels differ by more than 10% on {}'.format(identifier))

    return True


def votlage_level_lookup(grg_data):
    lookup = {}
    for identifier, component in walk_components(grg_data):
        if component['type'] == 'voltage_level':
            for voltage_point in component['voltage_points']:
                assert(not voltage_point in lookup)
                lookup[voltage_point] = component
    return lookup


def walk_components(grg_data):
    return _walk_components(grg_data['network']['components'])

def _walk_components(grg_components):
    for key, value in grg_components.items():
        yield key, value
        if isinstance(value, dict):
            for comp_list_name in common.component_list_names:
                if comp_list_name in value:
                    for nested_key, nested_value in _walk_components(value[comp_list_name]):
                        yield nested_key, nested_value

def walk_voltage_links(grg_data):
    for comp_id, comp_data in walk_components(grg_data):
        for comp_link_name in common.component_link_names:
            if comp_link_name in comp_data:
                yield (comp_data, comp_link_name)


def components_by_type(grg_data):
    comps = defaultdict(list)

    for identifier, component in walk_components(grg_data):
        typ = component['type']
        if typ not in comps:
            comps[typ] = []
        comps[typ].append(component)

    return comps


# lookup voltage levels by voltage points
def voltage_level_by_voltage_point(grg_data):
    cbt = components_by_type(grg_data)

    vl_lookup = {}
    for vl in cbt['voltage_level']:
        for vp in vl['voltage_points']:
            vl_lookup[vp] = vl

    return vl_lookup


# computes the set of voltage points that are connected to a bus
def bus_voltage_points(grg_data):
    cbt = components_by_type(grg_data)

    bus_vps = set()
    for bus in cbt['bus']:
        bus_vps.add(bus['link'])

    return bus_vps


# builds a mapping from all voltage points to unique int ids
# of shared voltage values
def collapse_voltage_points(grg_data, switch_status={}):
    cbt = components_by_type(grg_data)

    bus_vps = bus_voltage_points(grg_data)

    vp_mapping = {}
    for vl in cbt['voltage_level']:
        for vp in vl['voltage_points']:
            vp_mapping[vp] = frozenset([vp])

    for sw in cbt['switch']:
        sw_status = None
        if sw['id'] in switch_status:
            sw_status = switch_status[sw['id']]

        bus_pair = sw['link_1'] in bus_vps and sw['link_2'] in bus_vps

        if not bus_pair or sw['status'] == 'on' or sw_status == 'on':
            mvps = vp_mapping[sw['link_1']] | vp_mapping[sw['link_2']]
            for vp in mvps:
                vp_mapping[vp] = frozenset(mvps)

    active_sets = set(vp_mapping.values())

    vp2int = {}
    for i, active_set in enumerate(sorted(active_sets, key=lambda x: min(x))):
        for vp in sorted(active_set):
            vp2int[vp] = i

    return vp2int


# computes the set of voltage points that are connected to a bus
def active_voltage_points(grg_data, switch_status={}):
    cbt = components_by_type(grg_data)

    active_vps = bus_voltage_points(grg_data)

    for sw in cbt['switch']:
        sw_status = None
        if sw['id'] in switch_status:
            sw_status = switch_status[sw['id']]
        if sw['status'] == 'on' or sw_status == 'on':
            if sw['link_1'] in active_vps:
                active_vps.add(sw['link_2'])
            if sw['link_2'] in active_vps:
                active_vps.add(sw['link_1'])

    return active_vps


# computes the set of bus voltage points, that are not connected to components
def isolated_voltage_points(grg_data, switch_status={}):
    cbt = components_by_type(grg_data)

    comp_vps = set()

    for typ, comps in cbt.items():
        if typ != 'bus' and typ != 'switch':
            for comp in comps:
                for link_name in common.component_link_names:
                    if link_name in comp:
                        comp_vps.add(comp[link_name])

    for sw in cbt['switch']:
        sw_status = None
        if sw['id'] in switch_status:
            sw_status = switch_status[sw['id']]
        if sw['status'] == 'on' or sw_status == 'on':
            comp_vps.add(sw['link_2'])
            comp_vps.add(sw['link_1'])

    bus_vps = bus_voltage_points(grg_data)

    isolated_vps = set()
    for vp in bus_vps:
        if vp not in comp_vps:
            isolated_vps.add(vp)

    return isolated_vps


def walk_pointers(grg_data):
    iterators = []
    # this work around is used to avoid walking #/network/description, because it contains */*
    for key, value in grg_data.items():
        if key == 'network':
            iterators.append(_walk_pointers(value['components']))
        else:
            iterators.append(_walk_pointers(value))

    return itertools.chain(*iterators)

def _walk_pointers(data):
    if isinstance(data, str):
        #print(data, common.grg_pointer.match(data))
        if common.grg_pointer.match(data):
            yield data
    if isinstance(data, dict):
        for key, value in data.items():
            for pointer in _walk_pointers(value):
                yield pointer
    elif isinstance(data, list):
        for i, item in enumerate(data):
            for pointer in _walk_pointers(item):
                yield pointer

def walk_assignments(grg_data):
    for name, mapping in _get_items(grg_data, 'mappings'):
        for pointer, val in mapping.items():
            yield pointer, val

def walk_operation_constraints(grg_data):
    #for name, mapping in _get_items(grg_data, 'operation_constraints'):
    for pointer, val in _get_items(grg_data, 'operation_constraints'):
        yield pointer, val

def walk_time_series_assignments(grg_data):
    assert(False) # not yet implemented in GRG v1.5
    for name, time_series in _get_items(grg_data, 'network_time_series'):
        for pointer, val in time_series['assignments'].items():
            yield pointer, val

def walk_fault_lists(grg_data):
    assert(False) # not yet implemented in GRG v1.5
    for name, contingency in _get_items(grg_data, 'network_contingencies'):
        for pointer in contingency['fault_list']:
            yield pointer


def lookup_network(grg_data, transformation_id):
    assert('network_assignments' in grg_data) # TODO raise error message, if not validated previously
    assert(transformation_id in grg_data['network_assignments']) # TODO raise error message, if not validated previously

    transform = grg_data['network_assignments'][transformation_id]

    if 'network' in transform:
        root_network_id = transform['network']
        root_network = grg_data['networks'][root_network_id]

        return root_network

    else:
        assert('parent' in transform)
        return lookup_network(grg_data, transform['parent'])


def validate_pointer(pointer_string, grg_data, component_lookup, context = [], assignment = False):
    common.grg_pointer.match(pointer_string)
    pointer = pointer_string.split('/')
    root = pointer[0]
    if root == '#':
        lookup = grg_data
    #elif root == '!':
    #    lookup = grg_data['network']['components']
    elif root == '@': #no enclosing component
        assert(False) # no yet implemented
        assert(context[0] == 'network' and context[1] == 'components')
        lookup = grg_data['network']['components'][context[2]]
    else: # we assume this is a component-based lookup
        if root not in component_lookup:
            print('component id %s was not found' % root)
            return False
        lookup = component_lookup[root]

    if assignment:
        steps = pointer[1:-1]
    else:
        steps = pointer[1:]

    for val in steps:
        if val not in lookup:
            return False
        lookup = lookup[val]

    return True


def lookup_pointer(grg_data, pointer_string):
    pointer = pointer_string.split('/')
    #print(pointer)
    root = pointer[0]
    if root == '#':
        lookup = grg_data
    elif root == '!':
        lookup = grg_data['network']['components']
    elif root == '@': #TODO, this sould work
        print('pointer: %s' % pointer_string)
        assert(False)
        return None
    else: # context not supported
        print('ERROR bad pointer syntax: %s' % pointer_string)
        #assert(False) # TODO this should raise an inccorect pointer error
        return None

    for val in pointer[1:]:
        if not val in lookup:
            assert(False) # TODO this should raise an inccorect pointer error
        lookup = lookup[val]
    return lookup



def apply_assignment(network_data, pointer_string, value):
    pointer = pointer_string.split('/')
    root = pointer[0]
    if root == '#': #no for building a flat network
        return False
    elif root == '!':
        lookup = network_data['components']
    elif root == '@': #no enclosing component
        return False
    else: # context not supported
        assert(False) # TODO this should raise a warning, validator and schema are out of sync
        return False

    for val in pointer[1:-1]:
        assert(val in lookup) # if fails this is not a valid pointer!
        lookup = lookup[val]

    lookup[pointer[-1]] = value


def flatten_network(grg_data, transformation_id):
    assert('network_assignments' in grg_data) # TODO raise error message, if not validated previously
    assert(transformation_id in grg_data['network_assignments']) # TODO raise error message, if not validated previously

    transform = grg_data['network_assignments'][transformation_id]

    assert('network' in transform or 'parent' in transform) # TODO raise error message, if not validated previously
    if 'network' in transform:
        root_network_id = transform['network']

        assert('network' in grg_data) # TODO raise error message, if not validated previously
        assert(root_network_id == grg_data['network']['id']) # TODO raise error message, if not validated previously
        root_network = grg_data['network']

        flat_network_id = root_network_id
        flat_network = copy.deepcopy(root_network)

    else:
        assert('parent' in transform)
        root_network_id, root_network, flat_network_id, flat_network = flatten_network(grg_data, transform['parent'])

    assert(transform['type'] == 'refinement') # modifications not currently supported by this

    # TODO this needs to be extended to support *modifications*
    if 'assignments' in transform: # some configs may have no assignments
        for pointer, value in transform['assignments'].items():
            # assume that name is in components, part of grg data spec for configurations!
            apply_assignment(flat_network, pointer, value)

    return root_network_id, root_network, flat_network_id+'.'+transformation_id, flat_network

# def overwrite_component(comp, assignment):
#     for key, value in assignment.items():
#         if key in comp and isinstance(comp[key], dict) and isinstance(value, dict):
#             overwrite_component(comp[key], value)
#         else:
#             comp[key] = value


def build_cli_parser():
    parser = argparse.ArgumentParser(
        description='''grg_grgdata.%(prog)s is a tool for validating grg 
            network data.'''
    )

    parser.add_argument('file', help='a grg data file (.json)')

    #parser.add_argument('--foo', help='foo help')
    version = __import__('grg_grgdata').__version__
    parser.add_argument('-v', '--version', action='version', \
        version='grg_grgdata.%(prog)s (version '+version+')')

    return parser


def main(args):
    '''reads a GRG case file and runs the GRG data validation and parameter checks

    Args:
        args: an argparse data structure
    '''

    print_err('validating: {}'.format(args.file))
    case = grg_grgdata.io.parse_grg_case_file(args.file)

    print_err('grg file size: %d' % _dict_size(case))

    if validate_grg(case):
        print_err('valid grg data file.')
        if validate_grg_parameters(case):
            print_err('passed parameter checks.')
        else:
            print_err('failed parameter checks.')
    else:
        print_err('invalid grg data file.')


if __name__ == '__main__':
    parser = build_cli_parser()
    main(parser.parse_args())

