# -*- coding: utf-8 -*-

import os
from functools import wraps


def singleton(cls):
    instances = {}

    @wraps(cls)
    def getinstance(*args, **kw):
        if cls not in instances:
            instances[cls] = cls(*args, **kw)
        return instances[cls]
    return getinstance


@singleton
class Environment(object):
    """返回运行环境内的各类数据，例如：
          sampleset/model/training/... 文件路径/内容
    """

    def __init__(self, workdir=None, data_dir=None, group_dir=None, bucket_dir=None):
        """初始化环境中的各种路径

        Args:
            workdir    : 用户的工作目录
            data_dir   : 挂载数据集所在的目录
            group_dir  : 用户所在组共享存储挂载的目录
            bucket_dir : 用户所使用 bucket 数据挂载的目录
        """
        self.job_id = get_job_id()
        # workdir
        if workdir != None and os.path.isdir(workdir):
            self.workdir = workdir
        else:
            self.workdir = "/workspace"

        self.reset_basedir(data_dir=data_dir, group_dir=group_dir, bucket_dir=bucket_dir)
        self.reset_path()

    def reset_basedir(self, data_dir=None, group_dir=None, bucket_dir=None):
        """根据 workdir 配置其他 base dir
        """
        # data_dir
        self.data_dir = ""
        if data_dir != None and os.path.isdir(data_dir):
            self.data_dir = data_dir
        else:
            data_dir = os.path.join(self.workdir, "data")   # 兼容旧版本，都存在的话，后面覆盖前面
            if os.path.isdir(data_dir):
                self.data_dir = data_dir
            data_dir = os.path.join(self.workdir, "mnt/data")
            if os.path.isdir(data_dir):
                self.data_dir = data_dir

        # group_dir
        self.group_dir = ""
        if group_dir != None and os.path.isdir(group_dir):
            self.group_dir = group_dir
        else:
            group_dir = os.path.join(self.workdir, "mnt/group")
            if os.path.isdir(group_dir):
                self.group_dir = group_dir

        # bucket_dir
        self.bucket_dir = ""
        if bucket_dir != None and os.path.isdir(bucket_dir):
            self.bucket_dir = bucket_dir
        else:
            bucket_dir = os.path.join(self.workdir, "mnt/bucket")
            self.bucket_dir = bucket_dir if os.path.isdir(bucket_dir) else ""

    def reset_path(self, workdir=None, data_dir=None, group_dir=None, bucket_dir=None):
        """根据 base dir 重新配置各种文件路径

        Args:
            workdir    : 用户的工作目录
            data_dir   : 挂载数据集所在的目录
            group_dir  : 用户所在组共享存储挂载的目录
            bucket_dir : 用户所使用 bucket 数据挂载的目录
        """
        if workdir != None and os.path.isdir(workdir):
            self.workdir = workdir
        if data_dir != None and os.path.isdir(data_dir):
            self.data_dir = data_dir
        else:
            data_dir = os.path.join(self.workdir, "data")   # 兼容旧版本，都存在的话，后面覆盖前面
            if os.path.isdir(data_dir):
                self.data_dir = data_dir
            data_dir = os.path.join(self.workdir, "mnt/data")
            if os.path.isdir(data_dir):
                self.data_dir = data_dir
        if group_dir != None and os.path.isdir(group_dir):
            self.group_dir = group_dir
        else:
            group_dir = os.path.join(self.workdir, "mnt/group")
            if os.path.isdir(group_dir):
                self.group_dir = group_dir
        if bucket_dir != None and os.path.isdir(bucket_dir):
            self.bucket_dir = bucket_dir
        else:
            bucket_dir = os.path.join(self.workdir, "mnt/bucket")
            if os.path.isdir(bucket_dir):
                self.bucket_dir = bucket_dir

        #   config
        self.config_base_path = os.path.join(self.workdir, "config")
        #   params
        self.params_base_path = os.path.join(self.workdir, "params")
        self.params_file = self.params_base_path + "/default.json"
        #   trainset
        self.trainset_base_path = os.path.join(self.data_dir, "train")
        self.trainset_spec_file = os.path.join(self.config_base_path, "trainsetinfo")
        #   valset
        self.valset_base_path = os.path.join(self.data_dir, "val")
        self.valset_spec_file = os.path.join(self.config_base_path, "valsetinfo")
        #   testset
        self.testset_base_path = os.path.join(self.data_dir, "test")
        self.testset_spec_file = os.path.join(self.config_base_path, "testsetinfo")
        #   model
        self.model_base_path = os.path.join(self.workdir, "model")
        self.model_spec_file = os.path.join(self.config_base_path, "modelspec")
        #   training
        self.training_spec_file = os.path.join(self.workdir, "config/trainingspec")
        #   user
        self.user_info_file = os.path.join(self.config_base_path, "user")
        #   worker
        self.worker_info_file = os.path.join(self.config_base_path, "worker")
        #   evaluation
        self.evaluation_info_file = os.path.join(self.config_base_path, "evaluationinfo")
        #   dataset
        self.dataset_info_file = os.path.join(self.config_base_path, "datasetinfo")


def get_job_id():
    job_name = os.getenv("JOB_NAME", "")
    try:
        job_id = job_name.split("-")[2]
    except IndexError:
        job_id = ""
    return job_id
