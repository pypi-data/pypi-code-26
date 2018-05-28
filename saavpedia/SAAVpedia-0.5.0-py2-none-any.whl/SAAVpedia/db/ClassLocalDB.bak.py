#!/usr/bin/env python

################################################################################
# Copyright 2018 Young-Mook Kang <ymkang@thylove.org>
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
################################################################################

import requests, json
from ClassSQLite3 import SQLite3
from ClassSAAVpediaInputParser import SAAVpediaInputParser

class LocalDB(object) :

    def __init__(self):
        self.__itsSQLite = SQLite3()
        self.__itsInputParser = SAAVpediaInputParser()
        pass

    def __dataTupleToDictList(self, theTuple):
        theList = []
        for ithData in theTuple:
            theData = dict()
            idx = 0
            for jth in ithData:
                theData['col' + str(idx - 1)] = jth
                idx = idx + 1
                pass
            theList.append(theData)
            pass
        return theList

    def set(self, theInputText):
        self.__itsInputParser.set(theInputText)
        pass

    def fetchAll(self):
        theCommand = 'SELECT * FROM {0} WHERE {1}'.format('data', self.__itsInputParser.toSqlCondition())
        try:
            theRuturn = self.__itsSQLite.execute(theCommand)
            return theRuturn.fetchall()
        except:
            return []

    def setupToIdentifier(self):
        self.__itsInputParser.setupToIdentifier()
        pass

    def setupToRetrieval(self):
        self.__itsInputParser.setupToRetrieval()
        pass

    def open(self, theDBFilePath):
        return self.__itsSQLite.open(theDBFilePath)

    def getTitleAndDataLists(self):
        try:
            theData = self.fetchAll()
            print theData
            return theColumnNameList, changePosition(theData, theChangePositionList, isSQLite=True)
        except Exception as e:
            print str(e)
            return theColumnNameList, []

if __name__ == '__main__':
    theInput = "NDVDCAYLR\n" \
               "WLEAK\tQ7Z5L2\tNX_Q7Z5L2-3\n"

    theDB = LocalDB()
    theDB.open("/storage/SAAVPedia/PycharmProjects/SAAVpedia-v1/SAAVpedai.sqlite3.db")
    theDB.set(theInput)
    print len(theDB.fetchAll())

    theDB.set(theInput)
    theDB.setupToIdentifier()
    print len(theDB.fetchAll())

    theDB.set(theInput)
    theDB.setupToRetrieval()
    theTitle, theData = theDB.getTitleAndDataLists()

    print "\t".join(theTitle)
    for ith in theData:
        print "\t".join(ith)

    pass

