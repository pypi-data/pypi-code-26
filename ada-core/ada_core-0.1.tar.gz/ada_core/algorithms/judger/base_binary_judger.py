"""
Author: qiacai
"""

"""
This base function provide simple binary compare =, >, >=, <,<=
Both the left side & right side should be numeric at this version
"""

from numbers import Number

from ada_core.algorithms import Algorithm
from ada_core import exceptions
from ada_core.algorithms.judger import Judger
from ada_core.data.entry import Entry


class BaseBinaryJudger(Judger):
    def __init__(self, class_name, to_judge, comparator):
        """
        Initializer

        :return:
        """

        super(BaseBinaryJudger, self).__init__(class_name=class_name, to_judge=to_judge)
        self.left_value = BaseBinaryJudger._parse_to_judge(self.to_judge)
        self.right_value = BaseBinaryJudger._parse_comparator(comparator)

    @staticmethod
    def _parse_to_judge(to_judge):

        if isinstance(to_judge, Number):
            return to_judge
        elif isinstance(to_judge, Algorithm):
            to_judge_result = to_judge.run()
            if isinstance(to_judge_result, Number):
                return to_judge_result
            else:
                raise exceptions.ParametersNotPassed(
                    'ada_core.algorithms.judger.base_binary_judger._parse_to_judge, input Algorithm return not correct.')
        elif isinstance(to_judge, Entry):
            return to_judge.value
        else:
            raise exceptions.ParametersNotPassed(
                'ada_core.algorithms.judger.base_binary_judger._parse_to_judge, input not correct.')

    @staticmethod
    def _parse_comparator(comparator):
        if isinstance(comparator, Number):
            return comparator
        elif isinstance(comparator, Algorithm):
            comparator_result = comparator.run()
            if isinstance(comparator_result, Number):
                return comparator_result
            else:
                raise exceptions.ParametersNotPassed(
                        'ada_core.algorithms.judger.base_binary_judger._parse_comparator, input not correct.')
        elif isinstance(comparator, Entry):
            return comparator.value
        else:
            raise exceptions.ParametersNotPassed(
                    'ada_core.algorithms.judger.base_binary_judger._parse_comparator, input not correct.')

    def _judge(self):
        """
        The judge function, need override
        :return:
        """
        raise NotImplementedError


class EqualBinaryJudger(BaseBinaryJudger):
    def __init__(self, to_judge, comparator):
        super(EqualBinaryJudger, self).__init__(self.__class__.__name__, to_judge=to_judge, comparator=comparator)

    def _judge(self):
        if self.left_value == self.right_value:
            self.judgement = True


class GreaterThanBinaryJudger(BaseBinaryJudger):
    def __init__(self, to_judge, comparator):
        super(GreaterThanBinaryJudger, self).__init__(self.__class__.__name__, to_judge=to_judge, comparator=comparator)

    def _judge(self):
        if self.left_value > self.right_value:
            self.judgement = True


class GreaterThanOrEqualBinaryJudger(BaseBinaryJudger):
    def __init__(self, to_judge, comparator):
        super(GreaterThanOrEqualBinaryJudger, self).__init__(self.__class__.__name__, to_judge=to_judge,
                                                             comparator=comparator)

    def _judge(self):
        if self.left_value >= self.right_value:
            self.judgement = True


class LessThanBinaryJudger(BaseBinaryJudger):
    def __init__(self, to_judge, comparator):
        super(LessThanBinaryJudger, self).__init__(self.__class__.__name__, to_judge=to_judge, comparator=comparator)

    def _judge(self):
        if self.left_value < self.right_value:
            self.judgement = True


class LessThanOrEqualBinaryJudger(BaseBinaryJudger):
    def __init__(self, to_judge, comparator):
        super(LessThanOrEqualBinaryJudger, self).__init__(self.__class__.__name__, to_judge=to_judge,
                                                          comparator=comparator)

    def _judge(self):
        if self.left_value <= self.right_value:
            self.judgement = True