import pandas as pd
from time import time
from baseq.utils.file_reader import read_file_by_lines
from baseq.drops import extract_barcode

def count_barcode(path, output, protocol, min_reads, topreads=100):
    """
    Count the number of each barcode, write a count file.
    Usages:
    ::
        from baseq.drops import count_barcode
        count_barcodes("10X.1.fq.gz", "bc.counts.txt", "10X", min_reads=50, topreads=1000)

    Returns:
        A barcode_count file in csv (bc.counts.txt)

        cellbarcode, counts
    """
    bc_counts = {}
    index = 0
    start = time()
    print("[info] Process the top {}M reads in {}".format(topreads, path))
    print("[info] Barcode with less than {} reads is discard".format(min_reads))
    lines = read_file_by_lines(path, topreads * 1000 * 1000, 4)
    for line in lines:
        index += 1
        bc = extract_barcode(protocol, line[1])
        if index % 1000000 == 0:
            print("[info] Processed {}M lines in {}s".format(index/1000000, round(time()-start, 2)))
            start = time()
        if bc == "":
            continue
        if bc in bc_counts:
            bc_counts[bc] += 1
        else:
            bc_counts[bc] = 1

    bc_counts_filter = []
    for k, v in bc_counts.items():
        if v >= min_reads:
            bc_counts_filter.append([k, v])

    print("[info] Barcode depth file: {}".format(output))
    df = pd.DataFrame(bc_counts_filter, columns=["barcode", "counts"])
    df.to_csv(output, sep=",", index=False)