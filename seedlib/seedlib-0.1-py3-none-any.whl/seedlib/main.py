"""
    Random Useful Snippets for doing stuff in python
    Ankur Goswami
"""

import pandas as pd


def cat(filename):
    with open(filename, 'r') as rf:
        for line in rf:
            print(line)


def wcl(filename, without_empty_line=True):
    with open(filename, 'r') as rf:
        count = 0
        for line in rf:
            if without_empty_line:
                if line == "":
                    continue
            count += 1
        return count


def pd_print(df, jupyter=True):
    with pd.option_context('display.max_rows', 4000, 'display.max_columns', 4000, 'display.max_colwidth', 4000):
        if jupyter:
            display(df)
        else:
            print(df)


def split_data(df, train_size=0.8):
    train = df.sample(train_size)
    test = df.loc[~df.index.isin(train.index)]
    return train, test


def get_n_sets(df, n=10, train_size=0.8):
    train_sets = test_sets = []
    for i in range(0, n):
        train, test = split_data(df, train_size)
        train_sets.append(train)
        test_sets.append(test)
    return zip(train_sets, test_sets)
