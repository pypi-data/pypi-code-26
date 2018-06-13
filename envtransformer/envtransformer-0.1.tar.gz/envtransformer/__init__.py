import baker
import json
import boto3
import yaml

ssm = boto3.client('ssm', region_name='eu-west-1')

def getparameterstore(key):
    if key is not None:
        try:
            response = ssm.get_parameter(Name=key)
            paramval = response['Parameter']['Value']
            return paramval
        except Exception, e:
            print "%s Not Found" % key

def putparameter(key, value, description):
    response = ssm.put_parameter(Name=key, Description=description, Value=value, Type='String')
    return response

def inplace_changer(filename, old_string, new_string):
    # Safely read the input filename using 'with'
    with open(filename) as f:
        s = f.read()
        if old_string not in s:
            print '"{old_string}" not found in {filename}.'.format(**locals())
            return

    with open(filename, 'w') as f:
        print 'Changing "{old_string}"'.format(**locals())
        s = s.replace(old_string, new_string)
        f.write(s)

def serverless(path, stage):
    with open(path) as stream:
        data = yaml.load(stream)
        for v in data[stage].values():
            if "#" in v:
                envkey = v[1:]
                paramval = getparameterstore(envkey)
                if paramval is not None:
                    inplace_changer(path, v, paramval)

def chaliceconfig(path, stage):
   with open(path) as data_file:    
        data = json.load(data_file)
        subnetid = data['stages'][stage]['subnet_ids']
        if subnetid is not None:
            subnetidk = subnetid[1:]
            subnet = getparameterstore(subnetidk)
        
        securitygroup = data['stages'][stage]['security_group_ids']
        if securitygroup is not None:            
            securitygroupk = securitygroup[1:]
            securitygrp = getparameterstore(securitygroupk)

        for v in data['stages'][stage]['environment_variables'].values():
            if "#" in v:
                envkey = v[1:]
                paramval = getparameterstore(envkey)
                if paramval is not None:
                    inplace_changer(path, v, paramval) 

@baker.command
def path(path, ptype, stage):
    if ptype == 'chalice': 
        chaliceconfig(path, stage)
    if ptype == 'serverless':
        serverless(path,stage)

if __name__ == '__main__':
    baker.run()