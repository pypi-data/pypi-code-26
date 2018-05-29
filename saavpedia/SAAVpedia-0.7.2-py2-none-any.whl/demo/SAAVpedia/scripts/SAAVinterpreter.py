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

import argparse, sys
import time
from datetime import datetime
from SAAVpedia.ClassSAAVpedia import SAAVpedia

def main(theArgs):

    theStartTime = time.time()
    theSAAVpedia = SAAVpedia()

    # Reading Input file
    print 'Reading the input file...'
    #theSAAVpedia.set(file(theArgs.input).read())
    theSAAVpedia.openSCF(theArgs.input)
    #theSAAVpedia.setupToIdentifier()

    if theArgs.output:
        theOutputName = theArgs.output
    else :
        theOutputName = datetime.now().strftime('SAAVinterpreter-%Y-%m-%d-%Hh-%Mm-%S.%fs.scf')

    print 'Fetching output data...'
    theRESTBegin = time.time()
    theSAAVpedia.applyFilter(theArgs._get_kwargs())
    theSCFData = theSAAVpedia.data()
    theRESTEnd = time.time()
    print 'Estimated time for fetching data: {0:.3f}s'.format(theRESTEnd-theRESTBegin)

    print 'Writing {0} file...'.format(theOutputName)
    theWriter = file(theOutputName, 'w')
    for ithData in theSCFData:
        theWriter.write('\t'.join(ithData)+'\n')
    theWriter.close()

    theEndTime = time.time()
    print 'Total estimated time: {0:.3f}s'.format(theEndTime-theStartTime)

    pass

