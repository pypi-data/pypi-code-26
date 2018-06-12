#!/usr/bin/env python
# -*- encoding:utf-8 -*-
import requests
import csv
import json
import sys
import os
import configparser
import re

class API:

    def __init__(self, name=None, endPoint=None):
        self.setName(name)
        self.setEndPoint(endPoint)
        self.__queryResult = {}

    def setName(self, name):
        self.__name = name

    def name(self):
        return self.__name

    def setEndPoint(self, endPoint):
        self.__endPoint = endPoint

    def endPoint(self):
        return self.__endPoint

    def query(self, variable, value):
        url = "%s?%s=%s" % (self.endPoint(), variable, value)
        try:
            self.__queryResult = requests.get(url).json()
            return True
        except requests.ConnectionError:
            return False

    def queryResult(self, key):
        if str(key) in self.__queryResult:
            return self.__queryResult[key]

    def load(self, infosList):
        setters = [self.setName, self.setEndPoint, self.setDefaultQueryLabel, self.setResultKey]
        for z in zip(infosList, setters):
            # this is: setters[i](infosList[i])
            z[1](z[0])

class File:

    def __init__(self, name, content, directory):
        self.setName(name)
        self.setContent(content)
        self.setDirectory(directory)

    def setName(self, name):
        self.__name = str(name)

    def name(self):
        return self.__name

    def setContent(self, content):
        self.__content = content

    def content(self):
        return self.__content

    def setDirectory(self, directory):
        self.__directory = directory

    def directory(self):
        return self.__directory

    def URL(self):
        return "%s/%s" % (self.directory(), self.name())

    def saveCSV(self):
        content = self.content()
        keys = list(content[0].keys())
        keys.sort()
        csvContent = [keys]
        for c in content:
            row = [str(c[k]) for k in keys]
            csvContent.append(row)
        with open(self.URL() + ".csv", 'w', newline='') as file:
            writer = csv.writer(file, delimiter=',', quoting=csv.QUOTE_MINIMAL)
            writer.writerows(csvContent)

    def saveJSON(self):
        content = self.content()
        url = self.URL() + ".json"
        with open(url, 'w') as file:
            json.dump(content, file, indent=True)

    def saveTXT(self):
        content = ";\n".join([str(a) for a in self.content()])
        url = self.URL() + ".txt"
        with open(url, 'w') as file:
            file.write(content)
        return

