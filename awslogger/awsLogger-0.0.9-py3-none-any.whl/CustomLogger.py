#!/usr/bin/env python3
"""
Continuous integration utils
"""

__author__ = "Guillaume Ringwald"
__version__ = "0.1.0"
__license__ = "MIT"

import boto3
import subprocess
import json
import logging
import re
import urllib.request

# log utils
# create logger
console = logging.getLogger('console')
console.setLevel(logging.DEBUG)
# create console handler with a higher log level
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
# create file handler which logs even debug messages
fh = logging.FileHandler('awsloggerDebug.log')
fh.setLevel(logging.DEBUG)
# create formatter and add it to the handlers
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
fh.setFormatter(formatter)
# add the handler to the logger
console.addHandler(ch)
console.addHandler(fh)


def snakeCase(name):
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1-\2', name)
    return re.sub('([a-z0-9])([A-Z])', r'\1-\2', s1).lower()


def dumper(obj):
    try:
        return obj.toJSON()
    except:
        return obj.__dict__


def addLine(toLog, config):
    """add current values to csv file"""
    finalLog = json.dumps(toLog, default=dumper)
    console.info(f"type of entry to log:{type(toLog)} ", )
    with open(f'{config["filePath"]}{config["fileName"]}', 'a') as logFile:
        result = logFile.write(f'{finalLog}\n')
        console.info(f"logAndPush result: {result}")
        return result
    return False


def getFullConfig(config):

    if(not("bucketPathFromRoot" in config)):
        config["bucketPathFromRoot"] = 'logs/'

    if(not("filePath" in config)):
        config["filePath"] = './'
    if "projectId" in config and not("fileName" in config):
        config["fileName"] = f'{config["projectId"]}.log'
    if(not("fileName" in config)):
        config["fileName"] = 'awsLogger.log'
    if "projectId" in config and not("bucketName" in config):
        config["bucketName"] = snakeCase(config["projectId"])
    if(not("bucketName" in config)):
        config["bucketName"] = 'aws-logger'
    else:
        config["bucketName"] = snakeCase(config["bucketName"])
    if not("awsRegion" in config):
        config["awsRegion"] = "eu-west-1"

    console.info(["config : ", config])
    if "awsRole" in config:
        # retrieve credential from iam
        console.debug(["awsRole found", config["awsRole"]])
        url = f'http://169.254.169.254/latest/meta-data/iam/security-credentials/{config["awsRole"]}'

        console.debug(["url :", url])
        contents = urllib.request.urlopen(url).read()
        iamSecrets = json.loads(contents)

        config["awsId"] = iamSecrets["AccessKeyId"]
        config["awsSecret"] = iamSecrets["SecretAccessKey"]
        console.debug(["config : ", config, "iamSecrets:",
                       iamSecrets, "contents:", contents])

    return config


def push(config):
    """Upload file to s3"""
    try:
        conf = getFullConfig(config)
        console.info(
            f' push : {conf["filePath"]}{conf["fileName"]}')
        if ("awsId" in conf and "awsSecret" in conf):
            # an aws configuration is specified
            console.debug("custom aws credential found")
            session = boto3.Session(
                aws_access_key_id=conf["awsId"],
                aws_secret_access_key=conf["awsSecret"],
            )
        else:
            session = boto3.Session()
        s3 = session.resource('s3')

        data = open(f'{conf["filePath"]}{conf["fileName"]}', 'rb')
        r = s3.Bucket(conf["bucketName"]).put_object(
            Key=f'{conf["bucketPathFromRoot"]}{conf["fileName"]}', Body=data)
        console.info(f'file pushed: {r}')
        return r
    except Exception as e:
        console.exception(e)
        return False


def log(toLog, config):
    """ log a variable of any type and push it to s3 """
    conf = getFullConfig(config)
    console.info(f"start loggin with config : {conf}")
    result = addLine(toLog, conf)
    console.info(f"log result: {result}")
    return result


def logAndPush(toLog, config):
    """ log a variable of any type and push it to s3 """
    conf = getFullConfig(config)
    console.info(f"start loggin with config : {conf}")
    result = addLine(toLog, conf) and push(conf)
    console.info(f"logAndPush result: {result}")
    return result
