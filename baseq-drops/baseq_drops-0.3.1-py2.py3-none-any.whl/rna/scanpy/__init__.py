import numpy as np
import pandas as pd
import scanpy.api as sc

class SCANPY:
    """
    An Scanpy Object:

    .. graphviz::

        digraph foo {
            rankdir=LR;
            node[shape=plaintext, style=filled, fillcolor="#C0D0C0"];
            "read" -> "filter" -> "variable Genes" -> "PCA"  -> "TSNE";
       }

    Usage:
    ::
        sc = SCANPY("outdir")
    """
    def __init__(self, path):
        # verbosity: errors (0), warnings (1), info (2), hints (3)
        sc.settings.verbosity = 3
        # low dpi (dots per inch) yields small inline figures
        sc.settings.set_figure_params(dpi=120)
        sc.logging.print_versions()
        results_file = './write/pmbc3k.h5ad'


    def read_cellranger(self, path):
        """
        Read the ouput of cellranger process:
        ::
            sc.read_cellranger('./data/pbmc3k_filtered_gene_bc_matrices/hg19/')
        Return: An annodata object

        """
        adata = sc.read(path + 'matrix.mtx', cache=True).T  # transpose the data
        adata.var_names = pd.read_csv(path + 'genes.tsv', header=None, sep='\t')[1]
        adata.obs_names = pd.read_csv(path + 'barcodes.tsv', header=None)[0]
        adata.var_names_make_unique()
        self.adata = adata

    def filter_mito(self):
        """
        For each cell compute fraction of counts in mito genes vs. all genes;
        Filter cells with less 5% of MT gene reads;
        """
        mito_genes = [name for name in self.adata.var_names if name.startswith('MT-')]
        self.adata.obs['percent_mito'] = np.sum(
            self.adata[:, mito_genes].X, axis=1).A1 / np.sum(self.adata.X, axis=1).A1
        # add the total counts per cell as observations-annotation to adata
        self.adata.obs['n_counts'] = self.adata.X.sum(axis=1).A1
        sc.pl.violin(self.adata, ['n_genes', 'n_counts', 'percent_mito'],
                     jitter=0.4, multi_panel=True)
        self.adata = self.adata[self.adata.obs['percent_mito'] < 0.05, :]


    def filter_quality(self, min_genes=200, min_cells=3):
        """
        Filtering by min number of genes and min number of cells;
        """
        sc.pp.filter_cells(self.adata, min_genes)
        sc.pp.filter_genes(self.adata, min_cells)

    def set_raw(self):
        """
        Set the .raw attribute of AnnData object to the logarithmized raw gene expression for later use in differential testing and visualizations of gene expression. This simply freezes the state of the AnnData object returned by sc.pp.log1p.
        """
        self.adata.raw = sc.pp.log1p(self.adata, copy=True)

    def variable_genes(self):
        """
        Per-cell normalize the data matrix  X, identify highly-variable genes and compute logarithm.

        Logarithmize the data.

        Regress out effects of total counts per cell and the percentage of mitochondrial genes expressed.
         Scale the data to unit variance.
        """
        sc.pp.normalize_per_cell(self.adata, counts_per_cell_after=1e4)
        filter_result = sc.pp.filter_genes_dispersion(
            self.adata.X, min_mean=0.0125, max_mean=3, min_disp=0.5)
        sc.pl.filter_genes_dispersion(filter_result)

        self.adata = self.adata[:, filter_result.gene_subset]
        sc.pp.log1p(self.adata)

        sc.pp.regress_out(self.adata, ['n_counts', 'percent_mito'])
        sc.pp.scale(self.adata, max_value=10)

    def PCA(self, results_file, marker="CST3"):
        self.adata.obsm['X_pca'] *= -1  # multiply by -1 to match Seurat
        sc.pl.pca_scatter(self.adata, color=marker)
        sc.pl.pca_variance_ratio(self.adata, log=True)
        self.adata.write(results_file)

    def TSNE(self):
        pass