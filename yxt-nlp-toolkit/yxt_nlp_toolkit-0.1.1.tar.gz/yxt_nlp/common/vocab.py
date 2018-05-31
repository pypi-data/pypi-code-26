import collections


class Vocab:

    def __init__(self, words=(), from_freqs=None):
        self._freqs = collections.Counter(words)
        if from_freqs is not None:
            for k, v in from_freqs.items():
                self._freqs[k] += v

    def increase_freq(self, word, freq=1):
        self._freqs[word] += freq
        return self

    def shrink_(self, min_count):
        assert min_count >= 0
        freqs = dict((w, f) for w, f in self._freqs.items() if f >= min_count)
        self._freqs = collections.Counter(freqs)
        return self

    def shrink(self, min_count):
        assert min_count >= 0
        vocab = Vocab()
        for w, f in self._freqs.items():
            if f >= min_count:
                vocab[w] = f
        return vocab

    def __contains__(self, item):
        return item in self._freqs

    def __delitem__(self, key):
        del self._freqs[key]

    def __setitem__(self, key, value):
        self._freqs[key] = value

    def __getitem__(self, item):
        return self._freqs[item]

    def __iter__(self):
        return iter(self._freqs.keys())

    def __len__(self):
        return len(self._freqs)

    def __repr__(self):
        return '<Vocab(n_word={})>'.format(len(self))

    @classmethod
    def load(cls, file):
        vocab = Vocab()
        with open(file, 'r') as f:
            for line in f:
                try:
                    line = line.strip(' \n\t')
                    word, *count = line.split(' ')
                    if not word:
                        continue
                    if not count:
                        vocab.increase_freq(word)
                    else:
                        vocab.increase_freq(word, int(count[0]))
                except ValueError as e:
                    print(e)
        return vocab

    def dump(self, file):
        with open(file, 'w') as f:
            for word, freq in self._freqs.items():
                f.write('{} {}\n'.format(word, freq))

    def vocab_len(self, min_count=1):
        return len(self.shrink(min_count))

    def words(self, min_count=1):
        return tuple(self.shrink(min_count))

    def items(self):
        return self._freqs.items()


def build_vocab_from_corpus(corpus_or_corpus_seq, min_count=1):
    from yxt_nlp.utils.tokenizer import token_stream
    tokens = token_stream(corpus_or_corpus_seq)
    vocab = Vocab(words=tokens)
    return vocab.shrink(min_count=min_count)
