# Copyright 2017 Mycroft AI, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import re

from padatious.match_data import MatchData
from padatious.train_data import TrainData
from padatious.trainable import Trainable
from padatious.util import tokenize


class Intent(Trainable):
    """Full intent object to handle entity extraction and intent matching"""

    def __init__(self, *args, **kwargs):
        super(Intent, self).__init__(*args, **kwargs)
        self.pattern = None

    def match(self, sent, entities=None):
        match = self.pattern.match(' '.join(sent))
        if not match:
            return MatchData(self.name, sent)

        return MatchData(self.name, sent, self.__remove_ids(match.groupdict()), 1.0)

    def __remove_ids(self, matches):
        return {
            k.split('__')[0]: tokenize(v) for k, v in matches.items() if v
        }

    def __to_regex(self, lines):
        i = 0
        for line_tokens in lines:
            changed = None
            line = ' '.join(line_tokens)
            while changed != line:
                changed = re.sub(r'{([a-z_-]+)}', r'(?P<\1__{}>.*)'.format(i), line, count=1)
                yield changed
                line = changed
                i += 1

    def train(self, train_data: TrainData):
        pattern_str = '({})'.format('|'.join(
            self.__to_regex(train_data.my_sents(self.name))
        ))
        self.pattern = re.compile(pattern_str)
