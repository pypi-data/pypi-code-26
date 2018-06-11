import os
import logging
import sys
import time

from lxml import etree

logger = logging.getLogger('botomfa')


def setup_logger(logger, level=logging.DEBUG):
    """Logger settings"""
    stdout_handler = logging.StreamHandler(stream=sys.stdout)
    stdout_handler.setFormatter(logging.Formatter('%(levelname)s - %(message)s'))
    stdout_handler.setLevel(level)
    logger.addHandler(stdout_handler)
    logger.setLevel(level)


def log_error_and_exit(message):
    """Log an error message and exit with error"""
    logger.error(message)
    sys.exit(1)


def log_info_and_exit(message):
    """Log an error message and exit with error"""
    logger.info(message)
    sys.exit(1)


class Tiny:

    @staticmethod
    def xml2list(xml_string):
        """
        Converts Jenkins projects api/xml description into the list of job elements
        :param xml_string: api/xml description as a string
        :return: list of elements
        """
        return etree.fromstring(xml_string).xpath('//job')

    @staticmethod
    def xml_by_xpath(xml_string, xpath):
        """
        Converts Jenkins projects api/xml description into the list of job elements
        :param xml_string: api/xml description as a string
        :return: list of elements
        """
        return etree.fromstring(xml_string).xpath(xpath)

    @staticmethod
    def get_name(job_element):
        return job_element.getchildren()[0].text

    @staticmethod
    def get_class(job_element):
        return job_element.attrib['_class']

    # @staticmethod
    # def plugins2xml(list):
    #     for plugin in list:
    #


    @staticmethod
    def get_url(job_element):
        return job_element.getchildren()[1].text

    @staticmethod
    def get_to_folder(path=''):
        """
        Create local jenkins data
        :return:
        """
        if not path:
            path = os.getcwd() + '/jen2jen_%s' % time.strftime("%d.%m_%H:%M:%S")
            os.mkdir(path)
        if not os.path.isdir(path):
            os.mkdir(path)
        os.chdir(path)
        print('Jenkins jobs are being stored in your %s local directory' % path)

    @staticmethod
    def file2xml(file_path):
        """
        Get xml payload from a local file
        :param file_path:
        :return:
        """
        return open(file_path).read()

    @staticmethod
    def validate_destination(destination):
        if destination.endswith('/'):
            destination = destination[:-1]
        if not destination.startswith('/'):
            destination = '/' + destination
        if not 'job/' in destination and '/' in destination:
            destination = destination.replace('/', '/job/')
        return destination



class JenkinsClass:

    FOLDER = 'com.cloudbees.hudson.plugins.folder.Folder'
