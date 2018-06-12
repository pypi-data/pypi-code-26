"""
Author: qiacai
"""


class Algorithm(object):
    """
    Base class for Algorithm
    """

    def __init__(self, class_name):
        self.class_name = class_name

    def _get_result(self):
        raise NotImplementedError

    def _run(self):
        raise NotImplementedError

    def run(self):
        self._run()
        return self._get_result()

    def get_class_name(self):
        return self.class_name