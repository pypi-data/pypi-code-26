import tensorflow as tf
import numpy as np
import os
import sys

from . import chart_decoder
from .downloader import load_model

#%%

IS_PY2 = sys.version_info < (3,0)

ELMO_START_SENTENCE = 256
ELMO_STOP_SENTENCE = 257
ELMO_START_WORD = 258
ELMO_STOP_WORD = 259
ELMO_CHAR_PAD = 260

# Label vocab is made immutable because it is potentially exposed to users
# through the spacy plugin
LABEL_VOCAB = ((),
 ('S',),
 ('PP',),
 ('NP',),
 ('PRN',),
 ('VP',),
 ('ADVP',),
 ('SBAR', 'S'),
 ('ADJP',),
 ('QP',),
 ('UCP',),
 ('S', 'VP'),
 ('SBAR',),
 ('WHNP',),
 ('SINV',),
 ('FRAG',),
 ('NAC',),
 ('WHADVP',),
 ('NP', 'QP'),
 ('PRT',),
 ('S', 'PP'),
 ('S', 'NP'),
 ('NX',),
 ('S', 'ADJP'),
 ('WHPP',),
 ('SBAR', 'S', 'VP'),
 ('SBAR', 'SINV'),
 ('SQ',),
 ('NP', 'NP'),
 ('SBARQ',),
 ('SQ', 'VP'),
 ('CONJP',),
 ('ADJP', 'QP'),
 ('FRAG', 'NP'),
 ('FRAG', 'ADJP'),
 ('WHADJP',),
 ('ADJP', 'ADJP'),
 ('FRAG', 'PP'),
 ('S', 'ADVP'),
 ('FRAG', 'SBAR'),
 ('PRN', 'S'),
 ('PRN', 'S', 'VP'),
 ('INTJ',),
 ('X',),
 ('NP', 'NP', 'NP'),
 ('FRAG', 'S', 'VP'),
 ('ADVP', 'ADVP'),
 ('RRC',),
 ('VP', 'PP'),
 ('VP', 'VP'),
 ('SBAR', 'FRAG'),
 ('ADVP', 'ADJP'),
 ('LST',),
 ('NP', 'NP', 'QP'),
 ('PRN', 'SBAR'),
 ('VP', 'S', 'VP'),
 ('S', 'UCP'),
 ('FRAG', 'WHNP'),
 ('NP', 'PP'),
 ('NP', 'SBAR', 'S', 'VP'),
 ('WHNP', 'QP'),
 ('VP', 'FRAG', 'ADJP'),
 ('FRAG', 'WHADVP'),
 ('NP', 'ADJP'),
 ('VP', 'SBAR'),
 ('NP', 'S', 'VP'),
 ('X', 'PP'),
 ('S', 'VP', 'VP'),
 ('S', 'VP', 'ADVP'),
 ('WHNP', 'WHNP'),
 ('NX', 'NX'),
 ('FRAG', 'ADVP'),
 ('FRAG', 'VP'),
 ('VP', 'ADVP'),
 ('SBAR', 'WHNP'),
 ('FRAG', 'SBARQ'),
 ('PP', 'PP'),
 ('PRN', 'PP'),
 ('VP', 'NP'),
 ('X', 'NP'),
 ('PRN', 'SINV'),
 ('NP', 'SBAR'),
 ('PP', 'NP'),
 ('NP', 'INTJ'),
 ('FRAG', 'INTJ'),
 ('X', 'VP'),
 ('PRN', 'NP'),
 ('FRAG', 'UCP'),
 ('NP', 'ADVP'),
 ('SBAR', 'SBARQ'),
 ('SBAR', 'SBAR', 'S'),
 ('SBARQ', 'WHADVP'),
 ('ADVP', 'PRT'),
 ('UCP', 'ADJP'),
 ('PRN', 'FRAG', 'WHADJP'),
 ('FRAG', 'S'),
 ('S', 'S'),
 ('FRAG', 'S', 'ADJP'),
 ('INTJ', 'S'),
 ('ADJP', 'NP'),
 ('X', 'ADVP'),
 ('FRAG', 'WHPP'),
 ('NP', 'FRAG'),
 ('NX', 'QP'),
 ('NP', 'S'),
 ('SBAR', 'WHADVP'),
 ('X', 'SBARQ'),
 ('NP', 'PRN'),
 ('NX', 'S', 'VP'),
 ('NX', 'S'),
 ('UCP', 'PP'),
 ('RRC', 'VP'),
 ('ADJP', 'ADVP'))

#%%
class BaseParser(object):
    def __init__(self, filename):
        self._graph = tf.Graph()

        with self._graph.as_default():
            if isinstance(filename, str) and '/' not in filename:
                graph_def = tf.GraphDef.FromString(load_model(filename))
            elif not os.path.exists(filename):
                raise Exception("Argument is neither a valid module name nor a path to an existing file: {}".format(filename))
            else:
                with open(filename, 'rb') as f:
                    graph_def = tf.GraphDef.FromString(f.read())

            tf.import_graph_def(graph_def, name='')

        self._sess = tf.Session(graph=self._graph)
        self._chars = self._graph.get_tensor_by_name('chars:0')
        self._charts = self._graph.get_tensor_by_name('charts:0')

        # TODO(nikita): move this out of the source code
        self._label_vocab = LABEL_VOCAB

    def _charify(self, sentences):
        padded_len = max([len(sentence) + 2 for sentence in sentences])

        all_chars = np.zeros((len(sentences), padded_len, 50), dtype=np.int32)

        for snum, sentence in enumerate(sentences):
            all_chars[snum, :len(sentence)+2,:] = ELMO_CHAR_PAD

            all_chars[snum, 0, 0] = ELMO_START_WORD
            all_chars[snum, 0, 1] = ELMO_START_SENTENCE
            all_chars[snum, 0, 2] = ELMO_STOP_WORD

            for i, word in enumerate(sentence):
                if IS_PY2:
                    chars = [ELMO_START_WORD] + [ord(char) for char in word.encode('utf-8', 'ignore')[:(50-2)]] + [ELMO_STOP_WORD]
                else:
                    chars = [ELMO_START_WORD] + list(word.encode('utf-8', 'ignore')[:(50-2)]) + [ELMO_STOP_WORD]
                all_chars[snum, i+1, :len(chars)] = chars

            all_chars[snum, len(sentence)+1, 0] = ELMO_START_WORD
            all_chars[snum, len(sentence)+1, 1] = ELMO_STOP_SENTENCE
            all_chars[snum, len(sentence)+1, 2] = ELMO_STOP_WORD

            # Add 1; 0 is a reserved value for signaling words past the end of the
            # sentence, which we don't have because batch_size=1
            all_chars[snum, :len(sentence)+2,:] += 1

        return all_chars

    def _make_chart(self, sentence):
        inp_val = self._charify([sentence])
        out_val = self._sess.run(self._charts, {self._chars: inp_val})
        chart_size = len(sentence) + 1
        chart = out_val[0,:chart_size,:chart_size,:]
        return chart

    def _make_parse_raw(self, sentence):
        chart_np = self._make_chart(sentence)
        return chart_decoder.decode(chart_np)
