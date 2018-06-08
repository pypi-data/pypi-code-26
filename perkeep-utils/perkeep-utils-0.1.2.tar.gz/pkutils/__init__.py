#
# -*- coding: utf-8 -*-
# python-perkeep-utils
# Copyright (C) 2018  Markus Peröbner
#
import datetime
import hashlib
import json
from . import pkhttp
import random

web_client_config = None

def query(opts):
    web_client_config = get_web_client_config()
    with pkhttp.urlopen(web_client_config['searchRoot'] + 'camli/search/query', data=bytearray(json.dumps(opts), 'utf-8')) as req:
        return json.load(req)

def download(ref):
    return pkhttp.urlopen('/ui/download/{}/blob'.format(ref))

def persist(attributes):
    ref = create_permanode()
    for key, value in attributes.items():
        if(isinstance(value, list)):
            for v in value:
                add_permanode_attribute(ref, key, v)
        else:
            set_permanode_attribute(ref, key, value)
    return ref

def create_permanode(rand=None):
    if(rand is None):
        rand = random.random()
    claim = sign({
        'camliType': 'permanode',
        'random': rand,
    })
    return upload_claim(claim)

def set_permanode_attribute(ref, key, value):
    claim = sign({
        'camliType': 'claim',
        'permaNode': ref,
        'claimType': 'set-attribute',
        'claimDate': format_claim_datetime(datetime.datetime.utcnow()),
        'attribute': key,
        'value': value,
    })
    return upload_claim(claim)

def add_permanode_attribute(ref, key, value):
    claim = sign({
        'camliType': 'claim',
        'permaNode': ref,
        'claimType': 'add-attribute',
        'claimDate': format_claim_datetime(datetime.datetime.utcnow()),
        'attribute': key,
        'value': value,
    })
    return upload_claim(claim)

def format_claim_datetime(dt):
    millisecond = dt.microsecond / 1000
    return '{}.{:03.0f}Z'.format(dt.strftime('%Y-%m-%dT%H:%M:%S'), millisecond)

def sign(data):
    '''Signs an dict object.
    '''
    config = get_web_client_config()
    data['camliSigner'] = config['signing']['publicKeyBlobRef']
    clear_text = '{"camliVersion":1,\n' + json.dumps(data, indent='\t')[len('{\n'):]
    with pkhttp.urlopen(config['signing']['signHandler'], data='json={}'.format(clear_text).encode('utf-8'), content_type='application/x-www-form-urlencoded') as req:
        return req.read()

def upload(blob, file_name, path='/ui/?camli.mode=uploadhelper'):
    boundary, form = build_multipart_form('ui-upload-file-helper-form', blob, file_name=file_name)
    with pkhttp.urlopen(path, data=form, content_type='multipart/form-data; boundary={}'.format(boundary)) as req:
        req.info()
        body = json.load(req)
    return body['got'][0]['fileref']

def upload_claim(blob):
    m = hashlib.sha1()
    m.update(blob)
    ref = 'sha1-{}'.format(m.hexdigest())
    boundary, form = build_multipart_form(ref, blob)
    with pkhttp.urlopen('/bs-and-maybe-also-index/camli/upload', data=form, content_type='multipart/form-data; boundary={}'.format(boundary)) as req:
        body = json.load(req)
    return body['received'][0]['blobRef']

def build_multipart_form(form_name, blob, file_name=None, content_type='application/octet-stream'):
    '''Formats a blob into a multipart form.

    blob shoud have type bytes.

    -----------------------------6930946476218338041418917799
    Content-Disposition: form-data; name="ui-upload-file-helper-form"; filename="hello_world.txt"
    Content-Type: text/plain

    Hello World!

    -----------------------------6930946476218338041418917799--
    '''
    nl = b'\r\n'
    boundary = '-----------------------------6930946476218338041418917799'
    fragments = [
        b'--',
        boundary.encode('ascii'),
        nl,
        b'Content-Disposition: form-data; name="',
        form_name.encode('ascii'),
        b'"',
    ]
    if(not file_name is None):
        fragments = fragments + [
            b'; filename="',
            file_name.encode('ascii'),
            b'"',
        ]
    fragments = fragments + [
        nl,
        b'Content-Type: ',
        content_type.encode('ascii'),
        nl,
        nl,
        blob,
        nl,
        b'--',
        boundary.encode('ascii'),
        b'--',
    ]
    return boundary, b''.join(fragments)

def get_web_client_config():
    global web_client_config
    if(web_client_config is None):
        with pkhttp.urlopen('/ui/?camli.mode=config') as req:
            web_client_config = json.load(req)
    return web_client_config
