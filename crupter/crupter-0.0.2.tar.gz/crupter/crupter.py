import boto3
import sys
import jinja2
import yaml
import string
import random
import requests
# import logging
import json
import time
import datetime
# from yamllint import linter
# from yamllint.config import YamlLintConfig

from jinja2 import Environment, Template
from botocore.exceptions import ClientError, WaiterError

def myconverter(o):
    if isinstance(o, datetime.datetime):
        return o.__str__()

def dump(myvar):
    print(json.dumps(myvar, default = myconverter, indent=4))

def safe_get(var, kwargs):
    return None if var not in kwargs else kwargs[var]

# #logger = logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.DEBUG)
# logger = logging.getLogger()
# logger.setLevel(logging.INFO)
class Crupter(object):
    
    template_profile = None
    stack_status = None
    stack_name = None
    template_body = None
    template_parameters = None
    template_data = None
    template_profile = None
    parameters = None
    capabilities = None
    template_data_processed = {}
    tags = None
    role_arn = None

    def __init__(self, **kwargs):
        """
        Initialize with defaults.
        """
        for key in kwargs:
            setattr(self, key, kwargs[key])
        
        # validate some parameters
        if self.stack_name is None:
            print("Error, stack_name is mandatory")
            exit()
        if self.capabilities is not None and type(self.capabilities) not in (list, tuple):
            print("Error, capabilities must be a tuple")
            exit()
        if self.tags is not None and type(self.tags) not in (list, tuple):
            print("Error, tags must be a tuple")
            exit()
        
        self._initialize_aws_clients()
        
        # now do some template generation, which is not required with delete/show etc.
        if self.template_body is not None:
            if (
                self.template_body[:7] == "file://" or 
                self.template_body[:5] == "s3://" or
                self.template_body[:8] == "https://" ):
                pass
            else:
                print("Error, template_body must start with: file://, s3://, https://")
                exit()
            self._process_template()

    def show(self):
        """
        Just to test if all parameters are set correctly
        """
        print(self.template_body_processed)

    def test(self):
        """
        Just to test if all parameters are set correctly
        """
        dump(self.__dict__)

    def _process_template(self):
        """
        Render the template.
        """
        #check if start: file:// or s3://
        if(self.template_body is not None and self.template_body[:7] == "file://"):
            template = open(self.template_body[7:], 'r').read()
        elif(self.template_body is not None and self.template_body[:8] == "https://"):
            r = requests.get(self.template_body)
            template = r.text
        elif(self.template_body is not None and self.template_body[:5] == "s3://"):
            bucket = self.template_body.split('/')[2]
            key = self.template_body.replace("s3://"+bucket+"/", "")
            obj = self.s3.get_object(Bucket=bucket, Key=key)
            template = obj['Body'].read().decode('utf-8')
        
        # load the template
        j = Template(template)

        # render the template
        try:
            self.template_body_processed = j.render(self.template_data)
            self.template_body_processed += "\n" # jinja removes the trailing white space line
            
        except Exception as e:
            print("Something went wrong while rendering the template: {}".format(e))
            exit()

        # yaml validation
        # conf = YamlLintConfig(file="examples/yamllint.config")
        # linting_problems = linter.run(input=self.template_body_processed, conf=conf)
        # errors = ""
        # for l in linting_problems:
        #     errors += l.desc + ' at ' + str(l.line) + ', '
        # if len(errors) > 0:
        #     print("YAML Validation Error(s): " + errors)
        #     exit()

        # try validation or error
        try:
            self.cloudformation.validate_template(TemplateBody=self.template_body_processed)
        except Exception as e:
            print("Something went wrong while validating the template: {}".format(e))
            exit()

    def _initialize_aws_clients(self):
        """
        Initizalize AWS clients
        """
        # Use export AWS_DEFAULT_PROFILE=<profile> to change the role
        self.cloudformation = boto3.client('cloudformation')

        # use template profile to access templates in s3
        # or use the same profile running this command
        if(self.template_profile != None):
            session = boto3.Session(profile_name=self.template_profile)
            self.s3 = session.client('s3')
        else:
            self.s3 = boto3.client('s3')

    def _get_stack_status(self):
        """
        Get some details of the current status of the cloudformation
        """
        try:
            stack = self.cloudformation.describe_stacks(
                StackName = self.stack_name
            )
            self.stack_status = stack['Stacks'][0]
            #print("Found Stack with name {} .".format(self.stack_name))

            if(self.stack_status['ChangeSetId'] is not None):
                try:
                    stack = self.cloudformation.describe_change_set(
                        ChangeSetName = self.stack_status['ChangeSetId']
                    )
                    self.stack_status['CurrentChangeSet'] = {
                        'ChangeSetName': stack['ChangeSetName'],
                        'ExecutionStatus': stack['ExecutionStatus'],
                        'Status': stack['Status'],
                    }
                    #print("Found ChangeSet with id \"{}\".".format(self.stack_status['ChangeSetId']))
                except:
                    #print("ChangeSet with name/id \"{}\" does not exist.".format(self.stack_status['ChangeSetId']))
                    pass
        except:
            print("StackName {} does not exist. ".format(self.stack_name))
            pass

    def deploy(self, **kwargs):
        self.update(**kwargs)

    def create(**kwargs):
        self.update(**kwargs)

    def update(self):
        """
        creates, updates or deploys the stack
        """
        self._get_stack_status()
        if(self.stack_status == None):
            change_set_type = 'CREATE'
            waiter_type = "stack_create_complete"
        else:
            change_set_type = "UPDATE"
            waiter_type = "stack_update_complete"
        print("Change Set Type: {}".format(change_set_type))

        if(self.stack_status is not None and self.stack_status['StackStatus'] in ['CREATE_COMPLETE', 'UPDATE_COMPLETE']):
            try:
                result = self.cloudformation.describe_change_set(
                    StackName = self.stack_name,
                    ChangeSetName = self.change_set_name,
                )
                if('Status' in result and result['Status'] in ['CREATE_COMPLETE']):
                    self.cloudformation_client.delete_change_set(
                        StackName=self.stack_name,
                        ChangeSetName=self.changeset_name
                    )
                else:
                    print("This stack deployment is in progress, try again in a few moments.")
                    exit(100)
            except:
                # if the change set is not found, an error is raised which we should pass
                pass

        elif(self.stack_status is None):
            # if there is no stack yet, proceed with deployment
            pass
        else:
            print("Stack is not ready to deploy")
            exit()
            
        # get the kwargs ready
        kwargs = {
            'StackName' : self.stack_name,
            'ChangeSetName' : self.change_set_name,
            'TemplateBody' : self.template_body_processed,
            'ChangeSetType' : change_set_type,
        }
        if self.parameters is not None:
            kwargs['Parameters'] = self.parameters
        if self.role_arn is not None:
            kwargs['RoleARN'] = self.role_arn
        if self.tags is not None:
            kwargs['Tags'] = self.tags
        if self.capabilities is not None:
            kwargs['Capabilities'] = self.capabilities
        if self.tags is not None:
            kwargs['Tags'] = self.tags
        if self.role_arn is not None:
            kwargs['RoleARN'] = self.role_arn
        
        # fire the change set deploy
        try:
            result = self.cloudformation.create_change_set(**kwargs)
        except Exception as e:
            print("Something went wrong with the change set: {}".format(e))
            exit()

        # wait until the change set is ready to execute, or delete and exit if something fails
        try:
            waiter = self.cloudformation.get_waiter("change_set_create_complete")
            waiter.wait(ChangeSetName=self.change_set_name, StackName=self.stack_name, WaiterConfig={'Delay': 10, 'MaxAttempts': 30})
        except WaiterError as wait_error:
            print(wait_error)
            # if change set has no changes, then delete it immediately
            self.cloudformation.delete_change_set(
                StackName=self.stack_name,
                ChangeSetName=self.change_set_name
            )
            print("No changes found, deployment is not needed and change set is deleted.")
            exit(0)
        
        # nothing failed, so now execute the change set.
        self.cloudformation.execute_change_set(
            StackName = self.stack_name,
            ChangeSetName = self.change_set_name
        )

        self._watch_stack()

    def watch(self):
        """
        Watch the events happening.
        """
        self._watch_stack()
    
    def _watch_stack(self):
        """
        This function finds the last change and prints out the logs until it's finished.
        """
        #find the first event
        paginator = self.cloudformation.get_paginator('describe_stack_events')
        page_iterator = paginator.paginate(StackName = self.stack_name)
        events = []
        for page in page_iterator:
            for se in page['StackEvents']:
                events.append(se)
        events.reverse()
        for se in events:
            if( 'ResourceStatusReason' in se and
                se['ResourceStatus'] in ['UPDATE_IN_PROGRESS', 'CREATE_IN_PROGRESS'] and
                se['ResourceStatusReason'] in ['User Initiated']):
                    first = se['EventId']
        keep_watching = True
        printed = []

        while(keep_watching):
            paginator = self.cloudformation.get_paginator('describe_stack_events')
            page_iterator = paginator.paginate(StackName = self.stack_name)
            events = []
            for page in page_iterator:
                for se in page['StackEvents']:
                    events.append(se)
            events.reverse()
            start_printing = False
            for se in events:
                if(first in [se['EventId']]):
                    start_printing = True
                if(start_printing and se['EventId'] not in printed):
                    printed.append(se['EventId'])
                    print("{} {} {}".format(se['ResourceStatus'], se['ResourceType'], se['LogicalResourceId']))
                    # if something goes wrong during creation, terminate the whole stack
                    if se['ResourceStatus'] in ['CREATE_FAILED'] and se['ResourceType'] in ['AWS::CloudFormation::Stack']:
                        self.terminate()
                if( start_printing and
                    se['ResourceStatus'] in ['UPDATE_COMPLETE', 'CREATE_COMPLETE', 'ROLLBACK_COMPLETE'] and
                    se['ResourceType'] in ['AWS::CloudFormation::Stack']):
                        keep_watching = False
            if(keep_watching):
                time.sleep(3)

    def status(self):
        self._get_stack_status()
        dump(self.stack_status)

    def delete(self):
        self.terminate()

    def terminate(self):
        self.kill()

    def kill(self):
        """
        Terminate the stack
        """
        self._get_stack_status()
        if(self.stack_status is not None and self.stack_status['StackStatus'] in ['CREATE_COMPLETE', 'UPDATE_COMPLETE']):
            response = self.cloudformation.delete_stack(
                StackName=self.stack_name,
            )
            waiter = self.cloudformation.get_waiter("stack_delete_complete")
            waiter.wait(
                StackName=self.stack_name,
                WaiterConfig={'Delay': 10, 'MaxAttempts': 30}
            )
            print("Stack \"{}\" is deleted.".format(self.stack_name))
        else:
            print("Stack \"{}\" is NOT deleted.".format(self.stack_name))


if __name__ == '__main__':
    main()