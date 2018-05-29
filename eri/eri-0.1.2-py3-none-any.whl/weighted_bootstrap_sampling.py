#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Module: weighted_bootstrap_sampling.py
Author: mike.thurber@elderresearch.com
Created: 2018-05-29

Description:
    Functions for overcoming selection bias in labeled data. Weighted bootstrap
    sample creation when selection bias has been quantified.

    In predictive modeling, the labeled sample should be representative of the
    ultimate population to be scored. If this is not the case, then the scores
    will be biased, or skewed, in the direction of the raw sample. This is
    commonly called sample bias in machine learning.

    If, however, we have an estimate of the likelihood of each observation to be
    in the labeled data sample, we can "undo" this sample bias, with weighted
    boostrap sampling. The relative weight is simply the reciprocal of the
    likelihood to be in labeled sample. The weighted bootstrap sample becomes
    the model build sample, and will be representative of the population to be
    scored.

    Caution: This will preferentially select observations that rarely get a
    label, much more often than observations that always get a label. This is
    the intent, of course. But, the significance or accuracy of the model will
    be overstated because machine learning consider replicates of an observation
    as independent observations, which they are not. Therefore, the accuracy and
    performance of the model must be assessed against strictly independent
    samples!

Usage:
    The general use case is to import this module and utilize the
    `weighted_bootstrap` function defined within it

    >>> import eri.weighted_bootstrap_sampling as wbs

    >>> bootstrapped_df = wbs.weighted_bootstrap(
    >>>     df, relative_weight_col_name, size_requested
    >>> )

    look at the function `demo` defined within this module for a simple
    application of this function

"""

import numpy as _np
import pandas as _pd

from numpy.random import choice as _choice


# ----------------------------- #
#   Main routine                #
# ----------------------------- #

def scale_to_sum1(relative_weights):
    """Scale a numeric column such that values are not negative and the total
    sums to 1

    args:
        relative_weights (np.NdArray): the numeric weights we will normalize

    returns:
        np.NdArray: the rescaled array values

    raises:
        None

    """
    return abs(relative_weights/sum(abs(relative_weights)))


def weighted_bootstrap(df, relative_weight_col_name, size_requested):
    """Get a bootstrapped sample from weighted rows, where the likelihood of a
    row being selected is proportional to its relative weight value

    args:
        df (pd.DataFrame): the dataframe we will sample
        relative_weight_col_name (str): the name of the numeric column listing
            the relative weight of each row, such as 1./(prob of row to be be
            part of df)
        size_requested (int): the number of rows requested to be returned in the
            sample. if 0, then it is len(df).

    returns:
        pass

    raises:
        None

    """
    # the old index is added as a column, and a new sequential index is added
    df_ri = df.reset_index()

    weight_col = df_ri[relative_weight_col_name].values

    df_indicies = [
        _choice(df_ri.index.values, p=scale_to_sum1(weight_col), replace=True)
        for _ in range(len(df) if size_requested == 0 else size_requested)
    ]

    return df.iloc[df_indicies]


def demo():
    """demonstrate the proper use of the `weighted_boostrap` function"""
    x1 = 2 * x2 - 5 + _np.random.rand(20)
    x2 = 10 * _np.random.rand(20)

    lin_rand = _pd.DataFrame(x1, x2)
    lin_rand = lin_rand.reset_index()

    lin_rand['rel_weight'] = 1. / x2
    lin_rand.columns = ['x1', 'x2', 'rel_weight']
    bs_lin = weighted_bootstrap(lin_rand, 'rel_weight', 0)

    # Note how some highly weighted observations appear twice
    return bs_lin
