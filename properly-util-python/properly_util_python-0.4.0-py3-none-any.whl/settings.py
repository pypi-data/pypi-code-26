import os

import boto3

DEBUG = os.environ.get('DEBUG')

retry_browser_max = 3
realtor_scraper_loops = 1

aws_access_key_id = os.environ.get('AWS_ACCESS_KEY_ID')
aws_secret_access_key = os.environ.get('AWS_SECRET_ACCESS_KEY')

dynamodb_resource = boto3.resource('dynamodb', )

dynamodb_client = client = boto3.client('dynamodb', )
# todo why isn't this settings.py file being read in lambda_functions modules
sqs_client = boto3.client('sqs', )

s3_resource = boto3.resource(
            's3',
        )
STAGE = os.environ.get('STAGE', 'dev')


def get_clean_table_name():
    return STAGE + '-property-historical-clean-002'


dynamo_alternate_endpoint = os.environ.get('COM_GOPROPERLY_ALT_DYNAMO_ENDPOINT', None)

if (dynamo_alternate_endpoint is None):
    print("No Alternate Endpoint")
    dynamodb_resource = boto3.resource('dynamodb', )
    dynamodb_client = client = boto3.client('dynamodb', )


else:
    print("Working with alternate: {0}".format(dynamo_alternate_endpoint))
    dynamodb_resource = boto3.resource('dynamodb', endpoint_url=dynamo_alternate_endpoint, )
    dynamodb_client = client = boto3.client('dynamodb', endpoint_url=dynamo_alternate_endpoint, )

# todo why isn't this settings.py file being read in lambda_functions modules
sqs_client = boto3.client('sqs', )