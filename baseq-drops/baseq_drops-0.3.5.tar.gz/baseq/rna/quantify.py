import sys, os, re
from baseq.mgt import get_config, run_cmd
from baseq.fastq.files import check
import pandas as pd

def cufflinks(genome, bampath, outpath):
    """
    Run cufflinks. Receive genome, get the path of "cufflinks_anno" from "RNA_ref_<geome>" section.
    Default using 8 thread.
    Usage:
    ::
        from baseq.rna.quantify import cufflinks
        cufflinks("hg19", "sample.sort.bam", "./cuffs")
    Results:
    ::
        cuffs
        |---genes.fpkm_tracking
        |---genes.fpkm_tracking
        |---transcripts.gtf
        |---skipped.gtf
    """
    cufflinks = get_config("RNA", "cufflinks")
    cufflinks_anno = get_config("RNA_ref_"+genome, "cufflinks_anno")
    cufflinks_cmd = "{} -q -o {} -p 8 -G {} {}".format(cufflinks, outpath, cufflinks_anno, bampath)
    run_cmd("Hisat", cufflinks_cmd)

def listofbam(samplefile, bampath):
    bamfile = []
    if samplefile:
        samples = check(samplefile)
        sample_names = [sample[0] for sample in samples]
        for name in sample_names:
            bamname = os.listdir(os.path.join(bampath,name))
            bamfile.append("".join([os.path.join(bampath,name,fn) for fn in bamname if fn[-4:] == ".bam"]))
            print(bamfile)
        bamlist = " ".join([str(file) for file in bamfile])
    else:
        bamname = os.listdir(bampath)
        bamfile.append("".join([os.path.join(bampath,fn) for fn in bamname if fn[-4:] == ".bam"]))
        bamlist = " ".join([str(file) for file in bamfile])
    print(bamlist)
    return bamlist

def featureCounts(genome, feature, id, countsfile, bampath, seqtype, samplefile):
    """
    featureCounts_ takes as input SAM/BAM files and an annotation file including chromosomal coordinates
    of features. It outputs numbers of reads assigned to features (or meta-features). It also outputs stat
    info for the overall summrization results.

    .. _featureCounts: http://bioinf.wehi.edu.au/featureCounts/

    Usage:

    * For multiple datasets ,there are two kinds of bampath provided, one is suitable for all BAM files are in the same directory,
      the other one for BAM files seperated by directories named as sample names. If BAM files are seperated by directories,
      a sample list is also required
      ::
        # All BAM files in one directory
        your/bam/path
        |---sample_01.bam
        |---sample_02.bam
        |---sample_03.bam
        |---sample_04.bam
        # BAM files seperated by directories
        you/bam/path
        |---...
        |---sample01
        |   |---hisat2_sorted.bam
        |   |---...
        |---sample02
        |   |---hisat2_sorted.bam
        |   |---...
    * Feature type(e.g. exon, gene) and attirbute(e.g. gene_id, transcript_id, gene_name) of annotation are required,
      Attribute should be unique.
      ::
        # multiple datasets
        baseq-RNA featurecounts -g hg38 -f exon -d gene_id -t paired -m sample_names.txt -o HMC_test_features.txt -b /mnt/gpfs/Users/wufan/p16_baseq/hisat
        baseq-RNA featurecounts -g hg38 -f exon -d gene_id -t paired -o HMC_test_features.txt -b /mnt/gpfs/Users/wufan/p16_baseq/hisat
        # single datasets
        baseq-RNA featurecounts -g hg38 -f exon -d gene_id -t paired -o HMC_test_features.txt -b /mnt/gpfs/Users/wufan/p16_baseq/hisat/sample_01.bam

    Results:
    ::
      |---HMC_test_features.txt
      |---HMC_test_features.txt.csv
      |---HMC_test_features.txt.summary
    """
    featurecounts = get_config("RNA", "featurecounts")
    anno = get_config("RNA_ref_" + genome, "anno")
    if bampath[-4:] != ".bam" and samplefile:
        bamlist = listofbam(samplefile, bampath)
    elif bampath[-4:] != ".bam":
        bamlist = listofbam("",bampath)
    else:
        bamlist = bampath
    if seqtype == "single":
        featurecounts_cmd = "{} -T 5 -t {} -g {} -a {} -o {} {}".format(featurecounts, feature, id, anno, countsfile, bamlist)
    elif seqtype == "paired":
        featurecounts_cmd = "{} -p -T 5 -t {} -g {} -a {} -o {} {}".format(featurecounts, feature, id, anno, countsfile, bamlist)
    run_cmd("featurecounts", featurecounts_cmd)

    df = pd.read_table(countsfile, sep="\t",header=1)
    row_index = list(range(df.shape[0]))
    col_index = [0]
    for index in list(range(6,df.shape[1],1)):
         col_index.append(index)
    results = df.iloc[row_index, col_index]
    file = countsfile + ".csv"
    results.to_csv(file,index=False)

