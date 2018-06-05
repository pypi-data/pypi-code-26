import os

from golem.nlu.utils import data_dir


class FuzzyMatcher:
    def __init__(self, entity):
        self.entity = entity
        pass

    def train(self, training_data):
        for obj in training_data['data']:
            label = obj['label']
            examples = obj['examples']
            # TODO generate all words in edit distance and save them
