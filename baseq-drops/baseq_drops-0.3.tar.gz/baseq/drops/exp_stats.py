import pandas as pd

def stats_table(path):
    """
    Stats on the table of ...
    """
    df = pd.read_table(path, index_col=0)

    #Number of cells
    cells = len(df.index)

    #Number of genes
    gene_counts = (df>0).astype(int).sum(axis=1).median()
    UMI_counts = df.sum(axis=1).median()

    print("Cells Number: {}".format(cells))
    print("Median UMI Counts: {}".format(UMI_counts))
    print("Median Gene Counts: {}".format(gene_counts))