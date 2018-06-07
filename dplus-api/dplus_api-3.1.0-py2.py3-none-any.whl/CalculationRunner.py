from __future__ import absolute_import

import glob
import signal

import numpy
import codecs
import platform
import subprocess
import tempfile
import uuid
import os
import json
import shutil
import psutil as psutil
import requests
import time
import hashlib
import logging
from multiprocessing import Process

from dplus.FileReaders import handle_infinity, MyEncoder
from .CalculationResult import CalculationResult
# from .Fit import Fitter
import math





class JobRunningException(Exception):
    def __init__(self):
        self.value = "there is a job already running in this session"

    def __str__(self):
        return repr(self.value)

_is_windows = platform.system() == 'Windows'

class Runner(object):
    def generate(self, calc_data):
        '''
        :param calc_data:
        :return: a CalculationResult
        '''
        raise NotImplemented
    def generate_async(self, calc_data):
        '''
        :param calc_data:
        :return: a RunningJob
        '''
        raise NotImplemented
    def fit(self, calc_data):
        '''
        :param calc_data:
        :return: a CalculationResult
        '''
        raise NotImplemented
    def fit_async(self, calc_data):
        '''
        :param calc_data:
        :return: a RunningJob
        '''
        raise NotImplemented


class RunningJob(object):
    def _start(self, calc_data):
        '''
        :param calc_data:
        :return:
        '''
        raise NotImplemented
    def get_status(self):
        '''
        :return:
        '''
        raise NotImplemented
    def _get_result(self):
        '''
        :return:
        '''
        raise NotImplemented
    def abort(self):
        '''
        ends the current job.
        '''
        raise NotImplemented
    def _get_pdb(self, model_ptr, destination_folder=None):
        '''
        :param model_ptr:
        :return:
        '''
        raise NotImplemented
    def _get_amp(self, model_ptr, destination_folder=None):
        '''
        :param model_ptr:
        :return:
        '''
        raise NotImplemented
    def get_result(self, calc_data):
        return CalculationResult(calc_data, self._get_result(), self)

def as_job(job_dict):
    '''
    this is the function used as an object hook for json deserialization of a dictionary to a job object.
    all changes made to __init__ of RunningJob need to be reflected here.
    '''
    job = LocalRunner.RunningJob(job_dict["session_directory"], job_dict["pid"])
    return job

