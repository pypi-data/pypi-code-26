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

import re

class SAAVpediaInputParser(object):
    def __init__(self):
        self.__its2dStringData = []
        self.__its2dStringDataWithENSX = []
        self.__itsColOfSAAVpediaID    = 'data.col0'
        self.__itsColOfChr            = 'data.col1'
        self.__itsColOfNTPos          = 'data.col2'
        self.__itsColOfRsID           = 'data.col6'
        self.__itsColOfCosmicID       = 'data.col6'
        self.__itsColOfNextprot       = 'data.col7'
        self.__itsColOfUniprot        = 'data.col8'
        self.__itsColOfENSG           = 'ensx.col0'
        self.__itsColOfENST           = 'ensx.col0'
        self.__itsColOfENSP           = 'ensx.col0'

        self.__itsColOfSAAVpeptideSeq = 'data.col14'
        self.__itsColOfAAPos          = 'data.col73'

        self.__itsUniprotMatcher = re.compile( \
            '[OPQ][0-9][A-Z0-9]{3}[0-9]|[A-NR-Z][0-9]([A-Z][A-Z0-9]{2}[0-9]){1,2}')

        self.__itsSplitNum = 500
        pass

    def setSplitNumber(self, theNumber):
        theNumber = int(theNumber)
        if theNumber > 0:
            self.__itsSplitNum = theNumber
        pass

    def getSplitNumber(self):
        return int(self.__itsSplitNum)

    def __aListToSqlString(self, theStringList):
        def has(theList, theValue):
            for i in theList:
                if theValue in i:
                    return True
                pass
            return False

        def mergeENSX(theList):
            theListWithoutENSX = []
            theListIncludingENSG = []
            theListIncludingENST = []
            theListIncludingENSP = []
            for i in theList:
                if 'ensx.col0' in i and 'ENSG' in i:
                    theListIncludingENSG.append(i)
                elif 'ensx.col0' in i and 'ENST' in i:
                    theListIncludingENST.append(i)
                elif 'ensx.col0' in i and 'ENSP' in i:
                    theListIncludingENSP.append(i)
                else:
                    theListWithoutENSX.append(i)
                    pass
                pass
            if len(theListIncludingENSG) > 1:
                theMergedENSGQuery = '(' + ' OR '.join(theListIncludingENSG) + ')'
                theListWithoutENSX.append(theMergedENSGQuery)
            elif len(theListIncludingENSG) > 0:
                theMergedENSGQuery = theListIncludingENSG[0]
                theListWithoutENSX.append(theMergedENSGQuery)
                pass
            if len(theListIncludingENST) > 1:
                theMergedENSTQuery = '(' + ' OR '.join(theListIncludingENST) + ')'
                theListWithoutENSX.append(theMergedENSTQuery)
            elif len(theListIncludingENST) > 0:
                theMergedENSTQuery = theListIncludingENST[0]
                theListWithoutENSX.append(theMergedENSTQuery)
                pass
            if len(theListIncludingENSP) > 1:
                theMergedENSPQuery = '(' + ' OR '.join(theListIncludingENSP) + ')'
                theListWithoutENSX.append(theMergedENSPQuery)
            elif len(theListIncludingENSP) > 0:
                theMergedENSPQuery = theListIncludingENSP[0]
                theListWithoutENSX.append(theMergedENSPQuery)
                pass
            return theListWithoutENSX

        theList = []
        for i in theStringList:
            theElement = self.__stringToQuery(i)
            if not theElement == None:
                theList.append(theElement)
                pass
            pass

        theList = mergeENSX(theList)

        if has(theList, 'ensx.col0') :
            theList.append('(data.col0=ensx.col1)')
            pass


        if len(theList) > 1:
            return "("+" AND ".join(theList)+")"
        elif len(theList) > 0:
            return theList[0]
        return None

    def __2dListToSqlString(self, the2dList):
        theQueryList = self.__2dListToSingleQueryList(the2dList)
        if len(theQueryList) > 0:
            return "("+" OR ".join(theQueryList)+")"
        return ""

    def __2dListToSqlStringList(self, the2dList):
        theSplitNum = self.getSplitNumber()
        theQueryList = self.__2dListToSingleQueryList(the2dList)

        #theSplitList is 2D list
        theSplitList = self.__splitByNumber(theQueryList, theSplitNum)
        theSplitQueryList = []
        for ithList in theSplitList:
            theQuery = ""
            if len(ithList) > 0:
                theQuery = "("+" OR ".join(ithList)+")"
            theSplitQueryList.append(theQuery)
        return theSplitQueryList

    def __splitByNumber(self, theList, theNum):
        theSplitList = []
        theCount = 0
        theLength = len(theList)
        theSplitUnitList = []
        while theCount < theLength:
            theSplitUnitList.append(theList[theCount])
            if(((theCount+1) % theNum) == 0 or (theCount + 1) == theLength):
                theSplitList.append(theSplitUnitList)
                theSplitUnitList = []
            theCount += 1
            pass
        return theSplitList

    def __2dListToSingleQueryList(self, the2dList):
        theQueryList = []
        for ithList in the2dList:
            theSqlString = self.__aListToSqlString(ithList)
            if not theSqlString == None:
                theQueryList.append(theSqlString)
            pass
        return theQueryList

    def __aListToQueryDict(self, theStringList):
        theQueryDict = {}
        for i in theStringList:
            self.__addQueryToQueryDict(theQueryDict, i)
        return theQueryDict

    def __2dListToQueryDictList(self, the2dList):
        theQueryDictList = []
        for ithList in the2dList:
            theQueryDict = self.__aListToQueryDict(ithList)
            if len(theQueryDict) > 0:
                theQueryDictList.append(theQueryDict)
            pass
        return theQueryDictList

    def __isDigitIncludingPrefix(self, theString, thePrefix):
        if (len(theString) < len(thePrefix)) :
            return False
        if not (thePrefix.upper() == str(theString[:len(thePrefix)]).upper()):
            return False
        if (str(theString[len(thePrefix):]).isdigit()):
            return True
        return False

    def __hasPrefix(self, theString, thePrefix):
        if (len(theString) < len(thePrefix)) :
            return False
        if (thePrefix.upper() == str(theString[:len(thePrefix)]).upper()):
            return True
        return False

    def __isSAAVpediaID(self, theString):
        return self.__isDigitIncludingPrefix(theString, 'SAAVPD')

    def __isENSP(self, theString):
        return self.__isDigitIncludingPrefix(theString, 'ENSP')

    def __isENST(self, theString):
        return self.__isDigitIncludingPrefix(theString, 'ENST')

    def __isENSG(self, theString):
        return self.__isDigitIncludingPrefix(theString, 'ENSG')

    def __isRsID(self, theString):
        return self.__isDigitIncludingPrefix(theString, 'rs')

    def __isCosmicID(self, theString):
        return self.__isDigitIncludingPrefix(theString, 'COSM')

    def __isUniprot(self, theString):
        return bool(self.__itsUniprotMatcher.match(theString))

    def __isNextprot(self, theString):
        thePrefix = 'NX_'
        if len(theString) < len(thePrefix):
            return False
        theTail = theString[len(thePrefix):].split('-')[0]
        return bool(self.__itsUniprotMatcher.match(theTail))

    def __isChr(self, theString):
        return self.__hasPrefix(theString, 'chr:')

    def __isNTPos(self, theString):
        return self.__isDigitIncludingPrefix(theString, 'ntpos:')

    def __isAAPos(self, theString):
        return self.__isDigitIncludingPrefix(theString, 'aapos:')

    def __stringToQuery(self, theString):
        if self.__isSAAVpediaID(theString):
            return '({0}=\"{1}\")'.format(self.__itsColOfSAAVpediaID, theString.upper())
        elif self.__isCosmicID(theString):
            return '({0}=\"{1}\")'.format(self.__itsColOfCosmicID, theString.upper())
        elif self.__isRsID(theString):
            return '({0}=\"{1}\")'.format(self.__itsColOfRsID, theString.lower())
        elif self.__isENSG(theString):
            return '({0}=\"{1}\")'.format(self.__itsColOfENSG, theString.upper())
        elif self.__isENST(theString):
            return '({0}=\"{1}\")'.format(self.__itsColOfENST, theString.upper())
        elif self.__isENSP(theString):
            return '({0}=\"{1}\")'.format(self.__itsColOfENSP, theString.upper())
        elif self.__isUniprot(theString):
            return '({0}=\"{1}\")'.format(self.__itsColOfUniprot, theString.upper())
        elif self.__isNextprot(theString) and theString.count('-') > 0:
            return '({0}=\"{1}\")'.format(self.__itsColOfNextprot, theString.upper())
        elif self.__isNextprot(theString) and theString.count('-') == 0:
            return '({0}=\"{1}\")'.format(self.__itsColOfUniprot, theString[len("NX_"):])
        elif self.__isChr(theString):
            return '({0}=\"{1}\")'.format(self.__itsColOfChr, theString.upper().split('CHR:')[1])
        elif self.__isNTPos(theString):
            return '({0}=\"{1}\")'.format(self.__itsColOfNTPos, theString.upper().split('NTPOS:')[1])
        elif self.__isAAPos(theString):
            return '({0}=\"{1}\")'.format(self.__itsColOfAAPos, theString.upper().split('AAPOS:')[1])
        elif str(theString).isalpha():
            return '({0}=\"{1}\")'.format(self.__itsColOfSAAVpeptideSeq, theString.upper())
        else :
            return None

    def __addQueryToQueryDict(self, theQueryDict, theString):
        theKey = None
        theValue = theString
        if self.__isCosmicID(theString):
            theKey = 'cosmic'
        elif self.__isRsID(theString):
            theKey = 'rs'
        elif self.__isENSG(theString):
            theKey = 'ensg'
        elif self.__isENST(theString):
            theKey = 'enst'
        elif self.__isENSP(theString):
            theKey = 'ensp'
        elif self.__isUniprot(theString):
            theKey = 'uniprot'
        elif self.__isNextprot(theString):
            theKey = 'nextprot'
        elif self.__isChr(theString):
            theKey = 'chr'
        elif self.__isNTPos(theString):
            theKey = 'ntpos'
        elif self.__isAAPos(theString):
            theKey = 'aapos'
        elif str(theString).isalpha():
            theKey = 'seq'

        if theKey != None:
            if theQueryDict.has_key(theKey):
                if type(theQueryDict[theKey]) == type(list()):
                    theSet = set(theQueryDict[theKey])
                    theSet.add(theValue)
                    theQueryDict[theKey] = list(theSet)
                else:
                    theSet = set([theQueryDict[theKey], theValue])
                    theQueryDict[theKey] = list(theSet)
            else :
                theQueryDict[theKey] = theValue
                pass
            pass
        pass

    def __queryDictToString(self, theQueryDict = {}, theFilter = []):
        theKeySet = set(theQueryDict.keys())
        theFilterSet = set(theFilter)
        theIntersectionSet = theKeySet & theFilterSet
        theString = ""
        for ithKey in theIntersectionSet:
            if type(theQueryDict[ithKey]) == type(""):
                theString = theString + theQueryDict[ithKey] + "\t"
            elif type(theQueryDict[ithKey]) == type([]):
                theString = theString + "\t".join(theQueryDict[ithKey]) + "\t"
            pass
        if len(theString) > 0:
            theString = theString + "\n"
        return theString

    def __str__(self):
        return self.toString()

    def toSqlCondition(self):
        return '((' + self.toSqlConditionWithoutENSX() + ') OR ('\
                    + self.toSqlConditionOnlyENSX() + '))'

    def toSqlConditionOnlyENSX(self):
        return self.__2dListToSqlString(self.__its2dStringDataWithENSX)

    def toSqlConditionWithoutENSX(self):
        return self.__2dListToSqlString(self.__its2dStringData)

    def toSqlConditionListOnlyENSX(self):
        return self.__2dListToSqlStringList(self.__its2dStringDataWithENSX)

    def toSqlConditionListWithoutENSX(self):
        return self.__2dListToSqlStringList(self.__its2dStringData)

    def toQueryDictList(self):
        return self.__2dListToQueryDictList(self.__its2dStringData) + \
               self.__2dListToQueryDictList(self.__its2dStringDataWithENSX)

    def toQueryDictListOfOnlyENSX(self):
        return self.__2dListToQueryDictList(self.__its2dStringDataWithENSX)

    def toQueryDictListWithoutENSX(self):
        return self.__2dListToQueryDictList(self.__its2dStringData)

    def toSqlQueryForOnlyENSX(self):
        theSqlCondition = self.toSqlConditionOnlyENSX()
        if len(theSqlCondition) > 0:
            return "SELECT DISTINCT data.* FROM data, ensx WHERE " + theSqlCondition
        return ""

    def toSqlQueryWithoutENSX(self):
        theSqlCondition = self.toSqlConditionWithoutENSX()
        if len(theSqlCondition) > 0:
            return "SELECT DISTINCT * FROM data WHERE " + theSqlCondition
        return ""


    def toSqlQueryListForOnlyENSX(self):
        theSqlConditionList = self.toSqlConditionListOnlyENSX()
        theSqlQueryList = []
        for ithSqlCondition in theSqlConditionList:
            if len(ithSqlCondition) > 0:
                theSqlQueryList.append("SELECT DISTINCT data.* FROM data, ensx WHERE " + ithSqlCondition)
        return theSqlQueryList

    def toSqlQueryListWithoutENSX(self):
        theSqlConditionList = self.toSqlConditionListWithoutENSX()
        theSqlQueryList = []
        for ithSqlCondition in theSqlConditionList:
            if len(ithSqlCondition) > 0:
                theSqlQueryList.append("SELECT DISTINCT * FROM data WHERE " + ithSqlCondition)
        return theSqlQueryList

    def toSqlQuery(self):
        theSqlConditionForOnlyENSX = self.toSqlConditionOnlyENSX()
        theSqlConditionWithoutENSX = self.toSqlConditionWithoutENSX()
        theSqlCondition =  '((' + theSqlConditionWithoutENSX + ') OR (' + theSqlConditionWithoutENSX + '))'
        theSqlQuery = ''
        if len(theSqlConditionForOnlyENSX) > 0 and len(theSqlConditionWithoutENSX) > 0:
            theSqlQuery = "SELECT DISTINCT data.* FROM data, ensx WHERE " + theSqlCondition
        elif len(theSqlConditionForOnlyENSX) == 0 and len(theSqlConditionWithoutENSX) > 0:
            theSqlQuery = "SELECT DISTINCT data.* FROM data WHERE " + theSqlConditionWithoutENSX
        elif len(theSqlConditionForOnlyENSX) > 0 and len(theSqlConditionWithoutENSX) == 0:
            theSqlQuery = "SELECT DISTINCT data.* FROM data, ensx WHERE " + theSqlConditionForOnlyENSX
        return theSqlQuery

    def toSqlQueryList(self):
        return self.toSqlQueryListForOnlyENSX() + self.toSqlQueryListWithoutENSX()


    def toString(self):
        return str(self.toQueryDictList())

    def setupToIdentifier(self):
        theQueryDictList = self.toQueryDictList()
        theString = ""
        for ithDict in theQueryDictList:
            theString = theString + self.__queryDictToString(ithDict, ['seq'])
            pass
        self.set(theString)
        pass

    def setupToRetrieval(self):
        theQueryDictList = self.toQueryDictList()
        theString = ""
        for ithDict in theQueryDictList:
            theString = theString + self.__queryDictToString(ithDict, ['rs', 'cosmic', 'ensg', 'enst', 'ensp', 'ntpos', 'aapos', 'chr', 'uniprot', 'nextprot'])
            pass
        self.set(theString)
        pass

    def setupToSNVRetrieval(self):
        theQueryDictList = self.toQueryDictList()
        theString = ""
        for ithDict in theQueryDictList:
            theString = theString + self.__queryDictToString(ithDict, ['rs', 'cosmic',])
            pass
        self.set(theString)
        pass

    def setupToSAAVRetrieval(self):
        theQueryDictList = self.toQueryDictList()
        theString = ""
        for ithDict in theQueryDictList:
            theString = theString + self.__queryDictToString(ithDict, ['ensg', 'enst', 'ensp', 'ntpos', 'aapos', 'chr', 'uniprot', 'nextprot'])
            pass
        self.set(theString)
        pass

    def set(self, theStringInput):
        def hasENSX(theStringList):
            for ith in theStringList:
                if self.__isENSG(ith) or self.__isENST(ith) or self.__isENSP(ith):
                    return True
            return False

        the2dStringData = []
        the2dStringDataWithENSX = []
        theSplitedLineList = theStringInput.replace('\r','').strip().split('\n')
        for ithLine in theSplitedLineList:
            theStringList = ithLine.strip().split()
            if hasENSX(theStringList):
                the2dStringDataWithENSX.append(theStringList)
            else:
                the2dStringData.append(theStringList)
            pass
        self.__its2dStringData = the2dStringData
        self.__its2dStringDataWithENSX = the2dStringDataWithENSX
        pass
    pass


