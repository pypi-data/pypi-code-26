import json
import os.path
import platform
import subprocess
from typing import List

from src.core.InstallOptions import InstallOptions
from src.core.Module import Module, CommandWheel, runCmd, runCmdHide, downloadFile
from src.core.Store import Store
from src.core.log import pwarning, perror


def createIfNotExistFiles(path):
    if not os.path.isfile(path):
        res = subprocess.run(['/usr/bin/install -D /dev/null ' + path], shell=True, stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE)

        if res.returncode != 0:
            raise RuntimeError(res.stderr)


class YModule(Module):

    def __init__(self, fileContent, path):
        self.path = path
        self.fc = fileContent
        self.options = None # type: InstallOptions
        self.vars = dict()
        self.initSystemVar()
        super().__init__()

    def initSystemVar(self):
        self.vars['OS'] = platform.system()

    def initOptionVar(self):
        self.vars['INSTALLDIR'] = self.options.install
        self.vars['DLDIR'] = self.options.dl
        self.vars['EXTRACTDIR'] = self.options.extract
        self.vars['MAINDIR'] = self.options.maindir

    def search(self, var):
        for l in self.fc:
            ls = l.split(' ')
            if ls[0] == var:
                if var in ['NAME', 'AUTHOR', 'VERSION']:
                    return ls[1]
                else:
                    return l[len(ls[0]):]
        raise RuntimeError('Var ' + var + ' not found in\n\n' + str(self.fc) + '\nat ' + self.path)

    def getBlock(self, var):
        i = 0
        while i < len(self.fc):
            l = self.fc[i]
            ls = l.split(' ')
            if ls[0] == var:
                i += 1
                start = i
                while i < len(self.fc):
                    cl = self.fc[i]
                    cls = cl.split(' ')
                    if cls[0] in ['[VERIFY]', '[UPGRADE]']:
                        return start, i
                    i += 1
                return start, i
            i += 1

        raise RuntimeError('Block ' + var + ' not found in\n\n' + str(self.fc) + '\nat ' + self.path)

    def analyzeBlock(self, block, startline):

        skip = False

        startline -= 1

        cw = CommandWheel()
        savedir = None

        for l in block:
            startline +=1
            if len(l) <= 0:
                continue

            ls = l.split(' ')

            i = 0
            for p in ls:
                if p[0] == '#':
                    vname = p[1:]
                    if vname in self.vars:
                        l = l.replace(ls[i], self.vars[vname])
                    else:
                        raise RuntimeError('[PARSING YOYO FILE] Var ' + p + ' has not been declared.\n\tTry LET ' + p + ' SOMEVALUE' + '\nat ' + self.path + ':' + str(startline))
                i += 1

            if ls[0] == '-':
                arg = ls[1]

                if arg == 'LOCAL':
                    skip = not self.options.isLocal

                if arg == '!LOCAL':
                    skip = self.options.isLocal

                elif arg == 'ELSE':
                    skip = not skip

                elif arg == 'END':
                    skip = False

                elif arg == 'TRUE':
                    skip = False

                elif arg == 'FALSE':
                    skip = True

                elif arg != self.vars['OS']:
                        skip = True

                continue

            if skip:
                continue

            elif ls[0] == '//':
                continue

            elif ls[0] == 'DEFAULT':
                if len(cw.todo) > 0:
                    pwarning('[PARSING YOYO FILE] DEFAULT called but there is previous instructions which are not gonna be called' + '\nat ' + self.path + ':' + str(startline))
                return None

            elif ls[0] == 'LET':
                vname = ls[1]
                val = l[5 + len(ls[1]):]
                self.vars[vname] = val

            elif ls[0] == 'PRINT':
                cw.addNoCheck('print', print, l[6:])

            elif ls[0] == 'SAVEDIR':
                savedir = os.getcwd()

            elif ls[0] == 'DL':
                if len(ls) < 4:
                    raise RuntimeError(
                        '[PARSING YOYO FILE] DL call without enough param (3min: url, to, name)\n\t' + l + '\nat ' + self.path + ':' + str(startline))
                url = ls[1]
                to = ls[2]
                name = ls[3]
                cw.add('dl', downloadFile, url, to + name, self.options.useCached)


            elif ls[0] == 'RESTOREDIR':
                if savedir is None:
                    raise RuntimeError('[PARSING YOYO FILE] Tryying to RESTOREDIR without SAVEDIR before\n\t' + l + '\nat ' + self.path + ':' + str(startline))
                cw.add('changedir', os.chdir, savedir)

            elif ls[0] == 'CMD':
                nocheck = False
                hide = False
                try:
                    if ls[1] == 'NOCHECK':
                        del ls[1]
                        l = l.replace(' NOCHECK', '', 1)
                        nocheck = True

                    if ls[1] == 'HIDE':
                        del ls[1]
                        l = l.replace(' HIDE', '', 1)
                        hide = True

                    if ls[1] == 'NOCHECK':
                        del ls[1]
                        l = l.replace(' NOCHECK', '', 1)
                        nocheck = True


                    cmd = l[4:]
                    if nocheck:
                        if hide:
                            cw.addNoCheck('cmd', runCmdHide, cmd)
                        else:
                            cw.addNoCheck('cmd', runCmd, cmd)
                    else:
                        if hide:
                            cw.add('cmd', runCmdHide, cmd)
                        else:
                            cw.add('cmd', runCmd, cmd)
                except:
                    raise RuntimeError('[PARSING YOYO FILE] CMD without argument\n' + l + '\nat ' + self.path + ':' + str(startline))


            else:
                raise RuntimeError('[PARSING YOYO FILE] Unknown instruction:\n' + l + '\nat ' + self.path + ':' + str(startline))


        return cw

    def name(self) -> str:
        return self.search('NAME')

    def requirements(self) -> List[str]:
        ret = self.search('REQ')
        return ret.split(',')

    def version(self):
        return self.search('VERSION')

    def info(self):
        return self.search('INFO')

    def author(self):
        return self.search('AUTHOR')

    def install(self, options: InstallOptions):

        self.options = options
        self.initOptionVar()

        start, end = self.getBlock('[INSTALL]')
        cw = self.analyzeBlock(self.fc[start: end], start)

        if cw is None:
            return super(YModule, self).install(options)

        print(str(cw))
        cw.run()
        return False
        # return cw.run()


    def upgrade(self, options: InstallOptions):
        self.options = options
        self.initOptionVar()
        pass

    def uninstall(self, options: InstallOptions):
        self.options = options
        self.initOptionVar()
        pass

    def verify(self, options: InstallOptions):
        self.options = options
        self.initOptionVar()
        start, end = self.getBlock('[VERIFY]')
        cw = self.analyzeBlock(self.fc[start: end], start)

        if cw is None:
            return super(YModule, self).verify(options)

        return cw.run()


