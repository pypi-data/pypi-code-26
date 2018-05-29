import sys, os
import argparse
from pbxproj import XcodeProject
from jinja2 import exceptions, Environment, Template, FileSystemLoader, select_autoescape
import datetime
import yaml
from colorama import init, Fore, Style
from typing import List


def __add_to_project(project, filename, parent_group, targets=None):
    if targets and len(targets) > 0:
        print('[INFO] Adding {} to target(s) {}'.format(filename, targets))
        project.add_file(filename, force=False, parent=parent_group, target_name=targets)
    else:
        print('[INFO] Adding {} to all targets'.format(filename))
        project.add_file(filename, force=False, parent=parent_group)


def __create_default_yml_file(filename: str, project_name: str):
    default_settings = {'project_dir': project_name,
                            'templates_dir': '$TEMPLATES',
                            'uikit_controllers_group': 'VIPER_CONTROLLERS',
                            'author': 'MyCompany',
                            'targets': [project_name],
                            'base_viewcontroller': 'UIViewController'}

    project_full_dir = os.path.dirname(os.path.realpath(project_name))
        
    full_filename = os.path.join(project_full_dir, filename)
        
    with open(full_filename, 'w') as output_file:
        dump = yaml.dump(default_settings)
        output_file.write(dump)
        

def init_viper(config_path: str, project_name: str,
                   targets_list: List[str]):
    dir_path = os.path.dirname(os.path.realpath(__file__))
    common_dir = dir_path + '/Common'
    common_env = Environment(
        loader=FileSystemLoader(common_dir),
        autoescape=select_autoescape(['.swift'])
        )

    print('[INFO] Will use configuration file {}'.format(config_path))

    with open(config_path, 'r') as stream:
        yaml_data = yaml.load(stream)

    settings = yaml_data

    project = XcodeProject.load(project_name + '/project.pbxproj')
    print('[INFO] Using XCode project {}'.format(project_name))
    project_full_dir = os.path.dirname(os.path.realpath(project_name)) + '/' + settings['project_dir']

    project_common_dir = project_full_dir + '/ViperCommon'
    if not os.path.exists(project_common_dir):
        os.makedirs(project_common_dir)

    if 'targets' in settings:
        targets = settings['targets']
        
    # But this has higher priority
    if targets_list:
        targets = targets_list

    if 'base_viewcontroller' in settings:
        base_viewcontroller = settings['base_viewcontroller']
    else:
        base_viewcontroller = 'UIViewController'
            
    common_group = project.get_or_create_group('ViperCommon')
    for dirname, dirnames, filenames in os.walk(common_dir):
        for filename in filenames:
            template = common_env.get_template(filename)
            project_filename = os.path.join(project_common_dir, filename)
            rendered_template = template.render(base_viewcontroller=base_viewcontroller)
            output_file = open(project_filename, 'w')
            output_file.write(rendered_template)
            output_file.close()
            __add_to_project(project, project_filename, common_group, targets)
        
    for part in ['Views', 'Interactors', 'Presenters', 'Routers', 'ViewControllers']:
        part_dir_path = project_full_dir + '/' + part
        if not os.path.exists(part_dir_path):
            os.makedirs(part_dir_path)

    project.save()


