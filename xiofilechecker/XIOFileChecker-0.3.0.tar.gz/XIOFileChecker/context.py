#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
    :platform: Unix
    :synopsis: Processing context used in this module.

"""

import os
import re
from ConfigParser import ConfigParser
from multiprocessing import Lock, cpu_count, Value
from multiprocessing.managers import SyncManager

from utils.constants import CMIP6_FILENAME_PATTERN, IGNORED_FACETS, RUN_CARD, CONF_CARD, FILEDEF_DIRECTORY_FORMAT, \
    FILEDEF_ROOT
from utils.custom_exceptions import InvalidFilters, NoConfigCardFound, NoRunCardFound, OptionNotFound, YearsNotFound


class ProcessingContext(object):
    """
    Encapsulates the processing context/information for main process.

    :param ArgumentParser args: The command-line arguments parser
    :returns: The processing context
    :rtype: *ProcessingContext*

    """

    def __init__(self, args):
        # Get directory
        self.directory = args.directory
        # Get max process number
        self.processes = args.max_processes if args.max_processes <= cpu_count() else cpu_count()
        self.use_pool = (self.processes != 1)
        # Get xml path(s)
        if args.xml:
            self.xml = args.xml
        elif args.card:
            self.xml = list(get_xml_path_from_card(args.card))
        else:
            self.xml = args.directory
        # Get stdout lock
        self.lock = Lock()
        # Get facet keys
        facets = re.compile(CMIP6_FILENAME_PATTERN).groupindex
        for facet in IGNORED_FACETS:
            del (facets[facet])
        self.facets = facets
        # Clear re.compile cache to avoid groupindex deletion
        re.purge()
        # Get filters
        setattr(args, 'set_filter', args.set_filter or tuple())
        self.filters = dict(args.set_filter)
        wrong_filters = set(self.filters.keys()).difference(set(self.facets.keys()))
        if wrong_filters:
            raise InvalidFilters(wrong_filters, self.facets)
        # Set numbers of processes
        self.nbxml = 0
        self.nbcdf = 0
        self.nbentries = 0
        self.notinxml = 0
        self.notinxios = 0
        # Set process counter
        if self.use_pool:
            # Use process manager
            manager = SyncManager()
            manager.start()
            self.progress = manager.Value('i', 0)
        else:
            self.progress = Value('i', 0)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, traceback):
        pass


def get_xml_path_from_card(card_path):
    """
    Yields XML path from run.card and config.card attributes.

    :param str card_path: Directory including run.card and config.card
    :returns: The XML paths to use
    :rtype: *iter*

    """
    # Check cards exist
    if RUN_CARD not in os.listdir(card_path):
        raise NoRunCardFound(card_path)
    else:
        run_card = os.path.join(card_path, RUN_CARD)
    if CONF_CARD not in os.listdir(card_path):
        raise NoConfigCardFound(card_path)
    else:
        conf_card = os.path.join(card_path, CONF_CARD)
    # Extract info from cards
    config = ConfigParser()
    config.read(conf_card)
    xml_attrs = dict()
    xml_attrs['root'] = FILEDEF_ROOT
    if not config.has_option('UserChoices', 'longname'):
        raise OptionNotFound('LongName', 'UserChoices', conf_card)
    xml_attrs['longname'] = config.get('UserChoices', 'longname').strip('"')
    if not config.has_option('UserChoices', 'experimentname'):
        raise OptionNotFound('ExperimentName', 'UserChoices', conf_card)
    xml_attrs['experimentname'] = config.get('UserChoices', 'experimentname').strip('"')
    if not config.has_option('UserChoices', 'member'):
        raise OptionNotFound('Member', 'UserChoices', conf_card)
    xml_attrs['member'] = config.get('UserChoices', 'member').strip('"')
    with open(run_card, 'r') as f:
        lines = f.read().split('\n')
    lines = [line for line in lines if line.count('|') == 8]
    years = list()
    for line in lines:
        years.append(line.split()[3][:4])
        years.append(line.split()[5][:4])
    years = set(years)
    if not years:
        raise YearsNotFound(run_card)
    for year in years:
        xml_attrs['year'] = year
        yield FILEDEF_DIRECTORY_FORMAT.format(**xml_attrs)
