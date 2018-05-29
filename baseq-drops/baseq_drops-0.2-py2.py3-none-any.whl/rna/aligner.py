import sys, os, re
from baseq.mgt import get_config, run_cmd
from baseq.fastq.files import check
import pandas as pd

script = """
cd {0}
{1} --pen-noncansplice 1000000 -x {2} -1 {3} -2 {4} -p 8 -S hisat2_align.sam
{5} view -b -u -S hisat2_align.sam > hisat2_align.bam
{5} sort -@ 8 hisat2_align.bam hisat2_sorted
{5} index hisat2_sorted.bam
{4} flagstat hisat2_sorted.bam > hisat2_sorted.bam.stat
rm hisat2_align.sam hisat2_align.bam
"""

script1 = """
cd {0}
{1} --pen-noncansplice 1000000 -x {2} -U {3} -p 8 -S hisat2_align.sam
{4} view -b -u -S hisat2_align.sam > hisat2_align.bam
{4} sort -@ 8 hisat2_align.bam hisat2_sorted
{4} index hisat2_sorted.bam
{4} flagstat hisat2_sorted.bam > hisat2_sorted.bam.stat
rm hisat2_align.sam hisat2_align.bam
"""


script_star ="""
cd {} 
{} --runThreadN 10 --genomeDir {} --readFilesCommand zcat --readFilesIn {} {} --outSAMtype BAM SortedByCoordinate --outSAMstrandField intronMotif
{} flagstat Aligned.sortedByCoord.out.bam > flagstat.txt
"""

script_star_2 ="""
cd {} 
{} --runThreadN 10 --genomeDir {} --readFilesCommand zcat --readFilesIn {} --outSAMtype BAM SortedByCoordinate --outSAMstrandField intronMotif
{} flagstat Aligned.sortedByCoord.out.bam > flagstat.txt
"""

def HISAT2(fq1, fq2, genome, outdir):
    """
    Alignment using HISAT2_ .

    .. _HISAT2: http://ccb.jhu.edu/software/hisat2/index.shtml

    Usage:
    ::
        HISAT2("1.fq.gz", "2.fq.gz", "hg38", "RNAseq")
    Output:
    ::
        RNAseq
        |---hisat2_sorted.bam
        |---hisat2_sorted.bam.bai
        |---hisat2_sorted.bam.stat
    """
    hisat = get_config("RNA", "hisat")
    samtools = get_config("RNA", "samtools")
    hisat_ref = get_config("RNA_ref_"+genome, "hisat_index")

    if not os.path.exists(outdir):
        os.mkdir(outdir)

    if fq1 and fq2 and os.path.exists(fq1) and os.path.exists(fq2):
        cmd = script.format(outdir, hisat, hisat_ref, fq1, fq2, samtools)
    elif fq1 and os.path.exists(fq1):
        cmd = script1.format(outdir, hisat, hisat_ref, fq1, samtools)
    else:
        pass
    run_cmd("Hisat", cmd)


def STAR(fq1, fq2, genome, outdir):
    """
    Run STAR_, return the bamfile path;

    .. _STAR: https://github.com/alexdobin/STAR

    Usage:
    ::
        STAR("1.fq.gz", "2.fq.gz", "hg38", "RNAseq")

    Output:
    ::
        RNAseq
        |---Aligned.sortedByCoord.out.bam
        |---SJ.out.tab
        |---...
    """
    star = get_config("RNA", "star")
    star_index = get_config("RNA_ref_" + genome, "star_index")
    samtools = get_config("RNA", "samtools")

    if not os.path.exists(outdir):
        os.mkdir(outdir)

    if fq1 and fq2 and os.path.exists(fq1) and os.path.exists(fq2):
        cmd = script_star.format(outdir, star, star_index, fq1, fq2, samtools)
    elif fq1 and os.path.exists(fq1):
        cmd = script_star_2.format(outdir, star, star_index, fq1, samtools)
    else:
        pass
    run_cmd("STAR", cmd)