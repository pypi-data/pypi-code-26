import pandas as pd


"""Example Google style docstrings.

This module demonstrates documentation as specified by the `Google Python
Style Guide`_. Docstrings may extend over multiple lines. Sections are created
with a section header and a colon followed by a block of indented text.

Example:
    Examples can be given using either the ``Example`` or ``Examples``
    sections. Sections support any reStructuredText formatting, including
    literal blocks::

        $ python example_google.py

Section breaks are created by resuming unindented text. Section breaks
are also implicitly created anytime a new section starts.

Attributes:
    module_level_variable1 (int): Module level variables may be documented in
        either the ``Attributes`` section of the module docstring, or in an
        inline docstring immediately following the variable.

        Either form is acceptable, but the two should not be mixed. Choose
        one convention to document module level variables and be consistent
        with it.

Todo:
    * For module TODOs
    * You have to also use ``sphinx.ext.todo`` extension

.. _Google Python Style Guide:
   https://google.github.io/styleguide/pyguide.html

"""

def quality_enrich(name, bampath, intervals):
    """
    Check the coverage depth and enrichment quality.
    ::
        from baseq.snv.qc.enrich import quality
        quality("sample01", "aligned.bam", "panel.bed")

    Returns:
        Sample/Total/Mapped/Map_Ratio/Dup_ratio/PCT_10X/PCT_30X/...

    Todo:
        * For module TODOs
        * Median Coverage...
        * Estimate on distribution bias/ Gini index?
    """

    from baseq.bam.bamtype import BAMTYPE
    bam = BAMTYPE(bampath, bedfile=intervals)
    bam.stats_bases()
    bam.stats_duplicates()
    bam.stats_regions()
    bam.stats_region_coverage(1000)

    stats = {
        "Sample" : name,
        "Total" : bam.reads_total,
        "Mapped" : bam.reads_mapped,
        "Map_Ratio" : bam.mapping_ratio,
        "Dup_ratio" : bam.dup_ratio,
        "Mean_Depth": bam.mean_depth,
        "PCT_10X" :  bam.pct_10X,
        "PCT_30X": bam.pct_30X,
        "PCT_50X": bam.pct_50X,
        "PCT_100X": bam.pct_100X,
    }

    return stats



def quality_enrich_multiple(bamlist="", name="", bampath="", intervals=""):
    """
    Check the coverage depth and enrichment quality for multiple bamfiles, export a Excel File.
    Usage
    ::
        #bamlist.txt:
        sample01 sample01.bam
        sample02 sample02.bam
        ...

        from baseq.snv.qc.enrich import quality_multiple
        quality_multiple(bamlist = "bamlist.txt", intervals = "panel.bed")

    Result:
    ::
        QC.xls

    .. image:: http://p8v379qr8.bkt.clouddn.com/SNV.quality.jpg

    """

    if bamlist:
        with open(bamlist, 'r') as file:
            lines = file.readlines()
        bams = [line.strip().split() for line in lines]
    else:
        bams = [[name, bampath]]

    print("[info] {} Bam files".format(len(bams)))
    results = []

    import multiprocessing as mp
    pool = mp.Pool(processes = 1)
    for bam in bams:
        results.append(pool.apply_async(quality_enrich, (bam[0], bam[1], intervals)))
    pool.close()
    pool.join()
    print(results)
    results = [x.get() for x in results]

    df = pd.DataFrame(results,
                      columns=["Sample", "Total", "Mapped", "Map_Ratio", "Dup_ratio",
                               "Mean_Depth", "PCT_10X", "PCT_30X", "PCT_50X", "PCT_100X"])
    print("[info] Write QC Infos to {}".format("QC.xls"))
    df.to_excel("QC.xls")