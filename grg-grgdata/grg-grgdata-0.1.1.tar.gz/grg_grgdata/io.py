import json
import argparse

from tabulate import tabulate

import grg_grgdata
from grg_grgdata import cmd

def parse_grg_case_file(grg_file_name):
    '''opens the given path and parses it as json data

    Args:
        grg_file_name(str): path to the a json data file
    Returns:
        Dict: a dictionary case
    '''

    with open(grg_file_name, 'r') as grg_data:
        data = json.load(grg_data)
        grg_data.close()

    return data


def print_json(grg_data, selection = None):
    view_data = grg_data

    if selection != None:
        print_json_selection(grg_data, 'root', selection)
        # lookups = selection.split('.')
        # for lookup in lookups:
        #     if lookup in view_data:
        #         view_data = view_data[lookup]
        #     else:
        #         #TODO throw error
        #         print('selection %s not found' % lookups)
        #         return
        # print(' -> '.join(lookups))
    else:
        print(json.dumps(view_data, sort_keys=True, indent=2, separators=(',', ': ')))

def print_json_selection(data, prefix, selection):
    if isinstance(data, list):
        for i, v in enumerate(data):
            print_json_selection(v, prefix+'['+str(i)+']', selection)

    if isinstance(data, dict):
        if 'name' in data and data['name'] == selection:
            print(prefix)
            print(json.dumps(v, sort_keys=True, indent=2, separators=(',', ': ')))
        else:
            for k, v in data.items():
                if k == selection:
                    print(prefix+' -> '+k)
                    print(json.dumps(v, sort_keys=True, indent=2, separators=(',', ': ')))
                else:
                    if isinstance(v, dict) or isinstance(v, list):
                        print_json_selection(v, prefix+' -> '+k, selection)

def abstract_value_to_string(abs_value):
    if abs_value is None or isinstance(abs_value, int):
        return abs_value
    if isinstance(abs_value, float):
        return '%.3f' % abs_value
    if isinstance(abs_value, dict):
        if 'lb' in abs_value and 'ub' in abs_value:
            lb_val = abstract_value_to_string(abs_value['lb'])
            ub_val = abstract_value_to_string(abs_value['ub'])
            return '%s - %s' % (lb_val, ub_val)
        else:
            return '{...}(%d)' % len(abs_value)
    if isinstance(abs_value, list):
        if len(abs_value) <= 5:
            return '['+', '.join([abstract_value_to_string(val) for val in abs_value])+']'
        else:
            v0 = abstract_value_to_string(abs_value[0])
            v1 = abstract_value_to_string(abs_value[1])
            vn1 = abstract_value_to_string(abs_value[-2])
            vn0 = abstract_value_to_string(abs_value[-1])
            return '['+', '.join([v0, v1, '...', vn1, vn0])+'](%d)'%len(abs_value)
    return abs_value


rect_display = '%s, %s\033[1mi\033[0m'
polar_display = u'%s \u2220 %s'

electrical_value_names = ['impedance_rectangular', 'admittance_rectangular', \
    'power_rectangular', 'transform_polar', 'voltage_polar', \
    'ideal_transform']

def value_to_string(value):
    if isinstance(value, dict) \
        and 'type' in value \
        and value['type'] in electrical_value_names:
            e_val_type = value['type']
            if e_val_type == 'impedance_rectangular':
                return rect_display % (abstract_value_to_string(value['resistance']), abstract_value_to_string(value['reactance']))

            if e_val_type == 'admittance_rectangular':
                return rect_display % (abstract_value_to_string(value['conductance']), abstract_value_to_string(value['susceptance']))

            if e_val_type == 'power_rectangular':
                return rect_display % (abstract_value_to_string(value['active']), abstract_value_to_string(value['reactive']))

            if e_val_type == 'voltage_polar':
                return polar_display % (abstract_value_to_string(value['magnitude']), abstract_value_to_string(value['angle']))

            if e_val_type == 'transform_polar':
                return polar_display % (abstract_value_to_string(value['tap_ratio']), abstract_value_to_string(value['angle_shift']))

            if e_val_type == 'ideal_transform':
                return \
                    (rect_display % (abstract_value_to_string(value['resistance']), abstract_value_to_string(value['reactance']))) + ' :: ' +\
                    (polar_display % (abstract_value_to_string(value['tap_ratio']), abstract_value_to_string(value['angle_shift'])))

            #return abstract_value_to_string(value)
            assert(False) #all values in electrical_value_names should be enumerated here.
    else:
        return abstract_value_to_string(value)



def dict_to_list(name, data, keys):
    values = ['']*(len(keys)+1)
    values[0] = name
    for i, key in enumerate(keys):
        if key in data:
            values[i+1] = value_to_string(data[key])
    return values


