import base64
import json
import os
import requests
import time
import warnings

warnings.simplefilter('ignore')


class ATD:

    PRIORITY_DICT = {0: 'add_to_q', 1: 'run_now'}
    STATUS_DICT = {5: 'Sample has finished being analyzed.', 3: 'Sample is currently being analyzed.',
                   2: 'Sample is waiting to be analyzed.',
                   0: 'Sample has been submitted but is waiting to be put in the queue.',
                   -1: 'Sample failed during the analysis process.'}

    def __init__(self, username, password, ip):
        self.ip = ip
        self.username = username
        self.password = password
        self.ANALYZER_PROFILE_URL = 'https://{}/php/vmprofiles.php'.format(self.ip)
        self.ANALYSIS_REPORT_URL = 'https://{}/php/showreport.php'.format(self.ip)
        self.LOGIN_URL = 'https://{}/php/session.php'.format(self.ip)
        self.LOGOUT_URL = 'https://{}/php/session.php'.format(self.ip)
        self.HEARTBEAT_URL = 'https://{}/php/heartbeat.php'.format(self.ip)
        self.SAMPLE_STATUS_URL = 'https://{}/php/samplestatus.php'.format(self.ip)
        self.BULK_SAMPLE_STATUS_URL = 'https://{}/php/getBulkStatus.php'.format(self.ip)
        self.TASK_LOOKUP_URL = 'https://{}/php/getTaskIdList.php'.format(self.ip)
        self.UPLOAD_URL = 'https://{}/php/fileupload.php'.format(self.ip)
        self.BASE_HEADER = {'Accept': 'application/vnd.ve.v1.0+json'}

    def __enter__(self):
        self.login()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.logout()

    def login(self):
        self.ve_sdk_api = base64.b64encode('{}:{}'.format(self.username, self.password).encode('utf-8')).decode('utf-8')

        session_headers = self.BASE_HEADER
        session_headers['VE-SDK-API'] = self.ve_sdk_api
        response = requests.get(self.LOGIN_URL, headers=session_headers, verify=False)
        response_content = json.loads(response.text)

        if response_content['success'] is False:
            raise InvalidCredentialException('ATD login verification failed.')

        self.session_id = response_content['results']['session']
        self.user_id = response_content['results']['userId']
        self.ve_sdk_api = base64.b64encode('{}:{}'.format(self.session_id, self.user_id).encode('utf-8')).decode('utf-8')
        self.BASE_HEADER['VE-SDK-API'] = self.ve_sdk_api

    def logout(self):
        session_headers = self.BASE_HEADER
        session_headers['VE-SDK-API'] = self.ve_sdk_api
        response = requests.delete(self.LOGOUT_URL, headers=session_headers, verify=False)
        response_content = json.loads(response.text)

        if response_content['success'] is False:
            raise InvalidCredentialException('An error occurred while logging out of the ATD platform.')

    def heartbeat(self):
        heartbeat_headers = self.BASE_HEADER
        response = requests.get(self.HEARTBEAT_URL, headers=heartbeat_headers, verify=False)
        response_content = json.loads(response.text)

        return response_content['success']

    def analyze_file(self, file, priority=0, vm_profile=1):
        file_path = os.path.abspath(file)
        priority = self.PRIORITY_DICT[priority]

        upload_headers = self.BASE_HEADER
        upload_data = {'data':
                           '''{"data":
                               {"xMode":0,"overrideOS": 1, "messageId":"", "vmProfileList": "%s", 
                               "submitType": "0", "url": "", "filePriorityQ": "%s"}
                           }''' % (vm_profile, priority)
                       }
        file_upload = {'amas_filename': open(file_path, 'rb')}
        response = requests.post(self.UPLOAD_URL, upload_data, headers=upload_headers, files=file_upload, verify=False)
        response_content = json.loads(response.text)

        if response_content['success'] is False:
            raise InvalidPayloadException(
                'Some error occured with your file submission check the file you submitted and make sure the payload is not over 200MB.')
        else:
            sub_id = response_content['subId']
            mime = response_content['mimeType']
            task_id = response_content['results'][0]['taskId']
            p = self.Process(sub_id, self, os.path.basename(file), mime, task_id)
            return p

    def analyze_url(self, url, priority=0, vm_profile=1):
        priority = self.PRIORITY_DICT[priority]

        if not url.startswith('http://') or not url.startswith('https://'):
            url = 'http://{}'.format(url)

        upload_headers = self.BASE_HEADER
        upload_data = {'data':
                        '''{"data":
                            {"xMode":0,"overrideOS": 1, "messageId":"", "vmProfileList": "%s", 
                            "submitType": "1", "url": "%s", "filePriorityQ": "%s"}
                        }''' % (vm_profile, url, priority)
                       }
        response = requests.post(self.UPLOAD_URL, upload_data, headers=upload_headers, verify=False)
        response_content = json.loads(response.text)

        if response_content['success'] is False:
            raise InvalidUrlException('URL is invalid double check the url and make sure it begins with http:// or https://')
        else:
            sub_id = response_content['subId']
            mime = response_content['mimeType']
            task_id = response_content['results'][0]['taskId']
            p = self.Process(sub_id, self, url, mime, task_id)
            return p

    '''
    def get_all_sample_status(self):
        response = requests.post(self.BULK_SAMPLE_STATUS_URL, headers=self.BASE_HEADER, verify=False)
        response_content = json.loads(response.text)

        samples = {}
        print(response_content)
        for sample in response_content['results']:
            print(sample)
            name = str(sample['filename'])
            status = sample['status']
            job_id = sample['jobid']
            md5 = sample['md5']
            samples[name] = (job_id, status, md5)
        return samples
    '''

    def get_analyzer_profiles(self):
        response = requests.get(self.ANALYZER_PROFILE_URL, headers=self.BASE_HEADER, verify=False)
        response_content = json.loads(response.text)

        analyzers = {}
        for analyzer in response_content['results']:
            name = analyzer['name']
            id = analyzer['vmProfileid']
            analyzers[name] = id
        return analyzers

    class Process:

        def __init__(self, sub_id, atd, name=None, mime=None, task_id=None):
            self.name = name
            self.sub_id = sub_id
            self.mime = mime
            self.task_id = task_id
            self.atd = atd

            self.TASK_LOOKUP_URL = '{}?jobId={}'.format(self.atd.TASK_LOOKUP_URL, self.sub_id)

        def get_analysis_status(self):
            analysis = {}
            for task in self.get_task_list():
                SAMPLE_STATUS_URL = '{}?iTaskId={}'.format(self.atd.SAMPLE_STATUS_URL, task)
                response = requests.get(SAMPLE_STATUS_URL, headers=self.atd.BASE_HEADER, verify=False)
                response_content = json.loads(response.text)
                name = response_content['results']['filename']
                status = response_content['results']['status']
                md5 = response_content['results']['md5']
                submit_time = response_content['results']['submitTime']
                vm = response_content['results']['vmName']

                analysis[name] = (status, md5, submit_time, vm)
            return analysis

        def get_analysis_report(self, report_type='zip'):
            reports = []
            for task in self.get_task_list():
                analysis_report_url = '{}?iTaskId={}&iType={}'.format(self.atd.ANALYSIS_REPORT_URL, task,
                                                                        report_type)
                response = requests.get(analysis_report_url, headers=self.atd.BASE_HEADER, verify=False)
                if response.status_code == 400:
                    raise InvalidReportException(
                        'You did not provide the correct information to retrieve a report. Make sure you send either the job id or the md5 hash of the sample.')
                elif response.status_code != 500:
                    reports.append(response.content)
            return reports

        def get_task_list(self):
            response = requests.get(self.TASK_LOOKUP_URL, headers=self.atd.BASE_HEADER, verify=False)
            response_content = json.loads(response.text)

            if response_content['success']:
                task_list = response_content['result']['taskIdList'].split(',')
                return task_list
            else:
                raise JobNotFoundException('The file that was submitted failed and has no jobs tied to it.')


class InvalidPayloadException(Exception):
    def __init__(self, message):
        super().__init__(message)


class InvalidReportException(Exception):
    def __init__(self, message):
        super().__init__(message)


class InvalidUrlException(Exception):
    def __init__(self, message):
        super().__init__(message)


class InvalidCredentialException(Exception):
    def __init__(self, message):
        super().__init__(message)


class JobNotFoundException(Exception):
    def __init__(self, message):
        super().__init__(message)

