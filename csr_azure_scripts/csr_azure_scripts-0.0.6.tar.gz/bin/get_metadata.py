#!/usr/bin/env python
import json
import urllib2
import logging

metadata_url = 'http://169.254.169.254/metadata/instance?api-version=2017-03-01'
metadata_url_test = 'http://169.254.169.254/metadata/'
headers = {'Metadata': 'true'}

deviceType='localMachine'
try:
    import cli
    deviceType='csr1000v'
except Exception as e:
    print(e)

class metadata:
    def __init__(self):
        return

    def get_metadata(self):
        req = urllib2.Request(metadata_url, headers=headers)
        resp = urllib2.urlopen(req)
        resp_read = resp.read()
        data = json.loads(resp_read)
        return data

    def get_instance_id(self):
        '''
        :return: returns short instance id of instance.
        '''
        if deviceType == 'csr1000v':
            data = self.get_metadata()
            return data['compute']['vmId']
        else:
            return '1111-1111'

    def get_instance_name(self):
        '''
        :return: returns instance name from metadata
        '''
        if deviceType == 'csr1000v':
            data = self.get_metadata()
            return data['compute']['name']
        else:
            return 'myMac'

if __name__ == "__main__":
    csr = metadata()
    metadata = csr.get_metadata()
    print(json.dumps(metadata, indent=2))

    for i, interface in enumerate(metadata["network"]["interface"]):
        print "Port %d" % i
        print "Mac is %s" % interface["mac"]
        for j, ip in enumerate(interface["ipv4"]["ipaddress"]):
            print "Public ip is %s" % ip["publicip"]
            print "Private ip is %s" % ip["ipaddress"]
        for s, subnet in enumerate(interface["ipv4"]["subnet"]):
            print "subnet is %s/%s" % (subnet["address"], subnet["prefix"])