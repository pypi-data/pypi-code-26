"""Monte Carlo Simulator"""
import random
from statistics import mean, median

try:
    from matplotlib import pyplot
    USING_MATPLOTLIB = True
except ImportError:
    USING_MATPLOTLIB = False


class MonteCarloSimulaterController():
    def __init__(self, actions=[], results=[]):
        assert len(actions) >= 1 and isinstance(actions, list)
        assert len(results) >= 1 and isinstance(results, list)

        self._actions = actions
        self._results = results
        self._results_count = [0 for i in range(len(results))]
        self._iterations = 0


    @staticmethod
    def flip_a_coin(outputs=[0, 1]):
        """Flips A Coin
        params: output - What should it output - default: [0, 1]
        """
        assert len(output) == 2
        return random.choice(outputs)

    @staticmethod
    def roll_a_dice(outputs=[1, 2, 3, 4, 5, 6]):
        """Rolls A Dice
        params: output - What should it output - default: [ 1, 2, 3, 4, 5, 6]
        """
        assert len(outputs) == 6
        return random.choice(outputs)

    def _strength(self, result):
        """Gets The Strength of a Result"""
        for x, y in zip(self._results, self._results_count):
            if x == result:
                return y / self._iterations

    def take_action(self, available_actions=None):
        """Takes An Action"""
        available_actions = self._actions if available_actions is None else available_actions
        return random.choice(available_actions)


    def add_result(self, results):
        """Processes The Results
        params: resuts - The Result Which Occured"""
        for result_index in range(len(self._results)):
            if results == self._results[result_index]:
                self._results_count[result_index] += 1
                self._iterations += 1
                return
        raise Exception("Result Did'nt Match PreDefined Results")

    def max_result(self, strength=False):
        """Returns Result With Most Occurrence
        params: strength - if strength is true, the function will return strength of that result in decimal (Which can be converted in percentage by multiplying with 100"""
        maximum = self._results[self._results_count.index(max(self._results_count))]
        if not strength:
            return maximum
        else:
            return maximum, self._strength(maximum)

    def avg_result(self, strength=False):
        """Returns The Average Output"""
        avg_occur = mean(self._results_count)
        avg =  self._results[self._results_count.index(min(self._results_count, key=lambda x:abs(x-avg_occur)))]
        if not strength:
            return avg
        else:
            return avg, self._strength(avg)

    def median_result(self, strength=False):
        """Returns The Average Output"""
        median_occur = median(self._results_count)
        med =  self._results[self._results_count.index(min(self._results_count, key=lambda x:abs(x-median_occur)))]
        if not strength:
            return med
        else:
            return med, self._strength(med)

    def results_count(self):
        """Returns Each Result Count"""
        counts = {}
        for x, y in zip(self._results, self._results_count):
            counts[x] = y
        return counts


