#!/usr/bin/env python

import dxpy
import os
from abc import ABCMeta, abstractmethod
from utils import UploaderException
from soyuz import __version__ as version


class Property(object):
    JOB_ID = "jobId"
    RUN_FOLDER = "runFolder"
    VERSION = "version"
    PRODUCT = "product"
    SAMPLE_REFERENCE = "uploadSampleReference"


class Type(object):
    UPLOAD_DATA = "UploadData"
    UPLOAD_SENTINEL = "UploadSentinel"
    UPLOAD_JOB = "UPLOAD"
    BAM = "bam"
    FASTQ = "fastq"
    CSV = "csv"
    PDF = "pdf"
    XLSX = "xlsx"
    WESQCREPORT = "WESQcReport"


class State(object):
    RUNNING = "running"
    WAITING = "waiting_on_input"
    TERMINATED = "terminated"
    DONE = "done"
    OPEN = "open"
    CLOSING = "closing"
    CLOSED = "closed"


class DxContext(object):
    def __init__(self, token):
        self.__token = token
        dxpy.set_security_context({'auth_token_type': 'Bearer', 'auth_token': token})
        projects = self.__get_projects()
        size = len(projects)
        if size == 0 or size > 1:
            raise UploaderException("Auth Token must have access to exactly 1 project with UPLOAD permission.")
        self.__project = projects[0]
        dxpy.set_project_context(self.__project)
        dxpy.set_workspace_id(self.__project)

    def get_project_id(self):
        return self.__project

    def get_project(self):
        return dxpy.DXProject(self.get_project_id())

    @staticmethod
    def __get_projects():
        result = []
        try:
            for project in dxpy.bindings.search.find_projects(level='UPLOAD'):
                result.append(str(project['id']))
        except dxpy.exceptions.InvalidAuthentication:
            pass
        return result


class SentinelBase(object):
    __metaclass__ = ABCMeta

    DATA_KEY = "data"
    METRICS_KEY = "run_metrics"
    DX_LINK_KEY = "$dnanexus_link"

    def __init__(self, basedir, name):
        self._dxrecord = dxpy.new_dxrecord(types=[Type.UPLOAD_SENTINEL],
                                           folder=os.path.join(basedir, name),
                                           name="{}_upload_sentinel".format(name),
                                           properties={Property.RUN_FOLDER: name,
                                                       Property.VERSION: version},
                                           parents=True)

    @abstractmethod
    def add_file(self, data_file, file_id):
        raise NotImplementedError()

    def get_id(self):
        return self._dxrecord.get_id()

    def close(self):
        self._dxrecord.close()


class WesSignateraSentinel(SentinelBase):
    def add_file(self, data_file, file_id):
        details = self._dxrecord.get_details()
        sample_id = data_file.get_sample_id()
        if sample_id:
            self._dxrecord.add_tags([sample_id])
            self.__add_data_file_details(details, sample_id, file_id)
        else:
            self.__add_metrics_details(details, file_id)
        self._dxrecord.set_details(details)

    @staticmethod
    def __add_data_file_details(details, sample_id, file_id):
        if SentinelBase.DATA_KEY not in details:
            details[SentinelBase.DATA_KEY] = {}
        data_details = details[SentinelBase.DATA_KEY]
        if sample_id not in data_details:
            data_details[sample_id] = []
        data_details[sample_id].append({SentinelBase.DX_LINK_KEY: file_id})

    @staticmethod
    def __add_metrics_details(details, file_id):
        if SentinelBase.METRICS_KEY not in details:
            details[SentinelBase.METRICS_KEY] = []
        details[SentinelBase.METRICS_KEY].append({SentinelBase.DX_LINK_KEY: file_id})


class RawSentinel(SentinelBase):
    def add_file(self, data_file, file_id):
        pass


class DxUploaderBase(object):
    __metaclass__ = ABCMeta

    def __init__(self, dx, basedir):
        self._dx = dx
        self._basedir = basedir

    def upload(self, seq_folder):
        self.__validate_target_dir(seq_folder)

        print "Starting upload for {}".format(seq_folder.get_name())
        sentinel = self._create_sentinel(seq_folder.get_name())
        for data_file in seq_folder.list_files():
            dx_file = self.upload_file_with_details(data_file, seq_folder.get_name())
            sentinel.add_file(data_file, dx_file.get_id())
        sentinel.close()
        print "{} has been successfully uploaded".format(seq_folder.get_name())

    def __validate_target_dir(self, folder):
        project = dxpy.DXProject(self._dx.get_project_id())
        try:
            entities = project.list_folder(os.path.join(self._basedir, folder.get_name()))
            if len(entities["objects"]) > 0 or len(entities["folders"]) > 0:
                raise UploaderException(
                    "{} already exists under {}".format(folder.get_name(), self._basedir))
        except dxpy.exceptions.ResourceNotFound:
            pass

    def upload_file_with_details(self, data_file, seq_folder_name):
        dx_file = self.upload_file(data_file)

        if dx_file:
            types = self._get_additional_types(data_file)
            types.append(Type.UPLOAD_DATA)

            properties = self._get_additional_properties(data_file, seq_folder_name)
            properties[Property.RUN_FOLDER] = seq_folder_name

            dx_file.add_types(types)
            dx_file.set_properties(properties)
            dx_file.close()
        else:
            raise UploaderException("Failed to upload {}".format(data_file.get_full_path()))

        return dx_file

    def upload_file(self, data_file):
        remote_folder = os.path.join(self._basedir,
                                     data_file.get_seq_folder_name(),
                                     data_file.get_relative_path())
        print "Uploading {} to {}".format(data_file.get_full_path(), remote_folder)
        return dxpy.upload_local_file(data_file.get_full_path(),
                                      folder=remote_folder,
                                      keep_open=True,
                                      parents=True)

    @abstractmethod
    def _create_sentinel(self, seq_folder_name):
        raise NotImplementedError()

    @abstractmethod
    def _get_additional_types(self, data_file):
        raise NotImplementedError()

    @abstractmethod
    def _get_additional_properties(self, data_file, seq_folder_name):
        raise NotImplementedError()


class WesSignateraDxUploader(DxUploaderBase):
    def _create_sentinel(self, seq_folder_name):
        return WesSignateraSentinel(self._basedir, seq_folder_name)

    def _get_additional_types(self, data_file):
        types = []
        data_type = data_file.get_type()
        if data_type:
            types.append(data_type)
            if data_type == Type.CSV and data_file.get_name().startswith("WES-QCMetrics"):
                types.append(Type.WESQCREPORT)
        return types

    def _get_additional_properties(self, data_file, seq_folder_name):
        properties = {}
        if data_file.get_sample_id():
            properties[Property.SAMPLE_REFERENCE] = "{}/{}".format(seq_folder_name, data_file.get_sample_id())
        return properties


class RawDxUploader(DxUploaderBase):
    def _create_sentinel(self, seq_folder_name):
        return RawSentinel(self._basedir, seq_folder_name)

    def _get_additional_types(self, data_file):
        return []

    def _get_additional_properties(self, data_file, seq_folder_name):
        return {}
