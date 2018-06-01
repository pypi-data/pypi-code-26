from collections import Counter, defaultdict
import csv
from itertools import chain
import os
import numpy as np
import pandas as pd
import pickle
import regex
import logging

log = logging.getLogger(__name__)


def create_document_term_matrix(tokenized_corpus, document_labels, large_corpus=False):
    """Creates a document-term matrix.

    With this function you can create a document-term-matrix where rows \
    correspond to documents in the collection and columns correspond to terms. \
    Use the function :func:`read_from_pathlist()` to read and :func:`tokenize()` \
    to tokenize your text files.

    Args:
        tokenized_corpus (list): Tokenized corpus as an iterable containing one
            or more iterables containing tokens.
        document_labels (list): Name or label of each text file.
        large_corpus (bool, optional): Set to True, if ``tokenized_corpus`` is
            very large. Defaults to False.

    Returns:
        Document-term matrix as pandas DataFrame.

    Example:
        >>> tokenized_corpus = [['this', 'is', 'document', 'one'], ['this', 'is', 'document', 'two']]
        >>> document_labels = ['document_one', 'document_two']
        >>> create_document_term_matrix(tokenized_corpus, document_labels) #doctest: +NORMALIZE_WHITESPACE
                      this   is  document  two  one
        document_one   1.0  1.0       1.0  0.0  1.0
        document_two   1.0  1.0       1.0  1.0  0.0
        >>> document_term_matrix, document_ids, type_ids = create_document_term_matrix(tokenized_corpus, document_labels, True)
        >>> isinstance(document_term_matrix, pd.DataFrame) and isinstance(document_ids, dict) and isinstance(type_ids, dict)
        True
    """
    return _create_small_corpus_model(tokenized_corpus, document_labels)


def find_hapax_legomena(document_term_matrix, type_ids=None):
    """Creates a list with hapax legommena.

    With this function you can determine *hapax legomena* for each document. \
    Use the function :func:`create_document_term_matrix()` to create a \
    document-term matrix.

    Args:
        document_term_matrix (pandas.DataFrame): A document-term matrix.
        type_ids (dict): A dictionary with types as key and identifiers as values.
            If ``document_term_matrix`` is designed for large corpora, you have
            to commit ``type_ids``, too.

    Returns:
        Hapax legomena in a list.

    Example:
        >>> document_labels = ['document']
        >>> tokenized_corpus = [['hapax', 'stopword', 'stopword']]
        >>> document_term_matrix = create_document_term_matrix(tokenized_corpus, document_labels)
        >>> find_hapax_legomena(document_term_matrix)
        ['hapax']
        >>> document_term_matrix, _, type_ids = create_document_term_matrix(tokenized_corpus, document_labels, large_corpus=True)
        >>> find_hapax_legomena(document_term_matrix, type_ids)
        ['hapax']
    """
    log.info("Determining hapax legomena ...")
    return document_term_matrix.loc[:, document_term_matrix.max() == 1].columns.tolist()


def find_stopwords(document_term_matrix, most_frequent_tokens=100, type_ids=None):
    """Creates a list with stopword based on most frequent tokens.

    With this function you can determine *most frequent tokens*, also known as \
    *stopwords*. First, you have to translate your corpus into a document-term \
    matrix.
    Use the function :func:`create_document_term_matrix()` to create a \
    document-term matrix.

    Args:
        document_term_matrix (pandas.DataFrame): A document-term matrix.
        most_frequent_tokens (int, optional): Treshold for most frequent tokens.
        type_ids (dict): If ``document_term_matrix`` is designed for large corpora,
            you have to commit ``type_ids``, too.

    Returns:
        Most frequent tokens in a list.

    Example:
        >>> document_labels = ['document']
        >>> tokenized_corpus = [['hapax', 'stopword', 'stopword']]
        >>> document_term_matrix = create_document_term_matrix(tokenized_corpus, document_labels)
        >>> find_stopwords(document_term_matrix, 1)
        ['stopword']
        >>> document_term_matrix, _, type_ids = create_document_term_matrix(tokenized_corpus, document_labels, large_corpus=True)
        >>> find_stopwords(document_term_matrix, 1, type_ids)
        ['stopword']
    """
    log.info("Determining stopwords ...")
    return document_term_matrix.iloc[:, :most_frequent_tokens].columns.tolist()

    
