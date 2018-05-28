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
        self.__itsUrl = 'https://www.saavpedia.org/api/v1/post.json.php'
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

    def toSqlQuery(self):
        return self.__itsInputParser.toSqlQuery()

    def toSqlQueryList(self):
        return self.__itsInputParser.toSqlQueryList()

    def post(self):
        theHeader, theData = self.getHeaderAndData()
        return [theHeader] + theData

    def fetchAll(self):
        return self.post()

    def getHeaderAndData(self):
        if self.__isChanged == True:
            try:
                r = requests.post(self.url(), self.input())
                #print r.text
                theData = json.loads(r.text)
                self.__itsHeader = theData[0]
                self.__itsData = theData[1]
                self.__isChanged = False
                return self.__itsHeader, self.__itsData
            except Exception as e:
                #self.__isChanged = False
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

    def condition(self):
        return {'condition':self.__itsInputParser.toSqlQuery()}

    def input(self):
        return {'input':self.__itsInputText}

    def url(self):
        self.__isChanged = True
        return self.__itsUrl

    def __str__(self):
        return self.toString(2048)



if __name__ == '__main__':
    theInput = "NDVDCAYLR\n" \
               "LEAK ENSP00000358071"
    theDB = OnlineDB()
    theDB.set(theInput)
    #theDB.setupToIdentifier()
    print theDB.getHeader()
    print theDB.post()

    pass

