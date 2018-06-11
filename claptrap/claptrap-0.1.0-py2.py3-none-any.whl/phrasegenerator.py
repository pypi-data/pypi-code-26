import collections

from .munging import (
    mat_to_sparse,
    matgen,
    phrase,
    sparse_dump,
    sparse_load,
    word_gen,
)


IGNORE = {'ii', 'iii', 'iv', 'v', 'vi', 'vii', 'viii', 'ix', 'x', 'xi', 'xii', 'chapter', 'gutenberg'}


class PhraseGenerator:
    @classmethod
    def from_corpus(cls, corpus, threshold=1000):
        counter = collections.Counter(corpus)
        words = [
            word
            for word, count
            in counter.most_common(threshold)
            if word.lower() not in IGNORE
        ]
        sparse = mat_to_sparse(matgen(words, corpus))
        return cls(words, sparse)

    @staticmethod
    def _load_file(path):
        with open(path, 'rb') as f:
            if f.read(5) == b'\xfd7zXZ':
                f.seek(0)
                return f.read()
        with open(path, 'r') as f:
            return f.read()

    @classmethod
    def from_dump(cls, *, file=None, data=None):
        if file is not None:
            if isinstance(file, str):
                data = cls._load_file(file)
            else:
                data = file.read()

        sparse, words = sparse_load(data)
        return cls(words, sparse)

    def __init__(self, words, matrix):
        self.words = words
        self.matrix = matrix
        self.gen = word_gen(words, matrix)

    def phrase(self, length=[100, 120]):
        return phrase(self.gen, length)

    def to_file(self, path):
        with open(path, 'wb') as f:
            f.write(sparse_dump(self.matrix, self.words))