if __name__ == '__main__':
    theParser = argparse.ArgumentParser(description='SAAVpedia: SAAVinterpreter program')
    theParser.add_argument('--input', dest='input', help='SCF input file path')
    theParser.add_argument('--output', dest='output', help='SCF output file path')

    theParser.add_argument('--SAAV_QS', action='store_true', help='Quality Score(QS)')
    theParser.add_argument('--SAAV_Pvalue', action='store_true', help='P-value from the quality score distribution in SAAV list of input sample.')
    theParser.add_argument('--SAAV_filter', action='store_true', help='filter status')
    theParser.add_argument('--SAAV_Pos', action='store_true', help='Single amino-acid variant position(Pos)')
    theParser.add_argument('--SAAV_Ref', action='store_true', help='Single amino-acid variant reference(Ref) sequence')
    theParser.add_argument('--SAAV_Alt', action='store_true', help='Single amino-acid variant alteration(Alt) base.')
    theParser.add_argument('--SAAV_RS', action='store_true', help='Peptide reference sequence(RS) which contains one or more SAAVs.')
    theParser.add_argument('--SAAV_AS', action='store_true', help='Peptide alteration sequence(AS) which contains one or more SAAVs.')
    theParser.add_argument('--SAAV_SDM', action='store_true', help='Strand direction matching(SDM) information of SNV and SAAV.')
    theParser.add_argument('--SAAV_EC', action='store_true', help='Error correction(EC)')
    theParser.add_argument('--SNV_Chr', action='store_true', help='Chromosome(Chr). ')
    theParser.add_argument('--SNV_Pos', action='store_true', help='Single nucleotide variant position(Pos).')
    theParser.add_argument('--SNV_Ref', action='store_true', help='Single nucleotide variant reference(Ref) base')
    theParser.add_argument('--SNV_Alt', action='store_true', help='Single nucleotide variant alteration(Alt) base.')
    theParser.add_argument('--SNV_Strand', action='store_true', help='DNA strand information of each SNV.')
    theParser.add_argument('--SNV_ID', action='store_true', help='Genomic variation reference ID (dbSNP, Cosmic)')
    theParser.add_argument('--SNV_1000G_OC', action='store_true', help='Occurring(OC) in the 1000 Genomes variant list.')
    theParser.add_argument('--SNV_1000G_T_MAF', action='store_true', help='Minor allele frequency(MAF) in the 1000Genome population.')
    theParser.add_argument('--SNV_1000G_EAS_MAF', action='store_true', help='Minor allele frequency(MAF) in the 1000Genome East Asian population.')
    theParser.add_argument('--SNV_1000G_AMR_MAF', action='store_true', help='Minor allele frequency(MAF) in the 1000Genome American population.')
    theParser.add_argument('--SNV_1000G_EUR_MAF', action='store_true', help='Minor allele frequency(MAF) in the 1000Genome European population.')
    theParser.add_argument('--SNV_1000G_AFR_MAF', action='store_true', help='Minor allele frequency(MAF) in the 1000Genome African population.')
    theParser.add_argument('--SNV_1000G_SAS_MAF', action='store_true', help='Minor allele frequency(MAF) in the 1000Genome South Asian population.')
    theParser.add_argument('--SNV_VT', action='store_true', help='Variant Type(VT)')
    theParser.add_argument('--SNV_ESP_OC', action='store_true', help='Occurring(OC) in the Exome Sequencing Project(ESP) variant list.')
    theParser.add_argument('--SNV_ESP_AF_MAF', action='store_true', help='Minor allele frequency(MAF) in the ESP African(AF) population.')
    theParser.add_argument('--SNV_ESP_EU_MAF', action='store_true', help='Minor allele frequency(MAF) in the ESP European(EU) population.')
    theParser.add_argument('--SNV_ExAC_OC', action='store_true', help='Occurring(OC) in the Exome Aggregation Consortium(ExAC) variant list.')
    theParser.add_argument('--SNV_Phenotype', action='store_true', help='Phenotype term.')
    theParser.add_argument('--SNV_Source', action='store_true', help='Reference database of SNV_Phenotype.')
    theParser.add_argument('--SNV_OID', action='store_true', help='EFO ontology ID(OID) of SNV_Phenotype.')
    theParser.add_argument('--SNV_Phe_CLS', action='store_true', help='EFO phenotype class(CLS) name of SNV_Phenotype.')
    theParser.add_argument('--SNV_DB', action='store_true', help='Drug bank(DB) ID.')
    theParser.add_argument('--SNV_DN', action='store_true', help='Drug name(DN)')
    theParser.add_argument('--SNV_DT', action='store_true', help='Drug type(DT)')
    theParser.add_argument('--SNV_PGT', action='store_true', help='Pharmacological gene type')
    theParser.add_argument('--PROTEIN_Uniplot', action='store_true', help='Uniplot identifier')
    theParser.add_argument('--PROTEIN_Nextprot', action='store_true', help='NextProt identifier')
    theParser.add_argument('--PROTEIN_PDB', action='store_true', help='Protein Data Bank(PDB) identifier')
    theParser.add_argument('--PROTEIN_Enembl_Pro', action='store_true', help='Ensembl protein(Pro) identifier')
    theParser.add_argument('--TRANSCRIPT_Enembl_Tra', action='store_true', help='Ensembl transcript(Tra) identifier')
    theParser.add_argument('--GENE_Enembl_Gen', action='store_true', help='Ensembl Gene(Gen) identifier')
    theParser.add_argument('--GENE_GF', action='store_true', help='Gene Families(GF)')
    theParser.add_argument('--GENE_GD', action='store_true', help='Gene description(GD)')
    theParser.add_argument('--GENE_GS', action='store_true', help='Gene Symbol(GS)')
    theParser.add_argument('--GENE_HGNC', action='store_true', help='HGNC ID')
    theParser.add_argument('--GENE_UCSC', action='store_true', help='UCSC ID')
    theParser.add_argument('--GENE_Cosmic', action='store_true', help='Cosmic Gene ID')
    theParser.add_argument('--GENE_Entrez', action='store_true', help='Entrez ID')
    theParser.add_argument('--GENE_RefSeq', action='store_true', help='Reference Sequence (RefSeq) accession number.')
    theParser.add_argument('--Disease_Omim', action='store_true', help='Omim ID')
    theParser.add_argument('--DRUG_PharmGKB', action='store_true', help='PharmGKB ID')
    theParser.add_argument('--DRUG_CHEMBL', action='store_true', help='CHEMBL ID')
    theParser.add_argument('--Literature_PMID', action='store_true', help='Pubmed ID')
    theParser.add_argument('--Biological_function_STRING', action='store_true', help='STRING ID')
    theParser.add_argument('--Biological_function_Vega', action='store_true', help='Vega ID')
    theParser.add_argument('--Biological_function_ENA', action='store_true', help='European Nucleotide Archive ID')

    '''
    theParser.add_argument('--vsn_1000g_t_maf', action='store_true', help='Minor allele frequency in the 1000 Genome popuplation.')
    theParser.add_argument('--vsn_1000g_eas_maf', action='store_true', help='Minor allele frequency in the 1000 Genome East Asian popuplation.')
    theParser.add_argument('--vsn_1000g_amr_maf', action='store_true', help='Minor allele frequency in the 1000 Genome American popuplation.')
    theParser.add_argument('--vsn_1000g_eur_maf', action='store_true', help='Minor allele frequency in the 1000 Genome European popuplation.')
    theParser.add_argument('--vsn_1000g_afr_maf', action='store_true', help='Minor allele frequency in the 1000 Genome African popuplation.')
    theParser.add_argument('--vsn_1000g_sas_maf', action='store_true', help='Minor allele frequency in the 1000 Genome South Asian popuplation.')
    theParser.add_argument('--vsn_vt', action='store_true', help='Variant type.')
    theParser.add_argument('--vsn_esp_oc', action='store_true', help='Occurring in the Exome Sequencing Project variant list')
    theParser.add_argument('--vsn_esp_af_maf', action='store_true', help='Minor allele frequency in the ESP African popuplation.')
    theParser.add_argument('--vsn_esp_eu_maf', action='store_true', help='Minor allele frequency in the ESP European popuplation.')
    theParser.add_argument('--vsn_exac_oc', action='store_true', help='Occurring in the Exome Aggregation Consortium variant list')
    theParser.add_argument('--vsc_phenotype',action='store_true', help='Phenotype term')
    theParser.add_argument('--vsc_source',action='store_true', help='Reference database of VSC_phenotype')
    theParser.add_argument('--vsc_oid',action='store_true', help='EFO ontology ID of VSC_Phenotype')
    theParser.add_argument('--vsc_phe_cls',action='store_true', help='EFO phenotype class name of VSC_Phenotype')
    theParser.add_argument('--vsd_db',action='store_true', help='Drug bank ID')
    theParser.add_argument('--vsd_dn',action='store_true', help='Drug name')
    theParser.add_argument('--vsd_dt',action='store_true', help='Drug type')
    theParser.add_argument('--vsd_pgt',action='store_true', help='Pharmacological gene type')
    theParser.add_argument('--brp_uniprot',action='store_true', help='Uniprot identifier')
    theParser.add_argument('--brp_nextprot',action='store_true', help='Nextprot identitifer')
    theParser.add_argument('--brp_pdb',action='store_true', help='Protein Data Bank identifier')
    theParser.add_argument('--brp_ensembl_pro',action='store_true', help='Ensembl protein identifier')
    theParser.add_argument('--brp_ensembl_tra',action='store_true', help='Ensembl transcript identifier')
    theParser.add_argument('--brp_ensembl_gen',action='store_true', help='Ensembl Gene identifier')
    theParser.add_argument('--brp_gf',action='store_true', help='Gene Families')
    theParser.add_argument('--brp_gd',action='store_true', help='Gene description')
    theParser.add_argument('--brp_gs',action='store_true', help='Gene Symbol')
    theParser.add_argument('--brp_hgnc',action='store_true', help='HGNC ID')
    theParser.add_argument('--brp_ucsc',action='store_true', help='UCSC ID')
    theParser.add_argument('--brp_gcosmic',action='store_true', help='Cosmic Gene ID')
    theParser.add_argument('--brp_entrez',action='store_true', help='Entrez ID')
    theParser.add_argument('--brp_refseq',action='store_true', help='Reference Sequence (RefSeq) accession number.')
    theParser.add_argument('--brp_omim',action='store_true', help='Omim ID')
    theParser.add_argument('--brp_pharmgkb',action='store_true', help='PharmGKB ID')
    theParser.add_argument('--brp_chembl',action='store_true', help='CHEMBL ID')
    theParser.add_argument('--brp_pmid',action='store_true', help='Pubmed ID')
    theParser.add_argument('--brp_string',action='store_true', help='STRING ID')
    theParser.add_argument('--brp_vega',action='store_true', help='Vega ID')
    theParser.add_argument('--brp_ena',action='store_true', help='European Nucleotide Archive ID')

    theParser.add_argument('--vsn_1000g_oc', action='store_true', help='Occurring in the 1000 Genomes variant list')
    theParser.add_argument('--vsn_1000g_t_maf', action='store_true', help='Minor allele frequency in the 1000 Genome popuplation.')
    theParser.add_argument('--vsn_1000g_eas_maf', action='store_true', help='Minor allele frequency in the 1000 Genome East Asian popuplation.')
    theParser.add_argument('--vsn_1000g_amr_maf', action='store_true', help='Minor allele frequency in the 1000 Genome American popuplation.')
    theParser.add_argument('--vsn_1000g_eur_maf', action='store_true', help='Minor allele frequency in the 1000 Genome European popuplation.')
    theParser.add_argument('--vsn_1000g_afr_maf', action='store_true', help='Minor allele frequency in the 1000 Genome African popuplation.')
    theParser.add_argument('--vsn_1000g_sas_maf', action='store_true', help='Minor allele frequency in the 1000 Genome South Asian popuplation.')
    theParser.add_argument('--vsn_vt', action='store_true', help='Variant type.')
    theParser.add_argument('--vsn_esp_oc', action='store_true', help='Occurring in the Exome Sequencing Project variant list')
    theParser.add_argument('--vsn_esp_af_maf', action='store_true', help='Minor allele frequency in the ESP African popuplation.')
    theParser.add_argument('--vsn_esp_eu_maf', action='store_true', help='Minor allele frequency in the ESP European popuplation.')
    theParser.add_argument('--vsn_exac_oc', action='store_true', help='Occurring in the Exome Aggregation Consortium variant list')
    theParser.add_argument('--vsc_phenotype',action='store_true', help='Phenotype term')
    theParser.add_argument('--vsc_source',action='store_true', help='Reference database of VSC_phenotype')
    theParser.add_argument('--vsc_oid',action='store_true', help='EFO ontology ID of VSC_Phenotype')
    theParser.add_argument('--vsc_phe_cls',action='store_true', help='EFO phenotype class name of VSC_Phenotype')
    theParser.add_argument('--vsd_db',action='store_true', help='Drug bank ID')
    theParser.add_argument('--vsd_dn',action='store_true', help='Drug name')
    theParser.add_argument('--vsd_dt',action='store_true', help='Drug type')
    theParser.add_argument('--vsd_pgt',action='store_true', help='Pharmacological gene type')
    theParser.add_argument('--brp_uniprot',action='store_true', help='Uniprot identifier')
    theParser.add_argument('--brp_nextprot',action='store_true', help='Nextprot identitifer')
    theParser.add_argument('--brp_pdb',action='store_true', help='Protein Data Bank identifier')
    theParser.add_argument('--brp_ensembl_pro',action='store_true', help='Ensembl protein identifier')
    theParser.add_argument('--brp_ensembl_tra',action='store_true', help='Ensembl transcript identifier')
    theParser.add_argument('--brp_ensembl_gen',action='store_true', help='Ensembl Gene identifier')
    theParser.add_argument('--brp_gf',action='store_true', help='Gene Families')
    theParser.add_argument('--brp_gd',action='store_true', help='Gene description')
    theParser.add_argument('--brp_gs',action='store_true', help='Gene Symbol')
    theParser.add_argument('--brp_hgnc',action='store_true', help='HGNC ID')
    theParser.add_argument('--brp_ucsc',action='store_true', help='UCSC ID')
    theParser.add_argument('--brp_gcosmic',action='store_true', help='Cosmic Gene ID')
    theParser.add_argument('--brp_entrez',action='store_true', help='Entrez ID')
    theParser.add_argument('--brp_refseq',action='store_true', help='Reference Sequence (RefSeq) accession number.')
    theParser.add_argument('--brp_omim',action='store_true', help='Omim ID')
    theParser.add_argument('--brp_pharmgkb',action='store_true', help='PharmGKB ID')
    theParser.add_argument('--brp_chembl',action='store_true', help='CHEMBL ID')
    theParser.add_argument('--brp_pmid',action='store_true', help='Pubmed ID')
    theParser.add_argument('--brp_string',action='store_true', help='STRING ID')
    theParser.add_argument('--brp_vega',action='store_true', help='Vega ID')
    theParser.add_argument('--brp_ena',action='store_true', help='European Nucleotide Archive ID')
    '''
    theArgs = theParser.parse_args(sys.argv[1:])

    if not theArgs.input:
        theParser.print_help()
    else :
        main(theArgs)
    pass
