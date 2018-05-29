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

if __name__ == '__main__':
    pass

def filterSeq(theSeq):
    if theSeq.find('(') != -1:
        theBegin = theSeq.find('(')
        theEnd = theSeq.find(')', theBegin)
        if theEnd == -1:
            theEnd = len(theSeq)
        else:
            theEnd += 1
        if len(theSeq) != len(theSeq[theBegin:theEnd]):
            return filterSeq(theSeq[:theBegin]+theSeq[theEnd:len(theSeq)])
        pass
    return removeKR(theSeq)

def removeKR(theSeq):
    theBegin = theSeq.find('.') + 1
    theEnd = theSeq.find('.', theBegin)
    return theSeq[theBegin:theEnd].replace('-','')


def filterDTASelect(theDTASelectFile):
    theSplitedLines = open(theDTASelectFile,'r').read().replace('\r','').split('\n')
    theDTADataDict = {}
    for idx in range(len(theSplitedLines)):
        ithLine = theSplitedLines[idx]
        theCount = ithLine.count('\t')
        if theCount > 13:
            theSplitedLine = ithLine.split('\t')
            theXCorr = theSplitedLine[2]
            theDeltaCN = theSplitedLine[3]
            theSeq = theSplitedLine[-1]
            try:
                theXCorrValue = float(theXCorr)
                theDeltaCNValue = float(theDeltaCN)
                theSplitedSeq = filterSeq(theSeq)
                if(theSplitedSeq in theDTADataDict.keys()):
                    theDTADataDict[theSplitedSeq][0] += 1
                    theDTADataDict[theSplitedSeq][1] += theXCorrValue * theDeltaCNValue
                else:
                    theDTADataDict[theSplitedSeq] = [1, theXCorrValue * theDeltaCNValue]
                pass
            except:
                pass
            pass
        pass
    return theDTADataDict

def mergeDTASelectFiles(theDTADataDictList):
    theDTATempDataDict= {}
    theSumDataDict =  {}
    for ithDTADataDict in theDTADataDictList:
        for ithSeq in ithDTADataDict.keys():
            theCount = ithDTADataDict[ithSeq][0]
            theValue = ithDTADataDict[ithSeq][1]
            if(ithSeq in theSumDataDict.keys()):
                theSumDataDict[ithSeq][0] += theCount
                theSumDataDict[ithSeq][1] += theValue
            else:
                theSumDataDict[ithSeq] = [theCount, theValue]
                pass
            pass
        pass

    for ithSeq in theSumDataDict:
        theDTATempDataDict[ithSeq] = theSumDataDict[ithSeq][1] / theSumDataDict[ithSeq][0] * 1.0
        pass
    return theDTATempDataDict


def normalcdf(X):
    import math
    T = 1.0 / (1 + 0.2316419 * math.fabs(X))
    D = 0.3989423 * math.exp(-X * X / 2.0)
    Prob = D * T * (0.3193815 + T * (-0.3565638 + T * (1.781478 + T * (-1.821256 + T * 1.330274))))
    if (X>0):
        Prob = 1 - Prob
        pass
    return Prob

def standardDeviation(theValueList):
    import math
    n = len(theValueList)

    if n <= 1:
        return 0.0

    mean, sd = average(theValueList), 0.0

    # calculate stan. dev.
    for el in theValueList:
        sd += (float(el) - mean)**2
    sd = math.sqrt(sd / float(n-1))
    return sd

def average(theValueList):
    return sum(theValueList) / (len(theValueList) * 1.0)


def calculateQualityScore(theSCFData, theDTAFileList):
    theDTAList = []
    for ithFile in theDTAFileList:
        theDTAList.append(filterDTASelect(ithFile))
        pass

    theDTADataDict = mergeDTASelectFiles(theDTAList)
    return applyQualityScore(theSCFData, theDTADataDict)


def applyQualityScore(theSCFData, theDTADataDict):
    theDTASelectData = {}
    theDTASelectZTData = {}
    theDTASelectPValueData = {}
    #theSAAVDataDict = {}
    theDTASelectTotalCount = 0
    theDTASelectOccurrenceCount = 0
    theDTASelectPassCount = 0

    for ithSAAV in theSCFData:
        theSeq = ithSAAV[10]
        if theSeq in theDTADataDict:
            if '1' in ithSAAV[12]:
                theDTASelectData[theSeq] = float(theDTADataDict[theSeq])
            else:
                theDTASelectData[theSeq] = float(theDTADataDict[theSeq]) * 0.5
                pass
            theDTASelectOccurrenceCount += 1
            pass
        else:
            theDTASelectData[theSeq] = 0
            pass
        theDTASelectTotalCount += 1
        pass

    theDataList = []
    for ithSeq in theDTASelectData:
        theDataList.append(theDTASelectData[ithSeq])
        pass

    theMean = average(theDataList)
    theStdDev = standardDeviation(theDataList)
    for ithSeq in theDTASelectData:
        theZValue = (theDTASelectData[ithSeq] - theMean) / theStdDev
        theDTASelectZTData[ithSeq] = theZValue
        theDTASelectPValueData[ithSeq] = normalcdf(-theZValue)
        if theDTASelectPValueData[ithSeq] < 0.05:
            theDTASelectPassCount += 1
            pass
        pass

    theNewSCFData = []
    for ithSAAV in theSCFData:
        import copy
        ithNewSAAV = copy.deepcopy(ithSAAV)
        while len(ithNewSAAV) < 17:
            ithNewSAAV.append('')
        theSeq = ithNewSAAV[10]
        if theSeq in theDTADataDict:
            thePValue = float(theDTASelectPValueData[theSeq])
            ithNewSAAV[15] = '{0:.4f}'.format(float(theDTASelectData[theSeq]))
            ithNewSAAV[16] = '{0:.6f}'.format(float(thePValue))
            if thePValue < 0.05:
                ithNewSAAV[11] = 'PASS'
                pass
            else:
                ithNewSAAV[11] = 'FAIL'
                pass
        else:
            thePValue = normalcdf(theMean / theStdDev)
            ithNewSAAV[15] = '0'
            ithNewSAAV[16] = '{0:.6f}'.format(float(thePValue))
            ithNewSAAV[11] = 'Non occurrence'
        theNewSCFData.append(ithNewSAAV)

    return theNewSCFData

def getDTAFilePathList(thePath):
    import os
    theDTAFilePathList = []
    for root, dirs, files in os.walk(thePath, topdown=False):
        for name in files:
            if 'DTASelect-filter'.lower() in name.lower() and '.txt' in name.lower():
                theDTAFilePathList.append(os.path.abspath(os.path.join(root, name)))
                pass
            pass
        pass
    return theDTAFilePathList

if __name__ == '__main__':
    theFile = 'DTASelect-filter.txt'
    theFile1 = 'DTASelect-filter.1.txt'
    a = filterDTASelect(theFile)
    b = filterDTASelect(theFile1)

    print mergeDTASelectFiles([a,b])


    pass