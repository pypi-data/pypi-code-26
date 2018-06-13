# -*- coding: utf-8 -*-

from __future__ import print_function
from six.moves import urllib
import os
import sys
import json
import time
import argparse
import requests


__version__ = "1.1.5"


def begin_capture(apikey, capture_request):
    api_url = os.environ.get('SSAPI_URL', 'https://api.screenshotapi.io')
    api_endpoint = "{}/capture".format(api_url)
    print('Sending request: ' + capture_request['url'])
    capture_request['url'] = \
        urllib.request.pathname2url(capture_request['url']).encode('utf8')
    result = requests.post(
        api_endpoint,
        data=capture_request,
        headers={'apikey': apikey})
    print(result.text)
    if result.status_code == 401:
        raise Exception("Invalid API Key")
    return json.loads(result.text)['key']


def try_retrieve(apikey, key):
    api_url = os.environ.get('SSAPI_URL', 'https://api.screenshotapi.io')
    api_endpoint = "{}/retrieve".format(api_url)
    print('Trying to retrieve: ' + key)
    result = requests.get(
        api_endpoint,
        params={'key': key},
        headers={'apikey': apikey})
    json_results = json.loads(result.text)
    if json_results["status"] == "ready":
        print('Downloading image: ' + json_results["imageUrl"])
        image_result = requests.get(json_results["imageUrl"])
        return {'complete': True, 'bytes': image_result.content}
    else:
        return {'complete': False}


def get_screenshot(apikey, capture_request, save_path):
    key = begin_capture(apikey, capture_request)
    timeout_seconds = \
        int(os.environ.get('SSAPI_RETRIEVE_TIMEOUT_SECS', 1200))
    wait_seconds_counter = 0
    retry_delay_seconds = 5

    while True:
        result = try_retrieve(apikey, key)
        if result["complete"]:
            filename = os.path.join(save_path, '{}.png'.format(key))
            print("Saving screenshot to: " + key)
            open(filename, 'wb').write(result['bytes'])
            break
        else:
            wait_seconds_counter += retry_delay_seconds
            print("Screenshot not yet ready, waiting {} seconds...".format(retry_delay_seconds))
            time.sleep(retry_delay_seconds)
            if wait_seconds_counter > timeout_seconds:
                print("Timed out while attempting to retrieve: " + key)
                break


def main():
    print("ScreenshotAPI.io CLI version {}".format(__version__))

    parser = argparse.ArgumentParser()
    parser.add_argument('--apikey', required=False,
                        help='Alternatively supply environment variable SCREENSHOTAPI_KEY')
    parser.add_argument('--url', required=True)
    parser.add_argument('--webdriver',
                        default='firefox',
                        choices=['firefox', 'chrome', 'phantomjs'])
    parser.add_argument('--viewport',
                        default='1200x800',
                        help='The viewing area of the browser which is making the screenshot request.')
    parser.add_argument('--fullpage', dest='fullpage', action='store_true')
    parser.add_argument('--no-javascript', dest='javascript', action='store_false')
    parser.set_defaults(javascript=True)
    parser.add_argument('--wait-seconds', default=0,
                        help='The number of seconds to wait after the page has loaded before taking the screenshot.')
    parser.add_argument('--fresh', dest='fresh', action='store_true',
                        help='Forces a fresh capture, otherwise capture may be cached (max 72 hours)')
    parser.set_defaults(fresh=False)
    parser.add_argument('--save-path', default='./',
                        help='The local file path to save the screenshot jpegs to.')

    args = parser.parse_args()

    # prefer api keky from argument if present
    apikey = args.apikey
    # if not provided, fall back to the environment variable
    if not apikey:
        apikey = os.environ.get('SCREENSHOTAPI_KEY', None)
    # if neither provided, exit
    if not apikey:
        print("API key not given as --apikey argument or in SCREENSHOTAPI_KEY environment variable")
        print("Go to www.screenshotapi.io for a free API key")
        sys.exit(1)

    get_screenshot(
        apikey=apikey,
        capture_request={
            'url': args.url,
            'viewport': args.viewport,
            'fullpage': args.fullpage,
            'webdriver': args.webdriver,
            'javascript': args.javascript,
            'waitSeconds': args.wait_seconds,
            'fresh': args.fresh
        },
        save_path=args.save_path
    )
