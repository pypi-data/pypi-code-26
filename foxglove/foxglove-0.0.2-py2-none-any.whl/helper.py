from os.path import join, splitext, normpath, split
from os import fdopen

import tempfile
import requests


def get_addon_pref_file(work_dir, addon):
    return join(work_dir, 'addon_prefs', splitext(normpath(split(
        addon)[1]))[0] + '.js')


def download_xpi(name):

    xpi_path = None

    addon_url = \
        "https://addons.mozilla.org/firefox/downloads/latest/{}".format(name)
    r = requests.get(addon_url)

    if r.status_code == 200:
        (xpi_fd, xpi_path) = tempfile.mkstemp(suffix='.xpi')
        with fdopen(xpi_fd, 'wb') as xpi_file:
            xpi_file.write(r.text)

    return xpi_path
