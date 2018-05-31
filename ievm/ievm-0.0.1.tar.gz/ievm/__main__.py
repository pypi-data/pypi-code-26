import requests
import re
import argparse
import os
import hashlib
import functools


VMPAGE = "https://developer.microsoft.com/en-us/microsoft-edge/tools/vms/"
FILELIST = 'https://developer.microsoft.com/en-us/microsoft-edge/api/tools/vms/?id='
fileMap = {}
md5Map = {}

def getVmId():
    r = requests.get(VMPAGE)
    vmId = re.search(r'edgePortal.vmsId = (\d+)', str(r.content)).group(1)
    r.close()
    return vmId

def getFilelistJson(vmId):
    o = requests.get(FILELIST+vmId)
    result = o.json()
    o.close()
    return result


def prepare():
    result = getFilelistJson(getVmId())
    for version in result:
        versionArgs = re.search(r'(\w+)[ ]+on[ ]+(\w+)', version['name'])
        versionName = versionArgs.group(1) + '-' + versionArgs.group(2)
        versionName = versionName.lower()
        fileMap[versionName] = {}
        md5Map[versionName] = {}
        for software in version["software"]:
            softwareArgs = re.search(r'^(\w+)[ ]*', software['name'])
            softwareName = softwareArgs.group(1).lower()
            for f in software['files']:
                if f.get('md5') != None and f.get('url') != None:
                    fileMap[versionName][softwareName] = f['url']
                    md5Map[versionName][softwareName] = f['md5']
                    break

def md5sum(path, block_size=2**20):
    md5 = hashlib.md5()
    with open(path, 'rb') as f:
        while True:
            data = f.read(block_size)
            if not data:
                break
            md5.update(data)
    return md5.hexdigest()

def main():
    prepare()
    parser = argparse.ArgumentParser(description='download ie vms')
    versionHelp = 'valid versions are: ' + ', '.join(fileMap.keys())
    parser.add_argument('-v', '--version', type=str, help=versionHelp)

    typeSet = set()
    types = map(lambda x: x.keys(), fileMap.values())
    functools.reduce(lambda x, y: \
            x and typeSet.update(x) and y and typeSet.update(y), types)
    vmTypeHelp = 'valid types are: ' + ', '.join(list(typeSet))
    parser.add_argument('-t', '--type', type=str, help=vmTypeHelp)
    parser.add_argument('-p', '--path', type=str, help='save path')
    args = parser.parse_args()
    if args.type == None or args.version == None or args.path == None:
        parser.print_help()
        exit(0)
    url = fileMap[args.version][args.type]
    if not os.path.isfile(args.path):
        args.path = os.path.join(args.path, url.split('/')[-1])
    print("downloading " + url + " to "+args.path + "...")
    r = requests.get(url, stream=True)
    with open(args.path, 'wb+') as f:
        for chunk in r.iter_content(chunk_size=4096):
            if chunk:
                f.write(chunk)
    r.close()
    print("done. Now checking md5...")
    r = requests.get(md5Map[args.version][args.type])
    md5 = r.content.strip().lower()
    real_md5 = md5sum(args.path)
    if md5 != real_md5:
        print("md5 check fail: expected "+md5+" get "+real_md5)
    else:
        print("checksum ok")

if __name__ == '__main__':
    main()
