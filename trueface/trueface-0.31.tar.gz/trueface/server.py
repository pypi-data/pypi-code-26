# coding: utf-8
"""identify demo"""
import cv2
# import mxnet as mx
# from mtcnn_detector import MtcnnDetector
# from imutils.object_detection import non_max_suppression
import requests
import time
import pandas as pd
import base64
import json
import numpy as np
import dlib
import traceback
import random
import string
import mss
from requests_futures.sessions import FuturesSession
from art import text2art
import argparse
# import matplotlib.pyplot as plt
# from pubnub.enums import PNStatusCategory
# from pubnub.pnconfiguration import PNConfiguration
# from pubnub.pubnub import PubNub
# from imutils.video import WebcamVideoStream
# from imutils.video import FileVideoStream
# from termcolor import colored, cprint
# import os
import docker

ap = argparse.ArgumentParser(description="Trueface.ai Server Management")
# parser.add_argument('integers', metavar='N', type=int, nargs='+',
#                     help='an integer for the accumulator')

ap.add_argument("-sc", "--start-container", default=False, 
                help="phone number to send sms alerts to", action='store_true')

ap.add_argument("-st", "--show-tracking", default=False, 
                help="whether to show the tracking box", action='store_true')

args = vars(ap.parse_args())


def id_generator(size=6, chars=string.ascii_uppercase + string.digits):
	return ''.join(random.choice(chars) for _ in range(size))

def start_container(image_name, path, api_key, secret):
    client = docker.from_env()
    container = client.containers.run(image_name, ports={'8085/tcp': 8085}, detach=True)
    container.rename("truefaceServer_%s" % id_generator())
    #container.put_archive("creds", "")
    #container.exec_run("\"{'api_key':%s,'secret':%s} > creds.json\"" % (api_key, secret))
    #pass credentials and save them in the des
    print container.id
    #print client.containers


def main():
	if args['start_container']:
		start_container("tfv2-cpu:0.4", path, api_key, secret)
