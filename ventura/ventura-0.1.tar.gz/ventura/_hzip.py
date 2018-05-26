import zipfile
import os

def extract(file_url, path_to_extract):
	# load zip file
	zip_file = zipfile.ZipFile(file_url, 'r')
	# extract in the folder
	zip_file.extractall(path_to_extract)
	# close zip
	zip_file.close()
	# delete zip file
	os.remove(file_url)
