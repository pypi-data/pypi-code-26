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
    0, 1, 2, 3, 4, 6, 11, 12, 12, 13, 14, -1, -1, 7, -1, 16, -1, #SCF
    15, 5, 19, 24, 25, 26, 28, 27, 29,
    30, 20, 22, 23, 21,
    17, 18,
    32, 33, 74, 35,
    38, 39, 40, 41, # related to Drugs
    8, 49, 44, 10, 9, 53, 52, 51, 50, 56, 60, 55, 59, 62, 45, 47, 60, 48, 56, 58] #DB identifiers


theHeaderList = [
    # SCF begin
    'SAAVpedia_ID', #0

    'SNV_Chr', #1
    'SNV_Pos', #2
    'SNV_Ref', #3
    'SNV_Alt', #4
    'SNV_ID', #6

    'SAAV_Pos', #11
    'SAAV_Ref', #12
    'SAAV_Alt', #12
    'SAAV_RS', #13
    'SAAV_AS', #14

    'SAAV_filter',  # -1
    'SAAV_SDM',  # -1

    'PROTEIN_Nextprot', #7

    'Info', #-1
    'SAAV_QS',   #16
    'SAAV_Pvalue',   #-1
    # SCF end

    # 'SAAV_Pval',
    'SAAV_EC',
    'SNV_Strand',

    'SNV_1000G_OC',
    'SNV_1000G_T_MAF',
    'SNV_1000G_EAS_MAF',
    'SNV_1000G_AMR_MAF',
    'SNV_1000G_EUR_MAF',  # 20
    'SNV_1000G_AFR_MAF',
    'SNV_1000G_SAS_MAF',

    'SNV_VT',
    'SNV_ESP_OC',
    'SNV_ESP_AF_MAF',
    'SNV_ESP_EU_MAF',
    'SNV_ExAC_OC',

    'PTM',
    'PTM_Class',

    'SNV_Phenotype',
    'SNV_Source',
    'SNV_OID',
    'SNV_Phe_CLS',

    'SNV_DB',
    'SNV_DN',
    'SNV_DT',
    'SNV_PGT',

    'PROTEIN_Uniprot', #8
    'PROTEIN_PDB',
    'PROTEIN_Ensembl_Pro',
    'TRANSCRIPT_Ensembl_Tra',
    'GENE_Ensembl_Gen',
    'GENE_GF',
    'GENE_GD',
    'GENE_GS',
    'GENE_HGNC',
    'GENE_UCSC',
    'GENE_Cosmic',
    'GENE_Entrez',
    'GENE_RefSeq',
    'Disease_Omim', #50
    'DRUG_PharmGKB',
    'DRUG_ChEMBL',
    'Literature_PMID',
    'Biological_function_STRING',
    'Biological_function_Vega',
    'Biological_function_ENA'
]

theHeaderList_Bak = [
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

