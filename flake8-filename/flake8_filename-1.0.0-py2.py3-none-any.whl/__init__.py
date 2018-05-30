# -*- coding: utf-8 -*-

from flake8_filename import rules

__version__ = '1.0.0'


class FilenameChecker(object):
    """
    Flake8 plugin to validate filenames match a user defined pattern.
    """
    name = 'flake8-filename'
    version = __version__
    min_check = 1
    max_check = 50
    filename_checks = dict.fromkeys(["filename_check{}".format(x) for x in range(min_check, max_check)], {})

    @classmethod
    def add_options(cls, parser):
        """Required by flake8
        add the possible options, called first

        Args:
            parser (OptionsManager):
        """
        kwargs = {'action': 'store', 'default': '', 'parse_from_config': True,
                  'comma_separated_list': True}
        for num in range(cls.min_check, cls.max_check):
            parser.add_option(None, "--filename_check{}".format(num), **kwargs)

    @classmethod
    def parse_options(cls, options):
        """Required by flake8
        parse the options, called after add_options

        Args:
            options (dict): options to be parsed
        """
        d = {}
        for filename_check, dictionary in cls.filename_checks.items():
            # retrieve the marks from the passed options
            filename_data = getattr(options, filename_check)
            if len(filename_data) != 0:
                parsed_params = {}
                for single_line in filename_data:
                    a = [s.strip() for s in single_line.split('=')]
                    # whitelist the acceptable params
                    if a[0] in ['filter_regex', 'filename_regex']:
                        parsed_params[a[0]] = a[1]
                d[filename_check] = parsed_params
        cls.filename_checks.update(d)
        # delete any empty rules
        cls.filename_checks = {x: y for x, y in cls.filename_checks.items() if len(y) > 0}

    # noinspection PyUnusedLocal,PyUnusedLocal
    def __init__(self, tree, filename, *args, **kwargs):
        """Required by flake8

        Args:
            tree (ast.AST): An AST tree. (Required by flake8, but never used by this plug-in)
            filename (str): The name of the file to evaluate.
            args (list): A list of positional arguments.
            kwargs (dict): A dictionary of keyword arguments.
        """

        self.filename = filename

    def run(self):
        """Required by flake8
        Will be called after add_options and parse_options.

        Yields:
            tuple: (int, int, str, type) the tuple used by flake8 to construct a violation
        """

        if len(self.filename_checks) == 0:
            message = "N401 no configuration found for {}, " \
                      "please provide filename configuration in a flake8 config".format(self.name)
            yield (0, 0, message, type(self))

        rule_funcs = [rules.rule_n5xx]

        for rule_func in rule_funcs:
            for rule_name, configured_rule in self.filename_checks.items():
                for err in rule_func(self.filename, rule_name, configured_rule, type(self)):
                    yield err
