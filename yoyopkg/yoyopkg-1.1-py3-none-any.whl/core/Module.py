import sys

import os
import subprocess
from abc import ABC, abstractmethod
from typing import List

from src.core.InstallOptions import InstallOptions
from src.core.log import pdebug


def runCmdHide(cmd):
    return runCmd(cmd, False)

def runCmd(cmd, output=True):
    if not output:
        ret = subprocess.run([cmd], shell=True, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
        return ret.returncode == 0, ret.stdout, ret.stderr
    return subprocess.run([cmd], shell=True).returncode == 0

def gitClone(url, path, usecached=True, hideOutput=False) -> bool:
    pdebug('Cloning ' + url)
    if os.path.exists(path) and usecached:
        print('File ' + path + ' already exist and usecached is True, using cached file...')
        return True

    if os.path.exists(path):
        runCmd('rm -rf ' + path, False)

    success, out, err = runCmd('git clone ' + url + ' ' + path,False)

    if not success:
        print(err)

    return success

def downloadFile(url, path, usecached=True) -> bool:

    if os.path.isfile(path) and usecached:
        print('File ' + path + ' already exist and usecached is True, using cached file...')
        return True

    import requests

    try:
        link = url
        file_name = path
        with open(file_name, "wb") as f:
            print("Downloading %s" % file_name.split('/')[-1])
            response = requests.get(link, stream=True)
            total_length = response.headers.get('content-length')

            if total_length is None:  # no content length header
                f.write(response.content)
            else:
                dl = 0
                total_length = int(total_length)
                for data in response.iter_content(chunk_size=4096):
                    dl += len(data)
                    f.write(data)
                    done = int(50 * dl / total_length)
                    sys.stdout.write("\r[%s%s]" % ('=' * done, ' ' * (50 - done)) + ' ' + str(dl / 1000000) + 'mb/' + str(total_length / 1000000)+  'mb')
                    sys.stdout.flush()

            print('')
            return True
    except Exception as e:
        print('Error during download')

def uncompressArchive(path, to, usecached=True) -> bool:

    if os.path.exists(to) and usecached:
        print('File / Folder ' + to + ' already exist and usecached is True, using cached file...')
        return True

    import tarfile

    try:
        tar = tarfile.open(path, "r:gz")
        for tarinfo in tar:
            print("  Extracting %s (size: %db;)..." % (tarinfo.name, tarinfo.size))
            tar.extract(tarinfo, to)
    except Exception as e:
        print(e)
        return False
    return True

class CommandWheelInfo:
    def __init__(self, name):
        self.args = None
        self.cmd = None
        self.name = name
        self.toCheck = True

    def __str__(self):
        return self.name + '\t' + str(self.cmd) + '\n' + str(self.args) + '\nCheck: ' + str(self.toCheck)

class CommandWheel:
    def __init__(self):
        self.todo = list()

    def add(self, name, cmd, *args):
        info = CommandWheelInfo(name)
        info.args = args
        info.cmd = cmd
        self.todo.append(info)

    def addNoCheck(self, name, cmd, *args):
        info = CommandWheelInfo(name)
        info.args = args
        info.cmd = cmd
        info.toCheck = False
        self.todo.append(info)

    def run(self):
        for t in self.todo:
            if t.toCheck:
                ret = t.cmd(*t.args)
                if ret is False:
                    print('Error during ' + t.name)
                    return False
            else:
                t.cmd(*t.args)
        return True

    def __str__(self):
        out = ''
        for s in self.todo:
            out += str(s) + '\n\n'
        return out


class Module(ABC):
    @abstractmethod
    def __init__(self):
        pass

    @abstractmethod
    def name(self) -> str:
        pass

#Return list[str] required, list[list[str]] required one of
    @abstractmethod
    def requirements(self) -> List[str]:
        pass

    @abstractmethod
    def version(self):
        pass

    @abstractmethod
    def info(self):
        pass

    @abstractmethod
    def author(self):
        pass

    @abstractmethod
    def install(self, options: InstallOptions):
        pass

    @abstractmethod
    def upgrade(self, options: InstallOptions): # TODO a voir, ca peut etre chiant et pas le but
        pass

    @abstractmethod
    def uninstall(self, options: InstallOptions):
        pass

    @abstractmethod
    def verify(self, options: InstallOptions):
        success, err, out  = runCmd('which ' + self.name(), False)

        # if not success:
        #     print(err)
        return success

    def details(self):
        return 'Author: ' + self.author() + '\n\t\tVersion: ' + self.version() + '\n\t\tDesc: ' + self.info() + '\n\t\tRequirements: ' + str(self.requirements())