#!/home/data1/tools/bin/anaconda/bin/python
import sys, os, re, math, subprocess

#Usage: ./index_pointfinder_db.py <species>

if len(sys.argv) != 2:
    sys.exit("Usage: ./index_pointfinder_db.py <species>")
else:
    species = sys.argv[1]

out_path = species 
if not os.path.exists(out_path):
    os.makedirs(out_path)

kma_path = "/home/data1/services/cgMLSTFinder/database_cgs/KMA/kma_index"
db_path = "/home/data1/services/ResFinder/database_archive/database-3.0_Test_indels/%s"%species
#out_path = /home/data1/services/ResFinder/database_archive/database-3.0_Test_indels/tuberculosis/KMA_indexes
out_path = db_path + "/" 
if not os.path.exists(out_path):
    os.makedirs(out_path)


# open gene list and write all genes into one file
with open(db_path + "/genes.txt", "r") as gene_file:
    gene_list = [gene.strip() for gene in gene_file.readlines()]

print(gene_list)

out_lst = []

for gene in gene_list:
    with open(db_path + "/" + gene + ".fsa", "r") as gene_seq:
        header = gene_seq.readline()
        if header.startswith(">") == False:
            print("ERROR, this is not a header, %s"%header)
            sys.exit(1)
        seq_lines = [seq.strip() for seq in gene_seq.readlines()]
        seq = "\n".join(seq_lines)
        out_lst.append(">" + gene + "\n" + seq)

with open("all_fasta.fsa", "w") as out_file:
    out_file.write("\n".join(out_lst))


# Index the db for kma
KMA_cmd = "%s -i %s -o %s" %(kma_path, "all_fasta.fsa", out_path + species)
os.system(KMA_cmd)

