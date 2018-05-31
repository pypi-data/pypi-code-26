import importlib
import inspect
import logging

from abc import abstractmethod, ABCMeta


class BaseClient(object):
    __metaclass__ = ABCMeta

    def __init__(self, context):
        self.__context = context

    def __call__(self, user_script_path):
        """
        Run an analysis provided by the user

        Parameters
        ----------
        user_script_path : str
            Should look like 'path.to.module:object', where 'object' should be an importable analysis tool class
            or a function taking one 'context' argument.
        """
        logger = logging.getLogger(__name__)
        logger.info("Launching: {}".format(user_script_path))

        self.set_state_running()
        try:
            class_or_func = load_user_analysis(user_script_path)
            self.__context.fetch_analysis_data()

            # run the analysis
            assert inspect.isfunction(class_or_func)  # may allow classes to be used later
            self.__context.set_progress(value=0, message='Running')
            class_or_func(self.__context)
        except Exception as ex:
            self.__context.set_progress(message='Error')
            self.set_state_exception()
            logger.exception(ex)
            raise
        else:
            self.__context.set_progress(message='Completed')
            self.set_state_completed()
        finally:
            self.upload_log()
            self.logout()

    @abstractmethod
    def set_state_running(self):
        pass

    @abstractmethod
    def set_state_completed(self):
        pass

    @abstractmethod
    def set_state_exception(self):
        pass

    @abstractmethod
    def upload_log(self):
        pass

    @abstractmethod
    def logout(self):
        pass


class ExecClient(BaseClient):
    def __init__(self, analysis_id, comm, context, log_path):
        super(ExecClient, self).__init__(context)
        self.__analysis_id = analysis_id
        self.__comm = comm
        self.__log_path = log_path

    def __set_analysis_state(self, state, **kwargs):
        data_to_send = {
            "analysis_id": self.__analysis_id,
            "state": state,
        }
        data_to_send.update(kwargs)
        logging.getLogger(__name__).info('State = {state!r} for analysis {analysis_id}'.format(**data_to_send))
        self.__comm.send_request("analysis_manager/set_analysis_state", data_to_send)

    def set_state_running(self):
        return self.__set_analysis_state("running", log_path=self.__log_path)

    def set_state_completed(self):
        return self.__set_analysis_state("completed")

    def set_state_exception(self):
        return self.__set_analysis_state("exception")

    def upload_log(self):

        data_to_send = {
            'analysis_id': self.__analysis_id
        }
        log_contents = ''
        try:
            with open(self.__log_path, 'r') as log_file:
                log_contents = log_file.read()
        except IOError:
            log_contents = "Log file error ({})".format(self.__log_path)
        finally:
            self.__comm.send_files('analysis_manager/upload_log',
                                   files={'file': ('exec.log', log_contents)},
                                   req_data=data_to_send)

    def logout(self):
        ret = self.__comm.send_request("logout")
        if not ret['success']:
            # Not being able to logout is a security issue and must be a fatal error
            raise RuntimeError('Unable to logout')


def load_user_analysis(user_script_path):
    module_name, class_or_func_name = user_script_path.split(':')
    user_module = importlib.import_module(module_name)
    class_or_func = getattr(user_module, class_or_func_name)
    return class_or_func
