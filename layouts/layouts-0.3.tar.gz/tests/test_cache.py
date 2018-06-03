# layouts cache download tests

import os
import tarfile
import tempfile

import layouts
import pytest
import requests

from github import Github

def test_local_cache():
    '''
    Test local cache check

    Downloads .tar.gz from GitHub, extracts and uses
    '''
    # Prepare layout cache
    github_path = 'hid-io/layouts'
    tmp_dir = os.path.join(tempfile.gettempdir(), "layouts-python-test")
    os.makedirs(tmp_dir, exist_ok=True)
    version = 'master'

    # Check for environment variable Github token
    token = os.environ.get('GITHUB_APIKEY', None)

    # Retrieve repo information
    gh = Github(token)
    repo = gh.get_repo(github_path)
    commit = repo.get_commit(version)
    tar_url = repo.get_archive_link('tarball')

    # GitHub only uses the first 7 characters of the sha in the download
    dirname = "{}-{}".format(github_path.replace('/', '-'), commit.sha[:7])
    dirpath = os.path.join(tmp_dir, dirname)
    filename = "{}.tar.gz".format(dirname)
    filepath = os.path.join(tmp_dir, filename)

    # If directory doesn't exist, check if tarball does
    if not os.path.isdir(dirpath):
        # If tarball doesn't exist, download it
        if not os.path.isfile(filepath):
            # Retrieve tar file
            chunk_size = 2000
            req = requests.get(tar_url, stream=True)
            with open(filepath, 'wb') as infile:
                for chunk in req.iter_content(chunk_size):
                    infile.write(chunk)

        # Extract tarfile
        tar = tarfile.open(filepath)
        tar.extractall(tmp_dir)


    # Run actual test
    mgr = layouts.Layouts(layout_path=dirpath)
    assert mgr.list_layouts()

def test_github_cache():
    '''
    Test GitHub cache
    '''
    mgr = layouts.Layouts(force_refresh=True)
    assert mgr.list_layouts()

