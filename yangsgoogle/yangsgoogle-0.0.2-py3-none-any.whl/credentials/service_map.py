from yangsutil import StringUtil, ObjectUtil
from oauth2client.file import Storage
import os


class ServiceMap:
    # Service
    CALENDAR = 'calendar'
    DRIVE = 'drive'
    GMAIL = 'gmail'
    SHEETS = 'sheets'
    TEST = 'test'

    # CONST
    SERVICE_INFO_PACKAGE = 'yangsgoogle.core'
    SERVICE_INFO_CLASS = 'SERVICE'

    @staticmethod
    def get_credential_path(service_name, app_name, user_name, credential_root):
        return os.path.join(
            os.path.join(
                credential_root,
                StringUtil.blank_to_underscore(user_name),

            ),
            '%s.%s.json' % (
                service_name,
                StringUtil.blank_to_underscore(app_name)
            )
        )

    @staticmethod
    def credential_validator(service_name, app_name, user_name, credential_root):
        credential_path = ServiceMap.get_credential_path(
            service_name=service_name,
            app_name=app_name,
            user_name=user_name,
            credential_root=credential_root
        )

        ret = {'credential_path': credential_path}

        if not os.path.isfile(credential_path):
            return False, ret

        # get credential
        store = Storage(credential_path)
        ret['store'] = store

        credential = store.get()

        if not credential or credential.invalid:
            return False, ret

        else:
            ret['credential'] = credential
            return True, ret

    @staticmethod
    def get_service_info(service_name):
        return ObjectUtil.get_class(
            module_name='%s.%s' % (ServiceMap.SERVICE_INFO_PACKAGE, service_name),
            class_name=ServiceMap.SERVICE_INFO_CLASS
        )
