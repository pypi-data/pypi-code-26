import click
import json
import yaml
import random
import string
from crupter.crupter import Crupter

def validate_capabilities(ctx, param, value):
    print(value)
    if(value == "CAPABILITY_IAM" or
       value == "CAPABILITY_NAMED_IAM" or
       value == "CAPABILITY_NAMED_IAM CAPABILITY_IAM" or
       value == "CAPABILITY_IAM CAPABILITY_NAMED_IAM"
      ):
        return value
    else:
        raise click.BadParameter('Provide CAPABILITY_IAM, CAPABILITY_NAMED_IAM, or both separated with a space.')


def dump(myvar):
    """
    Just to dump some json in a readable format.
    """
    print(json.dumps(myvar, default = myconverter, indent=4))


def myconverter(o):
    """
    for json dump to show datetime as string instead of breaking with errors
    """
    if isinstance(o, datetime.datetime):
        return o.__str__()


def random_string(length, start = 's'):
    """
    Simple function to generate an unique random string
    Param start is 's' by default, because a change set in AWS requires a [a-z][A-Z]
    """
    for i in range(length):
        start += random.choice(string.ascii_uppercase + string.ascii_lowercase + string.digits)
    return str(start)


def process_params(params):
    """
    Compatible with AWS' way of using parameters and converting it to a list
    of dictionaries.
    'Key=env,Value=prod Key=bla,Value=bli\ bla\, blo'
    """
    params = params.replace(", ", ",")
    params = params.replace("\=", "<*equal*>")
    params = params.replace("\ ", "<*space*>")
    params = params.replace("\,", "<*comma*>")
    split1 = params.split(' ')
    ret = []
    for split in split1:
        split2 = split.split(',')
        obj = {}
        for s2 in split2:
            key, value = s2.split('=')
            value = value.replace('<*space*>', ' ')
            value = value.replace('<*comma*>', ',')
            value = value.replace('<*equal*>', '=')
            row = { key : value }
            obj = { **obj, **row }
        ret.append(obj)
    return ret


def process_params_simple(params):
    """
    Our own notation for parameters which is simpler.
    'Key=bli\ bla\, blo Env=Prod'
    """
    params = params.replace(", ", ",")
    params = params.replace("\=", "<*equal*>")
    params = params.replace("\ ", "<*space*>")
    params = params.replace("\,", "<*comma*>")
    split1 = params.split(' ')
    ret = {}
    for split in split1:
        key, value = split.split('=')
        value = value.replace('<*space*>', ' ')
        value = value.replace('<*comma*>', ',')
        value = value.replace('<*equal*>', '=')
        row = { key : value }
        ret = { **ret, **row }
    return ret


CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])

@click.command(context_settings=CONTEXT_SETTINGS)
@click.argument('action', 
                type=click.Choice(['create',
                                   'deploy',
                                   'update',
                                   'delete',
                                   'terminate',
                                   'show',
                                   'status',
                                   'test',
                                   'watch'
                                  ]))
@click.option('--template-body',
              default=None,
              help='Provide a file:// or s3:// path, to get the template file from S3. Allowed file formats: .yaml, .yml, .json, .jn2')
@click.option('--stack-name',
              required=True,
              help='Provide a name for the Stack.')
@click.option('--change-set-name',
              help='Provide a unique name for this change set.')
@click.option('--template-data',
              help='Provide a local path to a yaml')
@click.option('--template-parameters',
              help='Provide "Key=key1,Value=value1 ...," to use as data in Jinja2')
@click.option('--parameters', help='Provide a local path to a yaml file, or Key=key1,Value=value1 ... to pass as native Cloudformation Parameters')
@click.option('--tags', help='Tags. (Key=TagKey,Value=TagValue ...')
@click.option('--capabilities',
              help='Turn on or off capabilities (CAPABILITY_IAM CAPABILITY_NAMED_IAM)')
@click.option('--timeout-in-minutes', type=click.INT, default=60, help='Provide timeout in minutes. After this timeout a rollback is forced. (Default: 60)')
@click.option('--role-arn', help='The Role Arn for Cloudformation to Assume.')
@click.option('--template-profile', help='Provide the configured profile to access the templates on S3. By default the --profile is used.')
@click.option('--no-create', is_flag=True, default=False, help='When using update, do not create a new stack when this parameter is set.')
@click.option('--terminate', is_flag=True, default=False, help='Always terminate a stack after deployment.')
@click.option('--no-rollback', is_flag=True, default=False, help='Do not rollback a stack after deployment.')
# @click.option('--region', help='Enter the region.')
# @click.option('--profile', help='Enter a profile name with permissions to deploy.')
def main(**kwargs):
    """
    \b
    Crupter helps to easily create or update change sets in cloudformation with a single command.
    \b
    ACTION:

    \b
    create      Creates a new stack, error when stack already exists.
    update      Creates a new or updates an exisisting stack.
    deploy      Creates a new or updates an exisisting stack.
    delete      Terminates/deletes a stack.
    terminate   Terminates/deletes a stack.
    show        Show the output of a processed template.
    status      Show the status of the deployment.
    watch       Watch the status of a deployment.

    EXAMPLES:

    \b
    cruptor deploy --stack-name myproductionstack \\
                   --template-body s3://bucketname/template.yml.jn2 \\
                   --template-parameters file://data.yml
    """
    
    # process parameters native cloudformation
    if kwargs['parameters'] is not None:
        if(kwargs['parameters'][:1] == '['):
            kwargs['parameters'] = json.loads(kwargs['parameters'])
        else:
            kwargs['parameters'] = process_params(kwargs['parameters'])
    
    # make list for capabilities
    if kwargs['capabilities'] is not None :
        kwargs['capabilities'] = kwargs['capabilities'].split(' ')

    template_data = {}
    # read data for template_data
    if kwargs['template_data'] is not None:
        file = open(kwargs['template_data'][7:], 'r').read()
        template_data = yaml.load(file)
    
    # add parameters to template data
    if kwargs['template_parameters'] is not None:
        template_data['parameters'] = process_params_simple(kwargs['template_parameters'])
    
    kwargs['template_data'] = template_data

    # if no change set is set, generate a random string
    if kwargs['change_set_name'] is None:
        kwargs['change_set_name'] = random_string(16)

    # read the tags
    if kwargs['tags'] is not None:
        if(kwargs['tags'][:1] == '['):
            kwargs['tags'] = json.loads(kwargs['tags'])
        else:
            kwargs['tags'] = process_params(kwargs['tags'])

    # create object with provided arguments
    crupter = Crupter(**kwargs)

    # fire the action
    if kwargs['action'] == "test":
        crupter.test()
    elif kwargs['action'] in ['deploy', 'create', 'update']:
        if kwargs['template_body'] is not None:
            crupter.update()
        else:
            print('Error: Missing option "--template-body"')
            exit()
    elif kwargs['action'] in ['terminate', 'delete']:
        crupter.kill()
    elif kwargs['action'] == "show":
        if kwargs['template_body'] is not None:
            crupter.show()
        else:
            print('Error: Missing option "--template-body"')
            exit()
    elif kwargs['action'] == "status":
        crupter.status()
    elif kwargs['action'] == 'watch':
        crupter.watch()
    else:
        print("error")

if __name__ == '__main__':
    main()
