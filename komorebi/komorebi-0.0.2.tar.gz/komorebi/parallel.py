# -*- coding: utf-8 -*-

import json
import os
import pickle
import sys

from collections import Iterator
from itertools import chain
from pathlib import Path

from gensim.corpora.dictionary import Dictionary
from bounter import bounter

import torch
from torch import LongTensor
from torch.autograd import Variable

from komorebi.util import absolute_path, per_chunk, timing

class ParallelData(Iterator):
    def __init__(self,
                 src_file=None, trg_file=None,
                 src_vocab_size=10**5, trg_vocab_size=10**5,
                 chunk_size=10**5, delimiter=None, size_mb=4024,
                 start_symbol='<s>', end_symbol='</s>', unknown_symbol='UNK',
                 filter_on='tf', prune_at=10**10,
                 **kwargs):

        if 'loadfrom' not in kwargs: # Creating.
            self.src_file = src_file
            self.trg_file = trg_file

            # Check that inputs are not None.
            assert Path(self.src_file).exists(), "File {src_file} does not exist".format(src_file=src_file)
            assert Path(self.trg_file).exists(), "File {trg_file} does not exist".format(trg_file=trg_file)

            # Initialize the start, end and unknown symbols.
            self.START, self.START_IDX = start_symbol, 0
            self.END, self.END_IDX = end_symbol, 1
            self.UNK, self.UNK_IDX = unknown_symbol, 2

            # Save the user-specific delimiter
            self.delimiter = delimiter

            # Gensim related attribute to keep the pruning cap.
            self.prune_at = prune_at

            # Save the user-specified source/target vocab size.
            self.src_vocab_size = src_vocab_size
            self.trg_vocab_size = trg_vocab_size

            # Populate the source vocabulary.
            self.src_vocab = Dictionary([[start_symbol], [end_symbol], [unknown_symbol]],
                                           prune_at=self.prune_at)
            self.src_counter = bounter(size_mb=size_mb)
            print('Building source vocab and counter...', end=' ', file=sys.stderr)
            self.populate_dictionary(self.src_file, self.src_vocab,
                                     self.src_counter, chunk_size)

            # Populate the target vocabulary.
            self.trg_vocab = Dictionary([[start_symbol], [end_symbol], [unknown_symbol]],
                                           prune_at=self.prune_at)
            self.trg_counter = bounter(size_mb=size_mb)
            print('Building target vocab and counter...', end=' ', file=sys.stderr)
            self.populate_dictionary(self.trg_file, self.trg_vocab,
                                     self.trg_counter, chunk_size)

            # Keep the vocabulary to a max set by user.
            print('Filtering least frequent words in vocab.', end=' ', file=sys.stderr)
            if filter_on == 'tf':
                self.filter_n_least_frequent(self.src_vocab,
                                             self.src_counter,
                                             self.src_vocab_size)
                self.filter_n_least_frequent(self.trg_vocab,
                                             self.trg_counter,
                                             self.trg_vocab_size)
            elif filter_on == 'df':
                self.src_vocab.filter_extremes(no_below=1, no_above=self.prune_at,
                                               keep_n=self.src_vocab_size,
                                               keep_tokens=['<s>', '</s>', 'UNK'])
                self.trg_vocab.filter_extremes(no_below=1, no_above=self.prune_at,
                                               keep_n=self.src_vocab_size,
                                               keep_tokens=['<s>', '</s>', 'UNK'])

            self.iterable = self._iterate()

        else: # Loading.
            self.load(kwargs['loadfrom'], kwargs.get('load_counter', False))
            self.iterable = self._iterate()

        # PyTorch nonsense with CUDA... -_-|||
        if 'use_cuda' in kwargs:
            self.use_cuda = kwargs['use_cuda']
        else:
            self.use_cuda = torch.cuda.is_available()


    @timing
    def load(self, loadfrom, load_counter=False):
        """
        The load function.

        :param loadfrom: The path to load the directory for the ParallelData.
        :type loadfrom: str
        :param load_counter: Whether to load the src and trg bounter objects.
        :type load_counter: bool
        """
        config_file = loadfrom + '/ParallelData.json'
        if not Path(config_file).exists():
            raise DataError('{} config file not found!!'.format(config_file))
        else:
            print('Loading ParallelData from {}'.format(config_file),
                  end=' ', file=sys.stderr)
            with open(config_file) as fin:
                self.__dict__ = json.load(fin)

            with open(self.src_vocab, 'rb') as fin:
                self.src_vocab = pickle.load(fin)
            with open(self.trg_vocab, 'rb') as fin:
                self.trg_vocab = pickle.load(fin)

            if load_counter:
                if ('src_counter' not in self.__dict__ or
                    'trg_counter' not in self.__dict__):
                    raise DataError('source/target counter not found!!')
                with open(self.src_counter, 'rb') as fin:
                    self.src_counter = pickle.load(fin)
                with open(self.trg_counter, 'rb') as fin:
                    self.trg_counter = pickle.load(fin)

    @timing
    def save(self, saveto, save_counter=False):
        """
        The save function.

        :param saveto: The path to save the directory for the ParallelData.
        :type saveto: str
        :param save_counter: Whether to save the src and trg bounter objects.
        :type save_counter: bool
        """
        print("Saving ParallelData to {saveto}".format(saveto=saveto), end=' ', file=sys.stderr)
        # Create the directory if it doesn't exist.
        if not Path(saveto).exists():
            os.makedirs(saveto)
        # Save the vocab files.
        with open(saveto+'/src_vocab.pkl', 'wb') as fout:
            pickle.dump(self.src_vocab, fout)
        with open(saveto+'/trg_vocab.pkl', 'wb') as fout:
            pickle.dump(self.trg_vocab, fout)

        # Initialize the config file.
        config_json = {'src_file': absolute_path(self.src_file),
                       'trg_file': absolute_path(self.trg_file),
                       'delimiter': self.delimiter,
                       'START': self.START, 'START_IDX': self.START_IDX,
                       'END': self.END, 'END_IDX': self.END_IDX,
                       'UNK': self.UNK, 'UNK_IDX': self.UNK_IDX,
                       'src_vocab_size': self.src_vocab_size,
                       'trg_vocab_size': self.trg_vocab_size,
                       'src_vocab': absolute_path(saveto+'/src_vocab.pkl'),
                       'trg_vocab': absolute_path(saveto+'/trg_vocab.pkl')}


        # Check whether we should save the counter.
        if save_counter:
            with open(saveto+'/src_counter.pkl', 'wb') as fout:
                pickle.dump(self.src_counter, fout)
            with open(saveto+'/trg_counter.pkl', 'wb') as fout:
                pickle.dump(self.trg_counter, fout)
        config_json['src_counter'] = absolute_path(saveto+'/src_counter.pkl')
        config_json['trg_counter'] = absolute_path(saveto+'/trg_counter.pkl')

        # Dump the config file.
        with open(saveto+'/ParallelData.json', 'w') as fout:
            json.dump(config_json, fout, indent=2)


    def split_tokens(self, s):
        """
        A "tokenizer" that splits on space. If the delimiter is set to an empty
        string, it will read characters as tokens.

        :param s: The input string.
        :type s: str
        """
        if self.delimiter == '': # Character models.
            return list(s.strip())
        else: # Word models.
            return s.strip().split(self.delimiter)

    @timing
    def populate_dictionary(self, filename, vocab, counter, chunk_size):
        with open(filename) as trg_fin:
            for chunk in per_chunk(trg_fin, chunk_size):
                if all(c == None for c in chunk): break;
                chunk_list_of_tokens = [self.split_tokens(s) for s in chunk if s]
                vocab.add_documents(chunk_list_of_tokens, self.prune_at)
                counter.update(chain(*chunk_list_of_tokens))

    def filter_n_least_frequent(self, vocab, counter, n):
        """
        Remove the least frequent items form the vocabulary.

        :param vocab: self.src_vocab or self.trg_vocab
        :type vocab: gensim.Dictionary
        :param counter: self.src_counter or self.trg_counter
        :type counter: bounter
        :param n: The upper limit of how many items to keep in the vocabulary
        :type n: int
        """
        # If n is bigger than user specified size, don't filter anything.
        if n < len(vocab.token2id):
            good_ids = [vocab.token2id[token] for token, _ in
                       sorted(counter.items(), key=itemgetter(1))[-n:]
                       if token in vocab.token2id]
            vocab.filter_tokens(good_ids=good_ids)

    def vectorize_sent(self, sent, vocab, pad_start=True, pad_end=True):
        """
        Vectorize the sentence, converts it into a list of the indices based on
        the vocabulary. This is used by the `variable_from_sent()`.

        :param sent: The input sentence to convert to PyTorch Variable
        :type sent: list(str)
        :param vocab: self.src_vocab or self.trg_vocab
        :type vocab: gensim.Dictionary
        :param pad_start: Pad the start with the START_IDX [default: True]
        :type pad_end: bool
        :param pad_end: Pad the start with the END_IDX [default: True]
        :type pad_end: bool
        """
        sent = self.split_tokens(sent) if type(sent) == str else sent
        vsent = vocab.doc2idx(sent, unknown_word_index=self.UNK_IDX)
        if pad_start:
            vsent = [self.START_IDX] + vsent
        if pad_end:
            vsent = vsent + [self.END_IDX]
        return vsent

    def variable_from_sent(self, sent, vocab):
        """
        Create the PyTorch variable given a sentence

        :param sent: The input sentence to convert to PyTorch Variable
        :type sent: list(str) or str
        :param vocab: self.src_vocab or self.trg_vocab
        :type vocab: gensim.Dictionary
        """
        sent = self.split_tokens(sent) if type(sent) == str else sent
        vsent = self.vectorize_sent(sent, vocab)
        result = Variable(LongTensor(vsent).view(-1, 1))
        return result.cuda() if self.use_cuda else result

    def reset(self):
        """
        Resets the iterator to the 0th item.
        """
        self.iterable = self._iterate()

    def _iterate(self):
        """
        The helper function to iterate through the source and target file
        and convert the lines into PyTorch variables.
        """
        with open(self.src_file) as src_fin, open(self.trg_file) as trg_fin:
            for src_line, trg_line in zip(src_fin, trg_fin):
                src_sent = self.variable_from_sent(src_line, self.src_vocab)
                trg_sent = self.variable_from_sent(trg_line, self.trg_vocab)
                yield src_sent, trg_sent

    def __next__(self):
        return next(self.iterable)
