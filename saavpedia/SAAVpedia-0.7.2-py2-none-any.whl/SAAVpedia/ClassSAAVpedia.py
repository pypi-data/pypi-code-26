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

from db import LocalDB
from db import OnlineDB
import os, urllib2
from datetime import datetime
#import glob, shutil

class SAAVpedia(object) :

    def __init__(self):
        self.__itsDB = LocalDB()
        self.__isOnlineDB = False
        self.__itsKeyMap = dict()
        self.__isFilterChanged = False
        self.__itsFilteredHeader = []
        self.__itsFilteredData = []
        self.__itsSCFLength = 15

        pass

    def __applyKeyMap(self):
        theKeyMap = dict()
        theIndex = 0
        theHeader = self.__itsDB.getHeader()
        for ithKey in theHeader:
            theKeyMap[str(ithKey).lower()] = theIndex
            theIndex += 1
            pass
        self.__itsKeyMap = theKeyMap
        pass

    def __setDB(self, theInput):
        self.__isFilterChanged = False
        self.__itsDB.set(theInput)

    def set(self, theInputText):
        self.__setDB(theInputText)
        pass

    def open(self, theInputFile):
        with open(theInputFile, 'r') as theReader:
            self.__setDB(theReader.read())
        pass

    def openSCF(self, theSCFFile):
        with open(theSCFFile, 'r') as theReader:
            theString = ''
            theSplitedLines = theReader.read().strip().replace('\r','').split('\n')
            for ithLine in theSplitedLines:
                theID = ithLine.split('\t')[0]
                #print theID
                theString += (theID + '\n')
            self.__setDB(theString)
        pass

    def setupToSNVRetriever(self):
        self.__itsDB.setupToSNVRetriever()
        pass

    def setupToSAAVRetriever(self):
        self.__itsDB.setupToSAAVRetriever()
        pass

    def setupToRetriever(self):
        self.__itsDB.setupToRetriever()
        pass

    def setupToIdentifier(self):
        self.__itsDB.setupToIdentifier()
        pass

    def setSplitNum(self, theSplitNum):
        self.__itsDB.setSplitNum(theSplitNum)

    def changeLocalDB(self):
        if self.__isOnlineDB:
            self.__itsDB = LocalDB()
            self.__isFilterChanged = False
            self.__isOnlineDB = False
        pass

    def changeOnlineDB(self):
        if not self.__isOnlineDB:
            self.__itsDB = OnlineDB()
            self.__isFilterChanged = False
            self.__isOnlineDB = True
        pass

    def data(self):
        return self.getData()

    def header(self):
        return self.getHeader()

    def getData(self):
        theHeader, theData = self.getHeaderAndData()
        return theData

    def getHeader(self):
        theHeader, theData = self.getHeaderAndData()
        return theHeader

    def getHeaderAndData(self):
        if self.__isFilterChanged:
            return self.__itsFilteredHeader, self.__itsFilteredData
        theHeader, theData = self.__itsDB.getHeaderAndData()
        return theHeader, theData

    def toString(self, theLength = -1):
        return self.__itsDB.toString(theLength)

    def init(self):
        from db.ClassSQLite3 import SQLite3
        theSQLite3 = SQLite3()
        return theSQLite3.load()

    def install(self, theDestination = './SAAVpedia.tmp'):
        if self.init():
            return True
        theScriptDownloadList = [
            #['SAAVidentifier-Online.py', 'https://raw.githubusercontent.com/saavpedia/python/master/demo/SAAVpedia/scripts/SAAVidentifier-Online.py'],
            ['SAAVidentifier.py', 'https://raw.githubusercontent.com/saavpedia/python/master/demo/SAAVpedia/scripts/SAAVidentifier.py'],
            #['SAAVannotator-Online.py', 'https://raw.githubusercontent.com/saavpedia/python/master/demo/SAAVpedia/scripts/SAAVannotator-Online.py'],
            ['SAAVannotator.py', 'https://raw.githubusercontent.com/saavpedia/python/master/demo/SAAVpedia/scripts/SAAVannotator.py'],
            #['SAAVretriever-Online.py', 'https://raw.githubusercontent.com/saavpedia/python/master/demo/SAAVpedia/scripts/SAAVretriever-Online.py'],
            ['SAAVretriever.py', 'https://raw.githubusercontent.com/saavpedia/python/master/demo/SAAVpedia/scripts/SAAVretriever.py'],
            #['SNVretriever-Online.py', 'https://raw.githubusercontent.com/saavpedia/python/master/demo/SAAVpedia/scripts/SNVretriever-Online.py'],
            ['SNVretriever.py', 'https://raw.githubusercontent.com/saavpedia/python/master/demo/SAAVpedia/scripts/SNVretriever.py'],
        ]

        theInputDownloadList = [
            ['SAAVidentifier.input.txt', 'https://raw.githubusercontent.com/saavpedia/python/master/demo/SAAVpedia/test_data/SAAVidentifier.input.txt'],
            ['SAAVannotator.input.scf', 'https://raw.githubusercontent.com/saavpedia/python/master/demo/SAAVpedia/test_data/SAAVinterpreter.input.scf'],
            ['SAAVretriever.input.txt', 'https://raw.githubusercontent.com/saavpedia/python/master/demo/SAAVpedia/test_data/SAAVretriever.input.txt'],
            #['SAAVvisualizer.input.scf', 'https://raw.githubusercontent.com/saavpedia/python/master/demo/SAAVpedia/test_data/SAAVvisualizer.input.scf'],
            ['SNVretriever.input.txt', 'https://raw.githubusercontent.com/saavpedia/python/master/demo/SAAVpedia/test_data/SNVretriever.input.txt'],
            ['DTASelect-filter.txt', 'https://raw.githubusercontent.com/saavpedia/python/master/demo/SAAVpedia/test_data/DTASelect-filter.txt']
        ]

        if not os.path.exists(theDestination):
            os.mkdir(theDestination)
            pass

        theDestScriptPath = theDestination + os.sep #+ 'scripts'
        if not os.path.exists(theDestScriptPath):
            os.mkdir(theDestScriptPath)

        theDestTestDataPath = theDestination + os.sep + 'example'
        if not os.path.exists(theDestTestDataPath):
            os.mkdir(theDestTestDataPath)

        for ithScript in theScriptDownloadList:
            print 'Downloading {0} ...'.format(ithScript[0])
            theData = urllib2.urlopen(ithScript[1]).read()
            theWriter = open(theDestScriptPath + os.sep + ithScript[0], 'w')
            theWriter.write(theData)
            theWriter.close()

        for ithInput in theInputDownloadList:
            print 'Downloading {0} ...'.format(ithInput[0])
            theData = urllib2.urlopen(ithInput[1]).read()
            theWriter = open(theDestTestDataPath + os.sep + ithInput[0], 'w')
            theWriter.write(theData)
            theWriter.close()
        return False

    def __str__(self):
        #return str(self.getHeaderAndData())
        return self.__itsDB.toString(2048)


    def applyFilter(self, theArgList = []):
        self.__isFilterChanged = True
        self.__applyKeyMap()
        theHeader = self.__itsDB.getHeader()
        theData = self.__itsDB.getData()

        theNewFilteredHeader = []
        theNewFilteredData = []
        for idx in range(self.__itsSCFLength):
            theNewFilteredHeader.append(theHeader[idx])
            pass

        for ithElement in theData:
            theNewElement = []
            for idx in range(self.__itsSCFLength):
                #print idx, theData
                theNewElement.append(ithElement[idx])
                pass
            theNewFilteredData.append(theNewElement)
            pass

        theKeySet = set()
        for ithKey in theHeader:
            theKeySet.add(str(ithKey).lower())
        theKeyMapSet = set()
        for ithArg in theArgList:
            theKey = str(ithArg[0]).lower()
            if ithArg[1] and (theKey in theKeySet):
                #print self.__itsKeyMap
                theKeyMapSet.add(self.__itsKeyMap[theKey])
                pass
            pass
        theKeyMapList = list(theKeyMapSet)
        theKeyMapList.sort()
        for idx in theKeyMapList:
            theNewFilteredHeader.append(theHeader[idx])
            pass
        for ei in range(len(theData)):
            for ki in theKeyMapList:
                theNewFilteredData[ei].append(theData[ei][ki])
        self.__itsFilteredData = theNewFilteredData
        self.__itsFilteredHeader = theNewFilteredHeader
        pass

    def getMetaInfo(self):
        theMeta  = "##fileformat=SCFv1.0\n"
        theMeta += "##fileDate=" + datetime.now().strftime('%Y%m%d') + "\n"
        theMeta += "##SAAVpedia sequence database=neXtprot Jan 2017\n" \
                   "##Meta infromation\n##SNV_OID=<Description = \"EFO ontology ID(OID) of SNV_Phenotype.\", Reference database=\"EFO\",Class=\"Clinical information\">\n" \
                   "##SAAVPedia_ID=<Description = \"Internal identifier of SAAV\", Reference database=\"SAAVPedia\",Class=\"SAAV\">\n" \
                   "##SAAV_QS=<Description = \"Quality Score(QS),It was calculated quality scoring method and peptide calling score from SAAVpedia and proteomic analysis tools such as IP2\", Reference database=\"SAAVPedia\",Class=\"SAAV\">\n" \
                   "##SAAV_Pvalue=<Description = \"P-value from the quality score distribution in SAAV list of input sample\", Reference database=\"SAAVPedia\",Class=\"SAAV\">\n" \
                   "##SAAV_filter=<Description = \"filter status,PASS if this SAAV has less than 0.05 SA_Pval. If not, then FAIL\", Reference database=\"SAAVPedia\",Class=\"SAAV\">\n" \
                   "##SAAV_Pos=<Description = \"Single amino-acid variant position(Pos),The Proteome reference position of SAAV\", Reference database=\"NextProt\",Class=\"SAAV\">\n" \
                   "##SAAV_Ref=<Description = \"Single amino-acid variant reference(Ref) sequence\", Reference database=\"NextProt\",Class=\"SAAV\">\n" \
                   "##SAAV_Alt=<Description = \"Single amino-acid variant alteration(Alt) base\", Reference database=\"NextProt\",Class=\"SAAV\">\n" \
                   "##SAAV_RS=<Description = \"Peptide reference sequence(RS) which contains one or more SAAVs\", Reference database=\"NextProt\",Class=\"SAAV\">\n" \
                   "##SAAV_AS=<Description = \"Peptide alteration sequence(AS) which contains one or more SAAVs\", Reference database=\"NextProt\",Class=\"SAAV\">\n" \
                   "##SAAV_SDM=<Description = \"Strand direction matching(SDM) information of SNV and SAAV,If the information is correct, the score is 1 otherwise 0\", Reference database=\"NextProt\",Class=\"SAAV\">\n" \
                   "##SNV_Chr=<Description = \"Chromosome(Chr),An identifier from the reference genome\", Reference database=\"dbSNP Cosmic\",Class=\"SNV\">\n" \
                   "##SNV_Pos=<Description = \"Single nucleotide variant position(Pos),The Genome reference position, with the 1st base having position 1, Reference database=\"dbSNP Cosmic\",Class=\"SNV\">\n" \
                   "##SNV_Ref=<Description = \"Single nucleotide variant reference(Ref) base,Each base must be one of A,C,G,T,N (case insensitive)\", Reference database=\"dbSNP Cosmic\",Class=\"SNV\">\n" \
                   "##SNV_Alt=<Description = \"Single nucleotide variant alteration(Alt) base,Comma separated list of alternate non-reference alleles in genome\", Reference database=\"dbSNP Cosmic\",Class=\"SNV\">\n" \
                   "##SNV_Strand=<Description = \"Genomic variation reference ID (dbSNP, Cosmic)\", Reference database=\"dbSNP Cosmic\",Class=\"SNV\">\n" \
                   "##SNV_ID=<Description = \"Chromosome(Chr),An identifier from the reference genome\", Reference database=\"dbSNP Cosmic\",Class=\"SNV\">\n" \
                   "##SNV_1000G_T_MAF=<Description = \"Minor allele frequency(MAF) in the 1000Genome population\", Reference database=\"1000 Genome\",Class=\"SNV\">\n" \
                   "##SNV_1000G_EAS_MAF=<Description = \"Minor allele frequency(MAF) in the 1000Genome East Asian population\", Reference database=\"1000 Genome\",Class=\"SNV\">\n" \
                   "##SNV_1000G_AMR_MAF=<Description = \"Minor allele frequency(MAF) in the 1000Genome American population\", Reference database=\"1000 Genome\",Class=\"SNV\">\n" \
                   "##SNV_1000G_EUR_MAF=<Description = \"Minor allele frequency(MAF) in the 1000Genome European population\", Reference database=\"1000 Genome\",Class=\"SNV\">\n" \
                   "##SNV_1000G_AFR_MAF=<Description = \"Minor allele frequency(MAF) in the 1000Genome African population\", Reference database=\"1000 Genome\",Class=\"SNV\">\n" \
                   "##SNV_1000G_SAS_MAF=<Description = \"Minor allele frequency(MAF) in the 1000Genome South Asian population\", Reference database=\"1000 Genome\",Class=\"SNV\">\n" \
                   "##SNV_1000G_SAS_MAF=<Description = \"Minor allele frequency(MAF) in the 1000Genome South Asian population\", Reference database=\"1000 Genome\",Class=\"SNV\">\n" \
                   "##SNV_VT=<Description = \"Variant Type(VT),Rare: SNV_1000G_T_MAF <= 0.005,Common: SNV_1000G_T_MAF > 0.05\", Reference database=\"1000 Genome\",Class=\"SNV\">\n" \
                   "##SNV_ESP_OC=<Description = \"Occurring(OC) in the Exome Sequencing Project(ESP) variant list,It has two kinds of values(O,X)\", Reference database=\"Ensembl variation database\",Class=\"SNV\">\n##SNV_ESP_AF_MAF=<Description = \"Minor allele frequency(MAF) in the ESP African(AF) population\", Reference database=\"Ensembl variation database\",Class=\"SNV\">\n##SNV_ESP_EU_MAF=<Description = \"Minor allele frequency(MAF) in the ESP European(EU) population\", Reference database=\"Ensembl variation database\",Class=\"SNV\">\n##SNV_ExAC_OC=<Description = \"Occurring(OC) in the Exome Aggregation Consortium(ExAC) variant list,It has two kinds of values(O,X)\", Reference database=\"Ensembl variation database\",Class=\"SNV\">\n##SNV_Phenotype=<Description = \"Phenotype term,The information extracted from genomic variation- phenotype relationship database such as Clinvar\", Reference database=\"Ensembl variation database\",Class=\"Clinical information\">\n##SNV_Source=<Description = \"Reference database of SNV_Phenotype\", Reference database=\"Ensembl variation database\",Class=\"Clinical information\">\n##SNV_OID=<Description = \"EFO ontology ID(OID) of SNV_Phenotype\", Reference database=\"EFO\",Class=\"Clinical information\">\n##SNV_Phe_CLS=<Description = \"EFO phenotype class(CLS) name of SNV_Phenotype\", Reference database=\"EFO\",Class=\"Clinical information\">\n##SNV_DB=<Description = \"Drug bank(DB) ID,We integrated based on drug target gene that contained one or more SAAVs\", Reference database=\"Drugbank\",Class=\"Pharmacological information\">\n##SNV_DN=<Description = \"Drug name(DN)\", Reference database=\"Drugbank\",Class=\"Pharmacological information\">\n##SNV_DT=<Description = \"Drug type(DT),Drugs are categorized by type, which determines their origin (Small molecule or Biotech)\", Reference database=\"Drugbank\",Class=\"Pharmacological information\">\n##SNV_PGT=<Description = \"Pharmacological gene type,It consists of four types: target, enzyme, transporter, carrier\", Reference database=\"Drugbank\",Class=\"Pharmacological information\">\n##PROTEIN_Uniplot=<Description = \"Uniplot identifier\", Reference database=\"Uniplot\",Class=\"Protein\">\n##PROTEIN_Nextprott=<Description = \"NextProt identifier\", Reference database=\"NextProt\",Class=\"Protein\">\n##PROTEIN_PDB=<Description = \"Protein Data Bank(PDB) identifier\", Reference database=\"PDB\",Class=\"Protein\">\n##PROTEIN_Enemble_Pro=<Description = \"Ensemble protein(Pro) identifier\", Reference database=\"Ensemble\",Class=\"Protein\">\n##TRANSCRIPT_Enemble_Tra=<Description = \"Ensemble transcript(Tra) identifier\", Reference database=\"Ensemble\",Class=\"Transcript\">\n##GENE_Enemble_Gen=<Description = \"Ensemble Gene(Gen) identifier\", Reference database=\"Ensemble\",Class=\"Gene\">\n##GENE_GF=<Description = \"Gene Families(GF)\", Reference database=\"Ensemble\",Class=\"Gene\">\n##GENE_GD=<Description = \"Gene description(GD)\", Reference database=\"HGNC\",Class=\"Gene\">\n##GENE_GS=<Description = \"Gene Symbol(GS)\", Reference database=\"HGNC\",Class=\"Gene\">\n##GENE_HGNC=<Description = \"HGNC ID\", Reference database=\"HGNC\",Class=\"Gene\">\n##GENE_UCSC=<Description = \"UCSC ID\", Reference database=\"UCSC\",Class=\"Gene\">\n##GENE_Cosmic=<Description = \"Cosmic Gene ID\", Reference database=\"Cosmic\",Class=\"Gene\">\n##GENE_Entrez=<Description = \"Entrez ID\", Reference database=\"Ensemble\",Class=\"Gene\">\n##GENE_ RefSeq=<Description = \"Reference Sequence (RefSeq) accession number\", Reference database=\"Entrez\",Class=\"Gene\">\n##Disease_Omim=<Description = \"Omim ID\", Reference database=\"Omim\",Class=\"Clinical information\">\n##DRUG_PharmGKB=<Description = \"PharmGKB ID\", Reference database=\"PharmGKB\",Class=\"Pharmacological information\">\n##DRUG_CHEMBLI=<Description = \"CHEMBL ID\", Reference database=\"CHEMBLI\",Class=\"Pharmacological information\">\n##Literature_PMID=<Description = \"Pubmed ID\", Reference database=\"Pubmed\",Class=\"Literature\">\n" \
                   "##Biological function_STRING=<Description = \"STRING ID\", Reference database=\"STRING\",Class=\"Biological function\">\n" \
                   "##Biological function_Vega=<Description = \"Vega ID\", Reference database=\"Vega\",Class=\"Biological function\">\n" \
                   "##Biological function_ENA=<Description = \"European Nucleotide Archive ID\", Reference database=\"ENA\",Class=\"Biological function\">\n"
        return theMeta

if __name__ == '__main__':
    theInput = "NDVDCAYLR\n" \
               "LEAK"

    theSAAVpedia = SAAVpedia()

    theSAAVpedia.changeOnlineDB()
    theSAAVpedia.changeLocalDB()

    theSAAVpedia.set(theInput)
    theSAAVpedia.applyFilter()
    #print theSAAVpedia.toString()
    #theSAAVpedia.setupToIdentifier()

    theSAAVpedia.applyFilter([('snv_esp_oc', True),
                              ('brp_ENA', True),
                              ('brp_ensembl_gen', True),
                              ('brp_ensembl_pro', True),
                              ('brp_ensembl_tra', True),
                              ('brp_entrez', True),
                              ('brp_gcosmic', True),
                              ('brp_gd', True), ('brp_gf', True), ('brp_gs', True), ('brp_hgnc', True),
                              ('snv_exac_Oc', True), ('vsn_vt', True), ('saav_qs',True), ('saav_pvalue',True), ('snv_pgt', True)])
    #print theSAAVpedia
    print theSAAVpedia.toString()

    pass

