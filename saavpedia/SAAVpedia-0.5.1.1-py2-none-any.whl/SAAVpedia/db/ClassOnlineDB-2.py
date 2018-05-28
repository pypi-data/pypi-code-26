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
from ClassSAAVpediaInputParser import SAAVpediaInputParser

class OnlineDB(object) :

    def __init__(self):
        self.__itsUrl = 'https://www.saavpedia.org/api/v1/SQL.post.php'
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

    def url(self):
        self.__isChanged = True
        return self.__itsUrl

    def toSqlQuery(self):
        return self.__itsInputParser.toSqlQuery()

    def condition(self):
        return {'condition':self.__itsInputParser.toSqlQuery()}

    def post(self):
        theHeader, theData = self.getHeaderAndData()
        return [theHeader] + theData

    def fetchAll(self):
        return self.post()

    def getHeaderAndData(self):
        if self.__isChanged == True:
            try:
                theHeader, theDataRows = self.__getHeaderAndData()
                self.__itsHeader = theHeader
                self.__itsData = theDataRows
                self.__isChanged = False
                return self.__itsHeader, self.__itsData
            except Exception as e:
                print str(e)
                return [], []
            pass
        return self.__itsHeader, self.__itsData

    def __getHeaderAndData(self):
        theTextList = self.__splitTextByLines()

        theHeader = []
        theRows = []
        theIDSet = set()
        theCount = 0
        theParser = SAAVpediaInputParser()
        for ithText in theTextList:
            theParser.set(ithText)
            #print theCount
            theCondition = {'condition':theParser.toSqlQuery()}
            #print theCondition
            theResponse = requests.post(self.url(), theCondition)
            #print theResponse.text
            theData = json.loads(theResponse.text)
            if(theCount == 0):
                theHeader = theData[0]
            theNewRows = theData[1]
            for ithRow in theNewRows:
                if not ithRow[0] in theIDSet:
                    theRows.append(ithRow)
                    theIDSet.add(ithRow[0])
                pass
            theCount += 1
            pass
        return theHeader, theRows

    def __splitTextByLines(self, theNum=500):
        theTextList = []
        theSplitedLines = self.__itsInputText.split('\n')
        theCount = 0
        theString = ""
        theLength = len(theSplitedLines)
        while theCount < theLength:
            theString = theString + theSplitedLines[theCount] + '\n'
            if (((theCount + 1) % theNum) == 0 or (theCount + 1) == theLength):
                theTextList.append(theString)
                theString = ""
            theCount = theCount + 1
            pass
        return theTextList

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
    theInput = "NDVDCAYLR\n" \
               "LEAK"
    theDB = OnlineDB()
    theDB.set(theInput)
    theDB.setupToIdentifier()
    print theDB.getHeader()
    print theDB
    print theDB
    print theDB
    print theDB
    print theDB
    print theDB.toString()
    print theDB.post()

    pass

