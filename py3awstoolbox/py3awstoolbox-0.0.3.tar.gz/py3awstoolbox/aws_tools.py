import boto3
import maya


def get_s3_subfolders(bucket, prefix='') :
   s3 = boto3.client('s3')
   kwargs = {'Bucket': bucket , 'Delimiter' : '/' } 
   if isinstance(prefix, str): kwargs['Prefix'] = prefix 
   
   while True:
    resp = s3.list_objects_v2(**kwargs)
    try:
      if len(resp['CommonPrefixes'])>0 :
        for f in resp['CommonPrefixes']:
          yield ( f['Prefix'])
    except KeyError:
      try:
        kwargs['ContinuationToken'] = resp['NextContinuationToken']
      except KeyError:
        break     
      continue
    try:
      kwargs['ContinuationToken'] = resp['NextContinuationToken']
    except KeyError:
      break   
   
   
def get_s3_objects(bucket, prefix='', suffix='', recursive=True):
    s3 = boto3.client('s3')
    print (suffix)

    if recursive :
      kwargs = {'Bucket': bucket}
    else:
      kwargs = {'Bucket': bucket, 'Delimiter' : '/' }
    if isinstance(prefix, str): kwargs['Prefix'] = prefix
    while True:
      resp = s3.list_objects_v2(**kwargs)
      try:
        contents = resp['Contents']
      except KeyError:
        try:
          kwargs['ContinuationToken'] = resp['NextContinuationToken']
        except KeyError:
          break      
        continue

      for obj in contents:
        key = obj['Key']
        if key.endswith(suffix): yield obj

      try:
        kwargs['ContinuationToken'] = resp['NextContinuationToken']
      except KeyError:
        break

def get_s3_keys(bucket, prefix='', suffix='', recursive=True):
  for obj in get_s3_objects(bucket=bucket, prefix=prefix, suffix=suffix, recursive=recursive):
    yield obj['Key']
    
if __name__ == "__main__":
  #s3list = get_s3_objects(bucket='product-cache-prd', prefix='product/', suffix='', recursive=False)
  s3_folders = get_s3_keys('product-cache-prd', prefix='product/127/0019')
  for f in s3_folders: print (f)