class Application:

    def __init__(self, name, version, author, site, licensePath, configPath, docPath):
        self.setName(name)
        self.setVersion(version)
        self.setAuthor(author)
        self.setSite(site)
        self.setLicensePath(licensePath)
        self.setDocPath(docPath)
        self.__cmdArgs = sys.argv[1:]
        self.__apisIni = configparser.ConfigParser()
        self.__apisIni.read(configPath)

    def setName(self, name):
        self.__name = str(name)

    def name(self):
        return self.__name

    def setVersion(self, version):
        self.__version = str(version)

    def version(self):
        return self.__version

    def setAuthor(self, author):
        self.__author = str(author)

    def author(self):
        return self.__author

    def setSite(self, site):
        self.__site = str(site)

    def site(self):
        return self.__site

    def setLicensePath(self, path):
        self.__licensePath = str(path)

    def licensePath(self):
        return self.__licensePath

    def setDocPath(self, path):
        self.__docPath = str(path)

    def docPath(self):
        return self.__docPath

    def choices(self, choiceList, msg="Choice number: "):
        for a in range(len(choiceList)):
            print("%s\t-\t%s" % (a, choiceList[a]))

        number = input("\n%s" % msg)
        if number.isnumeric() and int(number) in range(len(choiceList)):
            return choiceList[int(number)]

    def ask(self, msg, trueConditionString):
        answer = input(msg)
        if answer.lower().replace("\s", '') == trueConditionString.lower().replace("\s", ''):
            return True
        return False

    def registeredAPIs(self):
        apis = self.__apisIni.sections()
        apisObjDict = {}
        for a in apis:
            name = self.__apisIni[a].get("apiname")
            endPoint = self.__apisIni[a].get("apiendpoint")
            apisObjDict[a] = API(name, endPoint)
        return apisObjDict

    def _lic(self):
        os.system("less %s" % self.licensePath())

    def _version(self):
        print("%s version: %s" % (self.name(), self.version()))

    def _add(self):
        apiInfo = self.__cmdArgs[1:]
        if len(apiInfo) == 2:
            apiName = re.sub(r"[\'|\"]", "", apiInfo[0])
            apiEndPoint = re.sub(r"[\'|\"]", "", apiInfo[1])
            if apiName not in self.registeredAPIs():
                self.__apisIni[apiName] = {"apiName": apiName, "apiEndPoint": apiEndPoint}
                with open("apis.ini", "w") as apiFile:
                    self.__apisIni.write(apiFile)
                    print("API '%s' was successfuly registered!" % apiName)
            else:
                print("API '%s' already registered" % apiName)
        else:
            print("API not registered.\n"
                  "The -add command need 2 arguments (apiName and apiEndPoint). %s given..." % len(apiInfo))

    def _remove(self):

        cmdArgs = self.__cmdArgs[1:]
        if cmdArgs:
            apiToRemove = cmdArgs[0]
            if apiToRemove in self.__apisIni:
                self.__apisIni.remove_section(apiToRemove)
                with open("apis.ini", "w") as apiFile:
                    self.__apisIni.write(apiFile)
                print("%s was removed." % apiToRemove)
            else:
                print("API not registered.")
        else:
            print("API name argument missing.")

    def _list(self):
        registeredAPIs = self.registeredAPIs()
        print("%s registered APIs:" % len(registeredAPIs))
        [print(r) for r in self.registeredAPIs()]

    def save(self, name, result):
        formatLoop = True
        while formatLoop:
            print("Available file formats:")
            fileObj = File(name, result, os.getcwd())
            formats = {".csv": fileObj.saveCSV, ".json": fileObj.saveJSON, ".txt": fileObj.saveTXT}
            formatKeys = list(formats.keys())
            formatKeys.sort()
            key = self.choices(formatKeys, "Choose format number: ")
            if key:
                pathLoop = True
                while pathLoop:
                    path = input("Path name: ")
                    if os.path.exists(path):
                        fileObj.setDirectory(path)
                        formats[key]()
                        print("File successfully saved!")
                        pathLoop = False
                    else:
                        print("This path doenst exist, try another one.")
                formatLoop = False
            else:
                print("Invalid number, try again.")

    def _query(self):
        queryInfo = self.__cmdArgs[1:]
        if len(queryInfo) == 4:
            apiName = re.sub(r"[\'|\"]", "", queryInfo[0])
            apiQueryVar = re.sub(r"[\'|\"]", "", queryInfo[1])
            queryArg = re.sub(r"[\'|\"]", "", queryInfo[2])
            resultKey = re.sub(r"[\'|\"]", "", queryInfo[3])
            print("Looking for '%s'..." % apiName)
            apisObj = self.registeredAPIs()
            if apiName in apisObj:
                os.system("clear")
                print("Using: %s" % apiName)
                print("Searching for '%s'..." % queryArg)
                api = apisObj[apiName]
                if api.query(apiQueryVar, queryArg):
                    result = api.queryResult(resultKey)
                    print("The query returned %s items!" % len(result))
                    if result:
                        [print(str(r)) for r in result]
                        if self.ask("Dow you want to save this result, [y/n]?", "y"):
                            self.save(queryArg, result)
                else:
                    print("Connection error.")
            else:
                print("Could not found '%s', use -add command to add a new API." % apiName)
        else:
            print(
                "The -query command need 4 arguments (apiName, apiQueryVar, queryArg and resultKey), %s given..." % len(
                    queryInfo))
        return

    def _help(self):
        print("\nAuthor: %s.\tGitHub: %s" % (self.author(), self.site()))
        commands = self.commands()
        print("Available commands of %s %s:\n" % (self.name(), self.version()))
        commandKeys = list(commands.keys())
        commandKeys.sort()
        [print("%s\t-\t%s" % (k, commands[k][1])) for k in commandKeys]

    def _doc(self):
        os.system("less %s" % self.docPath())

    def commands(self):
        commands = {"-version": (self._version, "Shows the current program version."),
                    "-license": (self._lic, "Shows the used license."),
                    "-add": (self._add,
                             "Adds a new API. Need arguments: apiName, apiEndpoint. Separe the arguments by space, use commas."),
                    "-query": (self._query,
                               "Do a query in a registered API. Need arguments: apiName, apiQueryVar, apiQueryArg, resultKey. Separe the arguments by space, use commas."),
                    "-remove": (self._remove, "Removes a registered API. Need arguments: apiName. Use commas."),
                    "-list": (self._list, "Shows a list of registered APIs."),
                    "-doc": (self._doc, "Shows the documentation.")}
        return commands

    def exec(self):
        commands = self.commands()

        if self.__cmdArgs:
            cmd = self.__cmdArgs[0]
            if cmd in commands:
                commands[cmd][0]()
            else:
                print("'%s' is not a command!" % cmd)
                self._help()
        else:
            self._help()

path = "/".join(os.path.dirname(__file__).split("/")[0:-1])

AUTHOR = "Odilon Vieira"
AUTHOR_EMAIL = "odilon.vieira95@gmail.com"
AUTHOR_PAGE = "https://github.com/OdilonVieira"
NAME = "apigett"
APP_URL = "https://github.com/OdilonVieira/apigett"
VERSION = "1.2.6"
LICENSE= "GNU"
LICENSE_DOC = "%s/LICENSE" % path
DOC_PATH = "%s/README.md" % path
API_PATH = "%s/apis.ini" % path
SHORT_DESCRIPTION = "Gets JSON-based API query result and saves them in a JSON, CSV or TXT file format."
LONG_DESCRIPTION = "More informations in: %s" % APP_URL
def run():
    app = Application(NAME,VERSION,AUTHOR,AUTHOR_PAGE,LICENSE_DOC,API_PATH,DOC_PATH)
    app.exec()