def add_viper_files(config_path: str, project_name: str, module_name: str,
                        targets_list: List[str], storyboard: str = None):
    with open(config_path, 'r') as stream:
        yaml_data = yaml.load(stream)

    settings = yaml_data

    project = XcodeProject.load(project_name + '/project.pbxproj')

    targets = []
    
    if 'targets' in settings:
        targets = settings['targets']

    # But this has higher priority
    if targets_list:
        targets = targets_list

    if storyboard:
        storyboard_name = storyboard
    else:
        storyboard_name = 'Main'

    today = datetime.date.today()
    today_str = today.strftime('%d.%m.%y')
    year_str = today.strftime('%Y')
        
    template_dir = settings['templates_dir']
    dir_path = os.path.dirname(os.path.realpath(__file__))
    if template_dir == '$TEMPLATES':
        template_dir = dir_path + '/Templates'

    project_full_dir = os.path.dirname(os.path.realpath(project_name)) + '/' + settings['project_dir']

    templates_env = Environment(
        loader=FileSystemLoader(template_dir),
        autoescape=select_autoescape(['.tpl.swift'])
        )

    parts = {'View': 'Views',
                 'Interactor': 'Interactors',
                 'Presenter': 'Presenters',
                 'Router': 'Routers',
                 'Controller': 'ViewControllers'
                 }
            
    for key in parts.keys():
        try:
            template = templates_env.get_template(key + '.tpl.swift')
        except exceptions.TemplateNotFound:
            print(Fore.RED + 'Cannot find template {0}'.format(key + '.tpl.swift'))
            print(Style.RESET_ALL)
            sys.exit(0)
        
        filename = '{2}/{3}/{1}{0}.swift'.format(key, module_name, project_full_dir, parts[key])
        rendered_template = template.render(module_name=module_name, file_type=key,
                                            creation_date=today_str, creation_year=year_str,
                                            storyboard_name=storyboard_name,
                                            project_author=settings['author'])

        try:
            output_file = open(filename, 'w')
            output_file.write(rendered_template)
            output_file.close()
        except FileNotFoundError:
            print(Fore.RED + 'Cannot find file {0}; try to use `swivigen init`'.format(filename))
            print(Style.RESET_ALL)
            sys.exit(0)
            
        if key == 'Controller':
            project_group = project.get_or_create_group(settings['uikit_controllers_group'])
        else:
            project_group = project.get_or_create_group('{0}s'.format(key))
        __add_to_project(project, filename, project_group, targets)

    project.save()
    

def __init_viper(args):    
    if args.config:
        config_path = args.config
    else:
        config_path = 'viper.yml'

    if args.initfile:
        __create_default_yml_file('viper.yml', args.project.replace('.xcodeproj', ''))

    init_viper(config_path, args.project, args.targets)
   

def __add_viper_files(args):
    if args.config:
        config_path = args.config
    else:
        config_path = 'viper.yml'

    add_viper_files(config_path, args.project, args.module, args.targets, args.storyboard)


def __print_greeting(args):
    print('swivigen - Generator of VIPER classes for Swift-based XCode projects')
    print('Run `swivigen -h` to learn more')

        
def main():
    init()
    
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(help='run `swivigen init --help` or `swivigen add --help` to know more about what you can do')
    parser_add = subparsers.add_parser('add', help='add VIPER files to specified project')
    parser_init = subparsers.add_parser('init', help='add base VIPER files and created required directories')
    
    parser_add.add_argument('-c',
                        '--config',
                        help='path to YAML config file')
    parser_add.add_argument('-s',
                        '--storyboard',
                        help='specify name of storyboard where created controller will be placed by user')
    parser_add.add_argument('-t',
                        '--targets',
                        help='specify list of targets where created files will be included; if not specified, all targets will include new files OR targets from config file will be used if any',
                        nargs='+')

    parser_add.add_argument('project', help='XCode project that should be modified')
    parser_add.add_argument('module', help='name for new viper module')

    parser_init.add_argument('-t',
                        '--targets',
                        help='specify list of targets where created files will be included; if not specified, all targets will include new files OR targets from config file will be used if any',
                        nargs='+')

    parser_init.add_argument('project', help='XCode project that should be modified')

    group = parser_init.add_mutually_exclusive_group()
    
    group.add_argument('-c',
                        '--config',
                        help='path to YAML config file')
    
    group.add_argument('-i',
                        '--initfile',
                        help='create default YAML config file',
                        action="store_true")

    parser.set_defaults(func=__print_greeting)
    parser_init.set_defaults(func=__init_viper)
    parser_add.set_defaults(func=__add_viper_files)
    
    args = parser.parse_args()
    args.func(args)
