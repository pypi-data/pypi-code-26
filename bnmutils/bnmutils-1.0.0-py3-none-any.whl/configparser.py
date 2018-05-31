import os

from typing import Iterable, Union, List

from configparser import ConfigParser as BuiltinConfigParser

from .exceptions import InvalidConfig, InvalidConfigOption
from .novelty import strip_blank_recursive, str_eval


class ConfigParser(BuiltinConfigParser):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Preserve casing for options
        self.optionxform = str

    @classmethod
    def from_files(cls, filenames: Union[str, os.PathLike, Iterable],
                   encoding=None, *args, **kwargs):

        # Transforming filenames into string format to work with older versions of python,  e.g. python 3.6.0
        if isinstance(filenames, Iterable) and \
                not isinstance(filenames, str):
            filenames = [str(i) for i in filenames]

        obj = cls(*args, **kwargs)
        obj.read(filenames, encoding=None)

        if not obj.sections():
            raise InvalidConfig(f"Ivalid config file/files: {filenames}.")

        return obj

    @classmethod
    def from_dict(cls, parse_dict: dict, *args, **kwargs):
        obj = cls(*args, **kwargs)

        flattened_dict = {}

        for section, val in parse_dict.items():
            flattened_dict[section] = obj._flatten_section_dict(val)

        obj.read_dict(flattened_dict)

        return obj

    def to_dict(self, section: str=None, option: str=None):
        """

        :param section:
        :param option:
        :return:
        """
        if option and not section:
            raise ValueError("Option cannot be passed on its own.")

        if section and option:
            option_str = self.get(section, option)
            return self._option_to_dict(option_str)

        if section:
            section_list = self.items(section)
            return self._section_to_dict(section_list)

        config_dict = {}
        for i in self.sections():
            config_dict[i] = self._section_to_dict(self.items(i))

        return config_dict

    def _option_to_dict(self, parse_option: str) -> dict:
        """
        Map the configuration option to dict.
        * Do not pass in the whole config section!*

        :param: parse_option: values from config.get('section', 'option')
        """
        try:
            str_split = parse_option.strip().split('\n')  # raise AttributeError
            mapped_list = list(map(lambda x: x.split(':', 1), str_split))

            strip_blank_recursive(mapped_list, evaluate=True)

            return dict(mapped_list)  # raises ValueError
        except AttributeError:
            raise InvalidConfigOption(f"option passed must be a string value, "
                                      f"not type of '{type(parse_option).__name__}'.")
        except ValueError:
            if '\n' not in parse_option:
                raise ValueError(f"'{parse_option}' cannot be converted to dict. alternatively, "
                                 f"use ConfigParser.get(section, value) to get the value.")

            raise InvalidConfigOption(f"{parse_option} is not a valid option, "
                                      f"please follow the convention of 'key: value'")

    def _section_to_dict(self, config_section: Union[List[tuple], dict]) -> dict:
        """
        Converting the ConfigParser *section* to a dictionary format

        :param config_section: values from config.items('section') or dict(config['section'])
        """
        if isinstance(config_section, dict):
            return {k: self._option_to_dict(v) if '\n' in v else str_eval(v)
                    for k, v in config_section.items()}

        if isinstance(config_section, list):
            return {i[0]: self._option_to_dict(i[1]) if '\n' in i[1] else str_eval(i[1])
                    for i in config_section}

        raise ValueError(f"Invalid section type '{type(config_section).__name__}'")

    def _flatten_section_dict(self, parse_dict: dict):
        """
        flatten nested dict config options for configuration file *sections*
        """
        flattened = {}

        for k, v in parse_dict.items():

            if isinstance(v, dict):
                val_list = [f'{k1}: {v1}' for k1, v1 in v.items()]

                str_val = '\n' + '\n'.join(val_list)
            else:
                str_val = str(v)

            flattened[k] = str_val

        return flattened
