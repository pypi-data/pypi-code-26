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


def changePosition(theData, theChangePositionList):
    theNewData = []
    for ithRow in theData:
        theNewRow = []
        for ithIndex in theChangePositionList:
            if(ithIndex > -1):
                theNewRow.append(ithRow[ithIndex])
            else:
                theNewRow.append('')
                pass
            pass
        theNewRow[5] = theNewRow[5].split(':')[0]
        theNewRow[6] = theNewRow[6].split(':')[1]
        theNewData.append(theNewRow)
        pass
    return theNewData

theChangePositionListV1 = [
    0, 1, 2, 3, 4, 6, 11, 12, 12, 13, 14, 16, -1, 8, -1, #SCF
    15, 5, 19, 24, 25, 26, 28, 27, 29,
    30, 20, 22, 23, 21,
    17, 18,
    32, 33, 74, 35,
    38, 39, 40, 41, # related to Drugs
    7, 49, 44, 10, 9, 53, 52, 51, 50, 56, 60, 55, 59, 62, 45, 47, 60, 48, 56, 58] #DB identifiers


theHeaderList = [
    # SCF begin
    'SAAVpedia_ID',

    'VSN_Chr',
    'VSN_Pos',
    'VSN_Ref',
    'VSN_Alt',
    'VSN_ID',

    'VSA_Pos',
    'VSA_Ref',
    'VSA_Alt',
    'VSA_RS',
    'VSA_AS',

    'VSA_QS',   #1
    'VSA_filter',

    'BRP_Uniprot',

    'SCF_Comment',
    # SCF end

    # 'VSA_Pval',
    'VSA_EC',
    'VSN_Strand',

    'VSN_1000G_OC',
    'VSN_1000G_T_MAF',
    'VSN_1000G_EAS_MAF',
    'VSN_1000G_AMR_MAF',
    'VSN_1000G_EUR_MAF',  # 20
    'VSN_1000G_AFR_MAF',
    'VSN_1000G_SAS_MAF',

    'VSN_VT',
    'VSN_ESP_OC',
    'VSN_ESP_AF_MAF',
    'VSN_ESP_EU_MAF',
    'VSN_ExAC_OC',

    'PTM',
    'PTM_Class',

    'VSC_Phenotype',
    'VSC_Source',
    'VSC_OID',
    'VSC_Phe_CLS',

    'VSD_DB',
    'VSD_DN',
    'VSD_DT',
    'VSD_PGT',

    'BRP_Nextprot',
    'BRP_PDB',
    'BRP_Ensembl_Pro',
    'BRP_Ensembl_Tra',
    'BRP_Ensembl_Gen',
    'BRP_GF',
    'BRP_GD',
    'BRP_GS',
    'BRP_HGNC',
    'BRP_UCSC',
    'BRP_GCosmic',
    'BRP_Entrez',
    'BRP_RefSeq',
    'BRP_Omim', #50
    'BRP_PharmGKB',
    'BRP_ChEMBL',
    'BRP_PMID',
    'BRP_STRING',
    'BRP_Vega',
    'BRP_ENA'
]


if __name__ == '__main__':
    pass

