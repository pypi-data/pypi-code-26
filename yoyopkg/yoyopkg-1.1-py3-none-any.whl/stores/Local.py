import sys

import importlib
import json
import os
import os.path
import subprocess

from src.core.Store import Store
from src.core.log import pwarning, perror


def createIfNotExistFiles(path):
    if not os.path.isfile(path):
        res = subprocess.run(['/usr/bin/install -D /dev/null ' + path], shell=True, stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE)

        if res.returncode != 0:
            raise RuntimeError(res.stderr)


class Local(Store):
    def __init__(self, options):
        super().__init__(options)
        self.saveloc = self.options.store + 'local/default.json'

        p = os.path.realpath(__file__)
        p = p.replace('stores/Local.py', '')
        p = p + 'modules/'

        self.paths = [self.options.store + 'local/modules/', p]
        # self.paths = ['/run/netsop/u/home-sam/home/dwyzlic/projects/EXPERIMENTS/install/modules']
        self.modules = dict()  # Name / Module
        self.modulesPath = dict()  # Name / Module

        createIfNotExistFiles(self.saveloc)

        self.getFromFile()

    def updatePath(self, path):

        old_path = sys.path
        sys.path = sys.path[:]
        sys.path.insert(0, path)

        for filename in os.listdir(path):
            if '__' in filename:
                continue

            if not filename.endswith('.py'):
                continue

            spec = importlib.util.spec_from_file_location(path + '/' + filename, path + '/' + filename)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)

            tmpModule = module.get()
            self.modules[tmpModule.name()] = tmpModule

            self.modulesPath[tmpModule.name()] = path + '/' + filename

        sys.path = old_path

    def update(self):
        self.modules = dict()

        for p in self.paths:
            try:
                self.updatePath(p)
            except Exception as e:
                pwarning('Error during parsing folder ' + p + '\n' + str(e))
                continue

        self.saveToFile()

    def getAll(self):
        out = []
        for k, i in self.modules.items():
            out.append(k)

        return out

    def print(self):
        for k, i in self.modules.items():
            print(k + ' ' + i)

    def remove(self, path):
        pass

    def name(self):
        return 'local'

    def add(self, path):
        if os.path.isfile(path):
            if not path in self.paths:
                self.paths.append(path)
            return True
        else:
            return False

    def __getitem__(self, item):
        return self.modules[item]

    def saveToFile(self, path=None):
        if path is None:
            path = self.saveloc

        out = dict()
        out['paths'] = self.paths
        out['modules'] = self.modulesPath

        with open(path, 'w') as outfile:
            json.dump(out, outfile)

    def getFromFile(self, path=None):
        if path is None:
            path = self.saveloc

        if os.path.getsize(path) <= 0:
            if self.options.isUpdateCmd:
                pwarning('[local] Store module file is empty you may need to run\n\tyoyo update')
            return

        data = None

        try:
            with open(path) as f:
                data = json.load(f)

        except Exception as e:
            print(e)
            perror(
                '[local] During loading JSON from store module file ' + path + '\nSeem corrupted.\nrun yoyo update to recreate it')

        try:
            self.paths = data['paths']
            # self.modulesPath = data['paths']
        except:
            pwarning('[local] Local store path of module not set.\nRun yoyo add local PATH')

        self.update()
