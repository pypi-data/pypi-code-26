import logging
import os
import requests
import time
import yaml

from .tiny import Tiny as _h
from .tiny import JenkinsClass
from lxml import etree


config = yaml.load(open('jen2jen_old/config.yml'))

logger = logging.getLogger('botomfa')


def request(func):
    def wrapper(self, *param):
        response = func(self, *param)
        if response.ok:
            if response.text:
                return response.text
        else:
            print(response.status_code)
            return response.status_code, response.reason
    return wrapper


class Jenkins:

    def __init__(self, url, login, password, crumb=True):
        if url.endswith('/'):
            url = url[:-1]
        self.url = url
        self.login = login
        self.password = password
        self.headers = {'Content-Type': 'text/xml'}
        if crumb:
            crumb_url = self.url + config['crumb-issuer']
            response = requests.get(
                crumb_url,
                auth=(self.login, self.password)
            )
            if response.ok:
                self.headers.update({**dict([response.text.split(':')])})
                print(response.status_code)
            else:
                print('No crumb received:', response.status_code, response.reason)

    @request
    def restart(self):
        return requests.get(
            self.url + config['restart-link'],
            auth=(self.login, self.password)
        )

    # @request
    def get_info(self):
        return requests.get(
                self.url + config['api-link'],
                auth=(self.login, self.password)
            )


class JenkinsExtractor(Jenkins):

    @request
    def get_config_xml(self, folder=''):
        """
        Get the content of the root level api/xml document
        :param folder: string
        :return: xml
        """
        if folder:
            url = self.url + '/job/' + folder.replace('/', '/job/') + config['api-link']
        else:
            url = self.url + config['api-link']
        return requests.get(
            url,
            auth=(self.login, self.password))

    @request
    def get_plugins_list(self):
        plugin_list_url = self.url + '/pluginManager/api/xml?depth=1'
        return requests.get(
            plugin_list_url,
            auth=(
                self.login, self.password
            )
        )

    def list_plugins_in_xml(self):
        plugins = self.get_plugins_list()
        plugins_tree = etree.fromstring(plugins)
        plugin_names = plugins_tree.xpath('//localPluginManager/plugin/shortName/text()')
        versions = plugins_tree.xpath('//localPluginManager/plugin/version/text()')
        plugins_xml_data = etree.Element("jenkins")
        for plugin in ['@'.join(map(str, i)) for i in zip(plugin_names, versions)]:
            plugins_xml_data.append(etree.Element('install', plugin=plugin))
        plugins_xml_data = etree.tostring(plugins_xml_data).decode('utf-8')
        return plugins_xml_data

    def save_plugins_list(self, local_plugins_directory):
        if not local_plugins_directory:
            local_plugins_directory = time.strftime("%d.%m_%H:%M:%S")
        if not os.path.isdir(local_plugins_directory):
            os.mkdir(local_plugins_directory)
        xml_string = self.list_plugins_in_xml()
        print(xml_string)
        with open(local_plugins_directory + '/config.xml', "w") as local_plugins_file:
            local_plugins_file.write(str(xml_string))

    @request
    def get_remote_job_xml(self, remote_job_link):
        """
        Get the contents of the config.xml file of some particular project
        :param remote_job_link: etree element
        :return: xml
        """
        return requests.get(
            _h.get_url(remote_job_link) + '/config.xml',
            auth=(
                self.login,
                self.password
            )
        )

    @staticmethod
    def save_job_xml_file(local_job_folder_path, jenkins_job_xml):
        """
        Store the job in some local directory
        :param local_job_folder_path: path to a directory to store config.xml to
        :param jenkins_job_xml: config.xml content
        :return:
        """
        if not os.path.isdir(local_job_folder_path):
            os.mkdir(local_job_folder_path)
        with open(local_job_folder_path + '/config.xml', "w") as local_job_xml_file:
            local_job_xml_file.write(jenkins_job_xml)

    def save_job_to_file(self, remote_job_link, local_job_folder_path):
        """
        Save a remote
        :param remote_job_link:
        :param local_job_folder_path:
        :return:
        """
        jenkins_job_xml = self.get_remote_job_xml(remote_job_link)
        self.save_job_xml_file(local_job_folder_path, jenkins_job_xml)

    def get_jobs_from_folder(self, remote_jenkins_folder_name, local_jobs_source_folder_name):
        """
        :param remote_jenkins_folder_name:
        :return:
        """
        if self.url in remote_jenkins_folder_name:
            remote_jenkins_folder_name = remote_jenkins_folder_name.replace(self.url, '')
        _h.get_to_folder(local_jobs_source_folder_name)
        self.extract_jobs(remote_jenkins_folder_name)

    def extract_jobs(self, job_directory=''):
        """
        Get jobs list from the root api/xml and then loop through it. If the job item is a folder create a subdirectory,
        get the folder-job config.xml, get a job list from it and loop through the list. Store every job's config.
        :param folder: string
        :return:
        """
        jobs_xml = self.get_config_xml(job_directory)
        jobs_elements_list = _h.xml2list(jobs_xml)
        for job_element in jobs_elements_list:
            job_name = _h.get_name(job_element)
            if job_directory:
                job_name = job_directory + '/' + job_name
            job_xml_source = self.get_remote_job_xml(job_element)
            self.save_job_xml_file(
                job_name,
                job_xml_source
            )
            if _h.get_class(job_element) == JenkinsClass.FOLDER:
                self.extract_jobs(job_name)


