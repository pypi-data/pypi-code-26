from baseq.mgt import get_config, run_cmd

def bowtie2_sort(fq1, fq2, bamfile, genome, reads=5*1000*1000, thread=8):
    """
    Align the fastq reads using bowtie2 and sort the samfile.
    ::
        from baseq.align.bowtie2 import bowtie2_sort

        #for single reads
        bowtie2_sort("read.1.fq.gz", "", "sample.bam", "hg38")

        #for multiple reads
        bowtie2_sort("read.1.fq.gz", "read.2.fq.gz", "sample.bam", "hg38")

    Results:
    ::
        sample.bam
        sample.bam.stats
    """

    bowtie2 = get_config("CNV", "bowtie2")
    samtools = get_config("CNV", "samtools")
    bowtie2_ref = genome
    samfile = bamfile+".sam"
    bamfile = bamfile
    statsfile = bamfile+".stat"

    print("[info] Bamfile Path : {}".format(bamfile))

    #Run Bowtie
    if fq1 and fq2:
        bowtie_cmd = [bowtie2, '-p', str(thread), '-x', bowtie2_ref, '-u', str(reads), '-1', fq1, '-2', fq2, '>', samfile]
    else:
        bowtie_cmd = [bowtie2, '-p', str(thread), '-x', bowtie2_ref, '-u', str(reads), '-U', fq1, '>', samfile]
    run_cmd("bowtie alignment", " ".join(bowtie_cmd))

    #run Samtools
    samtools_sort = [samtools, 'sort -@ ', str(thread), '-o', bamfile, samfile, ";", samtools, "index", bamfile, "; rm", samfile]
    run_cmd("samtools sort", " ".join(samtools_sort))

    #run flagstats
    cmd_stats = [samtools, "flagstat", bamfile, ">", statsfile]
    run_cmd("samtools stats", " ".join(cmd_stats))

    return bamfile