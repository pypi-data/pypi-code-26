#! /usr/bin/env python
# -*- coding: utf-8 -*-

# Victor Calderon
# Created      : 2018-05-09
# Last Modified: 2018-05-09
from __future__ import print_function, division, absolute_import
__author__     =['Victor Calderon']
__copyright__  =["Copyright 2018 Victor Calderon"]
__email__      =['victor.calderon@vanderbilt.edu']
__maintainer__ =['Victor Calderon']
__all__        =[   "url_checker"]

"""
Tools used to interact with web-related objects
"""

## Import modules
import requests
from   cosmo_utils.utils             import file_utils as fd
from   cosmo_utils.custom_exceptions import LSSUtils_Error

## Functions

## Checking if URL is valid
def url_checker(url_str):
    """
    Checks if the URL is valid or not.

    Parameters
    -----------
    url_str : `str`
        URL of the website to evaluate.

    Raises
    ----------
    LSSUtils_Error : `Exception`
        Program exception if input parameters are accepted
    """
    file_msg = fd.Program_Msg(__file__)
    ## Checking input parameters
    if not (isinstance(url_str, str)):
        msg = '{0} `url_str` ({1}) is not a STRING!'.format(file_msg,
            type(url_str))
        raise LSSUtils_Error(msg)
    ##
    ## Checking Website
    request_url = requests.get(url_str)
    if (request_url.status_code != 200):
        msg = '{0} `url_str` ({1}) does not exist!'.format(file_msg, url_str)
        raise LSSUtils_Error(msg)

