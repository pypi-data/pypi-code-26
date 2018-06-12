"""
Author: qiacai
"""

from ada_core.algorithms import Algorithm


__all__ = ['base_binary_judger']


class Judger(Algorithm):
    """
    Base class for Judgers, extend from Algorithm
    """

    def __init__(self, class_name, to_judge):
        """

        :param class_name:
        :param to_judge:
        :return:
        """
        super(Judger, self).__init__(class_name=class_name)
        self.to_judge = to_judge
        self.judgement = False

    def _judge(self):
        """
        The judge function, need override
        :return:
        """
        raise NotImplementedError

    def _get_result(self):
        """
        Get decision
        :return: Bool
        """
        return self.judgement

    def _run(self):
        """
        Execute the algorithm
        :return: Bool
        """
        self._judge()