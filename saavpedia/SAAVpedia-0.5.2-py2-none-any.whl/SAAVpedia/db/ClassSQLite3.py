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

import os
import sqlite3
import urllib2, math, shutil

class SQLite3(object) :

    def __init__(self):
        self.__itsCursor = None
        self.__itsVersionList = [
            {'date':'2018.05.04', 'size':10753868800, 'folder':'2018.05.04.sqlite.split', 'unit_size':10485760 }
        ]
        pass

    def __load(self):
        theBasePath = os.path.dirname(os.path.realpath(__file__))
        theDBFilePath = theBasePath + '/saavpedia.db'
        if os.path.exists(theDBFilePath):
            if os.path.isfile(theDBFilePath) and os.path.getsize(theDBFilePath) == self.__itsVersionList[-1]['size']:
                self.__itsConnection = sqlite3.connect(theDBFilePath)
                self.__itsCursor = self.__itsConnection.cursor()
                #print 'Local SAAVpedia DB is loaded.'
                return False
            pass
        self.__saveDB(theDBFilePath)
        self.__itsCursor = None
        return True

    def __saveDB(self, theDBFilePath):
        theLastVersionInfo = self.__itsVersionList[-1]
        theUnitSize = theLastVersionInfo['unit_size']
        theNumOfSplitFiles = int(math.ceil(theLastVersionInfo['size'] / (theUnitSize * 1.0)))
        theWriter = open(theDBFilePath, 'wb')
        theTempFileList = []
        theTempFolder = os.path.dirname(theDBFilePath) + os.sep + 'tmp'
        if not os.path.exists(theTempFolder):
            os.makedirs(theTempFolder)
        for idx in range(theNumOfSplitFiles):
            theTempFilePath = '{0}{1}SAAVpedia.sqlite.{2}.db'.format(theTempFolder, os.sep, str(idx))
            theTempFileList.append(theTempFilePath)
            if (not os.path.exists(theTempFilePath)) or (os.path.getsize(theTempFilePath) != theUnitSize):
                print 'Downloading SAAVpedia.sqlite.{0}.db - {1:.2f}%'.format(idx, (idx + 1.0) / theNumOfSplitFiles * 100.0)
                theTempWriter = open(theTempFilePath, 'wb')
                theURL = 'https://github.com/saavpedia/python/blob/master/SAAVpedia/db/{0}/SAAVpediaData.sqlite.db.{1}.kbsi?raw=true'.format(theLastVersionInfo['folder'], idx)
                theData = urllib2.urlopen(theURL).read()
                theTempWriter.write(theData)
                theTempWriter.close()
                pass
        print 'Download is completed.'
        theCount = 0
        for ithDBFile in theTempFileList:
            print 'Generating SAAVpedia DB... - {0:.2f}%'.format((theCount+1.0)/theNumOfSplitFiles*100.0)
            with open(ithDBFile, 'rb') as theReader:
                theWriter.write(theReader.read())
                pass
            theCount += 1
            pass

        theWriter.close()
        print 'Removing temporary files...'
        shutil.rmtree(theTempFolder)
        print 'SAAVpedia initilzation is completed.'

    def load(self):
        try:
            self.__load()
            return False
        except Exception as e:
            print str(e)
            return True

    def open(self, theDBFilePath):
        try:
            self.__itsConnection = sqlite3.connect(theDBFilePath)
            self.__itsCursor = self.__itsConnection.cursor()
            return False
        except:
            return True

    def close(self):
        if not self.__itsCursor == None:
            self.__itsCursor.close()
        self.__itsCursor = None
        pass

    def execute(self, theCommand):
        if not self.__itsCursor == None:
            return self.__itsCursor.execute(theCommand)
        return None

if __name__ == '__main__':
    theSQLite = SQLite3()
    theSQLite.load()
    pass

