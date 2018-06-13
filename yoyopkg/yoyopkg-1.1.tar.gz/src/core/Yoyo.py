import json
import os
import subprocess
from typing import Dict

from src.core.InstallOptions import InstallOptions
from src.core.Module import Module
from src.core.Store import Store
from src.core.log import pinfo, pdebug, pwarning, perror, psuccess, Fore
from src.stores.Local import Local
from src.stores.YLocal import YLocal


class InfoEncoder(json.JSONEncoder):
    def default(self, o):
        wanted = dict()
        wanted['store'] = o.store
        wanted['installed'] = o.installed

        return wanted


class Info:
    store = ''
    installed = False
    module = None  # type: Module

    def __str__(self):
        return self.store + '\t-\t' + (Fore.GREEN + 'Installed' if self.installed else Fore.RED + 'Not installed')


def createIfNotExistFiles(path):
    if not os.path.isfile(path):
        res = subprocess.run(['/usr/bin/install -D /dev/null ' + path], shell=True, stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE)

        if res.returncode != 0:
            raise RuntimeError(res.stderr)


class Yoyo:
    def __init__(self, scriptPath, local=False, force=False, nocache=False, showWarningModuleFileEmpty=True):
        self.allModules = dict()  # type: Dict[str, Info]  # Module name, store name TODO maybe change to store, loc, name (AND THEREFORE ALLOW MULTIPLE SAME NAME) // but to complicated
        self.stores = dict()  # type: Dict[str, Store]

        self.installOptions = InstallOptions()
        self.installOptions.maindir = os.path.expanduser('~/.yoyo/')
        self.installOptions.setStore('store/')
        self.installOptions.setCache('cache/')
        self.installOptions.setDL('dl/')
        self.installOptions.setExtract('extract/')
        self.installOptions.setInstall('installed/')

        self.installOptions.isLocal = local
        self.installOptions.isForce = force
        self.installOptions.useCached = not nocache

        self.showWarningModuleFileEmpty = showWarningModuleFileEmpty

        self.installOptions.createDirs()

        self.defaultModuleSaveLocation = self.installOptions.maindir + 'modules.json'
        self.defaultStoreSaveLocation = self.installOptions.maindir + 'stores.json'

        createIfNotExistFiles(self.defaultModuleSaveLocation)
        createIfNotExistFiles(self.defaultStoreSaveLocation)

        self.initDefaultStores()

        self.getAllModulesFromFile()

    def initDefaultStores(self):
        try:
            s = Local(self.installOptions)
            self.stores[s.name()] = s
        except Exception as e:
            perror('Error while loading default store local:\n' + str(e))

        try:
            s = YLocal(self.installOptions)
            self.stores[s.name()] = s
        except Exception as e:
            perror('Error while loading default store ylocal:\n' + str(e))

    def addStore(self, name, path):
        pass

    def getStore(self, name):
        return self.stores[name]

    def getAllModules(self):
        # Network not working ATM (else: wget url /getModules and return JSON: Name, URL
        return self.allModules

    def printAllModules(self):
        print('[MODULES]:')
        pwarning('\tNAME\t-\tSTORE\t\tSTATUS')
        for k, i in self.allModules.items():
            pdebug('\t' + k + '\t-\t' + str(i))

    def printDetails(self):
        print('[MODULES]:')
        pwarning('\tNAME\t-\tSTORE\t\tSTATUS')
        for k, i in self.allModules.items():
            pinfo('\t' + k + '\t-\t' + str(i))
            pdebug('\t\t' + i.module.details())
            pdebug('\n')

    def update(self):
        print('[UPDATING]')

        pinfo('[UPDATE] Found ' + str(len(self.stores)) + ' stores')
        for s in self.stores:
            print('\t' + s)

        for s in self.stores:
            pdebug('[UPDATE] - Store ' + s)
            try:
                self.stores[s].update()
            except Exception as e:
                perror('Error during update of store ' + s + '\n' + str(e))
                continue

            tmp = None

            try:
                tmp = self.stores[s].getAll()
            except Exception as e:
                perror('Error during \'getAll\' of store ' + s + '\n' + str(e))
                continue

            for m in tmp:
                info = Info()

                info.module = self.stores[s][m]
                info.installed = False
                info.store = s

                self.allModules[m] = info

        print('[UPDATE] Found ' + str(len(self.allModules)) + ' modules')
        print('[UPDATING] Done')

        self.saveAllModuleToFile()

        installed = 0
        for m in self.allModules:
            ret = None

            try:
                ret = self.allModules[m].module.verify(self.installOptions)
            except Exception as e:
                perror(e)

            self.allModules[m].installed = ret
            if ret:
                installed += 1

        pinfo(str(installed) + '/' + str(len(self.allModules)) + ' modules installed')
        self.saveAllModuleToFile()

    def install(self, name, numTab=0):

        pinfo('\t' * numTab + '[INSTALL] ' + name)

        try:
            m = self.searchModule(name).module
        except:
            perror('\t' * numTab + '[INSTALL] Module not found in availables modules: ' + name)
            return False

        if self.allModules[name].installed and not self.installOptions.isForce:
            pwarning('Module ' + name + ' already installed.\n\tUse yoyo install ' + name + ' --force to reinstall it')
            return True

        req = m.requirements()

        pinfo('\t' * numTab + '[REQUIREMENTS] ' + str(req))

        for r in req:
            pdebug('\t' * numTab + '[REQUIREMENTS] Testing ' + r)

            rModule = None

            try:
                rModule = self.searchModule(r).module
            except:
                pwarning('\t' * numTab + '[REQUIREMENTS] Not found in availables modules: ' + r)

                pdebug('\t' * numTab + '\tTryiing \'which\'')

                res = subprocess.run(['which ' + r], shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

                if res.returncode != 0:
                    perror('\t' * numTab + '\tNot found with which')
                    return False

                psuccess('\t' * numTab + '\tFound ' + r + ' !')
                continue

            if not rModule.verify(self.installOptions):
                tmpResult = self.install(r, numTab + 1)

                if not tmpResult:
                    perror(
                        '\t' * numTab + '\n[REQUIREMENTS] Error during installation of requirements ' + r + '.\n\tCan\'t install ' + name)
                    return False

            psuccess('\t' * numTab + '\tFound ' + r + ' !')

        if not self.installOptions.isForce:
            if m.verify(self.installOptions):
                pwarning(
                    '[WARNING] Module already installed ' + name + '\n\tUse yoyo install ' + name + ' --force to install')
                return True

        pinfo('\t' * numTab + '[INSTALLING] ' + name)

        result = None

        try:
            result = m.install(self.installOptions)
        except Exception as e:
            perror(e)

        if not result:
            perror('\t' * numTab + '[INSTALL] Error during installation of ' + name)
            return False

        psuccess('\t' * numTab + '[INSTALL] Successfully installed ' + name)
        # Add to installed modules

        self.allModules[name].installed = True

        self.saveAllModuleToFile()

        return True

    def saveAllModuleToFile(self, path=None):
        if path is None:
            path = self.defaultModuleSaveLocation

        with open(path, 'w') as outfile:
            json.dump(self.allModules, outfile, cls=InfoEncoder)

    def getAllModulesFromFile(self, path=None):

        if path is None:
            path = self.defaultModuleSaveLocation

        if os.path.getsize(path) <= 0:
            if self.showWarningModuleFileEmpty:
                if self.installOptions.isUpdateCmd:
                    pwarning('[' + path + '] Module file is empty you may need to run\n\tyoyo update')
            return

        data = None

        try:
            with open(path) as f:
                data = json.load(f)

        except Exception as e:
            print(e)
            print(
                '[ERROR] During loading JSON from module file ' + path + '\nSeem corrupted.\nrun yoyo update to recreate it')

        for m in data:
            info = Info()
            info.store = data[m]['store']
            info.installed = data[m]['installed']

            try:
                info.module = self.stores[info.store][m]
                self.allModules[m] = info
            except:
                print('[WARNING] Store ' + info.store + ' dont have module ' + m + ' \n\trun yoyo update')

    def remove(self, name):
        pass

    def info(self, name):
        pass

    def verify(self, name=None):
        pinfo('[VERIFY] ' + ('All' if name is None else name))

        pwarning('\tNAME\t-\tSTORE\t\tSTATUS')

        if name is not None:
            rModule = None
            try:
                rModule = self.searchModule(name).module
            except Exception:
                perror('[VERIFY] Not found in availables modules: ' + name)
                return False

            ret = None

            try:
                ret = rModule.verify(self.installOptions)
            except Exception as e:
                perror(e)

            self.allModules[name].installed = ret
            pdebug('\t' + name + '\t-\t' + str(self.allModules[name]))
            self.saveAllModuleToFile()
            return ret

        else:
            for m in self.allModules:
                ret = None

                try:
                    ret = self.allModules[m].module.verify(self.installOptions)
                except Exception as e:
                    perror(e)

                self.allModules[m].installed = ret

                pdebug('\t' + m + '\t-\t' + str(self.allModules[m]))

            self.saveAllModuleToFile()

            return True

    def searchModule(self, name):
        out = False
        try:
            return self.allModules[name]
        except:
            perror('Module ' + name + ' not found, searching stores...')
            for s in self.stores:
                if out:
                    break
                try:
                    self.stores[s][name]
                    psuccess('Found in store ' + s + ' !\nRunning yoyo update')
                    self.update()
                    return self.allModules[name]
                except:
                    pass
            if not out:
                perror('Not found in stores')
        raise RuntimeError()

    def upgrade(self, name):
        pass

    def upgradeAll(self):
        pass

    def getAllModulesInstalled(self):
        pass

    def tryToInstallWithApt(self, name):
        rep = ''

        while rep not in ['Y', 'y', 'N', 'n']:
            rep = str(input('Try to install ' + name + 'with apt ? Y/N'))

        if rep in ['Y', 'y']:
            ret = subprocess.run(['sudo apt install ' + name], shell=True)

            if ret.returncode != 0:
                print('Error during installation of ' + name + ' with apt')
                return False

        return True