def remove_features(features, document_term_matrix=None, tokenized_corpus=None, type_ids=None):
    """Removes features based on a list of tokens.

    With this function you can clean your corpus (either a document-term matrix \
    or a ``tokenized_corpus``) from *stopwords* and *hapax legomena*.
    Use the function :func:`create_document_term_matrix()` or :func:`tokenize` to \
    create a document-term matrix or to tokenize your corpus, respectively.

    Args:
        features (list): A list of tokens.
        document_term_matrix (pandas.DataFrame, optional): A document-term matrix.
        tokenized_corpus (list, optional): An iterable of one or more ``tokenized_document``.
        type_ids (dict, optional): A dictionary with types as key and identifiers as values.

    Returns:
        A clean document-term matrix as pandas DataFrame or ``tokenized_corpus`` as list.

    Example:
        >>> document_labels = ['document']
        >>> tokenized_corpus = [['this', 'is', 'a', 'document']]
        >>> document_term_matrix = create_document_term_matrix(tokenized_corpus, document_labels)
        >>> features = ['this']
        >>> remove_features(features, document_term_matrix) #doctest: +NORMALIZE_WHITESPACE
                   is  document    a
        document  1.0       1.0  1.0
        >>> document_term_matrix, _, type_ids = create_document_term_matrix(tokenized_corpus, document_labels, large_corpus=True)
        >>> len(remove_features(features, document_term_matrix, type_ids=type_ids))
        3
        >>> list(remove_features(features, tokenized_corpus=tokenized_corpus))
        [['is', 'a', 'document']]
    """
    log.info("Removing features ...")
    return _remove_features_from_small_corpus_model(document_term_matrix, features)


def tokenize(document, pattern=r'\p{L}+\p{P}?\p{L}+', lower=True):
    """Tokenizes with Unicode regular expressions.

    With this function you can tokenize a ``document`` with a regular expression. \
    You also have the ability to commit your own regular expression. The default \
    expression is ``\p{Letter}+\p{Punctuation}?\p{Letter}+``, which means one or \
    more letters, followed by one or no punctuation, followed by one or more \
    letters. So, one letter words will not match. In case you want to lower \
    all tokens, set the argument ``lower`` to True (it is by default).    
    Use the functions :func:`read_from_pathlist()` to read your text files.

    Args:
        document (str): Document text.
        pattern (str, optional): Regular expression to match tokens.
        lower (boolean, optional): If True, lowers all characters. Defaults to True.

    Yields:
        All matching tokens in the ``document``.

    Example:
        >>> list(tokenize("This is 1 example text."))
        ['this', 'is', 'example', 'text']
    """
    log.debug("Tokenizing document ...")
    if lower:
        log.debug("Lowering all characters ...")
        document = document.lower()
    compiled_pattern = regex.compile(pattern)
    tokenized_document = compiled_pattern.finditer(document)
    for match in tokenized_document:
        yield match.group()


def _create_small_corpus_model(tokenized_corpus, document_labels):
    """Creates a document-term matrix for small corpora.

    This private function is wrapped in :func:`create_document_term_matrix()`.

    Args:
        tokenized_corpus (list): Tokenized corpus as an iterable
            containing one or more iterables containing tokens.
        document_labels (list): Name or label of each text file.


    Returns:
        Document-term matrix as pandas DataFrame.

    Example:
        >>> tokenized_corpus = [['this', 'is', 'document', 'one'], ['this', 'is', 'document', 'two']]
        >>> document_labels = ['document_one', 'document_two']
        >>> _create_small_corpus_model(tokenized_corpus, document_labels) #doctest: +NORMALIZE_WHITESPACE
                      this   is  document  two  one
        document_one   1.0  1.0       1.0  0.0  1.0
        document_two   1.0  1.0       1.0  1.0  0.0
    """
    log.info("Creating document-term matrix for small corpus ...")
    document_term_matrix = pd.DataFrame()
    for tokenized_document, document_label in zip(tokenized_corpus, document_labels):
        log.debug("Updating {} in document-term matrix ...".format(document_label))
        current_document = pd.Series(Counter(tokenized_document))
        current_document.name = document_label
        document_term_matrix = document_term_matrix.append(current_document)
    document_term_matrix = document_term_matrix.loc[:, document_term_matrix.sum().sort_values(ascending=False).index]
    return document_term_matrix.fillna(0)


def _remove_features_from_small_corpus_model(document_term_matrix, features):
    """Removes features from small corpus model.

    This private function is wrapped in :func:`remove_features()`.

    Args:
        document_term_matrix (pandas.DataFrame): A document-term matrix.
        features (list): A list of tokens.

    Returns:
        A clean document-term matrix as pandas DataFrame.

    Example:
        >>> document_labels = ['document']
        >>> tokenized_corpus = [['token', 'stopword', 'stopword']]
        >>> document_term_matrix = create_document_term_matrix(tokenized_corpus, document_labels)
        >>> _remove_features_from_small_corpus_model(document_term_matrix, ['token']) #doctest: +NORMALIZE_WHITESPACE
                  stopword
        document       2.0

    """
    features = [token for token in features if token in document_term_matrix.columns]
    return document_term_matrix.drop(features, axis=1)
