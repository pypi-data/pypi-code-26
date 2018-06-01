import os


class ConfigWriter:
    AVAILABLE_PATH = "/etc/nginx/sites-available"
    ENABLED_PATH = "/etc/nginx/sites-enabled"
    FILENAME_PREFIX = "ngrp_"

    def __init__(self, domain):
        self._domain = domain

    def write(self, config_str, force=False):
        if os.path.exists(self._available_path) and not force:
            raise ConfigFileExistsError(self._available_path)
        self._save_config(config_str)
        self.enable_config(force=force)

    def enable_config(self, force=False):
        if os.path.exists(self._enabled_path):
            if os.path.islink(self._enabled_path):
                if not force:
                    raise ConfigLinkExistsError(self._enabled_path)
                else:
                    os.remove(self._enabled_path)
            else:
                raise ConfigLinkConflictError(self._enabled_path)

        os.symlink(self._available_path, self._enabled_path)

    def disable_config(self):
        if os.path.exists(self._enabled_path):
            if os.path.islink(self._enabled_path):
                os.remove(self._enabled_path)
            else:
                raise ConfigLinkConflictError(self._enabled_path)

    def _save_config(self, config_str):
        ConfigWriter._make_dirs()
        with open(self._available_path, "w") as f:
            f.write(config_str)

    @property
    def _available_path(self):
        return "{}/{}".format(ConfigWriter.AVAILABLE_PATH, self._filename)

    @property
    def _enabled_path(self):
        return "{}/{}".format(ConfigWriter.ENABLED_PATH, self._filename)

    @property
    def _filename(self):
        return "{}{}".format(ConfigWriter.FILENAME_PREFIX, self._domain)

    @staticmethod
    def _make_dirs():
        if not os.path.exists(ConfigWriter.AVAILABLE_PATH):
            os.makedirs(ConfigWriter.AVAILABLE_PATH)
        if not os.path.exists(ConfigWriter.ENABLED_PATH):
            os.makedirs(ConfigWriter.ENABLED_PATH)


class ConfigFileExistsError(FileExistsError):
    def __init__(self, filepath):
        self.filepath = filepath


class ConfigLinkExistsError(FileExistsError):
    def __init__(self, filepath):
        self.filepath = filepath


class ConfigLinkConflictError(FileExistsError):
    def __init__(self, filepath):
        self.filepath = filepath