class LocalRunner(Runner):
    class RunningJob(RunningJob):
        def __init__(self, session_directory, pid=-1):
            self.session_directory = os.path.abspath(session_directory)
            self.pid=pid
            #self.jobtype=jobtype


        def _check_running(self):
            try:
                if self.pid != -1:
                    process = psutil.Process(self.pid)
                    if process.status() == psutil.STATUS_ZOMBIE:
                        process.wait()
                    else:
                        raise JobRunningException
            except psutil.NoSuchProcess:
                pass

        def _clean_folder(self):
            filename = os.path.join(self.session_directory, "data.json")
            if os.path.exists(filename):
                os.remove(filename)


        def _start(self, calc_data):
            # 1: check that no job is already running in this session folder
            self._check_running()
            # clean out the session folder
            self._clean_folder()


            # save the calc_data as args
            filename = os.path.join(self.session_directory, "args.json")


            with open(filename, 'w') as outfile:
                json.dump(handle_infinity(calc_data.args), outfile, cls=MyEncoder)

            #save an initial job status file:
            filename = os.path.join(self.session_directory, "job.json")
            jobstat={"isRunning":True, "progress":0.0, "code":0}
            with open(filename, 'w') as outfile:
                json.dump(jobstat, outfile, cls=MyEncoder)

        def get_status(self):
            filename = os.path.join(self.session_directory, "job.json")
            for x in range(4):  # try 3 times
                try:
                    with codecs.open(filename, 'r', encoding='utf8') as f:
                        result = json.load(f)
                        return result
                        break
                except json.JSONDecodeError:
                    if x==4:
                        raise BlockingIOError("Failed to access job status")
                    time.sleep(0.1)


        def _get_file_status(self):
            filename = os.path.join(self.session_directory, "notrunning")
            with open(filename, 'r') as f:
                status=f.readline()
            return status=="True"

        def _get_result(self):
            filename = os.path.join(self.session_directory, "data.json")
            with codecs.open(filename, 'r', encoding='utf8') as f:
                result = json.load(f)
            if type(result) is dict:
                if 'error' in result.keys():
                    error_message_dict = result['error']
                    raise Exception(error_message_dict['message'])
            return result

        def abort(self):
            try:
                os.kill(self.pid, signal.SIGTERM)
            finally:
                filename = os.path.join(self.session_directory, "isrunning")
                os.remove(filename)

        def _get_pdb(self, model_ptr, destination_folder=None):
            '''
            :param model_ptr:
            :return:
            '''

            ptr_string = '%08d.pdb' % (int(model_ptr))
            file_location=os.path.join(self.session_directory, 'pdb', ptr_string)
            if os.path.isfile(file_location):
                if destination_folder:
                    shutil.copy2(file_location, destination_folder)
                    return os.path.join(destination_folder, ptr_string)
                return file_location
            raise FileNotFoundError


        def _get_amp(self, model_ptr, destination_folder=None):
            '''
            :param model_ptr:
            :return:
            '''
            ptr_string = '%08d.amp' % (int(model_ptr))
            file_location=os.path.join(self.session_directory, 'cache', ptr_string)
            if os.path.isfile(file_location):
                if destination_folder:
                    shutil.copy2(file_location, destination_folder)
                    return os.path.join(destination_folder, ptr_string)
                return file_location
            raise FileNotFoundError


    def __init__(self, exe_directory=None, session_directory=None):
        if not exe_directory:
            try:
                exe_directory = self._find_dplus()
            except Exception as e:
                raise ValueError("Can't locate D+, please specify the D+ backend directory manually", e)
        if not session_directory:
            session_directory = tempfile.mkdtemp()

        self._exe_directory = os.path.abspath(exe_directory)
        self._check_exe_directory()

        self._session_directory = os.path.abspath(session_directory)
        self._make_file_directories(session_directory)

    @property
    def session_directory(self):
        return self._session_directory

    @session_directory.setter
    def session_directory(self, session_dir):
        self._session_directory = os.path.abspath(session_dir)
        self._make_file_directories(session_dir)

    def _find_dplus(self):
        if not _is_windows:
            raise ValueError("Can't find D+ on non Windows machine")

        import winreg
        RawKey = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\HUJI")
        d_plus = ""
        try:
            i = 0
            while 1: # will fail when there are no more keys in  "SOFTWARE\HUJI"
                tmp_name = winreg.EnumKey(RawKey, i)
                if "D+" in tmp_name:
                    d_plus = tmp_name
                i += 1
        except WindowsError:
            pass
        if d_plus == "":
            raise  "D+ does not exists"

        dplus_key = os.path.join("SOFTWARE\HUJI", d_plus)
        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE,dplus_key) as key:
            exe_dir = winreg.QueryValueEx(key, "binDir")[0]
            return exe_dir

    def _get_program_path(self, calculation_type):
        program_path = os.path.join(self._exe_directory, calculation_type)
        if _is_windows:
            program_path += ".exe"
        return program_path

    def _check_exe_directory(self):
        if not os.path.isdir(self._exe_directory):
            raise NotADirectoryError("%s is not a directory" % self._exe_directory)

        programs = ['generate', 'fit', 'getallmetadata']
        paths = [self._get_program_path(program) for program in programs]
        valid = [os.path.isfile(path) for path in paths]

        if not all(valid):
            raise ValueError("The directory %s does not seem to contain the D+ backend executables" % self._exe_directory)

    def _make_file_directories(self, directory):
        os.makedirs(os.path.join(directory, 'pdb'), exist_ok=True)
        os.makedirs(os.path.join(directory, 'amp'), exist_ok=True)
        os.makedirs(os.path.join(directory, 'cache'), exist_ok=True)

    def generate(self, calc_data):
        result= self._run(calc_data)
        calc_result = CalculationResult(calc_data, result, LocalRunner.RunningJob(self._session_directory))
        return calc_result

    def generate_async(self, calc_data):
        job=self._run(calc_data, async=True)
        return job

    def fit(self, calc_data):
        result= self._run(calc_data, calculation_type="fit")
        calc_result = CalculationResult(calc_data, result, LocalRunner.RunningJob(self._session_directory))
        return calc_result

    # def python_fit(self, calc_data):
    #     temprunner=LocalRunner(exe_directory=self._exe_directory)
    #     fitter = Fitter(temprunner, calc_data)
    #     result = fitter.fit(self._session_directory)
    #     return result.to_dplus()

    # def python_fit_async(self, calc_data):
    #     job=LocalRunner.RunningJob(self._session_directory)
    #     job.start(calc_data)
    #     err_file = open(os.path.join(self._session_directory, "error.txt"), 'w')
    #     out_file = open(os.path.join(self._session_directory, "output.txt"), 'w')
    #     python_path=r"D:\UserData\devora\Sources\dplus\PythonInterface\env35\Scripts\python.exe"
    #     program_path=r"D:\UserData\devora\Sources\dplus\PythonInterface\fitwrapper.py"
    #     process = subprocess.Popen([python_path, program_path, self._exe_directory, self._session_directory], stdout=out_file, stderr=err_file)
    #     job.pid= process.pid
    #     return job

    def fit_async(self, calc_data):
        job= self._run(calc_data, calculation_type="fit", async=True)
        return job

    def _run(self, calc_data, calculation_type="generate", async=False):
        #1 start the job
        job=LocalRunner.RunningJob(self._session_directory)
        job._start(calc_data)
        #2 call the executable process
        process=self._call_exe(calculation_type)
        job.pid=process.pid
        #3 return, based on async
        if async:
            return job

        process.communicate()
        return job._get_result()

    def _call_exe(self, calculation_type):
        err_file = open(os.path.join(self._session_directory, "error.txt"), 'w')
        out_file = open(os.path.join(self._session_directory, "output.txt"), 'w')
        program_path = self._get_program_path(calculation_type)
        if not os.path.isfile(program_path):
            raise FileNotFoundError
        process = subprocess.Popen([program_path, self._session_directory], cwd=self._exe_directory, stdout=out_file, stderr=err_file)
        return process

    @staticmethod
    def get_running_job(session):
        return LocalRunner.RunningJob(session)


