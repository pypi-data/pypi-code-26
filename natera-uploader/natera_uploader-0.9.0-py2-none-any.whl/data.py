#!/usr/bin/env python

import os
import re
from abc import ABCMeta, abstractmethod
from utils import UploaderException
from dx import Type


class DataFile(object):
    __metaclass__ = ABCMeta

    def __init__(self, location, name, seq_folder):
        self.__location = location
        self.__name = name
        self.__seq_folder = seq_folder

    def get_location(self):
        return self.__location

    def get_name(self):
        return self.__name

    def is_valid(self):
        return bool(self.get_regex().match(self.get_name()))

    def get_seq_folder_name(self):
        return self.__seq_folder.get_name()

    def get_relative_path(self):
        relpath = os.path.relpath(self.get_location(), self.__seq_folder.get_path())
        if relpath == ".":
            return ""
        return relpath

    def get_full_path(self):
        return os.path.join(self.__location, self.__name)

    @abstractmethod
    def get_type(self):
        raise NotImplementedError()

    @abstractmethod
    def get_regex(self):
        raise NotImplementedError()

    @abstractmethod
    def get_sample_id(self):
        raise NotImplementedError()


class RawDataFile(DataFile):
    def get_sample_id(self):
        return None

    def get_type(self):
        return None

    def get_regex(self):
        return re.compile(".+?")


class WesDataFile(DataFile):
    def get_regex(self):
        return re.compile("(?P<sample_id>[A-Za-z0-9-.]*-(FX[BG]|BXE))_[A-Za-z0-9-_]*.(?P<extension>fastq.gz|fastq|bam)")

    def get_type(self):
        m = self.get_regex().match(self.get_name())
        if m:
            extension = m.group("extension")
            if extension == "fastq.gz" or extension == "fastq":
                return Type.FASTQ
            if extension == "bam":
                return Type.BAM
        return None

    def get_sample_id(self):
        m = self.get_regex().match(self.get_name())
        if m:
            return m.group("sample_id")
        return None


class QcDataFile(DataFile):
    def get_regex(self):
        return re.compile("[A-Za-z0-9-_ ]*.(?P<extension>csv|pdf|xlsx)")

    def get_type(self):
        m = self.get_regex().match(self.get_name())
        if m:
            extension = m.group("extension")
            if extension == "csv":
                return Type.CSV
            if extension == "pdf":
                return Type.PDF
            if extension == "xlsx":
                return Type.XLSX
        return None

    def get_sample_id(self):
        return None


class SeqFolderBase(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def __init__(self, path):
        self._path = self.__get_abs_path(path)

    def get_name(self):
        return os.path.basename(self._path)

    def get_path(self):
        return self._path

    @abstractmethod
    def is_valid(self):
        raise NotImplementedError()

    @abstractmethod
    def list_files(self):
        raise NotImplementedError()

    @staticmethod
    def __get_abs_path(path):
        abs_path = os.path.abspath(os.path.expanduser(path))
        if not os.path.isdir(abs_path):
            raise UploaderException("{} does not exist".format(abs_path))
        return abs_path


class WesSignateraSeqFolder(SeqFolderBase):
    FOLDER_REGEX = re.compile("[A-Z0-9]*_[0-9]{8}")

    def __init__(self, path):
        SeqFolderBase.__init__(self, path)
        self.__wes_subfolder = os.path.join(self._path, "WES_data")
        self.__qc_subfolder = os.path.join(self._path, "QC_reports")

    def is_valid(self):
        if WesSignateraSeqFolder.FOLDER_REGEX.match(self.get_name()) is None \
                or not os.path.isdir(self.__wes_subfolder) \
                or not os.path.isdir(self.__qc_subfolder):
            return False

        if len(self.__list_from_wes()) == 0:
            print "{} does not contain any data".format(self.__wes_subfolder)
            return False
        if len(self.__list_from_qc_reports()) == 0:
            print "{} does not contain any data".format(self.__qc_subfolder)
            return False

        success = True
        for f in self.list_files():
            if not f.is_valid():
                print "{} has invalid format".format(f.get_full_path())
                success = False
        return success

    def list_files(self):
        return self.__list_from_wes() + self.__list_from_qc_reports()

    def __list_from_wes(self):
        result = []
        for f in os.listdir(self.__wes_subfolder):
            result.append(WesDataFile(self.__wes_subfolder, f, self))
        return result

    def __list_from_qc_reports(self):
        result = []
        for f in os.listdir(self.__qc_subfolder):
            result.append(QcDataFile(self.__qc_subfolder, f, self))
        return result


class RawSeqFolder(SeqFolderBase):
    def __init__(self, path):
        super(RawSeqFolder, self).__init__(path)

    def is_valid(self):
        return True

    def list_files(self):
        result = []
        for root, subdirs, files in os.walk(self._path):
            for f in files:
                result.append(RawDataFile(root, f, self))
        return result
