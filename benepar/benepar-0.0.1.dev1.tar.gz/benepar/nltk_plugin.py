import nltk
from nltk import Tree

from .base_parser import BaseParser

class Parser(BaseParser):
    """
    Berkeley Neural Parser (benepar), integrated with NLTK.

    Sample usage:
    >>> parser = benepar.Parser("benepar_en")
    >>> parser.parse("The quick brown fox jumps over the lazy dog.")

    Note that the self-attentive parsing model is only tasked with constructing
    constituency parse trees from tokenized, untagged, single-sentence inputs.
    Any other elements of the NLP pipeline (i.e. sentence segmentation,
    tokenization, and part-of-speech tagging) will be done using the default
    NLTK models.
    """
    def __init__(self, filename):
        """
        Load a parsing model from a filename on disk

        filename (str): Path to saved TensorFlow model graph
        """
        super(Parser, self).__init__(filename)

    def _make_nltk_tree(self, sentence):
        # The optimized cython decoder implementation doesn't actually
        # generate trees, only scores and span indices. When converting to a
        # tree, we assume that the indices follow a preorder traversal.
        score, p_i, p_j, p_label = self._make_parse_raw([word for word, tag in sentence])

        label_vocab = self._label_vocab
        last_splits = []

        # Python 2 doesn't support "nonlocal", so wrap idx in a list
        idx_cell = [-1]
        def make_tree():
            idx_cell[0] += 1
            idx = idx_cell[0]
            i, j, label_idx = p_i[idx], p_j[idx], p_label[idx]
            label = label_vocab[label_idx]
            if (i + 1) >= j:
                word, tag = sentence[i]
                tree = Tree(tag, [word])
                for sublabel in label[::-1]:
                    tree = Tree(sublabel, [tree])
                return [tree]
            else:
                left_trees = make_tree()
                right_trees = make_tree()
                children = left_trees + right_trees
                if label:
                    tree = Tree(label[-1], children)
                    for sublabel in reversed(label[:-1]):
                        tree = Tree(sublabel, [tree])
                    return [tree]
                else:
                    return children

        tree = make_tree()[0]
        tree.score = score

        return tree

    def parse(self, sentence):
        """
        Parse a single sentence

        The argument "sentence" can be a list of tokens to be passed to the
        parser. It can also be a string, in which case the sentence will be
        tokenized using the default NLTK tokenizer.

        sentence (str or List[str]): sentence to parse

        Returns: nltk.Tree
        """
        if isinstance(sentence, str):
            sentence = nltk.word_tokenize(sentence)
            sentence = nltk.pos_tag(sentence)
        else:
            sentence = nltk.pos_tag(sentence)

        return self._make_nltk_tree(sentence)

    def parse_sents(self, sents):
        """
        Parse multiple sentences

        If "sents" is a string, it will be segmented into sentences using NLTK.
        Otherwise, each element of "sents" will be treated as a sentence.

        sents (str or Iterable[str] or Iterable[List[str]]): sentences to parse

        Returns: Iter[nltk.Tree]
        """
        if isinstance(sents, str):
            sents = nltk.sent_tokenize(sents)

        for sentence in sents:
            yield self.parse(sentence)
