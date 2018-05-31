import argparse, json, pprint

module_mappings = {
    'providers' : {
        'list' : {"kwargs" : {"endpoint" : "/providers", "data" : '{}'}, "root_keys" : ["providers"], "keys" : ["provider_name", 'driver_name', 'location']},
    },
    'apps' : {
        'list' : {
            'running' : {"kwargs" : {'endpoint' : '/providers/info'}, 'data' : {}, 'method' : 'post', "keys" : ['provider_name', 'servers']},
            'available' : {"kwargs" : {'endpoint' : '/providers/info}', 'data' : {}, 'method' : 'post'}, 'keys' : ['provider_name', 'servers'], 'filters' : {"servers" : {"status" : "ACTIVE"}}},
        }, 
        'directory' : {
            'users' : {
                'list' : {"kwargs" : {'endpoint' : '/panels/action', 'data' : {'action' : 'list_users'}, "method" : "post"}, 'root_keys' : ['users'], 'keys' : ['username', 'name', 'description', 'flags'], 'method' : 'post'}, 
                'locked' : {"kwargs" : {'endpoint' : '/panels/action', 'data' : {'action' : 'list_users'}, 'method' : 'post'}, 'keys' : ['users'], 'method' : 'post'},
            }
        }
    },
    'services' : {
        'list' : {
            'kwargs' : {"endpoint" : '/services', 'data' : {}}, 
            'ok' : {"kwargs" : {'endpoint' : '/services/by_status', 'data' : {"status" : "OK"}}},
            'critical' : {"kwargs" : {'endpoint' : '/services/by_status', 'data' : {"status" : "CRITICAL"}}},
        }
    },
    'vpn' :  {
        'list' : {"kwargs" : {"endpoint" : '/apps/vpn_users', 'data' : {}}}, 
        'status' : {"kwargs" :  {"endpoint" : '/apps/vpn_status', 'data' : {}}},
        'add' : {"kwargs" : {'endpoint' : '/apps/add_vpn_user', 'method' : 'post', 'data' : {}}}, 
        'get-cert' : {"kwargs" : {'endpoint' : '/apps/download_vpn_cert', 'method' : 'post', 'data' : {}}},
    }
}

module_args = {
    'providers' : {
        'description' : 'Allows you to call various providers related functions. ', 
        'choices' : ['list'], 
        'help' : 'Specific provider command. ', 
    },'apps' : {
        'description' : 'Allows you to call various apps related functions. ', 
        'choices' : ['list', 'running', 'available', 'directory', 'users', 'users', 'all', 'locked'], 
        'extra_args' : ['--server-name'], 
    },'vpn' : {
        'description' : 'Allows you to call various vpn related functions. ', 
        'choices' : ['list', 'status', 'add', 'get-cert'], 
        'extra_args' : ['--username'], 
    },'services' : {
        'description' : 'Allows you to call various services related functions. ', 
        'choices' : ['list', 'ok', 'critical'], 
    },

}
#Will traverse a mapping by using keys from the command. If it gets to the end of the command but not to the end of the tree, will raise an exception. If a command key is invalid, will also raise an exception. 
def get_mapping_arguments(mapping, command):
    extra_args = {}
    for key in command: 
        if key not in mapping.keys():
            #If the key is not in the expected command keys, it might be an argument. See if command has extra_args. 
            if mapping.get('kwargs', {}).get('extra_args', []):
                #Add the first key to the first argument in extra_args
                pass
            #Key is not in the expected keys, and there are more keys than arguments. There is an error. 
            else:
                expected_keys = [x if x != 'kwargs' else '<End of command>'  for x in mapping.keys()]
                raise Exception('Invalid command: ' + ' '.join(command) + '; Failed at ' + key + '. Did not find it in expected keys : ' + str(expected_keys) + '. Maybe there are too many arguments? Collected so far : ' + str(extra_args))

        mapping = mapping[key]

    #We have iterated throughout the entire command. If mapping does not contain "kwargs", we are not at the bottom of the tree. 
    if 'kwargs' not in mapping.keys():
        raise Exception('Invalid command: ' + ' '.join(command) + '; Parsed the entire command but did not find a suitable function. Maybe add one of these keywords : ' + str(mapping.keys()))

    return mapping

def extract_data_with_keys(result, keys = []):
    if not keys: return result
    final_result = []
    for data in result: 
#        print ('Data is : ', data)
        for k in keys: 
            if k not in data.keys(): 
                raise Exception('Key ' + k + ' not found in ' + str(data.keys()))
        data = {x : data[x] for x in keys}
        final_result.append(data)
    return final_result

def dict_contains_dict(d1, d2):
    return set(d2.items()).issubset(set(d1.items()))

def filter_results(result, filters):
    for val in result: 
        for filt in filters:
            temp_result = val[filt]
            temp_result = [x for x in temp_result if dict_contains_dict(x, filters[filt])]
            val[filt] = temp_result
    return result

def no_unicode(object, context, maxlevels, level):
    """ change unicode u'foo' to string 'foo' when pretty printing"""
    if pprint._type(object) is unicode:
        object = unicode(object)
    return pprint._safe_repr(object, context, maxlevels, level)
