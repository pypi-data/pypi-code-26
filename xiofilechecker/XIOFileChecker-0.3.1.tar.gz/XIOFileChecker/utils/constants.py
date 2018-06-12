#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
    :platform: Unix
    :synopsis: Constants used in this package.

"""

from datetime import datetime

# Program version
VERSION = '0.3.1'

# Date
VERSION_DATE = datetime(year=2018, month=6, day=12).strftime("%Y-%d-%m")

# List of variable required by each process
PROCESS_VARS = ['filters',
                'lock',
                'nbxml',
                'nbcdf',
                'progress']

# CMIP6 filename format
CMIP6_FILENAME_PATTERN = '^(?P<variable_id>[\w.-]+)_' \
                         '(?P<table_id>[\w.-]+)_' \
                         '(?P<source_id>[\w.-]+)_' \
                         '(?P<experiment_id>[\w.-]+)_' \
                         '(?P<variant_label>[\w.-]+)_' \
                         '(?P<grid_label>[^-_]+)' \
                         '(_(?P<period_start>[\w.-]+)-(?P<period_end>[\w.-]+))?' \
                         '\\.nc$'

# Filedef directory format
FILEDEF_ROOT = '/ccc/work/cont003/igcmg/igcmg/IGCM'
FILEDEF_DIRECTORY_FORMAT = '{root}/CMIP6/{longname}/IPSL-CM6A-LR/{experimentname}/{member}/{year}'

# Table labels
XIOS_LABEL = 'XIOS out'
DR2XML_LABEL = 'in XML'

# Table widths
XIOS_WIDTH = len(XIOS_LABEL) + 2
DR2XML_WIDTH = len(DR2XML_LABEL) + 2

# IS/IS NOT labels
IS = 'Yes'
ISNOT = 'No'

# Cards name
RUN_CARD = 'run.card'
CONF_CARD = 'config.card'

# Facet to ignore
IGNORED_FACETS = ['period_start', 'period_end']

# Help
TITLE = \
    """
    ____ _ ___ ___ _ _ _______ _ _________ _ __________|n
    ._ _|_|___| __|_| |___ ___| |_ ___ ___| |_ ___ ___.|n
    |_'_| | . | __| | | -_| __| . | -_| __| '_| -_| __||n
    |_,_|_|___|_| |_|_|___|___|_|_|___|___|_,_|___|_|__|n

    """
URL = \
    """
    See full documentation and references at:|n
    http://prodiguer.github.io/xiofilechecker/.

    """

DEFAULT = \
    """
    The default values are displayed next to the corresponding flags.

    """

PROGRAM_DESC = \
    """
    {}|n|n

    XIOFileChecker allows you to easily check the consistency of XIOS inputs|n
    and outputs. This means XIOFileChecker compares what should be written by|n
    XIOS according to the DR2XML files definition and what was really written|n
    on disk.|n|n

    {}|n|n

    {}

    """.format(TITLE, URL, DEFAULT)

EPILOG = \
    """
    Developed by:|n
    Levavasseur, G. (UPMC/IPSL - glipsl@ipsl.fr)|n
    Moine, M.-P. (CNRM/CERFACS - marie-pierre.moine@cerfacs.fr)

    """

OPTIONAL = \
    """Optional arguments"""

POSITIONAL = \
    """Positional arguments"""

HELP = \
    """
    Show this help message and exit.

    """

LOG_HELP = \
    """
    Logfile directory.|n
    Default is the working directory.|n
    If not, standard output is used.

    """

DEBUG_HELP = \
    """
    Debug mode.

    """

ALL_HELP = \
    """
    Show all results/entries.|n
    Default only print differences.

    """

FULL_TABLE_HELP = \
    """
    Force all columns display.|n
    Default hide facets with unchanged values.

    """

VERSION_HELP = \
    """
    Program version.

    """

DIRECTORY_HELP = \
    """
    Input directory including XIOS output netCDF files.

    """

XML_HELP = \
    """
    One or several directory with DR2XML files used for|n
    the simulation.

    """

CARD_HELP = \
    """
    The libIGCM directory with "run.card" and "config.card"|n
    of the simulation. This option is IPSL-specific.

    """

SET_FILTER_HELP = \
    """
    Filter facet values matching the regular expression.|n
    Duplicate the flag to set several filters.|n
    Default includes all values (i.e., no filters).
    
    """

MAX_PROCESSES_HELP = \
    """
    Number of maximal processes to simultaneously treat|n
    several files. Max is the CPU count.|n
    Set to 1 seems sequential processing.|n
    Set to -1 uses the max CPU count.|n
    Default is set to 4 processes.

    """
