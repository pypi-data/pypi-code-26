# -*- coding: utf-8 -*-

import re
from os.path import basename, splitext


def _generate_mark_code(rule_name):
    """Generates a two digit string based on a provided string

    Args:
        rule_name (str): A configured rule name 'pytest_mark3'.

    Returns:
        str: A two digit code based on the provided string '03'
    """
    code = ''.join([i for i in str(rule_name) if i.isdigit()])
    code = code.zfill(2)
    return code


def rule_n5xx(filename, rule_name, rule_conf, class_type):
    """Validate filename against a pattern if the filename passes the filter.

    Args:
        filename (str): The name of the file being parsed by flake8.
        rule_name (str): The name of the rule.
        rule_conf (dict): The dictionary containing the properties of the rule
        class_type (class): The class that this rule was called from

    Yields:
        tuple: (int, int, str, type) the tuple used by flake8 to construct a violation
    """

    line_num = 0
    code = _generate_mark_code(rule_name)
    message = "N5{} filename failed regex validation '{}'".format(code, rule_conf['filename_regex'])

    sanitized_filename = splitext(basename(filename))[0]    # Strip path and extension

    if re.match(rule_conf['filter_regex'], sanitized_filename):
        if not re.match(rule_conf['filename_regex'], sanitized_filename):
            yield (line_num, 0, message, class_type)
