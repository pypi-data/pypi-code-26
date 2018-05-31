import logging

from qmenta.sdk.client import BaseClient


class LocalExecClient(BaseClient):
    @staticmethod
    def __set_analysis_state(state):
        logging.getLogger(__name__).info('State = {state!r} for local execution'.format(state=state))

    def set_state_running(self):
        return self.__set_analysis_state("running")

    def set_state_completed(self):
        return self.__set_analysis_state("completed")

    def set_state_exception(self):
        return self.__set_analysis_state("exception")

    def upload_log(self):
        pass

    def logout(self):
        pass