def print_tabular_summary_network(grg_data):
    network_data = grg_data['network']
    print('network: %s' % network_data['id'])
    print('description: %s' % network_data['description'])
    print('per unit: %s' % network_data['per_unit'])
    #print('base mva: %s' % network_data['base_mva'])

    comps_by_type = {}
    for name, component_data in cmd.walk_components(grg_data):
        comp_type = component_data['type']
        if not comp_type in comps_by_type:
            comp_list = {}
            comps_by_type[comp_type] = comp_list
        else:
            comp_list = comps_by_type[comp_type]

        comp_list[name] = component_data

    #print(comps_by_type.keys())

    print('')
    print('component type counts:')
    for comp_type in sorted(comps_by_type.keys()):
        print('  {}: {}'.format(comp_type, len(comps_by_type[comp_type])))

    for comp_type in sorted(comps_by_type.keys()):
        fields = set([])
        for name, component_data in comps_by_type[comp_type].items():
            fields |= set(component_data.keys())
        fields.remove('type')

        fields = sorted(fields)
        comp_names = sorted(comps_by_type[comp_type].keys())
        comp_list = [ dict_to_list(name, comps_by_type[comp_type][name], fields) for name in comp_names]

        print('')
        print('component type: \033[1m%s\033[0m' % comp_type)
        print(tabulate(comp_list, headers=['name']+fields, floatfmt=".3f"))


def print_tabular_summary(grg_data):

    print('****************')
    print('*** network ***')
    print('****************')
    print('')

    print_tabular_summary_network(grg_data)
    print('')


    # if 'transformations' in grg_data:
    #     print('***********************')
    #     print('*** transformations ***')
    #     print('***********************')
    #     print('')

    #     for name, transformation_data in grg_data['transformations'].items():
    #         print('transformation: %s' % name)
    #         if 'description' in transformation_data:
    #             print('description: %s' % transformation_data['description'])
    #         print('type: %s' % transformation_data['type'])

    #         if 'network' in transformation_data:
    #             print('network: %s' % transformation_data['network'])
    #         if 'parent' in transformation_data:
    #             print('parent: %s' % transformation_data['parent'])
    #         if 'problem_class' in transformation_data:
    #             print('problem_class: %s' % transformation_data['problem_class'])
    #         if 'complete_assignment' in transformation_data:
    #             print('complete_assignment: %s' % transformation_data['complete_assignment'])

    #         if 'component_assignments' in transformation_data:
    #             print('component_assignments: %d\n  %s' % (len(transformation_data['component_assignments']), ', '.join(sorted(transformation_data['component_assignments'].keys()))))

    #         if 'time_series' in transformation_data:
    #             time_series = transformation_data['time_series']
    #             print('time_series: %d step of %.3f %s duration' % (time_series['steps'], time_series['step_duration'], time_series['step_duration_units']))
    #             print('  component_assignments: %d\n    %s' % (len(time_series['component_assignments']), ', '.join(sorted(time_series['component_assignments'].keys()))))

    #         print('')
    #     print('')



def build_cli_parser():
    parser = argparse.ArgumentParser(
        description='''grg_grgdata.%(prog)s is a tool for processing grg 
            network data.''',

        epilog='''Please file bugs at...''',
    )


    subparsers = parser.add_subparsers(help='sub-commands', dest='cmd')

    parser_summary = subparsers.add_parser('smry', help = 'displays a summary of the data file')
    parser_summary.add_argument('file', help='a grg data file (.json)')
    parser_summary.add_argument('-t', '--transform', help='a transformation in the file')

    parser_view = subparsers.add_parser('view', help = 'displays a sub-tree of the data file')
    parser_view.add_argument('file', help='a grg data file (.json)')
    parser_view.add_argument('-s', '--select', help='a substree of the data file')

    #parser.add_argument('--foo', help='foo help')
    version = __import__('grg_grgdata').__version__
    parser.add_argument('-v', '--version', action='version', \
        version='grg_grgdata.%(prog)s (version '+version+')')

    return parser


# Note main(args) used here instead of main(), to enable easy unit testing
def main(args):
    '''reads a matpower or grg case files and processes them based on command 
    line arguments.

    Args:
        args: an argparse data structure
    '''
    if args.cmd == 'smry':
        grg_data = parse_grg_case_file(args.file)
        if grg_grgdata.cmd.validate_grg(grg_data):
            if args.transform == None:
                print_tabular_summary(grg_data)
            else:
                root_network_id, root_network, flat_network_id, flat_network = grg_grgdata.struct.flatten_network(grg_data, args.transform)
                print_tabular_summary_network(flat_network_id, flat_network)
        else:
            print('invalid grg data file!')

    if args.cmd == 'view':
        grg_data = parse_grg_case_file(args.file)
        if grg_grgdata.cmd.validate_grg(grg_data):
            print_json(grg_data, args.select)
        else:
            print('invalid grg data file!')


if __name__ == '__main__':
    parser = build_cli_parser()
    main(parser.parse_args())

