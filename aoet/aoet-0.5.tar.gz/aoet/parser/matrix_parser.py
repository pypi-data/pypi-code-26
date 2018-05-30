import aoet.report.generator as generator
import aoet.proxy.splitter as splitter
import aoet

import pandas as pd
import numpy as np
import difflib
import json
import os

CONVERTED_DATA_TYPE = np.float64
OBJECT_SEPARATOR = '.'
DIFFERENT_TYPE_DIFF = CONVERTED_DATA_TYPE(1)
UNDEFINED_DIFF = CONVERTED_DATA_TYPE(1)
NULL_DIFF = CONVERTED_DATA_TYPE(1)


class MatrixParser:
    def __init__(self, in_dir, out, function):
        self.in_dir = in_dir
        self.out = out
        self.function = function

    @staticmethod
    def _zip_keys(a, b):
        t = list(a.keys()) if a is not None else []
        if b is not None:
            for i in b.keys():
                if i not in t:
                    t.append(i)
        return t

    def compare_dicts(self, prefix, a, b):
        a_k = set(a.keys())
        b_k = set(b.keys())
        ret = list(map(lambda x: prefix + OBJECT_SEPARATOR + x, a_k.symmetric_difference(b_k)))
        for k in a_k.intersection(b_k):
            if a[k] != b[k]:
                if isinstance(a[k], dict) and isinstance(b[k], dict):
                    ret.extend(self.compare_dicts(prefix + OBJECT_SEPARATOR + k, a[k], b[k]))
                else:
                    ret.append(prefix + OBJECT_SEPARATOR + k)
        return set(ret)

    def first_iteration(self, prd, tst):
        diff_body = set()
        diffs = set()

        for i in range(len(prd)):
            p_i = prd[i]
            t_i = tst[i]
            for b in self._zip_keys(p_i.body, t_i.body):
                if p_i.body is None or t_i.body is None:
                    diff_body.add(b)
                    diffs.add(i)
                elif b not in p_i.body or b not in t_i.body \
                        or (p_i.body[b] is None and t_i.body[b] is not None) \
                        or (t_i.body[b] is None and p_i.body[b] is not None):
                    if b in p_i.body and p_i.body[b] is not None and type(p_i.body[b]) == dict:
                        diff_body = diff_body.union(set(map(lambda x: b + OBJECT_SEPARATOR + x, p_i.body[b].keys())))
                    elif b in t_i.body and t_i.body[b] is not None and type(t_i.body[b]) == dict:
                        diff_body = diff_body.union(set(map(lambda x: b + OBJECT_SEPARATOR + x, t_i.body[b].keys())))
                    else:
                        diff_body.add(b)
                    diffs.add(i)
                else:
                    if p_i.body[b] != t_i.body[b] or not isinstance(p_i.body[b], type(t_i.body[b])):
                        diffs.add(i)
                        if isinstance(p_i.body[b], dict):
                            if isinstance(t_i.body[b], dict):
                                diff_body = diff_body.union(self.compare_dicts(b, p_i.body[b], t_i.body[b]))
                            else:
                                diff_body = diff_body.union(
                                    set(map(lambda x: b + OBJECT_SEPARATOR + x, p_i.body[b].keys())))
                        elif isinstance(t_i.body[b], dict):
                            diff_body = diff_body.union(set(map(lambda x: b + OBJECT_SEPARATOR + x, t_i.body[b].keys())))
                        else:
                            diff_body.add(b)

        uniques = list(diffs)
        uniques.sort()
        return list(diff_body), uniques

    def cmp_numbers(self, a, b):
        if a == np.float32(0) or b == np.float32(0):
            return 0.5
        if np.abs(a) > np.abs(b):
            return np.abs(b / a)
        else:
            return np.abs(a / b)

    def to_hashable(self, a):
        if type(a) == dict:
            return ','.join(['%s:%s' % (key, value) for (key, value) in sorted(a.items())])
        elif type(a) == list:
            return ','.join(map(str, a))
        else:
            return a

    def set_seqs(self, a, b):
        t = difflib.SequenceMatcher()
        t.set_seqs(list(map(self.to_hashable, a)), list(map(self.to_hashable, b)))
        return t

    def to_value(self, a, b):
        if isinstance(a, type(b)):
            if a == b:
                return 0
            if type(a) == bool:
                return 0.5
            elif type(a) == int or type(a) == float:
                ta, tb = CONVERTED_DATA_TYPE(a), CONVERTED_DATA_TYPE(b)
                return self.function(self.cmp_numbers(ta, tb))
            elif type(a) == str:
                t = difflib.SequenceMatcher()
                t.set_seqs(a, b)
                r = t.ratio()
                return self.function(CONVERTED_DATA_TYPE(1 - r))
            elif type(a) == list or type(a) == dict:
                r = self.set_seqs(a, b).ratio()
                return self.function(CONVERTED_DATA_TYPE(1 - r))
        else:
            return DIFFERENT_TYPE_DIFF

    def compare_values(self, a, b, key):
        keys = key.split(OBJECT_SEPARATOR)
        if a is None and b is None:
            return 0
        elif a is None or b is None:
            if a is None and keys[0] in b:
                obj = b[keys[0]]
            elif b is None and keys[0] in a:
                obj = a[keys[0]]
            else:
                return 0
            for k in keys[1:]:
                if k in obj:
                    obj = obj[k]
                else:
                    obj = None
                    break
            if obj is None:
                return 0
            else:
                return UNDEFINED_DIFF

        if keys[0] not in a and keys[0] not in b:
            return 0

        if len(keys) > 1:
            if keys[0] in a and keys[0] in b:
                if isinstance(a[keys[0]], dict) and isinstance(b[keys[0]], dict):
                    return self.compare_values(a[keys[0]], b[keys[0]], OBJECT_SEPARATOR.join(keys[1:]))
                elif isinstance(a[keys[0]], dict) or isinstance(b[keys[0]], dict):
                    return DIFFERENT_TYPE_DIFF if isinstance(a[keys[0]], dict) else DIFFERENT_TYPE_DIFF
                else:
                    return 0
            elif keys[0] in a or keys[0] in b:
                return UNDEFINED_DIFF if keys[0] in a else UNDEFINED_DIFF
            else:
                return 0
        else:
            if keys[0] in a and keys[0] in b:
                return self.to_value(a[keys[0]], b[keys[0]])
            else:
                return NULL_DIFF if keys[0] in a else NULL_DIFF

    def second_iteration(self, prd, tst, diff_body, uniques=None):
        if uniques is None:
            b_matrix = np.zeros((len(prd), len(diff_body)))
            uniques = range(len(prd))
        else:
            b_matrix = np.zeros((len(uniques), len(diff_body)))

        i = 0
        for u in uniques:
            p_u = prd[u]
            t_u = tst[u]
            for j in range(len(diff_body)):
                b = diff_body[j]
                v = self.compare_values(p_u.body, t_u.body, b)
                b_matrix[i, j] = v
            i += 1

        return b_matrix

    def _parse(self):
        req, prd, tst = splitter.ResponsesContainer.load(self.in_dir)
        body, unique = self.first_iteration(prd, tst)
        body_matr = self.second_iteration(prd, tst, body, unique)

        pd.DataFrame(body_matr, columns=body).to_csv(os.path.join(self.out, aoet.BODY_MATRIX), columns=body)

        with open(os.path.join(self.out, aoet.UNIQUES_LIST), 'w') as fp:
            json.dump(unique, fp)

        return body_matr, unique


def parse(arguments):
    func = lambda x: x
    if arguments.function == 'tanh':
        func = lambda x: np.tahn(8 * x)
    mp = MatrixParser(arguments.in_dir, arguments.out, func)
    mp._parse()


def add_subparsers(subparsers):
    parser_a = subparsers.add_parser('parse', help='Converts raw input data to a matrix format, '
                                                   'filters out duplicating responses')
    parser_a.add_argument('--in', '-i', dest='in_dir', type=str, default='./out', help='Input files folder with prd, '
                                                                                       'tst and requests json files')
    parser_a.add_argument('--out', '-o', dest='out', type=str, default='./out', help='Output folder')
    parser_a.add_argument('--func', dest='function', type=str, default='lin', choices=['lin', 'tanh'],
                          help='Apply linear/tanh function to converted values. While linear function results in large '
                               'stretched clusters which are easily grouped by DBSCAN, tanh outputs more groups of '
                               'narrow clusters which might be easier to check')
    parser_a.set_defaults(func=parse)
