import pandas as pd

from baseq.drops.apa.scaner import detect_peaks

def scan_genes(genome, bam, name):
    """
    Read the gencode annotation of the genome and find the genes that with
    Usage:
    ::
        scan_genes("hg38", "sample01.bam", "sample01")
    Results:
    ::
        peaks.sample01.txt/peaks.sample01.xls
        peaks_image_sample01/**.png
    """

    from baseq.bam import BAMTYPE
    from baseq.rna.gtf.gencode import read_gencode

    df = read_gencode(genome, "UTR")
    df['length'] = df.end - df.start
    df = df.sort_values(by=['length'])
    df = df.groupby("gene").last()
    df = df.loc[df.length>1000]
    bam = BAMTYPE(bam)

    import multiprocessing as mp
    pool = mp.Pool(processes=20)
    results = []
    for index, row in df.iterrows():
        results.append(pool.apply_async(detect_peaks, (bam, index, row['chr'], row['start'], row['end'], 50)))
    pool.close()
    pool.join()

    results = [x.get() for x in results]
    results = [y for x in results for y in x]
    results = [df.loc[x[0],:].tolist() + x  for x in results]
    df_peaks = pd.DataFrame(results, columns=["chr", "start", 'end', 'strand', 'transc',
                                              'exon', 'length', 'gene', 'pos', 'mean_depth',
                                              "mid", "left", "right", "counts"])

    df_peaks = df_peaks.drop(columns=["transc", 'exon'])
    file_tsv = "peaks.{}.txt".format(name)
    file_xls = "peaks.{}.xls".format(name)
    df_peaks.to_csv("peaks.{}.txt".format(name), sep="\t")
    df_peaks.to_excel("peaks.{}.xls".format(name))
    print("[info] The peaks files are write to: {}/{}".format(file_tsv, file_xls))