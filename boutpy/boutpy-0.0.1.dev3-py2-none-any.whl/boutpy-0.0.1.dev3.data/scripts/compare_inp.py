#!python
# -*- coding: utf-8 -*-
"""Parser config files

* parser configure files
* convert a dict to a **level1** dict
* compare BOUT.inps
* dataframe with 'sec-opt' multi_index for config file

"""

from __future__ import (absolute_import, division,
                        print_function, unicode_literals)

__all__ = ['str_to_num', 'parser_config', 'dict_to_level1',
           'multi_index', 'compare_inp']

__date__ = '01/04/2018'
__version__ = '0.5.1.1'
__author__ = 'J.G. Chen'
__email__ = 'cjgls@pku.edu.cn'

from StringIO import StringIO
import pandas as pd

import numpy as np
from configobj import ConfigObj
from boutpy.boututils.functions import sort_nicely


def str_to_num(x):
    """Convert str 'x' to int or float if possible, otherwise return itself.
    """

    if isinstance(x, str):
        try:
            return int(x)
        except ValueError:
            try:
                return float(x)
            except ValueError:
                return x
    else:
        return x


def dict_colored(Dict, format_code=[98, 91, 94, 92, 95, 93, 96]):
    """ add color str to 2-levels dict according to the count of values."""

    format_base = '\033[{}m{}\033[0m'
    fc = format_code[:]
    nsize = len(Dict)
    ncode = len(fc)
    if ncode < nsize:
        fc.extend(np.ones(nsize-ncode))
    count = zip(*np.unique(Dict.values(), return_counts=True))
    if len(count[0]) < 2:
        return Dict
    else: # at least 2 different value
        count = sorted(count, key=lambda x: x[1], reverse=True)
        keys = zip(*count)[0]
        keys_c = dict(zip(keys, fc))
        return {k: format_base.format(keys_c[Dict[k]], Dict[k]) \
                   for k in Dict.keys()}


def df_colored(dataframe, format_code=[98, 91, 94, 92, 95, 93, 96],
               columns=[('Sec', 'Opt')], title_color=47):
    """ add color str to dataframe elements to highlight difference.

    Parameters
    ----------
    dataframe : DataFrame
    format_code : list of int, optional, default: [k, r, b, g, c, y, m]
        color code in '\033[{}m{}\033[0m'.format(format_code, cell) for
        different color.

    """

    if not isinstance(dataframe, pd.core.frame.DataFrame):
        raise TypeError("DataFrame type required!!")

    dict_df = dataframe.fillna('NaN').to_dict('index')
    result = {k: dict_colored(dict_df[k], format_code=format_code) \
              for k in dict_df.keys()}
    result = pd.DataFrame.from_dict(result, orient='index')
    # due to the color code add extra string,
    # need to add the columns' name to result
    pd_case = sort_nicely(result.columns)
    df_title = pd.DataFrame(['\033[{}m{}\033[0m'.format(title_color, i) \
                                for i in pd_case],
                            columns=columns, index=pd_case).T
    result = df_title.append(result)
    result = result.reindex(pd.MultiIndex.from_tuples(result.index))
    # keep original columns' order
    result = result.reindex_axis(dataframe.columns, axis=1)

    return result


def dict_to_level1(Dict, sep='.'):
    """Convert a dict to a one level dict.

    Parameters
    ----------
    Dict : dict
        its values may be in *dict* type
    sep : char
        a seperator to join keys in the multi-level dict

    Returns
    -------
    result : dict
        its values are not in *dict* type

    Examples
    --------

    .. code-block:: python

        >>> test1 = {'A': {'a': 1,'b': 2}, 'B': 3}
        >>> dict_to_level1(test1)
        #  {'A.a': 1, 'A.b': 2, 'B': 3}
        >>> test2 = {'A':{'a': 1, 'b': 2}, 'a': 3}
        >>> dict_to_level1(test2)
        #  {'A.a': 1, 'A.b': 2, 'a': 3}

    """

    result = {}
    if isinstance(Dict, dict):
        for key in Dict.keys():
            if not isinstance(Dict[key], dict):
                # add key-value pairs whose value is not a dict
                result[key] = Dict[key]
            else:
                # key-value pairs whose value is a dict
                subresult = {}
                for ikey in Dict[key].keys():
                    subresult[sep.join([key, ikey])] = Dict[key][ikey]
                subresult = dict_to_level1(subresult, sep=sep)
                result.update(subresult)

    return result


