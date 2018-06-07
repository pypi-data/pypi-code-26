# -*- coding: utf-8 -*-

"""Main module."""
import os
from subprocess import run as shell_run

current_path = os.path.dirname(os.path.abspath(__file__))


def merge_docx(result_docx, *merging_docx):
    cmd_script = ['php', '{}/engine/merge_docx.php'.format(current_path), ] + list(merging_docx) + [result_docx, ]
    shell_result = shell_run(cmd_script)
    return shell_result
