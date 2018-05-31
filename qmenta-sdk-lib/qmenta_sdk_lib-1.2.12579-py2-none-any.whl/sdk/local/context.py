import logging
import os
import re
import shutil
import zipfile

from qmenta.sdk.directory_utils import TemporaryDirectory
from qmenta.sdk.directory_utils import mkdirs


class LocalAnalysisContext:
    def __init__(self, settings, src_folder, out_folder, res_folder):
        """
        Context object that interfaces with the QMENTA platform. Should not be created directly.
        """
        self.__settings = settings
        self.__src_folder = src_folder
        self.__out_folder = out_folder
        self.__res_folder = res_folder

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
        return {
            'state': 'local_running',
            'name': 'local',
            'script_name': 'local',
            'user_id': 'local',
            'patient_secret_name': 'local',
            'ssid': 'local',
            'settings': self.__settings,
            'tags': 'local',
            'version': 'local'
        }

    @staticmethod
    def set_progress(value=None, message=None):
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

        if value:
            value = int(value)  # Cast to int to avoid float/string problems
            if value > 100:
                logger.warning('The progress value should be between 0 and 100 (using 100 instead)')
                value = 100
            elif value < 0:
                logger.warning('The progress value should be between 0 and 100 (using 0 instead)')
                value = 0

        logger.info('Progress: {} -> {}'.format(value, message))

    def get_settings(self):
        """
        Analysis settings.

        Returns
        -------
        dict
            Settings for the current analysis.
        """
        return self.__settings

    def get_files(self, input_id, modality=None, tags=None, reg_expression=None, file_filter_condition_name=None):
        """
        Returns the files in the input container specified by `input_id` that match the modality, tags
        and regular expression, if any.

        Parameters
        ----------
        input_id : str
            Identifier "id" of the input container in advanced settings.
        modality : None
            Only None is currently accepted for local testing
        tags : None
            Only None is currently accepted for local testing
        reg_expression : None
            Only None is currently accepted for local testing
        file_filter_condition_name: None
            Not supported for local execution

        Returns
        -------
        list of File
            List of selected files from the container.
        """
        logger = logging.getLogger(__name__)
        logger.info(
            'Get files: {} [modality={} / tags={} / regex={}]'.format(input_id, modality, tags, reg_expression)
        )

        file_handlers = []

        # Create File
        for file_description in self.__settings[input_id]:
            if 'path' not in file_description:
                msg = 'Cannot find the key "path" for the input container {}'.format(input_id)
                logger.error(msg)
                raise RuntimeError(msg)

            # Use file_filter_condition_name if available
            if file_filter_condition_name:
                if 'file_filter_condition_name' not in file_description:
                    continue
                else:
                    desc_ff_name = file_description['file_filter_condition_name'].replace('c_', '')
                    func_ff_name = file_filter_condition_name.replace('c_', '')
                    if func_ff_name != desc_ff_name:
                        continue

            # Skip file conditions
            if modality:
                if 'modality' not in file_description:
                    continue
                else:
                    assert isinstance(file_description['modality'], basestring)
                    if file_description['modality'] != modality:
                        continue  # Skip this file

            if tags is not None:
                if 'tags' not in file_description:
                    continue
                else:
                    assert isinstance(file_description['tags'], list)
                    if set(file_description['tags']) != set(tags):
                        continue  # Skip this file

            if reg_expression and not re.match(reg_expression, os.path.basename(file_description['path'])):
                continue

            if 'file_info' in file_description:
                assert isinstance(file_description['file_info'], dict)

            fh = LocalFile(file_description['path'], os.path.join(self.__src_folder, str(input_id)),
                           modality=file_description.get('modality', None),
                           tags=set(file_description.get('tags', [])),
                           file_info=file_description.get('file_info', dict()))
            file_handlers.append(fh)

        return file_handlers

    def upload_file(self, source_file_path, destination_path, modality=None, tags=None, file_info=None,
                    file_format=None, container_id=None):
        """
        Upload a file to the platform, to be part of the result files.

        Parameters
        ----------
        source_file_path : str
            Path to the file to be uploaded.
        destination_path : str
            Path in the output container. Will be shown in the platform.
        modality : str
        tags : None
            Only None is currently accepted for local testing
        file_info : None
        file_format : None
        container_id : None
        """
        logger = logging.getLogger(__name__)
        if tags:
            logger.warning('Tags ignored (local execution): {}'.format(tags))
        if modality:
            logger.warning('Modality ignored (local execution): {}'.format(modality))
        if file_info:
            logger.warning('File information ignored (local execution): {}'.format(file_info))
        if file_format:
            logger.warning('File information ignored (local execution): {}'.format(file_format))
        if container_id:
            logger.warning('File information ignored (local execution): {}'.format(container_id))

        out_path = os.path.join(self.__out_folder, destination_path)
        mkdirs(os.path.dirname(out_path))
        logger.info('Uploading {!r} to {!r}'.format(source_file_path, out_path))
        shutil.copyfile(source_file_path, out_path)

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
        Downloads a resource file to the container.

        Parameters
        ----------
        path : str
            Path to the file in the resources fi
        destination_file_path : str
            Path where the file will be downloaded to
        type : str
            The resource type
        """
        logger = logging.getLogger(__name__)
        logger.info(self.__res_folder)
        if not self.__res_folder:  # Default keyword for external users
            logger.error('Resources are not properly configured. Ignoring...')
            return
        else:
            logger.info('Mocking resources from directory: {}'.format(self.__res_folder))
            logger.info('The selected mode ({}) is ignored in local execution.'.format(type))

        logger.info('Downloading resource {!r} to {!r}'.format(path, destination_file_path))

        mkdirs(os.path.dirname(destination_file_path))
        try:
            shutil.copyfile(os.path.join(self.__res_folder, path), destination_file_path)
            logger.debug('Saving {!r}'.format(destination_file_path))
        except IOError:
            logger.error('Cannot find the requested resource file.')

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
        logger.warning('Getting manual analysis data is not supported locally. Skipping...')
        return {}

    def _set_metadata_value(self, key, value):
        """
        Sets the value of a metadata parameter. Not supported for local testing.

        Parameters
        ----------
        key : str
            The ID of the metadata parameter.
        value : int, str, float
            The new content of the parameter.
        """
        logger = logging.getLogger(__name__)
        logger.info('Setting metadata value: {} -> {}'.format(key, value))
        logger.warning('Setting metadata values is not supported locally. Skipping...')

    def _get_metadata_value(self, key):
        """
        Gets the value of a metadata parameter. Not supported for local testing.

        Parameters
        ----------
        key : str
            The ID of the metadata parameter.

        Returns
        -------
        The value of the parameter
        """
        logger = logging.getLogger(__name__)
        logger.info('Getting metadata value: return <- {}'.format(key))
        logger.warning('Getting metadata values is not supported locally. Skipping...')
        return None

    def _assure_metadata_parameters(self, params):
        """
        Check whether a metadata parameter exists, creating it if not. Not supported for local testing.

        Parameters
        ----------
        params : dict
            The definition of the parameter. It may contain "title", "type", "visible", "readonly" or "order".
        """
        logger = logging.getLogger(__name__)
        logger.info('Setting metadata param (ckeck): {}'.format(params))
        logger.warning('Assuring metadata params is not supported locally. Skipping...')


class LocalFile:
    def __init__(self, name, input_container_path, modality, tags, file_info):
        """
        Object that represents a file and all its metadata in the platform. Should not be created directly.
        """
        self.name = name
        self.__input_container_path = input_container_path
        self.__download_path = None
        self.__modality = modality
        self.__tags = tags
        self.__file_info = file_info

    def get_file_modality(self):
        """
        Get the modality of the file.

        Returns
        -------
        str or None
            Modality of the file or None if not known.
        """
        return self.__modality

    @staticmethod
    def get_file_format():
        """
        Get the format of the file (e.g. 'nifti', 'txt', etc.).

        Returns
        -------
        str or None
            File format or None if not known.
        """
        return None

    def get_file_info(self):
        """
        Get the file information. The type of information depends on the type of file
        (e.g. nifti files include information such as 'Data strides', 'Data type', 'Dimensions' or 'Voxel size').

        Returns
        -------
        dict
            Dictionary of key-value pairs that depend on the format of the file.
        """
        return self.__file_info

    def get_file_tags(self):
        """
        Get the file tags.

        Returns
        -------
        set
            Set of tags associated to this file
        """
        return self.__tags

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
        logger = logging.getLogger(__name__)
        logger.info('Downloading {!r} to {!r}'.format(self.name, destination_file_path))
        mkdirs(os.path.dirname(destination_file_path))
        source_file = os.path.join(self.__input_container_path, self.name)
        shutil.copyfile(source_file, destination_file_path)
        self.__download_path = destination_file_path

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
        else:
            destination_file_path = os.path.join(dest_path, source_file)
            self.__download_file(destination_file_path)
            return self.__download_path
