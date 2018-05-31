import json
import logging
import os
import re
import uuid
import zipfile

import requests

from qmenta.sdk.directory_utils import TemporaryDirectory
from qmenta.sdk.directory_utils import mkdirs


class AnalysisContext:
    def __init__(self, analysis_id, comm):
        """
        Context object that interfaces with the QMENTA platform. Should not be created directly.
        """
        self.analysis_id = analysis_id
        self.__comm = comm
        self.__containers_data = {}
        self.analysis_data = None

    def fetch_analysis_data(self):
        """
        Fetch information about current analysis.

        Returns
        -------
        dict
            Dictionary that contains important information about the current analysis, such as:
                * state (str) : State of the analysis
                * name (str) : Name of the analysis
                * script_name (str) : Name of the script
                * user_id (str) : Username of the user that started the analysis
                * patient_secret_name (str) : Name of the subject
                * ssid (str) : Timepoint identifier
                * settings (dict) : Settings dictionary. See documentation in method `get_settings`
                * tags (list) : List of tags
                * version (str) : Tool version
        """
        res = self.__comm.send_request("analysis_manager/get_analysis_list", {"id": self.analysis_id})
        if res:
            self.analysis_data = res[0]
            return self.analysis_data
        else:
            error_msg = "Analysis with ID={} not found".format(self.analysis_id)
            raise ValueError(error_msg)

    def set_progress(self, message=None, value=None):
        """
        Sets analysis progress.

        Parameters
        ----------
        value : int, optional
            Number between 0 and 100 indicating the current status of the execution
        message : str, optional
            Progress message.
        """
        logger = logging.getLogger(__name__)

        if not value and not message:
            logger.warning('No information is available to report the progress')
            return

        data_to_send = {
            'analysis_id': self.analysis_id
        }

        if value:
            value = int(value)  # Cast to int to avoid float/string problems
            if value > 100:
                logger.warning('The progress value should be between 0 and 100 (using 100 instead)')
                value = 100
            elif value < 0:
                logger.warning('The progress value should be between 0 and 100 (using 0 instead)')
                value = 0
            data_to_send['value'] = value

        if message:
            data_to_send['message'] = message

        logger.info('Progress: {} -> {}'.format(value, message))
        self.__comm.send_request("analysis_manager/set_analysis_progress", data_to_send)

    def get_settings(self):
        """
        Analysis settings.

        Returns
        -------
        dict
            Settings for the current analysis.
        """
        return self.analysis_data["settings"]

    def get_files(self, input_id, modality=None, tags=None, reg_expression=None, file_filter_condition_name=None):
        """
        Returns the files in the input container specified by `input_id` that match the modality, tags
        and regular expression, if any. (X)OR that are selected by the file filter condition
        defined in the tool settings.

        Parameters
        ----------
        input_id : str
            Identifier "id" of the input container in advanced settings.
        modality : str, optional
            Optional modality, will allow any modalities if None given.
            Default is None.
        tags : set, optional
            Optional set of tags, will allow any tags if None given, and will match any set of tags (including
            the empty set) otherwise.
            Default is None.
        reg_expression : str, optional
            Regular expression to match with the file names in the specified container, will allow any file names
            if None given.
            Default is None.
        file_filter_condition_name : str, optional
            File filter specified in the settings of the tool.
            Default is None.

        Returns
        -------
        list of qmenta.sdk.context.File
            List of selected files from the container.
        """
        logger = logging.getLogger(__name__)
        logger.info(
            'Get files: {} [modality={} / tags={} / regex={}]'.format(input_id, modality, tags, reg_expression)
        )

        file_filter_condition_name = file_filter_condition_name or ''

        input_settings = self.analysis_data["settings"][input_id]
        if input_id not in self.__containers_data:
            # find the id from the settings
            container_id = input_settings["container_id"]
            res = self.__comm.send_request("file_manager/get_container_files", {"container_id": container_id})
            self.__containers_data[input_id] = res["data"]
        else:
            container_id = input_settings["container_id"]

        if file_filter_condition_name:

            selected_files = []

            if input_settings["passed"]:
                try:
                    file_filter_spec = input_settings["filters"][file_filter_condition_name]
                except KeyError:
                    msg = "File filter condition {} not specified in the container {} settings !".format(
                        file_filter_condition_name, input_id
                    )
                    logger.error(msg)
                    raise Exception(msg)
                else:
                    for file_desc in file_filter_spec["files"]:
                        metadata = self.__containers_data[input_id]["meta"]
                        find_file_data = [f for f in metadata if f["name"] == file_desc["name"]]
                        if find_file_data:
                            file_data = find_file_data[0]
                            selected_files.append(File(
                                container_id, file_data["name"], file_data["metadata"], file_data["tags"], self.__comm
                            ))

            return selected_files
        else:
            # in case the file filter condition name is not specified then we need to take the other
            # concrete search conditions i.e. modality, tags, reg_expression

            # filter the files according to the filter defined
            container_data = self.__containers_data[input_id]
            return self.__files_from_container_data(container_data, container_id, modality, tags, reg_expression)

    def _get_files_from_container(self, container_id, modality=None, tags=None, reg_expression=None):
        logger = logging.getLogger(__name__)
        logger.info('Get files from container {}'.format(container_id))
        res = self.__comm.send_request("file_manager/get_container_files", {"container_id": container_id})
        if res["success"]:
            return self.__files_from_container_data(res["data"], container_id, modality, tags, reg_expression)
        else:
            raise RuntimeError(res["error"])

    def __files_from_container_data(self, container_data, container_id, modality, tags, reg_expression):
        selected_files = []
        for file_data in container_data["meta"]:

            # TODO: Here we are assuming that file metadata has a name and a metadata attribute. Need of jsonschema

            fname, fmetadata, ftags = file_data['name'], file_data['metadata'], set(file_data['tags'])
            assume_file_selected = _should_include_file(fname, fmetadata, ftags, modality, tags, reg_expression)

            if assume_file_selected:
                selected_files.append(File(container_id, fname, fmetadata, ftags, self.__comm))
        return selected_files

    def upload_file(
            self, source_file_path, destination_path, modality=None, tags=None, file_info=None, file_format=None,
            container_id=None
    ):
        """
        Upload a file to the platform, to be part of the result files.

        Parameters
        ----------
        source_file_path : str
            Path to the file to be uploaded.
        destination_path : str
            Path in the output container. Will be shown in the platform.
        modality: str, optional
            Optional modality of the uploaded file.
            None by default.
        tags : set, optional
            Set of tags for the uploaded file.
            None by default.
        file_info : dict, optional
            File information metadata.
        file_format : str, optional
            Inferred format of the file (dicom, nifti, bvec, bval, &c).
        container_id : int, optional
            The ID of the output container, only needed in special cases.
        """
        logger = logging.getLogger(__name__)

        tags = tags or set()

        if modality:
            tags.add('m:' + modality)

        logger.info('Uploading {!r} to {!r}'.format(source_file_path, destination_path))

        # File information
        file_name = destination_path.split("/")[-1]
        total_bytes = os.path.getsize(source_file_path)
        session_id = str(uuid.uuid4())
        logger.debug('Upload file {} with size {} bytes and session ID {}'.format(
            source_file_path, total_bytes, session_id
        ))

        # making chunks of the file and sending one by one
        with open(source_file_path, "r") as file_object:
            # Upload
            for chunk_num, data in enumerate(iter(lambda: file_object.read(self.__comm.chunk_size), b"")):
                start_position = chunk_num * self.__comm.chunk_size
                end_position = start_position + self.__comm.chunk_size - 1
                bytes_to_send = self.__comm.chunk_size

                if end_position >= total_bytes:
                    end_position = total_bytes - 1
                    bytes_to_send = total_bytes - chunk_num * self.__comm.chunk_size

                bytes_range = "bytes {}-{}/{}".format(start_position, end_position, total_bytes)

                # Request headers
                req_headers = dict()
                req_headers["Content-Type"] = "application/octet-stream"
                req_headers["Content-Range"] = bytes_range
                req_headers["Session-ID"] = str(session_id)
                req_headers["Content-Length"] = str(bytes_to_send)
                req_headers["Content-Disposition"] = 'attachment; filename={}'.format(file_name)

                # If it is the last chunk, define more header fields
                if chunk_num * self.__comm.chunk_size + bytes_to_send == total_bytes:
                    logger.debug('Sending last data chunk')
                    req_headers["X-Mint-Analysis-Output"] = str(self.analysis_id)
                    req_headers["X-Mint-File-Destination-Path"] = destination_path
                    req_headers["X-Mint-File-Tags"] = ",".join(tags)
                    if file_info:
                        req_headers["X-Mint-File-Info"] = json.dumps(file_info)
                    if file_format:
                        req_headers["X-Mint-File-Format"] = str(file_format)
                    if container_id:
                        req_headers["X-Mint-Container"] = str(container_id)
                    req_headers["X-Requested-With"] = "XMLHttpRequest"

                response = self.__comm.send_request("upload", data, req_headers, return_json=False)

            # Verify that file has been indeed saved into the platform
            if response and json.loads(response.content)['success']:
                logger.info('Upload completed')
            else:
                msg = 'File {} could not be uploaded to the platform'.format(source_file_path)
                logger.error(msg)
                raise RuntimeError(msg)

    def download_resource(self, resource_path, destination_path):
        """
        Downloads a file from the user/group tool resources. The resource path can include subdirectories and must
        be relative:

        >>> context.download_resource('dir/subdir/file.nii.gz', '/root/file.nii.gz')

        Parameters
        ----------
        path : str
            Path to the file in the resources bucket.
        destination_file_path : str
            Path where the file will be downloaded.
        """

        self._download_resource(resource_path, destination_path, type='tool_resource')

    def _download_resource(self, path, destination_file_path, type='template'):
        """
        Downloads a resource file from the bucket (user/group based resources, or legacy).

        Parameters
        ----------
        path : str
            Path to the file in the resources bucket.
        destination_file_path : str
            Path where the file will be downloaded.
        type : str
            The resource type
        """
        logger = logging.getLogger(__name__)
        logger.info('Downloading resource {!r} to {!r}'.format(path, destination_file_path))

        data_to_send = {
            'analysis_id': self.analysis_id,
            'type': type,
            'path': path,
        }
        try:
            res = self.__comm.send_request("analysis_manager/get_resource", data_to_send, total_retry=1,
                                           return_json=False, stream=True)
        except requests.HTTPError as ex:
            logger.exception(ex)
            if ex.response.status_code == 404:
                msg = "Resource file {!r} not found".format(path)
                logger.error(msg)
                raise Exception(msg)

            raise

        mkdirs(os.path.dirname(destination_file_path))

        logger.debug('Saving {!r}'.format(destination_file_path))
        with open(destination_file_path, 'wb') as fp:
            for chunk in res.iter_content(chunk_size=self.__comm.chunk_size):
                if chunk:  # filter out keep-alive new chunks
                    fp.write(chunk)
                    fp.flush()
        logger.debug('Finished downloading resource {!r}'.format(destination_file_path))

    def _get_manual_analysis_data(self):
        """
        Returns a dictionary with the manual analysis data generated during the manual step (user interaction)

        Returns
        -------
        dict
            The values generated during the manual step.
        """
        logger = logging.getLogger(__name__)
        logger.info('Getting manual analysis data')

        data_to_send = {
            'analysis_id': self.analysis_id,
        }
        try:
            res = self.__comm.send_request("analysis_manager/get_manual_analysis_data", data_to_send, total_retry=1)
        except requests.HTTPError as ex:
            logger.exception(ex)
            if ex.response.status_code == 404:
                msg = "Manual analysis data not found (request exception)"
                logger.error(msg)
                raise Exception(msg)
            raise
        else:
            return res['value']

    def _set_metadata_value(self, key, value):
        """
        Sets the value of a metadata parameter.

        Parameters
        ----------
        key : str
            The ID of the metadata parameter.
        value : int, str, float
            The new content of the parameter.
        """
        logger = logging.getLogger(__name__)

        data_to_send = {
            'analysis_id': self.analysis_id,
            'key': key,
            'value': value,
            'patient_secret_name': self.analysis_data['patient_secret_name'],
            'ssid': self.analysis_data['ssid']
        }

        logger.info('Setting metadata value: {} -> {}'.format(key, value))

        try:
            res = self.__comm.send_request("analysis_manager/set_metadata_value", data_to_send, total_retry=1)
            if not res['success']:
                msg = "Metadata error: {!r}".format(res['error'])
                logger.error(msg)
                raise Exception(msg)
        except requests.HTTPError as ex:
            logger.exception(ex)
            raise

    def _get_metadata_value(self, key):
        """
        Gets the value of a metadata parameter.

        Parameters
        ----------
        key : str
            The ID of the metadata parameter.

        Returns
        -------
        The value of the parameter
        """
        logger = logging.getLogger(__name__)

        data_to_send = {
            "key": key,
            "analysis_id": self.analysis_id,
            "ssid": self.analysis_data['ssid'],
            "patient_secret_name": self.analysis_data['patient_secret_name'],
        }

        logger.info('Getting metadata value: return <- {}'.format(key))

        try:
            res = self.__comm.send_request("analysis_manager/get_metadata_value", data_to_send, total_retry=1)
            if not res['success']:
                msg = "Metadata error: {!r}".format(res['error'])
                logger.error(msg)
                raise Exception(msg)
        except requests.HTTPError as ex:
            logger.exception(ex)
            raise
        else:
            return res['value']

    def _assure_metadata_parameters(self, params):
        """
        Ensure that a parameter exists.

        Parameters
        ----------
        params : dict or dictionary of lists
            The definition of the parameter. It may contain "title", "type", "visible", "readonly" or "order".
        """
        logger = logging.getLogger(__name__)

        if not isinstance(params, list):
            params = list(params)

        for data_to_send in params:
            if not isinstance(data_to_send, dict):
                msg = "Format error. Metadata param configuration should be stored in a dictionary"
                logger.error(msg)
                raise TypeError(msg)

            data_to_send['analysis_id'] = self.analysis_id
            logger.info('Checking metadata param config: {}'.format(data_to_send))
            try:
                res = self.__comm.send_request("analysis_manager/set_metadata_param", data_to_send, total_retry=1)
                if not res['success']:
                    msg = "Metadata error: {!r}".format(res['error'])
                    logger.error(msg)
                    raise Exception(msg)
            except requests.HTTPError as ex:
                logger.exception(ex)
                raise


