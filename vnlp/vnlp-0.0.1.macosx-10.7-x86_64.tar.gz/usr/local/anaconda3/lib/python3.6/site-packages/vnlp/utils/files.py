import os
import logging
import requests


def download(url, fname, skip_if_exists=True, chunk_size=1024):
    """
    Downloads a file from an URL.
    """
    if os.path.isfile(fname) and skip_if_exists:
        return
    logging.info('Downloading from {} to {}'.format(url, fname))
    r = requests.get(url, stream=True)
    with open(fname, 'wb') as f:
        for chunk in r.iter_content(chunk_size=chunk_size): 
            if chunk:
                f.write(chunk)
