#
# -*- coding: utf-8 -*-
# python-perkeep-utils
# Copyright (C) 2018  Markus Peröbner
#
from . import fs
from . import pk

def build_from_fs_scheme(path):
    return fs.FileSystemDatasetReader(path)

def build_from_pk_scheme(expression):
    return pk.PerkeepDatasetExpressionReader(expression)

SCHEME_HANDLERS = {
    'fs': build_from_fs_scheme,
    'pk': build_from_pk_scheme,
}

def build_from_resource_identifier(resource_identifier):
    '''Returns a dataset insance for the given resource identifier.

    Resource identifier may be for example:
    - fs:some/path
    - pk:attr:"per:type":dataset
    '''
    sep_index = resource_identifier.index(':')
    scheme = resource_identifier[:sep_index]
    args = resource_identifier[sep_index+1:]
    return SCHEME_HANDLERS[scheme](args)
