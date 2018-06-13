# -*- coding: utf-8 -*-

"""Top-level package for twinthread."""

__author__ = """Brent Baumgartner"""
__email__ = 'brent.baumgartner@twinthread.com'
__version__ = '0.2.0'

def fetch(token):
    """
    Fetch data from TwinThread's servers
    :param token: Authenticates access to one group of datasets. Fetch from TwinThread UI.
    :return: data: Pandas dataframe
    """
    print("Fetching data...")
    from azure.storage.common import CloudStorageAccount
    import pandas as pd
    import os
    X = token.split(",")
    X[3] = X[3] + "=="
    (blob, container, name, key) = X
    account = CloudStorageAccount(account_name=name, account_key=key)
    service = account.create_block_blob_service()
    service.get_blob_to_path(container, blob, "tempfile")
    print("Parsing data...")
    data = pd.read_csv("tempfile")
    os.remove("tempfile")
    from IPython.display import clear_output
    clear_output()
    return data
