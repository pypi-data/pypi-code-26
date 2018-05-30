import click
import os
from . import error

def print_tsv_errors(errors, fh, print_all=True, header=True, print_value=False):
    errors = sorted(errors, key=error.error_sort_key)

    if not print_all:
        errors = error.filter_first_seen(errors)

    if print_value:
        outkeys = ['sheet', 'column', 'row', 'value', 'message']
    else:
        outkeys = ['sheet', 'column', 'row', 'message']

    outlines = []
    if header:
        outlines.append('#%s' % '\t'.join(outkeys))

    for e in errors:
        # Convert all values to unicode strings and concatenate before output
        e = error.stringify(e)
        outlines.append('\t'.join([e[k] for k in outkeys]))

    fh.write(os.linesep.join(outlines) + os.linesep)
