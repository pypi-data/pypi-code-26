#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
    :platform: Unix
    :synopsis: Tool to compare filedef produces by dr2xml with outfile file from XIOS.

"""
import itertools
import os
import re
import sys
from multiprocessing import Pool
from xml.etree.ElementTree import parse

from context import ProcessingContext
from handler import Filename
from utils.constants import *
from utils.custom_exceptions import *
from utils.misc import _ArgumentParser, MultilineFormatter, DirectoryChecker, keyval_converter, \
    processes_validator, COLORS, ProcessContext, Print

__version__ = 'v{} {}'.format(VERSION, VERSION_DATE)


def get_args():
    """
    Returns parsed command-line arguments.

    :returns: The argument parser
    :rtype: *argparse.Namespace*

    """
    parser = _ArgumentParser(
        prog='XIOFileChecker',
        description=PROGRAM_DESC,
        formatter_class=MultilineFormatter,
        add_help=False,
        epilog=EPILOG)
    parser._optionals.title = OPTIONAL
    parser._positionals.title = POSITIONAL
    parser.add_argument(
        '-h', '--help',
        action='help',
        help=HELP)
    parser.add_argument(
        '-v', '--version',
        action='version',
        version='%(prog)s ({})'.format(__version__),
        help=VERSION_HELP)
    parser.add_argument(
        '-l', '--log',
        metavar='CWD',
        type=str,
        const='{}/logs'.format(os.getcwd()),
        nargs='?',
        help=LOG_HELP)
    parser.add_argument(
        '-d', '--debug',
        action='store_true',
        default=False,
        help=DEBUG_HELP)
    parser.add_argument(
        '-a', '--all',
        action='store_true',
        default=False,
        help=ALL_HELP)
    parser.add_argument(
        '--full-table',
        action='store_true',
        default=False,
        help=FULL_TABLE_HELP)
    parser.add_argument(
        'directory',
        action=DirectoryChecker,
        help=DIRECTORY_HELP)
    group = parser.add_mutually_exclusive_group(required=False)
    group.add_argument(
        '-x', '--xml',
        action=DirectoryChecker,
        nargs='+',
        help=XML_HELP)
    group.add_argument(
        '-c', '--card',
        action=DirectoryChecker,
        help=CARD_HELP)
    parser.add_argument(
        '--set-filter',
        metavar='FACET_KEY=REGEX',
        type=keyval_converter,
        action='append',
        help=SET_FILTER_HELP)
    parser.add_argument(
        '--max-processes',
        metavar='INT',
        type=processes_validator,
        default=4,
        help=MAX_PROCESSES_HELP)
    return parser.prog, parser.parse_args()


def yield_files(path):
    """
    Yields all non-hidden NetCDF file into the directory recursively scan.

    :param str path: The path to scan
    :returns: The filename deserialized with facets
    :rtype: *dict*

    """
    for root, _, filenames in os.walk(path, followlinks=True):
        for filename in filenames:
            if os.path.isfile(os.path.join(root, filename)) and re.search('^.*\.nc$', filename):
                yield filename


def get_patterns_from_files(filename):
    """
    Processes a filename.
    Each filename pattern is deserialized as a dictionary of facet: value.

    :param str filename: The path to scan
    :returns: The filename deserialized with facets
    :rtype: *dict*

    """
    # Get process content from process global env
    assert 'pctx' in globals().keys()
    pctx = globals()['pctx']
    with pctx.lock:
        Print.debug(COLORS.OKGREEN + '\nProcess netCDF file :: ' + COLORS.ENDC + '{}'.format(filename))
    fn = Filename(filename, pctx.filters)
    # Print progress
    with pctx.lock:
        pctx.progress.value += 1
        percentage = int(pctx.progress.value * 100 / pctx.nbcdf)
        msg = COLORS.OKGREEN + '\rProcess netCDF file(s): ' + COLORS.ENDC
        msg += '{}% | {}/{} files'.format(percentage, pctx.progress.value, pctx.nbcdf)
        Print.progress(msg)
    if fn.in_scope():
        return fn


def yield_filedef(paths):
    """
    Yields all file definition produced by dr2xml as input for XIOS.

    :param list paths: The list of filedef path
    :returns: The dr2xml files
    :rtype: *iter*

    """
    for path in paths:
        for root, _, filenames in os.walk(path, followlinks=True):
            for filename in filenames:
                ffp = os.path.join(root, filename)
                if os.path.isfile(ffp) and re.search('^dr2xml_.*\.xml$', filename):
                    yield ffp


def get_patterns_from_filedef(path):
    """
    Parses dr2xml files.
    Each filename pattern is deserialized as a dictionary of facet: value.

    :param str path: The path to scan
    :returns: The filename deserialized with facets
    :rtype: *dict*

    """
    # Get process content from process global env
    assert 'pctx' in globals().keys()
    pctx = globals()['pctx']
    with pctx.lock:
        Print.debug(COLORS.OKGREEN + '\nParse XML filedef :: ' + COLORS.ENDC + '{}'.format(path))
    xml_tree = parse(path)
    patterns = list()
    for item in xml_tree.iterfind('*/file'):
        # Get XML file_id entry name
        item = item.attrib['name'].strip()
        # Ignore "cfsites_grid" entry
        if item == 'cfsites_grid':
            continue
        with pctx.lock:
            Print.debug('\nProcess XML file_id entry :: {}'.format(item))
        fn = Filename(item, pctx.filters)
        if fn.in_scope():
            patterns.append(fn)
    # Print progress
    with pctx.lock:
        pctx.progress.value += 1
        percentage = int(pctx.progress.value * 100 / pctx.nbxml)
        msg = COLORS.OKGREEN + '\rProcess XML file(s): ' + COLORS.ENDC
        msg += '{}% | {}/{} files'.format(percentage,
                                          pctx.progress.value,
                                          pctx.nbxml)
        Print.progress(msg)
    return patterns


def tupleized(facets, filenames):
    """
    Returns the filename patterns as a set of tuples

    :param list filenames: The list of deserialized filenames dictionaries
    :param dict facets: The facet dictionary
    :returns: The filename patterns tupleized
    :rtype: *set*

    """
    patterns = list()
    for filename in filenames:
        assert len(filename) == len(facets)
        x = list()
        for i in sorted(facets.values()):
            facet = facets.keys()[facets.values().index(i)]
            if facet not in IGNORED_FACETS:
                x.append(filename[facet])
        patterns.append(tuple(x))
    return set(patterns)


def get_labels(facets):
    """
    Returns the labels of table columns to display results

    :param dict facets: The facet dictionary
    :returns: The title labels
    :rtype: *list*

    """
    labels = list()
    for i in sorted(facets.values()):
        facet = facets.keys()[facets.values().index(i)]
        if facet not in IGNORED_FACETS:
            labels.append(facet)
    return labels


def get_widths(labels, fields):
    """
    Returns the column widths to display results

    :param list labels: The list of labels
    :param list fields: The list of entries
    :returns: The list of widths
    :rtype: *list*

    """
    widths = list()
    fields = list(fields)
    fields.append(tuple(labels))
    li = zip(*fields)
    for i in range(len(li)):
        widths.append(len(max(li[i], key=len)) + 2)
    return widths


def align(fields, widths, sep='| '):
    """
    Returns line with alignment.

    :param list fields: The list of fields to align
    :param list widths:  The list of width for each field
    :param list or str sep: The column separators
    :returns: The formatted line
    :rtype: *str*

    """
    assert len(fields) == len(widths)
    line = list()
    for field in fields:
        line.append(field.ljust(widths[fields.index(field)]))
        # Add colors
        if field in [DR2XML_LABEL, XIOS_LABEL]:
            line[-1] = COLORS.HEADER + line[-1] + COLORS.ENDC
        if field == IS:
            line[-1] = COLORS.OKGREEN + line[-1] + COLORS.ENDC
        if field == ISNOT:
            line[-1] = COLORS.FAIL + line[-1] + COLORS.ENDC
    if isinstance(sep, list):
        assert len(sep) == (len(line) - 1)
        for i in range(len(line) - 2, -1, -1):
            line.insert(i + 1, sep[i])
        return ''.join(line)
    else:
        return sep.join(line)


def initializer(keys, values):
    """
    Initialize process context by setting particular variables as global variables.

    :param list keys: Filters name list
    :param list values: Filters value list

    """
    assert len(keys) == len(values)
    global pctx
    pctx = ProcessContext({key: values[i] for i, key in enumerate(keys)})


def main():
    """
    Run main program

    """
    # Get command-line arguments
    prog, args = get_args()
    # Init print management
    Print.init(log=args.log, debug=args.debug, all=args.all, cmd=prog)
    # Print command-line
    Print.command(COLORS.OKBLUE + 'Command: ' + COLORS.ENDC + ' '.join(sys.argv))
    # Instantiate processing context
    with ProcessingContext(args) as ctx:
        # Collecting data
        Print.progress('\rCollecting data, please wait...')
        # Get number of XML
        ctx.nbxml = len([x for x in yield_filedef(ctx.xml)])
        # Get number of files
        ctx.nbcdf = len([x for x in yield_files(ctx.directory)])
        # Init process context
        cctx = {name: getattr(ctx, name) for name in PROCESS_VARS}
        # Process XML files
        if ctx.use_pool:
            # Init processes pool
            pool = Pool(processes=ctx.processes, initializer=initializer, initargs=(cctx.keys(),
                                                                                    cctx.values()))
            xios_input = [i for x in pool.imap(get_patterns_from_filedef, yield_filedef(ctx.xml)) for i in x]
            # Close pool of workers
            pool.close()
            pool.join()
        else:
            initializer(cctx.keys(), cctx.values())
            xios_input = [i for x in itertools.imap(get_patterns_from_filedef, yield_filedef(ctx.xml)) for i in x]
        # Get number of entries
        ctx.nbentries = len(xios_input)
        Print.progress('\n')
        # Reset progress counter
        cctx['progress'].value = 0
        # Process XIOS files
        if ctx.use_pool:
            # Init processes pool
            pool = Pool(processes=ctx.processes, initializer=initializer, initargs=(cctx.keys(),
                                                                                    cctx.values()))
            xios_output = [x for x in pool.imap(get_patterns_from_files, yield_files(ctx.directory))]
            # Close pool of workers
            pool.close()
            pool.join()
        else:
            initializer(cctx.keys(), cctx.values())
            xios_output = [x for x in itertools.imap(get_patterns_from_files, yield_files(ctx.directory))]
        # Control
        assert ctx.nbcdf == len(xios_output)
        # Check sources have been found
        if not xios_input:
            raise NoPatternFound()
        if not xios_output:
            raise NoFileFound()
        # Remove unchanged facet among all entries for better display
        if not args.full_table:
            xios_all = [x.get_attrs().values() for x in xios_input]
            xios_all.extend([x.get_attrs().values() for x in xios_output])
            fn_facets = xios_input[0].get_attrs()
            hidden_facets = [fn_facets.keys()[fn_facets.values().index(i[0])] for i in zip(*xios_all) if
                             len(set(i)) == 1]
            for facet in hidden_facets:
                del (ctx.facets[facet])
            xios_input = tupleized(ctx.facets, [x.mask(hidden_facets) for x in xios_input])
            xios_output = tupleized(ctx.facets, [x.mask(hidden_facets) for x in xios_output])
        else:
            xios_input = tupleized(ctx.facets, [x.get_attrs() for x in xios_input])
            xios_output = tupleized(ctx.facets, [x.get_attrs() for x in xios_output])
        # Run comparison between input and output
        # What is in input AND in output
        common = xios_input.intersection(xios_output)
        # What is in input BUT NOT in output
        missing_output = xios_input.difference(xios_output)
        # What is in output BUT NOT in input
        missing_input = xios_output.difference(xios_input)
        # Build table title
        labels = get_labels(ctx.facets)
        # Build table width
        widths = get_widths(labels, xios_input.union(xios_output))
        # Add labels for results
        labels.extend([DR2XML_LABEL, XIOS_LABEL])
        widths.extend([DR2XML_WIDTH, XIOS_WIDTH])
        # Table separators
        separators = ['| '] * (len(ctx.facets) - 1)
        separators += ['| ', '| ']
        # Get total width for display
        total_width = sum(widths) + sum([len(sep) for sep in separators]) + 1
        # No print if no differences
        if missing_input or missing_output:
            # Print table header
            Print.success('\n\n' + '+' + ''.center(total_width, '-') + '+' + '\n')
            Print.success('| ' + align(labels, widths, sep=separators) + '|' + '\n')
            Print.success('+' + ''.center(total_width, '-') + '+' + '\n')
            # Print results for each entry
            lines = 0
            input_total = 0
            output_total = 0
            for tup in sorted(xios_input.union(xios_output)):
                line = list(tup)
                if tup in common:
                    if args.all:
                        line.extend([IS, IS])
                        input_total += 1
                        output_total += 1
                    else:
                        continue
                elif tup in missing_input:
                    line.extend([ISNOT, IS])
                    output_total += 1
                    ctx.notinxml += 1
                elif tup in missing_output:
                    line.extend([IS, ISNOT])
                    input_total += 1
                    ctx.notinxios += 1
                else:
                    line.extend([ISNOT, ISNOT])
                lines += 1
                Print.success('| ' + align(line, widths, sep=separators) + '|' + '\n')
            # Print table footer with totals
            Print.success('+' + ''.center(total_width, '-') + '+' + '\n')
            line = align(fields=['Totals = {}'.format(lines), str(input_total), str(output_total)],
                         widths=[len(align(labels[:-2], widths[:-2])), widths[-2], widths[-1]],
                         sep=['| ', '| '])
            Print.success('| ' + line + '|' + '\n')
            Print.success('+' + ''.center(total_width, '-') + '+')
        # Print summary
        msg = COLORS.HEADER + '\n\nNumber of DR2XML file(s) scanned: {}'.format(ctx.nbxml) + COLORS.ENDC
        msg += COLORS.HEADER + '\nNumber of DR2XML entry(ies) scanned: {}'.format(ctx.nbentries) + COLORS.ENDC
        msg += COLORS.HEADER + '\nNumber of netCDF file(s) scanned: {}'.format(ctx.nbcdf) + COLORS.ENDC
        if (ctx.notinxml + ctx.notinxios):
            msg += COLORS.FAIL
        else:
            msg += COLORS.OKGREEN
        msg += '\nNumber of difference(s) between XML and XIOS outputs: {}'.format(
            ctx.notinxml + ctx.notinxios) + COLORS.ENDC
        if ctx.notinxml:
            msg += COLORS.FAIL
        else:
            msg += COLORS.OKGREEN
        msg += '\nNumber of XIOS output(s) not in XML files: {}'.format(ctx.notinxml) + COLORS.ENDC
        if ctx.notinxios:
            msg += COLORS.FAIL
        else:
            msg += COLORS.OKGREEN
        msg += '\nNumber of XML entry(ies) not as XIOS output: {}\n'.format(ctx.notinxios) + COLORS.ENDC
        # Critical level used to print in any case
        Print.summary(msg)
        # Print log path if exists
        Print.info(COLORS.HEADER + '\nSee log: {}\n'.format(Print.LOGFILE) + COLORS.ENDC)
    # Evaluate errors and exit with appropriate return code
    if ctx.notinxios or ctx.notinxml:
        # Some datasets (at least one) has error(s). Error code = nb datasets with error(s)
        sys.exit(1)
    else:
        # No errors. Error code = 0
        sys.exit(0)


if __name__ == "__main__":
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
    main()
