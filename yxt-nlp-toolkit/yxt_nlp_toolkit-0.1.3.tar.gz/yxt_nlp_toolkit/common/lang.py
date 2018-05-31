import numpy as np


class Lang:
    SOS_TOKEN, SOS_INDEX = '<sos>', 0
    EOS_TOKEN, EOS_INDEX = '<eos>', 1
    NIL_TOKEN, NIL_INDEX = '<nil>', 2

    def __init__(self, words, name='zh'):
        self._name = name
        self._word2ix = self._build_word2ix(words)
        self._ix2word = self._build_ix2word(self._word2ix)

    def word_iter(self):
        return iter(self._word2ix.keys())

    def index_iter(self):
        return iter(range(0, self.vocab_size))

    def __len__(self):
        return len(self._word2ix)

    def __contains__(self, item):
        if isinstance(item, int):
            return item in self._ix2word
        elif isinstance(item, str):
            return item in self._word2ix
        else:
            return False

    def __iter__(self):
        return iter(self._word2ix.items())

    def __repr__(self):
        return str(self)

    def __str__(self):
        return 'Lang(name={name},vocab_size={vocab_size})'.format(
            name=self._name, vocab_size=self.vocab_size)

    def __getitem__(self, item):
        if isinstance(item, int):
            return self.word(item)
        elif isinstance(item, str):
            return self.ix(item)
        raise TypeError("only support int,str:but found:{}({})".format(
            type(item), item))

    def build_embedding(self, wv, out_embedding=None):
        from ..embedding.wordembedding import WordEmbedding
        if not isinstance(wv, WordEmbedding):
            raise TypeError('only support WordEmbedding,but found {}'.format(type(wv)))
        if out_embedding is None:
            out_embedding = np.random.randn(self.vocab_size, wv.embedding_dim)
        for ix, word in self._ix2word.items():
            try:
                if ix < len(out_embedding):
                    out_embedding[ix] = wv[word]
            except KeyError:
                pass
        return out_embedding

    @property
    def vocab_size(self):
        return len(self._word2ix)

    @property
    def name(self):
        return self._name

    def in_vocab(self, word):
        return word in self._word2ix

    def ix(self, word):
        assert isinstance(word, str)
        return self._word2ix.get(word, Lang.NIL_INDEX)

    def word(self, index):
        assert isinstance(index, int)
        if index == Lang.NIL_INDEX:
            return Lang.NIL_TOKEN
        if index in self._ix2word:
            return self._ix2word[index]
        raise ValueError('unknown index:{}'.format(index))

    def vocabulary(self):
        return tuple(self._word2ix.keys())

    @staticmethod
    def _build_word2ix(words):
        word2ix = {
            Lang.SOS_TOKEN: Lang.SOS_INDEX,
            Lang.EOS_TOKEN: Lang.EOS_INDEX,
            Lang.NIL_TOKEN: Lang.NIL_INDEX
        }
        for w in set(words):
            if w not in word2ix:
                word2ix[w] = len(word2ix)

        return word2ix

    @staticmethod
    def _build_ix2word(word2ix):
        return dict((ix, w) for w, ix in word2ix.items())

    def dump(self, path):
        import pickle
        with open(path, 'wb') as f:
            pickle.dump(self, f)

    @classmethod
    def load(cls, path):
        import pickle
        with open(path, 'rb') as f:
            return pickle.load(f)


def build_lang_from_token_stream(token_stream, min_count=1, lang_name='zh'):
    from collections import Counter
    words_freq = Counter(token_stream)
    words = tuple(w for w, freq in words_freq.items() if freq >= min_count)
    return Lang(name=lang_name, words=words)


def build_lang_from_corpus(corpus_or_corpus_seq, min_count=1, lang_name='zh'):
    from yxt_nlp_toolkit.utils.tokenizer import token_stream
    tokens = token_stream(corpus_or_corpus_seq)
    return build_lang_from_token_stream(tokens, min_count=min_count, lang_name=lang_name)
