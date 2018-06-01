import json
import os
import re
from urllib.parse import urljoin

import ipykernel
import requests
from notebook.notebookapp import list_running_servers

from .logging_init import info




def jupyformatter():
    """
    """
    notebook_name = get_notebook_name()

    os.system('jupyter nbconvert --to script {}'.format(notebook_name))
    info('Created `{}.py` at {}'.format(notebook_name, os.getcwd()))


def get_notebook_name():
    """
    Return the name of the current jupyter notebook.

    References:
        https://github.com/jupyter/notebook/issues/1000#issuecomment-359875246
        https://stackoverflow.com/a/13055551
    """
    kernel_id = re.search('kernel-(.*).json',
                          ipykernel.connect.get_connection_file()).group(1)
    servers = list_running_servers()
    for ss in servers:
        response = requests.get(urljoin(ss['url'], 'api/sessions'),
                                params={'token': ss.get('token', '')})
        for nn in json.loads(response.text):
            if nn['kernel']['id'] == kernel_id:
                relative_path = nn['notebook']['path']
                match = re.search(r'/?(\w+).ipynb', relative_path)
                notebook_name = match.group(1)
                return notebook_name