import os
from pathlib import Path
import urllib.parse
import urllib.request
import urllib.error
import json
import re
# import numpy as np
# import pandas as pd

# _usedb = True
_uri = "N10/Nordling-ID1446937-D20150825-N10-E15-SNR3291-IDY15968.json"
_database = "https://bitbucket.org/api/2.0/repositories/sonnhammergrni/gs-datasets/src/master"


def Load(uri=None, database=None, wildcard="*"):
    """Load genespider datasets from the official repository
        https://bitbucket.org/api/1.0/repositories/sonnhammergrni/gs-datasets/raw/master/.
        With no input Load() will load a default dataset.

        Parameters
        ----------
        uri : location of file or directory,
            default: N10/Nordling-ID1446937-D20150825-N10-E15-SNR3291-IDY15968.json
            this file will be loaded from remote location using the default database location.
            This string can be an absolute path or relative path to a local file.
            If the path does not start with a "." the parameter usedb needs to be
            set to false for use on local files or directories.

        database : A database specific string can be provided in uri format.

        wildcard : a string for listing files in local file structure, default "*".
            Used when traversing local directory structures, for example.
            Setting this to "**/*.json" will list all json files under the specified directory.

            For remote directories this is interpreted as a python regular expression
            default ".*" for selecting files in the directory.

        Examples
        --------
        >>> dirs = Load("./") # Returns list of current dir content
        >>> dirs = Load("/") # Returns list of database root dir content
        >>> data = Load(relative_path, database) # Load specified dataset from specified database.

        Returns
        -------
        loaded : the data as a dictionary, alternatively a list of files and
            directories under the specified directory.
    """

    if uri == "test":  # Load default sample data
        uri = _uri
        database = _database

    uribits = __parse_uribits(uri, database)

    response = __load_uri(uribits, wildcard)

    if "page" in response:  # This might be bitbucket specific, more rules may have to be added for other databases
        response = __iterate_remote_paths(response, wildcard)

    return response


def __parse_uribits(URI, database):

    if database is None:
        location = urllib.parse.urlparse(URI)
    else:
        if URI is None:
            URI = ""

        if urllib.parse.urlparse(URI).scheme is not "":  # if database exist but a scheme is present in the URI, use the uri path
            database = URI

        location = urllib.parse.urlparse(database)
        location = location._replace(path=os.path.normpath(location.path + "/" + URI))

    if location.netloc == ".":
        URI = os.path.abspath(location.netloc + location.path)
        location = urllib.parse.urlparse(URI)

    return location


def __load_uri(uribits, wildcard):

    if uribits.scheme is '':
        local = Path(uribits.path)
        if local.is_dir():
            return sorted([str(d) for d in local.glob(wildcard)])

        else:
            full_uri = urllib.parse.urlunparse(uribits)
            # full_uri = Path(Path(full_uri).absolute()).as_uri()
            full_uri = Path(full_uri).absolute().as_uri()
    else:
        full_uri = urllib.parse.urlunparse(uribits)

    # local = Path(urllib.parse.urlparse(full_uri)[2])

    try:
        if not full_uri.endswith(".json"):
            full_uri = full_uri + "/"

        with urllib.request.urlopen(full_uri) as URI:
            uri_string = URI.read().decode()

        return json.loads(uri_string)

    except urllib.error.URLError as e:
        print("Path: {}\n".format(full_uri))
        print(e.reason)
        return None


def __iterate_remote_paths(loaded, wildcard):

    if wildcard == "*":
        wildcard = ".*"

    # nfiles = paths["size"]
    paths = [p["path"] for p in loaded["values"] if ((p["path"].endswith(".json") and re.search(wildcard, p["path"])) or p["type"] == 'commit_directory')]

    while "next" in loaded:
        with urllib.request.urlopen(loaded["next"]) as URI:
            uri_string = URI.read().decode()
            loaded = json.loads(uri_string)

        paths.extend([p["path"] for p in loaded["values"] if ((p["path"].endswith(".json") and re.search(wildcard, p["path"])) or p["type"] == 'commit_directory')])

    return paths