def parser_config(configfile, level1=False, header=None, dataframe=False):
    r"""Parser config files.

    Return a dict contains all options information in the config files.

    Parameters
    ----------
    configfile : string
        path to file or config string
    level1 : bool, optional, default: False
        If ``level1=False`` [default], then using 'sec.opt' as keys.
        Otherwise, Using all options as keys.
    header : string, optional
        section header for the beginning section if it doesn't have one.
        Default is ``None`` which means it does not try to add header for
        the beginning section.
    dataframe : bool, optional, default: False
        return the result in pd.DataFrame format if ``dataframe=True``.

    Returns
    -------
    result : dict | pd.DataFrame
        a dict with 'sec.subsec[.subsubsec...].opt' as key if
        ``level1 = True``. Otherwise it is a multi-levels dict by default.
        return the result in pd.DataFrame format if ``dataframe=True``.

    Examples
    --------

    .. code-block:: python

        >>> result = parser_config('/path/to/BOUT.inp')
        # ConfigObj({'NOUT': '250', 'TIMESTEP': '1.e0',
        # ...
        # 'kappa': {'bndry_core': 'neumann', 'bndry_sol': 'neumann'}})
        >>> result = parser_config('[header]\noption1=1', header='main')
        # ConfigObj({'header': {'option1': '1'}})
        >>> result = parser_config('#comments\noptions=1')
        # ConfigObj({'options': '1'})
        >>> result = parser_config('#comments\noptions=1', header='main')
        # ConfigObj({'main': {'options': '1'}})

    """

    # for Python>3.2
    # import configparser
    # configparser.read_string('[main]\noption=1')

    try:
        with open(configfile) as lines:
            lines = lines.read()
    except IOError:
        # not a file, try to parse it directly
        lines = configfile

    if header is not None:
        lines = '[{}]\n{}'.format(header, lines)

    result = ConfigObj(StringIO(lines))

    # delete the `header` section if there are no options.
    if header in result and len(result[header]) == 0:
        result.pop(header)

    result = dict(result)
    if level1:
    # WARNING: deprecated
        result = dict_to_level1(result)

    if dataframe:
        # transpose, otherwise the DataFrame try to
        # keep same dtype in one column.
        # e.g.
        #   df = pd.DataFrame([[1, 2], [5.3, 6]])
        # df:
        #   1.0 2
        #   5.3 6
        result = pd.DataFrame.from_dict(result).T
        result = result.applymap(lambda x: str_to_num(x))

    return result


def multi_index(boutinp, header='global', column='Value'):
    """Return a panda.DataFrame with ['Sec', 'Opt'] as multi-index.

    Parameters
    ----------
    boutinp : str
        path to BOUT.inp file.
    header : str, optional, default: 'global'
        the header name for the first section
    column : str, optional, default: 'Value'
        column's name

    Returns
    -------
    df : pandas.DataFrame
        pandas.DataFrame with multi-index

    """

    boutinp_dict = parser_config(boutinp, header=header)
    # stack --> obtain multi-index pd.Series
    df = pd.DataFrame.from_dict(boutinp_dict).stack()
    # index: ['Sec', 'Opt']
    df = df.swaplevel()
    # group by section name
    df.sort_index(inplace=True)
    df = pd.DataFrame(df)
    # reindex as the order of section in the BOUT.inp
    df = df.reindex_axis(boutinp_dict.keys(), axis=0, level=0)
    df.index.set_names(['Sec', 'Opt'], inplace=True)
    df.rename(columns={0: column}, inplace=True)

    df = df.applymap(lambda x: str_to_num(x))

    return df