class YLocal(Store):
    def __init__(self, options):
        super().__init__(options)
        self.saveloc = self.options.store + 'y_local/default.json'

        p = os.path.realpath(__file__)
        p = p.replace('stores/YLocal.py', '')
        p = p + 'ymodules/'

        self.paths = [self.options.store + 'y_local/modules/', p]
        self.modules = dict()  # Name / Module
        self.modulesPath = dict()  # Name / Module

        createIfNotExistFiles(self.saveloc)

        self.getFromFile()

    def updatePath(self, path):

        for filename in os.listdir(path):
            if '__' in filename:
                continue

            lines = [line.rstrip('\n') for line in open(path + '/' + filename)]

            tmpModule = YModule(lines, path + '/' + filename)
            self.modules[tmpModule.name()] = tmpModule

            self.modulesPath[tmpModule.name()] = path + '/' + filename

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
        return 'y_local'

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
                pwarning('[y_local] Store module file is empty you may need to run\n\tyoyo update')
            return

        data = None

        try:
            with open(path) as f:
                data = json.load(f)

        except Exception as e:
            perror(e)
            perror(
                '[y_local] During loading JSON from store module file ' + path + '\nSeem corrupted.\nrun yoyo update to recreate it')

        try:
            self.paths = data['paths']
            # self.modulesPath = data['paths']
        except Exception:
            pwarning('[y_local] y_local store path of ymodule not set.\nRun yoyo add y_local PATH')

        self.update()
