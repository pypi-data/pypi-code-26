import boto3

def get_client():
    return boto3.client('s3')

def list_buckets():
    s3 = get_client()
    response = s3.list_buckets()
    if response:
        for bucket in response.get('Buckets', []):
            yield bucket['Name']

def list_objects(bucket):
    s3 = get_client()
    response = s3.list_objects(Bucket=bucket)
    if response:
        for _object in response.get('Contents', []):
            yield _object['Key']

def read_object(bucket, key):
    s3 = get_client()
    response = s3.get_object(Bucket=bucket, Key=key)
    if response:
        return response['Body'].read()


def put_object(bucket, key, body):
    s3 = get_client()
    s3.put_object(Bucket=bucket, Key=key, Body=body)


def main():
    for bucket in list_buckets():
        print '[ {} ]'.format(bucket)
        for key in list_objects(bucket):
            print ' => {}'.format(key)
