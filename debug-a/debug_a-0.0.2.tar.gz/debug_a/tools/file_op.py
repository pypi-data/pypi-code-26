# coding: utf-8
"""
file operation
==========================================================================
"""
import os

def ensure_file_exist(file):
    if not os.path.exists(file):
        create_file(file)


def create_file(file, content=None, mode="a", encoding='utf-8'):
    with open(file, mode, encoding=encoding) as f:
        if isinstance(content, str):
            content += "\n"
            f.write(content)
        elif isinstance(content, list):
            content = [i.strip("\n")+'\n' for i in content]
            f.writelines(content)
        elif content is None:
            return
        else:
            raise ValueError("If content is not None, it must be list or str!")


def write_file(file, content, mode='a', encoding='utf-8'):
    create_file(file, content=content, mode=mode, encoding=encoding)


def read_file(file, encoding='utf-8'):
    with open(file, 'r', encoding=encoding) as f:
        lines = f.readlines()
        lines = [line.strip("\n") for line in lines]
    if len(lines) > 0:
        return lines
    else:
        raise ValueError("file is empty!")