class JenkinsElevator(Jenkins):

    @request
    def post_new_job(self, job_details):
        """
        Submit a job to some Jenkins instance from some local config.xml file
        :param job_details: dictionary
        :return:
        """
        remote_folder = ''
        if job_details['json']:
            raise NotImplementedError('Posting jobs from JSON sources is not supported yet')
        else:
            if job_details['local_job_folder'].endswith('/config.xml'):
                job_xml_file_path = job_details['local_job_folder']
            else:
                job_xml_file_path = job_details['local_job_folder'] + '/config.xml'
            job_xml = _h.file2xml(job_xml_file_path)
        if 'remote_job_folder' in job_details.keys():
            remote_folder = job_details['remote_job_folder']
        url = self.url + remote_folder + config['create-item'] % job_details['job_name']
        print(url, job_xml, '\n\n\n')
        return requests.post(
            url,
            auth=(self.login, self.password),
            data=job_xml,
            headers=self.headers
        )

    def create_a_job(self, job_name, job_content_path=None, destination=None):
        if job_content_path:
            job_content = _h.file2xml(job_content_path)
        else:
            job_content = _h.file2xml('jen2jen_old/folder.xml')
        if destination:
            destination = _h.validate_destination(destination)
            url = self.url + destination + config['create-item'] % job_name
        else:
            url = self.url + config['create-item'] % job_name

        return requests.post(
            url,
            auth=(self.login, self.password),
            data=job_content,
            headers=self.headers
        )

    def process_local_folder(self, folder_name, json=False):
        """
        Loop through the local folder and submit the jobs to the recepient Jenkins instance
        :param folder_name: name of the folder to loop through
        :param json: boolean
        :return:
        """
        folder_name = folder_name.rstrip('/')
        for root, dirs, files in os.walk(folder_name):
            for name in dirs:
                local_job_folder = root + '/' + name
                if os.path.isdir(local_job_folder):
                    job_details = {
                        'json': json,
                        'job_name': name,
                        'local_job_folder': local_job_folder,
                    }
                    if root == folder_name:
                        self.post_new_job(job_details)
                    else:
                        job_details.update(
                            {
                                'remote_job_folder': root.replace(folder_name, '').replace('/', '/job/')
                            }
                        )
                        self.post_new_job(job_details)

    @request
    def post_plugins(self, data):
        """
        Get the contents of the config.xml file of some particular project
        :param remote_job_link: etree element
        :return: xml
        """
        print(data)
        url = self.url + '/pluginManager/installNecessaryPlugins'
        return requests.post(
            url,
            data=data,
            auth=(
                self.login,
                self.password
            ),
            headers=self.headers
        )

    def install_plugins(self, local_plugins_folder):
        with open(local_plugins_folder + '/config.xml', 'r') as plugins_data:
            self.post_plugins(plugins_data.read())