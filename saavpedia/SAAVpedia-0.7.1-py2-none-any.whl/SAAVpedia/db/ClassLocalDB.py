#!/usr/bin/env python

################################################################################
# Copyright 2017-2018 Young-Mook Kang <ymkang@thylove.org>
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
from assign import *

class LocalDB(object) :

    def __init__(self):
        self.__itsSQLite = SQLite3()
        self.__itsInputParser = SAAVpediaInputParser()
        self.__itsInputText = ''
        self.__itsHeader = []
        self.__itsData = []
        self.__isChanged = True
        pass

    def __dataTupleToDictList(self, theTuple):
        theList = []
        for ithData in theTuple:
            theData = dict()
            idx = 0
            for jth in ithData:
                theData['col' + str(idx)] = jth
                idx = idx + 1
                pass
            theList.append(theData)
            pass
        return theList

    def set(self, theInputText):
        self.__isChanged = True
        self.__itsInputText = theInputText
        self.__itsInputParser.set(theInputText)
        pass

    def setSplitNum(self, theSplitNum):
        self.__itsInputParser.setSplitNumber(theSplitNum)

    def toSqlQuery(self):
        return self.__itsInputParser.toSqlQuery()

    def toSqlQueryList(self):
        return self.__itsInputParser.toSqlQueryList()

    def fetchAll(self):
        theHeader, theData = self.getHeaderAndData()
        return [theHeader] + theData

    def getHeaderAndData(self):
        if self.__isChanged == True:
            try:
                self.__itsSQLite.load()
                theQeuryList = self.__itsInputParser.toSqlQueryList()
                #print theQeuryList
                theFetchAllResult = []
                for ithQuery in theQeuryList:
                    theFetchAllResult += self.__itsSQLite.execute(ithQuery).fetchall()
                    pass
                theChangedData = changePosition(theFetchAllResult, theChangePositionListV1)
                for ithData in theChangedData:
                    theSplitedAA = ithData[7].split(':')
                    ithData[7] = theSplitedAA[0]
                    ithData[8] = theSplitedAA[1]
                    ithData[14] = '' #ithData[15] + ';' + ithData[16]
                    if 'correct' in ithData[17]:
                        ithData[12] = '1'
                    else:
                        ithData[12] = '0'
                    pass
                self.__itsHeader = theHeaderList
                self.__itsData = theChangedData

                self.__isChanged = False
                return self.__itsHeader, self.__itsData
            except Exception as e:
                print str(e)
                return [], []
            pass
        return self.__itsHeader, self.__itsData

    def getHeader(self):
        return self.getHeaderAndData()[0]

    def header(self):
        return self.getHeader()

    def getData(self):
        return self.getHeaderAndData()[1]

    def data(self):
        return self.getData()

    def setupToIdentifier(self):
        self.__isChanged = True
        self.__itsInputParser.setupToIdentifier()
        pass

    def setupToRetrieval(self):
        self.__isChanged = True
        self.__itsInputParser.setupToRetrieval()
        pass

    def setupToSNVRetrieval(self):
        self.__isChanged = True
        self.__itsInputParser.setupToSNVRetrieval()
        pass

    def setupToSAAVRetrieval(self):
        self.__isChanged = True
        self.__itsInputParser.setupToSAAVRetrieval()
        pass

    def setupToSNVRetriever(self):
        self.__isChanged = True
        self.__itsInputParser.setupToSNVRetrieval()
        pass

    def setupToSAAVRetriever(self):
        self.__isChanged = True
        self.__itsInputParser.setupToSAAVRetrieval()
        pass

    def toString(self, theLength = -1):
        theHeader, theData = self.getHeaderAndData()
        theString = '\t'.join(theHeader) + '\n'
        if theLength > -1 and len(theString) > theLength:
            return theString[:theLength]
        for ith in theData:
            theString = theString + '\t'.join(ith) + '\n'
            if theLength > -1 and len(theString) > theLength:
                return theString[:theLength] + ' ...'
            pass
        return theString

    def __str__(self):
        return self.toString(2048)


if __name__ == '__main__':
    theInput = "NDVDCAYLR\nLEAK\n" \
               "LEAK ENSP00000358071"
    theInput = "P04259\tENSP00000252252\nchr:12\tNX_P04259-1\tAApos:97\tENSP00000252252\nP04259\tENSP00000252252\tchr:12\tAApos:97\nNX_P04259-1\tAApos:97\nchr:12\tENSP00000252252\tP04259\nchr:12\tENSP00000252252\tP04259\tAApos:63\nchr:12\tENSP00000369317\tAApos:97\nNX_P02538-1\tAApos:97\nAApos:97\tENSP00000369317\tP02538\tchr:12\nNX_P02538-1\nP27695\tchr:14\nENSP00000216714\tNX_P27695-1\nP27695\nNX_P27695-1\tENSP00000216714\tchr:14\tAApos:121\nENSP00000216714\tP27695\tAApos:148\tchr:14\nENSP00000216714\tAApos:148\tchr:14\nAApos:248\tchr:14\tENSP00000216714\nchr:14\tP27695\tENSP00000216714\nAApos:436\tNX_P06865-1\tENSP00000268097\nENSP00000268097\tAApos:8\tP06865"
    theDB = LocalDB()
    theDB.set(theInput)
    theDB.setSplitNum(1)
    print theDB
    #theDB.setupToIdentifier()
    #print theDB.getHeader()
    #print theDB.post()

    pass

