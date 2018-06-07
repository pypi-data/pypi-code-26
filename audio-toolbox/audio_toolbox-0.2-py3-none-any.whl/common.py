import subprocess
import os

def run_in_foreground(cmd):
    print(cmd)
    return subprocess.check_output(cmd.split(), shell=False)

def append_suffix_to_filename(file, suffix):
    root_and_ext = os.path.splitext(file)
    return root_and_ext[0] + suffix + root_and_ext[1]

def remove_file(file):
    os.remove(file)
