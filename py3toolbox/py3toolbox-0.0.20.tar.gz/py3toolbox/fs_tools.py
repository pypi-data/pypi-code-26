import os
import sys
import re
import hashlib
import glob
from shutil import copyfile


def rm_folder(folder_name):
  shutil.rmtree(folder_name,ignore_errors=True)
    
def mk_folder(folder_name) :
  os.makedirs(folder_name, exist_ok=True)

def clean_folder(folder_name):
  for the_file in os.listdir(folder_name):
    file_path = os.path.join(folder_name, the_file)
    if   os.path.isfile(file_path) : rm_file(file_path)
    elif os.path.isdir(file_path)  : rm_folder(file_path)
  
def is_file_exists(file_name):
  return os.path.exists(file_name)
  
def copy_file(src_file,dest_file):
  if is_file_exists(src_file) :  copyfile(src_file,dest_file)    
  
def rm_file(file_name) :
  if os.path.isfile(file_name): 
    os.remove(file_name)
    
def write_file(file_name, text, mode='w', is_new = False):
  if is_new == True: rm_file(file_name)
  with open(file_name, mode) as fh:
    fh.write(text)

def write_log(file_name, text, is_new = False):
  write_file(file_name=file_name, text=text + "\n", mode='a', is_new=is_new)
    
def read_file(file_name, return_type='str'):
  if return_type == 'str' :
    return open(file_name, 'r').read()
    
  if return_type == 'list' :
    return open(file_name, 'r').readlines() 
    
def get_md5(file_name) :  
  hasher = hashlib.md5()
  with open(file_name, 'rb') as fh:
    buf = fh.read()
    hasher.update(buf)
  return (hasher.hexdigest())

def get_files(folder, ftype = '.*', recursive=True) :
  files = glob.glob(folder + '/**/*' + ftype , recursive=recursive)
  return (files)


    