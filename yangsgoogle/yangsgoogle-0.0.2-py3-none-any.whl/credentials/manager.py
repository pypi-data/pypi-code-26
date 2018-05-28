from yangsutil import LogUtil, FileUtil
from yangsgoogle.credentials.service_map import ServiceMap
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage
from apiclient import discovery
import httplib2


class CredentialManager:
    def __init__(self, logger=None):
        if logger is None:
            self.logger = LogUtil.get_logger(app_name='Google Credential Manager')
        else:
            self.logger = logger

    def create(self, option, flags):

        credential = self.__get(
            service_name=option['service_name'],
            app_name=option['app_name'],
            user_name=option['user_name'],
            credential_root=option['credential_root']
        )

        if credential is None:
            self.logger.info('Create credential...')

        else:
            self.logger.info('Credential Found...')
            return

        ###################
        # credential path #
        ###################
        credential_path = ServiceMap.get_credential_path(
            service_name=option['service_name'],
            app_name=option['app_name'],
            user_name=option['user_name'],
            credential_root=option['credential_root']
        )

        self.logger.info('Credential Path : %s' % credential_path)

        # create folder
        FileUtil.make_folder(credential_path)

        ##########
        # create #
        ##########
        # service info
        service = ServiceMap.get_service_info(option['service_name'])

        # client secret
        flow = client.flow_from_clientsecrets(option['client_secret'], service['scope'])
        flow.user_agent = option['app_name']

        # generate
        if flags:
            tools.run_flow(flow, Storage(credential_path), flags)

    def service(self, service_name, app_name, user_name, credential_root):

        credential = self.__get(
            service_name=service_name,
            app_name=app_name,
            user_name=user_name,
            credential_root=credential_root
        )

        if credential is None:
            self.logger.info('Not found credential...')
            return None

        # service info
        service_info = ServiceMap.get_service_info(service_name)

        # make service
        try:
            service = discovery.build(
                service_name,
                service_info['version'],
                http=credential.authorize(httplib2.Http()),
                discoveryServiceUrl=service_info['discovery_url']
            )
        except KeyError:
            service = discovery.build(
                service_name,
                service_info['version'],
                http=credential.authorize(httplib2.Http())
            )

        return service

    # private
    def __get(self, service_name, app_name, user_name, credential_root):

        status, credential_info = ServiceMap.credential_validator(
            service_name=service_name,
            app_name=app_name,
            user_name=user_name,
            credential_root=credential_root
        )
        self.logger.info('Credential Path : %s' % credential_info['credential_path'])

        if status is False:
            try:
                store = credential_info['store']
            except KeyError:
                self.logger.info('Not found credential file...')
                return None

            self.logger.info('Invalid credential... (%s)' % str(store))
            return None

        else:
            credential = credential_info['credential']
            self.logger.info('Credential : %s' % str(credential))
            return credential

    def test_for_get(self, service_name, app_name, user_name, credential_root):
        return self.__get(service_name, app_name, user_name, credential_root)
