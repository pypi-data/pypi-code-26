#!/usr/bin/python
# -*- coding:utf-8 -*-

from com.obs.client.obs_client import ObsClient
import argparse

DOCUMENTATION = '''
---
module: huawei_obs
short_description: 华为OBS服务的上传功能实现
description:
  1. 通过华为的SDK实现将本地的指定文件上传到华为云的对象存储服务（OBS）
  2. 华为云OBS的接口实现中，如果存在已经有了指定bucket，还是会创建成果，不会报错
version_added: "1.1"
'''

def main():
    cmd_parser = argparse.ArgumentParser()
    cmd_parser.add_argument("--AK", dest="ak", help="Access Key Id")
    cmd_parser.add_argument("--SK", dest="sk", help="Secret Access Key")
    cmd_parser.add_argument("--server", dest='server', help="Bucket Server")
    cmd_parser.add_argument("--bucketName", dest='bucketName', help="Bucket Name")
    cmd_parser.add_argument("--objectKey", dest='objectKey', help="Object Key")
    cmd_parser.add_argument("--localPath", dest='localPath', help="Local File Path")
    args = cmd_parser.parse_args()

    obsClient = ObsClient(access_key_id=args.ak, secret_access_key=args.sk, server=args.server, is_secure=False)

    try:
        from com.obs.models.put_object_header import PutObjectHeader

        headers = PutObjectHeader()
        headers.contentType = 'text/plain'

        resps = obsClient.putFile(args.bucketName, args.objectKey, args.localPath, headers=headers)

        for res in resps:
            if res[1].status < 300:
                print('file: %s is upload success.' % res[0])
            else:
                print('file: %s is upload failed.' % res[0])
                print('errorCode:', res[1].errorCode)
                print('errorMessage:', res[1].errorMessage)
    except:
        import traceback
        print(traceback.format_exc())

if __name__ == '__main__':
    main()