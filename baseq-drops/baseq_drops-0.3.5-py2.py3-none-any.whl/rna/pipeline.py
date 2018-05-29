import sys, os, re
from baseq.mgt import get_config, run_cmd
from baseq.fastq.files import check
import pandas as pd
from baseq.rna.quantify import cufflinks
from baseq.rna.aligner import HISAT2, STAR

def quantify_cmd(fq1, fq2, genome, outdir, aligner="hisat", quantify="cufflinks"):
    """
    Integrate Aligner and Quantufier...
    """
    if aligner == "hisat":
        HISAT2(fq1, fq2, genome, outdir)
        bamfile = outdir+"/hisat2_sorted.bam"
    if aligner == "star":
        STAR(fq1, fq2, genome, outdir)
        bamfile = outdir+"/Aligned.sortedByCoord.out.bam"

    #Quantify...
    if quantify == "cufflinks":
        cufflinks(genome, bamfile, outdir)


def align_quantify(name, fq1, fq2, samplefile, genome, aligner="hisat", quantify="cufflinks", parallel=4):
    """
    This function uses HISAT2_ to map RNA-Seq reads against genome. And then bam file(s) is quantifity by cufflinks.
    Output files include indexed bam file and QC statistics. A sample name list is required if you want to run multiple samples.
    Sample list at least has two columns which the fist columns is the sample name and the second(and third)
    is the absolute path of fastq files.

    .. _HISAT2: http://ccb.jhu.edu/software/hisat2/manual.shtml

    Example of sample list(tab delimited):
    ::
        # singel-end read dataset
        sample_01   ./sample_01.1.fq.gz
        sample_02   ./sample_02.1.fq.gz
        # paired-end read dataset
        sample_03   ./sample_03.1.fq.gz   ./sample_03.2.fq.gz
        sample_04   ./sample_04.1.fq.gz   ./sample_04.2.fq.gz
        sample_05   ./sample_05.1.fq.gz   ./sample_05.2.fq.gz

    Usage:
    ::
        # in Python
        run_multiple_hisat(name, fq1, fq2, path, genome, outdir, parallel=4)

        # single sample
        baseq-RNA run_hisat -g hg38 -n Hisat -1 sample_03.1.fq.gz -2 sample_03.2.fq.gz
        baseq-RNA run_hisat -g hg38 -n Hisat -1 sample_01.1.fq.gz

        # multiple samples
        ## Use hisat and cufflinks
        baseq-RNA run_hisat -n Hisat -m samples.txt -g hg38
        ## Use STAR and cufflinks
        baseq-RNA run_hisat -n Hisat2 -m samples.txt -g hg38 -p 3 -a star

    Result:
    A folder named Hisat will be created:
    ::
        Hisat
        |---FPKM.txt (For cufflinks)
        |---Counts.txt (For Featurecounts)
        |---QC.txt
        |---sample01
        |   |---hisat2_sorted.bam
        |   |---hisat2_sorted.bam.stat
        |   |---genes.fpkm_tracking (if cufflinks used..)
        |   |---isoforms.fpkm_tracking (if cufflinks used..)
        |   |---...
        |---sample02
        |   |...
    """
    print("[info] Aligner is {}".format(aligner))

    samples = check(samplefile, name, fq1, fq2)
    print("[info] {} samples...".format(len(samples)))

    if not os.path.exists(name):
        os.mkdir(name)

    import multiprocessing as mp
    pool = mp.Pool(processes=parallel)
    results = []
    for sample in samples:
        fq1 = sample[1]
        fq2 = sample[2]
        outdir = name+"/"+sample[0]
        results.append(pool.apply_async(quantify_cmd, (fq1, fq2, genome, outdir, aligner, quantify,)))
    pool.close()
    pool.join()
    [x.get() for x in results]

def build_FPKM_table(processdir, samplefile, outpath):
    """
    This tool is aim to generate a FPKM table of all samples after cufflinks quantification. 
    The sample list used in alignment step is also required. In the process directory, 
    each sample do have its own directory named as sample name for cufflinks output.
    Usage:
    ::
      # command line
      baseq-RNA aggr_FPKM_QC -d /alignment/outputdir/results -m /path/of/sample_list.txt -o ./
      # python
      build_FPKM_table("/alignment/outputdir/results", "/path/of/sample_list.txt", "./")

    Return:
    ::
      FPKM_table.txt
    """
    samples = check(samplefile)
    sample_names = [sample[0] for sample in samples]
    fpkm_file_path = outpath + "fpkm.txt"

    qc_file_path = outpath + "qc.txt"
    fpkm = {}
    qc = ["\t".join(['sample', 'reads', 'mapped', 'ratio', 'genecounts'])]
    for sample in sample_names:
        #build fpkm table
        sample_fpkm = []
        salmon_gene_path = os.path.join(processdir, sample, 'genes.fpkm_tracking')
        if not os.path.exists(salmon_gene_path):
            print("[info] File not exists for {}".format(sample))
            continue
        with open(salmon_gene_path, 'r') as infile:
            infile.readline()
            for line in infile:
                infos = re.split("\t", line)
                gene = infos[4]
                sample_fpkm.append(float(infos[9]))
                if not gene in fpkm:
                    fpkm[gene] = [float(infos[9])]
                else:
                    fpkm[gene].append(float(infos[9]))

        #Genes Detected
        genes_FPKM_1 = sum([1 for x in sample_fpkm if x>=1])

        #build QC data
        metainfo = os.path.join(processdir, sample, 'flagstat.txt')
        with open(metainfo, "r") as file:
            qc_info = file.readlines()
            datas = [x.split(" ") for x in qc_info]
            qc_sample = [sample, int(datas[0][0]), int(datas[4][0]), float(int(datas[4][0]))/int(datas[0][0]), genes_FPKM_1]
            qc.append("\t".join([str(x) for x in qc_sample]))

    #Write FPKM
    fpkm_file = open(fpkm_file_path, "w")
    fpkm_file.write("\t".join(["gene"] + sample_names) + "\n")
    for gene in fpkm:
        sum_fpkm_genes = sum(fpkm[gene])
        if sum_fpkm_genes > 0:
            fpkm_file.write("\t".join([gene] + [str(x) for x in fpkm[gene]]) + "\n")
    fpkm_file.close()
    print("[info] FPKM file: {}".format(fpkm_file_path))

    #Write QC Table
    qc_file = open(qc_file_path, "w")
    qc_file.writelines("\n".join(qc))
    qc_file.close()

