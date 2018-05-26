import pathlib
import shutil
import os

def create_dir(dir):	
	dir = os.path.dirname(dir)
	if dir == '':
		return
	
	path = pathlib.Path(dir)
	path.mkdir(parents = True, exist_ok = True) 

def	is_folder(text):
	return text.endswith("\\")

def remove_file(file):
	if os.path.isfile(file):
		os.remove(file)
		
def remove_folder(folder):
	if os.path.isdir(folder):
		shutil.rmtree(folder)
	
def delete_files(files):
	for file in files:
		if is_folder(file):
			remove_folder(file)
		else:
			remove_file(file)
