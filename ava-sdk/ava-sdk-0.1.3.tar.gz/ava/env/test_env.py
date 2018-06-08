# -*- coding: utf-8 -*-

import os
import pytest
import ava.utils.fileloc as fileloc
from ava.env import environment

@pytest.fixture
def test_env(scope="module"):
    workdir = "testrun"
    fileloc.mkdir_p(workdir)
    e = environment.Environment(workdir=workdir)
    fileloc.rm_path(workdir)
    return e

def empty_dir(dir_path):
    fileloc.rm_path(dir_path)
    fileloc.mkdir_p(dir_path)

def test_env1(test_env):
    empty_dir(test_env.workdir)
    assert test_env.workdir == "testrun"
    data_dir = os.path.join(test_env.workdir, "data")
    fileloc.mkdir_p(data_dir)
    test_env.reset_path(workdir=test_env.workdir)
    #assert os.path.abspath(test_env.data_dir) == os.path.abspath(data_dir)
    assert test_env.data_dir == data_dir
    assert test_env.group_dir == ""

def test_env2(test_env):
    empty_dir(test_env.workdir)
    data_dir = os.path.join(test_env.workdir, "mnt/data")
    fileloc.mkdir_p(data_dir)
    test_env.reset_path(workdir=test_env.workdir)
    assert os.path.abspath(test_env.data_dir) == os.path.abspath(data_dir)
    assert test_env.group_dir == ""

def test_env3(test_env):
    empty_dir(test_env.workdir)
    group_dir = os.path.join(test_env.workdir, "mnt/group")
    fileloc.mkdir_p(group_dir)
    bucket_dir = os.path.join(test_env.workdir, "mnt/bucket")
    fileloc.mkdir_p(bucket_dir)
    test_env.reset_path(workdir=test_env.workdir)
    assert os.path.abspath(test_env.group_dir) == os.path.abspath(group_dir)
    assert os.path.abspath(test_env.bucket_dir) == os.path.abspath(bucket_dir)