class File:
    def __init__(self, container_id, name, metadata, tags, comm):
        """
        Object that represents a file and all its metadata in the platform. Should not be created directly.
        """
        self.__comm = comm
        self.__container_id = container_id
        self.name = name
        self.__metadata = metadata
        self.__tags = tags
        self.__download_path = None

    def get_file_modality(self):
        """
        Get the modality of the file.

        Returns
        -------
        str or None
            Modality of the file or None if not known.
        """
        return self.__metadata.get("modality", None)

    def get_file_format(self):
        """
        Get the format of the file (e.g. 'nifti', 'txt', etc.).

        Returns
        -------
        str
            File format or None if not known.
        """
        return self.__metadata.get("format", None)

    def get_file_info(self):
        """
        Get the file information. The type of information depends on the type of file
        (e.g. nifti files include information such as 'Data strides', 'Data type', 'Dimensions' or 'Voxel size').

        Returns
        -------
        dict
            Dictionary of key-value pairs that depend on the format of the file.
        """
        return self.__metadata.get("info", {})

    def get_file_tags(self):
        """
        Get the file tags.

        Returns
        -------
        set
            Set of tags associated to this file
        """
        return self.__tags if self.__tags is not None else set()

    def get_file_path(self):
        """
        Get the file download path.

        Returns
        -------
        str
            The path of the file where it has been downloaded

        Raises
        ------
        RuntimeError
            If `get_file_path` is called before the file has been downloaded
        """
        if self.__download_path is None:
            err_msg = "File {!r} has no path because it has not been downloaded".format(self.name)
            logging.getLogger(__name__).error(err_msg)
            raise RuntimeError(err_msg)
        else:
            return self.__download_path

    def __download_file(self, destination_file_path):
        """
        Downloads the file into the specified `destination_file_path`.

        Parameters
        ----------
        destination_file_path : str
            Path where the file should be downloaded.
        """
        source_file = self.name

        logger = logging.getLogger(__name__)
        logger.info('Downloading {!r} to {!r}'.format(source_file, destination_file_path))

        data_to_send = {"container_id": self.__container_id, "files": source_file}
        logger.debug('Accessing {files!r} from container {container_id!r}'.format(**data_to_send))
        res = self.__comm.send_request("file_manager/download_file", data_to_send, return_json=False, stream=True)

        mkdirs(os.path.dirname(destination_file_path))

        with open(destination_file_path, 'wb') as fp:
            for chunk in res.iter_content(chunk_size=self.__comm.chunk_size):
                if chunk:  # filter out keep-alive new chunks
                    fp.write(chunk)
                    fp.flush()

        self.__download_path = destination_file_path
        logger.debug('Finished downloading {!r}'.format(destination_file_path))

    def download(self, dest_path, unpack=True):
        """
        Downloads a file or the contents of a packed file to to the specified `path`.

        Parameters
        ----------
        dest_path:
            Path where the file should be downloaded to.
        unpack:
            Tells the function whether the file should be unpacked to the given folder.

        Returns
        -------
        str:
            The full path of the file or the folder with the unpacked files.
        """
        logger = logging.getLogger(__name__)
        source_file = self.name

        # Normalize path
        dest_path = os.path.abspath(dest_path)

        logger.debug('Using path {!r}'.format(dest_path))

        if source_file.endswith('.zip') and unpack:
            # Download the zip to a temporary directory and unpack its contents to the user dir path
            with TemporaryDirectory() as temp_dir:
                temp_path = os.path.join(temp_dir, source_file)
                self.__download_file(temp_path)
                with zipfile.ZipFile(temp_path, 'r') as zip_ref:
                    file_list = zip_ref.namelist()
                    logger.info('Decompressing {!r} to {!r}'.format(file_list, dest_path))
                    mkdirs(dest_path)
                    zip_ref.extractall(path=dest_path)

            self.__download_path = dest_path  # Replace download path with directory
            return dest_path

        # Download the file to the directory and return the full path
        else:
            destination_file_path = os.path.join(dest_path, source_file)
            self.__download_file(destination_file_path)
            return destination_file_path


""" HELPERS """


def _should_include_file(fname, fmetadata, ftags, search_modality, search_tags, search_reg_expression):
    """ Checks if file should be selected or not according to the specified selectors. """

    assume_file_selected = True

    if search_modality is not None:
        try:
            if fmetadata['modality'] != search_modality:
                return False
        except KeyError:
            # No modality in metadata, do not include this file
            return False

    if search_tags is not None:
        assert isinstance(ftags, set)
        assert isinstance(search_tags, set)
        if search_tags != ftags:
            return False

    if search_reg_expression is not None:
        if not re.match(search_reg_expression, fname):
            return False

    return assume_file_selected
