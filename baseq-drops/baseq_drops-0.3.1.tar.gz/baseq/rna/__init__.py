import click
CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])

@click.group(context_settings=CONTEXT_SETTINGS)
def cli():
    click.echo("Welcome to baseq-RNA")

from .cmd import *

__all__ = ['run_salmon','run_multiple_salmons',
           'HISAT2', 'STAR',
           'cufflinks', 'featureCounts',
           'align_quantify',
           'build_FPKM_table',  'build_tpm_table'
           ]

from baseq.rna.salmon import *
from baseq.rna.aligner import HISAT2, STAR
from baseq.rna.quantify import cufflinks,featureCounts
from baseq.rna.pipeline import align_quantify, build_FPKM_table