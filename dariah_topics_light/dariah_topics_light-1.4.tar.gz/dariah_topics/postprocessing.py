import itertools
import operator
import os
import numpy as np
import pandas as pd
import logging

log = logging.getLogger(__name__)


def show_document_topics(topics, model=None, document_labels=None, doc_topics_file=None, doc2bow=None, num_keys=3, easy_file_format=True):
    """Shows topic distribution for each document.
    
    With this function you can show the topic distributions for all documents in a pandas DataFrame. \
    For each topic, the top ``num_keys`` keys will be considered. If you have a
    * `lda <https://pypi.python.org/pypi/lda>`_ model, you have to pass the model \
    as ``model`` and the document-term matrix vocabulary as ``vocabulary``.
    * `Gensim <https://radimrehurek.com/gensim/>`_ model, you have to pass only the model \
    as ``model``.
    * `MALLET <http://mallet.cs.umass.edu/topics.php>`_ based workflow, you have to\
    pass only the ``doc_topics_file``.
    
    Args:
        topics (pandas.DataFrame, optional): Only for lda models. A pandas DataFrame
            containing all topics.
        model (optional): lda or Gensim model.
        document_labels (list, optional): An list of all document labels.
        doc_topics_file (str, optional): Only for MALLET. Path to the doc-topics file.
        doc2bow (list, optional): A list of lists containing tuples of ``type_id`` and
            frequency.
        num_keys (int, optional): Number of top keys for each topic.
    
    Returns:
        A pandas DataFrame with rows corresponding to topics and columns corresponding
            to keys.

    Example:
    """
    index = [' '.join(keys[:num_keys]) for keys in topics.values]
    return _show_lda_document_topics(model, document_labels, index).round(4)


def show_topics(model=None, vocabulary=None, topic_keys_file=None, num_keys=10):
    """Shows topics of LDA model.
    
    With this function you can show all topics of a LDA model in a pandas DataFrame. \
    For each topic, the top ``num_keys`` keys will be considered. If you have a
    * `lda <https://pypi.python.org/pypi/lda>`_ model, you have to pass the model \
    as ``model`` and the document-term matrix vocabulary as ``vocabulary``.
    * `Gensim <https://radimrehurek.com/gensim/>`_ model, you have to pass only the model \
    as ``model``.
    * `MALLET <http://mallet.cs.umass.edu/topics.php>`_ based workflow, you have to\
    pass only the ``topic_keys_file``.
    
    Args:
        model (optional): lda or Gensim model.
        vocabulary (list, optional): Only for lda. The vocabulary of the 
            document-term matrix.
        topic_keys_file (str): Only for MALLET. Path to the topic keys file.
        num_keys (int, optional): Number of top keys for each topic. 
    
    Returns:
        A pandas DataFrame with rows corresponding to topics and columns corresponding
            to keys.

    Example:
    """
    return _show_lda_topics(model, vocabulary, num_keys)


def _show_lda_document_topics(model, document_labels, index):
    """Creates a doc_topic_matrix for lda output.
    
    Description:
        With this function you can convert lda output to a DataFrame, 
        a more convenient datastructure.
        Use 'lda2DataFrame()' to get topics.
        
    Note:

    Args:
        model: Gensim LDA model.
        topics: DataFrame.
        doc_labels (list[str]): List of doc labels as string.

    Returns:
        DataFrame

    Example:
        >>> import lda
        >>> from dariah_topics import preprocessing
        >>> tokenized_corpus = [['this', 'is', 'the', 'first', 'document'], ['this', 'is', 'the', 'second', 'document']]
        >>> document_labels = ['document_one', 'document_two']
        >>> document_term_matrix = preprocessing.create_document_term_matrix(tokenized_corpus, document_labels)
        >>> vocabulary = document_term_matrix.columns
        >>> model = lda.LDA(n_topics=2, n_iter=1)
        >>> model = model.fit(document_term_matrix.as_matrix().astype(int))
        >>> topics = _show_lda_topics(model, vocabulary, num_keys=5)
        >>> index = [' '.join(keys[:3]) for keys in topics.values]
        >>> isinstance(_show_lda_document_topics(model, document_labels, index), pd.DataFrame)
        True
    """
    return pd.DataFrame(model.doc_topic_, index=document_labels, columns=index).T
    

def _show_lda_topics(model, vocabulary, num_keys):
    """Converts lda output to a DataFrame
    
    Description:
        With this function you can convert lda output to a DataFrame, 
        a more convenient datastructure.
        
    Note:

    Args:
        model: LDA model.
        vocab (list[str]): List of strings containing corpus vocabulary. 
        num_keys (int): Number of top keywords for topic
        
    Returns:
        DataFrame

    Example:
        >>> import lda
        >>> from dariah_topics import preprocessing
        >>> tokenized_corpus = [['this', 'is', 'the', 'first', 'document'], ['this', 'is', 'the', 'second', 'document']]
        >>> document_labels = ['document_one', 'document_two']
        >>> document_term_matrix = preprocessing.create_document_term_matrix(tokenized_corpus, document_labels)
        >>> vocabulary = document_term_matrix.columns
        >>> model = lda.LDA(n_topics=2, n_iter=1)
        >>> model = model.fit(document_term_matrix.as_matrix().astype(int))
        >>> isinstance(_show_lda_topics(model, vocabulary, num_keys=5), pd.DataFrame)
        True
    """
    log.info("Accessing topics from lda model ...")
    topics = []
    topic_word = model.topic_word_
    for i, topic_distribution in enumerate(topic_word):
        topics.append(np.array(vocabulary)[np.argsort(topic_distribution)][:-num_keys-1:-1])
    index = ['Topic {}'.format(n) for n in range(len(topics))]
    columns = ['Key {}'.format(n) for n in range(num_keys)]
    return pd.DataFrame(topics, index=index, columns=columns)

