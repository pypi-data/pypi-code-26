# coding: utf-8

import os


def cd(arg, display_cwd=True):
    os.chdir(arg)
    if display_cwd:
        print(os.getcwd())
