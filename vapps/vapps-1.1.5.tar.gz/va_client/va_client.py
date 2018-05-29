import os.path

from pprint import PrettyPrinter
import argparse, json
from va_api import APIManager

import va_client_utils
from va_client_utils import module_mappings, module_args

import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

base_path = os.path.dirname(os.path.abspath(__file__))

def call_function(va_master_url, method, user, password, request_data):
    url_components = [x for x in request_data if '=' not in x]
    data_components = [x.split('=') for x in request_data if '=' in x]

    endpoint = '/' + '/'.join(url_components)
    data = {x[0] : x[1] for x in data_components}
    method = method.lower()

    api = APIManager(va_url=va_master_url, va_user=user, va_pass=password, verify=False)
    result = api.api_call(endpoint, data = data, method = method)

    return result


def call_function_with_mapping(user, password, mapping, command, va_master_url = 'https://127.0.0.1:443', **data):
    cmd_map = va_client_utils.get_mapping_arguments(mapping, command)
    kwargs = cmd_map['kwargs']

    print kwargs

    kwargs['user'] = user
    kwargs['password'] = password
    kwargs['va_master_url'] = va_master_url

    if type(kwargs['data']) == str: 
        kwargs['data'] = json.loads(kwargs['data'])

    kwargs['data'].update(data)

    result = call_function(**kwargs)
    if type(result) == dict: 
        if not result['success'] : 
            raise Exception('API call failed : ', result['message'])

        result = result['data']
        if type(result) == dict: 
            for key in cmd_map.get('root_keys', []):
                result = result[key]

        if type(result) == list:
            result = va_client_utils.extract_data_with_keys(result, cmd_map.get('keys', []))
        if cmd_map.get('filters'):
            result = va_client_utils.filter_results(result, cmd_map['filters'])

    return result

def prepare_request_args(sub_parsers):
    api_request = sub_parsers.add_parser('request', description = 'Performs an api call on the va_master. ')
    api_request.set_defaults(sub = 'api_request')

    api_request.add_argument('method', help = 'The method to make the call with. Should be GET, POST, PUT or DELETE. ')
    api_request.add_argument('request_data', nargs = '+', help = 'The request data. All arguments with an equal sign in them will be converted to json key-value data, and all other arugments will be used to construct an endpoint. Example: vapps request panels new_panel server_name=my_server role=my_role will call /api/panels/new_panel --data \'{"server_name" : "my_server", "role" : "my_role"}\'')

def prepare_conf_args(sub_parsers):
    confs = sub_parsers.add_parser('conf', description = 'Creates a VapourApps configuration file which you can use instead of using the username and password arguments all the time. ')
    confs.set_defaults(sub = 'confs')

    confs.add_argument('--user', description = 'The username which will be saved in the configuration')
    confs.add_argument('--password', description = 'The password for the configuration. ')
    confs.add_argument('--va-master-url', description = 'The URL of the VA master')

def create_va_configuration(path, username, password, va_url):
    conf_data = {"user" : username, "password" : password, "va_master_url" : va_url}
    with open(path, 'w') as f: 
        f.write(json.dumps(conf_data))
    return conf_data

def load_va_configuration(path):
    if not os.path.exists(path):
        return None

    with open(path) as f: 
        conf = f.read()

    conf = json.loads(conf)
    return conf

def get_credentials(args):
    conf = load_va_configuration(args.conf_path)
    if conf: 
        return conf
    else: 
        print 'Could not find a va_master configuration - either the --load-conf path is incorrect, or a configuration has not been generated yet. Please answer the following prompts : '
        user = raw_input("Enter the va_master username : ")
        password = raw_input("Enter the va_master password : ")
        print 'Enter the VA master url. Include the http:// and the port, example : https://127.0.0.1:443'
        va_url = raw_input("VA master url : ")

        new_conf = create_va_configuration(args.conf_path, user, password, va_url)
        return new_conf
        

def main():
    parser = argparse.ArgumentParser(description = 'VA client argument parse. ')
#    parser.add_argument('--user', help = 'The username with which to make the request. ', default = '')
#    parser.add_argument('--password', help = 'The password with which to authenticate the request. ', default = '')
    parser.add_argument('--conf-path', help = 'If you have a configuration file in a custom location, you can specify said location with this argument. You may also have multiple configurations and choose one with this. ', default = base_path + '/vapp_config.json')

    sub_parsers = parser.add_subparsers()
    prepare_request_args(sub_parsers)

    for module in module_args: 
        m = sub_parsers.add_parser(module, description = module_args[module].get('description', ''))
        m.set_defaults(sub = module)

        m.add_argument('command', nargs = '*', choices = module_args[module]['choices'], help = module_args[module].get('help', ''))

        for a in module_args[module].get('extra_args', []):
            m.add_argument(a)


    args, unknown = parser.parse_known_args()
    creds = get_credentials(args)

    kwargs = vars(args)
    kwargs = {x : kwargs[x] for x in kwargs if x[0] != '_' and x not in ['sub', 'conf_path']}
    kwargs.update(creds)

    if args.sub == 'api_request' : 
        result = call_function(**kwargs)

    else: 
        mapping = module_mappings[args.sub]
        kwargs['mapping'] = mapping
        result = call_function_with_mapping(**kwargs)

    if type(result) in [list, dict]: 
        pprinter = PrettyPrinter(indent = 4)
        pprinter.format = va_client_utils.no_unicode
        pprinter.pprint(result)
    else: 
        print result

main()