if __name__ == '__main__':
    theInput = "LEAK COSM915367 rs140436110 ENSG00000108091 ENSG00000108094 ENST00000108094 ENSP00000108094	NTpos:35322192	AApos:329 chr:10 Q9P0M6 NX_Q9P0M6-1\nLEAK\tNX_Q9P0M6\nLEAK\nLEAK"
    theInput = 'SAAVPD00044212\n' \
               'SAAVPD00053316\n' \
               'SAAVPD00111397\n' \
               'SAAVPD00129018\n' \
               'SAAVPD00134053\n' \
               'SAAVPD00134054'

    theInput = "LEAK ENSP00000330836 ENSP00000357633 ENSP00000435445\nLEAK ENSP00000330836 ENSP00000357633 ENSP00000435445\nLEAK ENSP00000330836 ENSP00000357633 ENSP00000435445\nLEAK ENSP00000330836 ENSP00000357633 ENSP00000435445"


    parser = SAAVpediaInputParser()
    parser.setSplitNumber(2)

    parser.set(theInput)
    print parser.toQueryDictList()
    print parser.toSqlQuery()

    parser.setupToIdentifier()
    print parser.toQueryDictList()
    print parser.toSqlQuery()
    print parser.toSqlConditionListWithoutENSX()
    print (parser.toSqlQueryList())


    parser.set(theInput)
    parser.setupToRetrieval()
    print '####### Retrieval ######'
    print parser.toQueryDictList()
    print parser.toSqlQuery()
    print (parser.toSqlQueryList())


    pass