def compare_inp(*configfiles, **kwargs):
    """Comparison of configfiles, return & print details of differences.

    Parameters
    ----------
    configfiles : list|tuple of stings
        path of BOUT.inps
    grid : bool, optional, default: False
        output grid names if they are different.
    quiet : bool, optional, default: False
        print comparison result to screen.
    case : bool, optional, default: True
        case sensitive if `case` is True
    short : bool, optional, default: True
        Using short name for cases
    render : bool, optional, default: True
        highlight different values in terminal output.

    Returns
    -------
    tuple(cases, table)
    cases, table : pandas.DataFrame
        cases : name of each case
        table : differences of each case

    Examples
    --------

    .. code-block:: python

        >>> import glob
        >>> cases, table = compare_inp(glob.glob("*/BOUT.inp"), grid=False)

    """

    result_dict = {}
    cases = {}
    count = 0
    # header for the beginning section
    header = 'global'

    showgrid = kwargs.get('grid', False)
    # case sensitive or not
    casesensitive = kwargs.get('case', True)
    render = kwargs.get('render', True)
    # using short name or not
    shortname = kwargs.get('short', True)
    quiet = kwargs.get('quiet', False)
    pd.set_option('display.max_colwidth', -1)
    pd.set_option('display.max_rows', 500)
    pd.set_option('display.max_columns', 500)
    pd.set_option('display.width', 1000)

    for i in configfiles:
        if isinstance(i, (list, tuple)):
            for ii in sort_nicely(i):
                case = 'case{}'.format(count)
                if ii.endswith('/BOUT.inp'):
                    cases[case] = ii.replace('/BOUT.inp', '')
                else:
                    cases[case] = ii
                result_dict[case] = multi_index(ii, header=header,
                                                column=case)
                count += 1
        else:
            case = 'case{}'.format(count)
            result_dict[case] = multi_index(i, header=header, column=case)
            cases[case] = i
            count += 1

    # secs' and opts' name in boutinp
    boutinp_secs = result_dict['case0'].index.levels[0]
    boutinp_opts = result_dict['case0'].index.levels[1]
    table = pd.concat(result_dict.values(), axis=1)
    table = table.reindex_axis(boutinp_secs, axis=0, level=0)
    table.sort_index(axis=1, inplace=True)

    if casesensitive:
        drop_keys = [i for i in table.index
                     if (len(table.loc[i].unique()) == 1)]
    else:
        drop_keys = [i for i in table.index
                     if (len(
                        table.loc[i].astype(str).str.lower().unique()) == 1)]
    df_cases = pd.DataFrame(
        pd.Series.from_array(cases.values(), index=cases.keys()),
        columns=['Name'])
    # df_cases = df_cases.sort_index(axis=0)
    df_cases = df_cases.loc[sort_nicely(df_cases.index)]

    if shortname and (not quiet):
        print("-" * 50)
        print("cases:\n", df_cases.to_string(justify='left'))

    # extract grid info due to its value too long
    grid_ind = (header, 'grid')
    if grid_ind not in drop_keys:
        drop_keys.append(grid_ind)
        if showgrid and (not quiet):
            grid = pd.DataFrame(table.loc[grid_ind])[header]
            print("-" * 50)
            if shortname:
                print("grids:\n", grid.to_string(justify='left'))
            else:
                print("grids:\n",
                      grid.rename(index=cases).to_string(justify='left'))
    if len(cases) > 1:
        table.drop(drop_keys, inplace=True)
    else:
        table.drop(grid_ind, inplace=True)
    # table = table.reindex_axis(table_ind, axis=0, level=0)
    # nicely sort columes
    table = table.reindex_axis(sort_nicely(table.columns), axis=1)

    if not table.empty:
        if not shortname:
            table.rename(columns=cases, inplace=True)
        if not quiet:
            print("-" * 50)
            print("differences:")
            if render:
                print(df_colored(table).to_string(
                          justify='left', header=False))
            else:
                print(table.to_string(justify='left'))
    elif not quiet:
        print(">>>>>> **ALL** options are **SAME** <<<<<<")

    return cases, table


if __name__ == '__main__':
    # execute only if run as a script
    import argparse

    parser = argparse.ArgumentParser(
        description='get differences of configure files',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("configfiles", nargs='*',
                        help="name of configure files")
    parser.add_argument("-g", "--grid", action='store_false',
                        help="output difference of grid names")
    parser.add_argument("-c", "--case", action='store_false',
                        help="case sensitive about the option value")
    parser.add_argument("-r", "--render", action='store_false',
                        help="render the output in terminal")
    parser.add_argument("-s", "--short", action='store_false',
                        help="use short name for cases name")

    args = parser.parse_args()

    tmp = compare_inp(args.configfiles, grid=args.grid, case=args.case,
                      short=args.short, render=args.render)
