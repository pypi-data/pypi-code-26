import os
import subprocess


def createIfNotExistFiles(path):
    if not os.path.isfile(path):
        res = subprocess.run(['/usr/bin/install -D /dev/null ' + path], shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        if res.returncode != 0:
            raise RuntimeError(res.stderr)


class InstallOptions:
    maindir = None # type: str
    store = None # type: str
    cache = None # type: str
    dl = None # type: str
    extract = None # type: str
    install = None # type: str

    isLocal = False
    isForce = False
    useCached = True
    isUpdateCmd = False

    def setStore(self, path):
        self.store = self.maindir + path

    def setCache(self, path):
        self.cache = self.maindir + path

    def setDL(self, path):
        self.dl = self.cache + path

    def setExtract(self, path):
        self.extract = self.cache + path

    def setInstall(self, path):
        self.install = self.maindir + path

    def createDirs(self):
        createIfNotExistFiles(self.maindir + '.empty')
        createIfNotExistFiles(self.store + '.empty')
        createIfNotExistFiles(self.cache + '.empty')
        createIfNotExistFiles(self.cache + '.empty')
        createIfNotExistFiles(self.dl + '.empty')
        createIfNotExistFiles(self.extract + '.empty')
        createIfNotExistFiles(self.install + '.empty')
