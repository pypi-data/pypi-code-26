#!/home/data1/tools/bin/anaconda/bin/python
import sys, os, re, math, subprocess

db_path = "/home/data1/services/ResFinder/database_archive/database-3.0_Test_indels"
db_out_path = db_path + "/KMA_indel_rf/resfinder_db_index"
kma_path = "/home/data1/services/cgMLSTFinder/database_cgs/KMA/kma_index"


# Read database files into one file


all_fasta_filename = "%s/KMA_index_rf/all_fasta.fsa"%(db_path)
with open(all_fasta_filename, "w") as outfile:
    subprocess.call("cat %s/*.fsa >> %s"%(db_path, all_fasta_filename), shell=True)

# Index the db for kma
KMA_cmd = "%s -i %s -o %s "%(kma_path, all_fasta_filename, db_out_pat)
os.system(KMA_cmd)