class WebRunner(Runner):
    class RunningJob(RunningJob):
        def __init__(self, base_url, token, session):
            self._url = base_url + r'api/v1/'
            self._header = {'Authorization': "Token " + str(token)}
            self._session = str(uuid.uuid4())
            self._session_string = "?ID=" + session
        def _start(self, calc_data):
            # check if files
            self._check_files(calc_data)

        def get_status(self):
            jobstatus = requests.get(url=self._url + 'job' + self._session_string, headers=self._header)
            if jobstatus.status_code==200:
                result = json.loads(jobstatus.text)
                print("requested job status, results were", result)
                return result
            else:
                print("error fetching result")


        def _get_result(self, calculation_type="generate"):
            response = requests.get(url=self._url + calculation_type + self._session_string, headers=self._header)
            result = json.loads(response.text)
            if type(result) is dict:
                if 'error' in result.keys():
                    error_message_dict = result['error']
                    raise Exception(error_message_dict['message'])
            return result

        def _check_files(self, calc_data):
            def calc_file_hash(filepath):  # taken from stackexchange 1869885/calculating-sha1-of-a-file
                sha = hashlib.sha1()
                with open(filepath, 'rb') as f:
                    while True:
                        block = f.read(2 ** 10)  # Magic number: one-megabyte blocks.
                        if not block: break
                        sha.update(block)
                    return sha.hexdigest().upper()

            filedict = {'files': []}
            for filename in calc_data.filenames:
                dict = {}
                dict['filename'] = filename
                dict['size'] = os.stat(filename).st_size
                dict['hash'] = calc_file_hash(filename)
                filedict['files'].append(dict)
            data = json.dumps(filedict)
            response = requests.post(url=self._url + 'files', data=data, headers=self._header)
            statuses = json.loads(response.text)

            files_missing = []
            for filename in calc_data.filenames:
                if statuses[filename]['status'] == 'MISSING':
                    files_missing.append((filename, statuses[filename]['id']))

            self._upload_files(files_missing)

        def _upload_files(self, filenames):
            for filename, id in filenames:
                url = self.url + 'files/' + str(id)
                files = {'file': open(filename, 'rb')}
                response = requests.post(url=url, headers=self.header, files=files)

        def _get_pdb(self, model_ptr, destination_folder=None):
            '''
            :param model_ptr:
            :return: file address
            '''
            if not destination_folder:
                destination_folder=tempfile.mkdtemp()
            ptr_string = '%08d.pdb' % (int(model_ptr))
            destination_file= os.path.join(destination_folder, ptr_string)
            #code used from: https://stackoverflow.com/a/16696317/5961793
            response = requests.get(url=self._url + "pdb/"+str(model_ptr) + self._session_string, headers=self._header, stream=True)
            with open(destination_file, 'wb') as f:
                for chunk in response.iter_content(chunk_size=1024):
                    if chunk:  # filter out keep-alive new chunks
                        f.write(chunk)
            return destination_file

        def _get_amp(self, model_ptr, destination_folder=None):
            '''
            :param model_ptr:
            :return: file address
            '''
            if not destination_folder:
                destination_folder=tempfile.mkdtemp()
            ptr_string = '%08d.amp' % (int(model_ptr))
            destination_file= os.path.join(destination_folder, ptr_string)
            #code used from: https://stackoverflow.com/questions/13137817/how-to-download-image-using-requests
            response = requests.get(url=self._url + "amplitude/"+str(model_ptr) + self._session_string, headers=self._header, stream=True)
            with open(destination_file, 'wb') as f:
                for chunk in response.iter_content(chunk_size=1024):
                    if chunk:  # filter out keep-alive new chunks
                        f.write(chunk)
            return destination_file




    def __init__(self, base_url, token):
        self._url = base_url + r'api/v1/'
        self._header = {'Authorization': "Token "+str(token)}
        self._session=str(uuid.uuid4())
        self._session_string = "?ID=" + self._session
        self._job = WebRunner.RunningJob(base_url, token, self._session)

    def generate(self, calc_data):
        result = self._run(calc_data)
        calc_result = CalculationResult(calc_data, result['result'], self._job)
        return calc_result

    def generate_async(self, calc_data):
        return self._run(calc_data, async=True)

    def fit(self, calc_data):
        result = self._run(calc_data, calculation_type="fit")
        calc_result = CalculationResult(calc_data, result['result'], self._job)
        return calc_result

    def fit_async(self, calc_data):
        return self._run(calc_data, calculation_type="fit", async=True)

    def _run(self, calc_data, calculation_type="generate", async=False):
        #1: start the job (checks files)
        self._job._start(calc_data)
        #2: make the necessary call
        data = json.dumps(calc_data.args['args'])
        test = requests.put(url=self._url + calculation_type + self._session_string, data=data, headers=self._header)
        #3 return depending on sync or async
        if async:
            return self._job

        while True:
            res=self._job.get_status()
            if res['result']['isRunning'] == False:
                break
            time.sleep(1)

        return self._job._get_result(calculation_type)


    @staticmethod
    def get_running_job(url, token, session):
        return WebRunner.RunningJob(url, token, session)