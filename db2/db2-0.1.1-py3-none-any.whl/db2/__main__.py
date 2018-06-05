#! usr/bin/python3.6

import sys
import os
import subprocess

SETTINGS_CODE=\
'''
#! usr/bin/python3.6

USER = 'root'
HOST = 'localhost'
DATABASE = ''
PASSWORD = ''

DEBUG = True

'''

MODELS_CODE =\
'''#! usr/bin/python3.6

from db2 import Base

class Model(Base):
    id = PositiveInteger(primary_key=True, auto_increment=True)

'''

def migrate(project_name):
	DIR = project_name
	sys.path.append(DIR)
	try:
		import settings
		from db2 import Session
	except Exception as e:
		print("Can not perform migrations.\nNo settings.py file in directory %s"%DIR)
		raise e

	s = Session(settings)
	s.makemigrations()
	print("Done...")

def runserver(project_name):
	'''
	Runs a python cgi server in a subprocess.
	'''
	DIR = os.listdir(project_name)

	if 'settings.py' not in DIR:
		raise NotImplementedError('No file called: settings.py found in %s'%project_name)

	CGI_BIN_FOLDER = os.path.join(project_name, 'cgi', 'cgi-bin')
	CGI_FOLDER = os.path.join(project_name, 'cgi')
	if not os.path.exists(CGI_BIN_FOLDER):
		os.makedirs(CGI_BIN_FOLDER)

	os.chdir(CGI_FOLDER)
	subprocess.Popen("python -m http.server --cgi 8000")


def startproject(project_name):
	if not os.path.exists(project_name):
		os.makedirs(project_name)

	SETTINGS = os.path.join(project_name, 'settings.py')
	MODELS = os.path.join(project_name, 'models.py')
	INIT = os.path.join(project_name, '__init__.py')

	if not os.path.exists(SETTINGS):
		with open(SETTINGS, 'w') as f:
			f.write(SETTINGS_CODE.strip())

	if not os.path.exists(MODELS):
		with open(MODELS, 'w') as f:
			f.write(MODELS_CODE.rstrip())

	if not os.path.exists(INIT):
		with open(INIT, 'w') as f:
			pass


def Main():
	ARGS = sys.argv

	CUR_DIR = os.getcwd()
	command = ARGS[1]
	length = len(ARGS)

	if  length == 3 and command == 'startproject':
		project_name = os.path.abspath(os.path.join(CUR_DIR, ARGS[2]))
		startproject(project_name)

	elif length == 3 and command =='runserver':
		project_name = os.path.abspath(os.path.join(CUR_DIR, ARGS[2]))
		runserver(project_name)

	elif length == 2 and command =='runserver':
		project_name = os.path.abspath(CUR_DIR)
		runserver(project_name)
	
	elif length == 3 and command == 'migrate':
		project_name = os.path.abspath(os.path.join(CUR_DIR, ARGS[2]))
		migrate(project_name)
	elif length == 2 and command == 'migrate':
		project_name = os.path.abspath(CUR_DIR)
		migrate(project_name)
	
			
if __name__ == '__main__':
	Main()
	


		
		
