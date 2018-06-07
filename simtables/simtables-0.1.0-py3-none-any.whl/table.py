import csv
import json
import yaml
import math
import string
import operator
import subprocess
import itertools
import functools
from .record import Record


def any_equal(iterable):
    l = list(iterable)
    return len(l) != len(set(l))


def unique(s):
    n = len(s)
    if n == 0:
        return []

    u = {}
    try:
        for x in s:
            u[x] = 1
    except TypeError:
        del u  # move on to the next method
    else:
        return u.keys()

    try:
        t = list(s)
        t.sort()
    except TypeError:
        del t  # move on to the next method
    else:
        assert n > 0
        last = t[0]
        lasti = i = 1
        while i < n:
            if t[i] != last:
                t[lasti] = last = t[i]
                lasti += 1
            i += 1
        return t[:lasti]

    u = []
    for x in s:
        if x not in u:
            u.append(x)
    return u


def partition(iterable, key=None):
    good = []
    bad = []
    if key is None:
        for element in iterable:
            (good if element else bad).append(element)
    else:
        for element in iterable:
            (good if key(element) else bad).append(element)
    return good, bad


def sorted_groupby(iterable, key=None, reverse=False):
    return itertools.groupby(
        sorted(iterable, key=key, reverse=reverse),
        key=key,
    )


def full_groupby(iterable, key=None):
    l = list(iterable)
    if key is None:
        keys = l
    else:
        keys = [key(item) for item in l]
    heads = []
    groups = []
    for key, item in zip(keys, l):
        if key in heads:
            groups[heads.index(key)].append(item)
        else:
            heads.append(key)
            groups.append([item])
    return list(zip(heads, groups))


def sanitise(s):
    return ''.join([c for c in s if c in string.ascii_letters])


def safe(s):
    return sanitise(s) == s


class Table(list):
    @staticmethod
    def from_dict(d):
        if len(set(len(d[k]) for k in d)) != 1:
            raise ValueError
        return Table(
            map(Record, zip(*[[(k, v) for v in value] for k, value in d.items()]))
            )

    @staticmethod
    def from_list_of_dicts(l):
        return Table(map(Record, l))

    @staticmethod
    def from_dict_of_lists(d):
        raise NotImplementedError()
        # [dict(zip(d.keys(),t)) for t in zip(*DL.values())]

    @staticmethod
    def from_list_of_tuples(keys, l):
        return Table.from_list_of_dicts(zip(keys, li) for li in l)

    @staticmethod
    def from_sql(connection, table_name, keys=None):
        if not safe(table_name):
            raise ValueError('Table name is not safe: {}'.format(table_name))
        cursor = connection.cursor()
        table_info = list(cursor.execute('pragma table_info({})'.format(table_name)))
        if not table_info:
            raise ValueError("No table '{}' in {}".format(table_name, connection))
        if keys is None:
            keys = [row[1] for row in table_info]
        for key in keys:
            if not safe(key):
                raise ValueError('Key name is not safe: {}'.format(key))
        return Table.from_list_of_tuples(
            keys,
            list(cursor.execute('select {} from {}'.format(','.join(keys), table_name)))
        )

    def from_csv(fh):
        return Table.from_list_of_dicts(csv.DictReader(fh))
    load_csv = from_csv

    def save_csv(table, fh, first_keys=None, *args, **kwargs):
        if first_keys is None:
            first_keys = []
        keys = first_keys + sorted([key for key in table.keys() if key not in first_keys])
        for key in table.keys():
            if key not in table.keys():
                raise ValueError('Key \'{}\' not in Table'.format(key))
        writer = csv.DictWriter(fh, keys, *args, **kwargs)
        writer.writeheader()
        for record in table:
            writer.writerow(record)

    def from_json(fh):
        return Table.from_list_of_dicts(json.load(fh))

    def from_yaml(fh):
        return Table.from_list_of_dicts(yaml.load(fh))

    def copy(self):
        return Table(record.copy() for record in self)

    def __getitem__(self, key):
        if isinstance(key, slice):
            return Table(list.__getitem__(self, key))

        try:
            return list.__getitem__(self, key)
        except TypeError:
            pass

        try:
            return Table(list.__getitem__(self, k) for k in key)
        except TypeError:
            pass
        records = [record[key] for record in self]
        if isinstance(key, str):
            return records
        else:
            return Table(records)

    def __setitem__(self, key, value):
        try:
            list.__setitem__(self, key, value)
        except TypeError:
            value = list(value)
            if len(value) != len(self):
                raise ValueError("Trying to set table key to list of different length\n{0}".format(value))
            for record, val in zip(self, value):
                record[key] = val

    def get(self, key, default=None):
        return Table(record.get(key, default) for record in self)

    def pop(self, key):
        try:
            return list.pop(self, key)
        except TypeError:
            records = [record.pop(key) for record in self]
            if isinstance(key, str):
                return records
            else:
                return Table(records)

    def keys(self):
        keys = set()
        for record in self:
            keys.update(record.keys())
        return list(keys)

    def __str__(self):
        try:
            _, n_cols = subprocess.check_output(['stty', 'size']).split()
        except:
            n_cols = 40
        n_cols = int(n_cols)

        keys = self.keys()
        n_keys = len(keys)

        unpadded_width = n_cols - 3*(n_keys - 1) - 4

        text = Table(Record({key: str(record.get(key, '')).replace('\n','') for key in keys}) for record in self)
        lens = {key: max([len(string) for string in text[key]] + [len(key)]) for key in keys}

        remaining_width = unpadded_width
        remaining_keys = lens
        portioned_keys = {}
        while remaining_keys:
            fair_width = int(math.floor(remaining_width/len(remaining_keys)))
            next_smallest_field = min(remaining_keys, key=remaining_keys.get)
            width_portion = min(fair_width, remaining_keys[next_smallest_field])
            remaining_width -= width_portion
            portioned_keys[next_smallest_field] = width_portion
            remaining_keys.pop(next_smallest_field)

        formatstr = ' | '.join(['{:^' + str(portioned_keys[key]) + '}' for key in keys]).join(['| ', ' |'])
        hline = '-+-'.join(['-'*portioned_keys[key] for key in keys]).join(['+-', '-+'])

        return '\n'.join(
            [hline, formatstr.format(*[key[:portioned_keys[key]] for key in keys]), hline]
            + [formatstr.format(*[record[key][:portioned_keys[key]] for key in keys]) for record in text]
            + [hline])

    def __repr__(self):
        return ''.join(['Table(', list.__repr__(self), ')'])

    def __add__(self, other):
        return Table(list.__add__(self, other))

    def sorted(self, key=None, reverse=False):
        return Table(sorted(self, key=key, reverse=reverse))

    def filter(self, function):
        return Table(record for record in self if function(record))

    def partition(self, key=None):
        return tuple(Table(x) for x in partition(self, key=key))

    def full_groupby(self, key=None):
        return Table(full_groupby(self, key=key))

    def key_index(self, kwargs, start=None, end=None):
        if start is None:
            start = 0
        if end is None:
            end = len(self)
        return self.get(kwargs.keys()).index(kwargs, start, end)

    def key_count(self, kwargs):
        return self.get(kwargs.keys()).count(kwargs)

    def key_sort(self, keys, reverse=False):
        self.sort(key=operator.itemgetter(*keys), reverse=reverse)

    def key_sorted(self, keys, reverse=False):
        return self.sorted(key=operator.itemgetter(*keys), reverse=reverse)

    def key_filter(self, kwargs):
        return self.filter(
            lambda record: record.get(kwargs.keys()) == kwargs)

    def key_partition(self, keys):
        return self.partition(lambda record: record[keys()])

    def key_groupby(self, keys):
        return itertools.groupby(self, key=lambda r: r.get(keys))

    def key_sorted_groupby(self, keys):
        return self.key_sorted(keys).key_groupby(keys)

    def key_full_groupby(self, keys):
        return [
            (record, Table(subtable))
            for record, subtable
            in full_groupby(self, key=lambda r: r.get(keys))
        ]

    def key_partition(self, kwargs):
        return self.partition(lambda record: record[kwargs.keys()] == kwargs)

    @staticmethod
    def _merge_helper(table1, table2):
        l1 = []
        l2 = []
        for i, record in enumerate(table1):
            try:
                l2.append(table2.argmatch(record))
                l1.append(i)
            except StopIteration:
                pass

        if any_equal(l2):
            raise ValueError

        return Table(
            [Record.merge([table1[i], table2[j]]) for i, j in zip(l1, l2)]
            + [table1[i] for i in range(len(table1)) if i not in l1]
            + [table2[i] for i in range(len(table2)) if i not in l2])

    @staticmethod
    def merge(tables):
        return functools.reduce(Table._merge_helper, tables)

    @staticmethod
    def zip_merge(*tables):
        return Table(Record.merge(records) for records in zip(*tables))

    def argmatch(self, record):
        iterable = (
            i for i, r in enumerate(self) if Record._mergable(record, r))
        try:
            first = next(iterable)
        except StopIteration:
            raise ValueError(
                "No match found for {0}\nConflicts:\n{1}".format(
                    record,
                    Table(
                        Record(
                            {k: "x" for k in conflict}
                        )
                        for conflict in self.match_conflicts(record)
                    ),
                )
            )
        try:
            second = next(iterable)
            raise ValueError("Could not find unique match for\n{0}\nMatches are\n{1}".format(Table([record]), self[[first, second]]))
        except StopIteration:
            pass
        return first

    def match(self, record):
        return self[self.argmatch(record)]

    def match_without(self, record):
        return self.match(record).without(record)

    def match_conflicts(self, record):
        return [
            Record.merge_conflicts([record, r])
            for r in self
        ]

    @classmethod
    def concatenate(cls, iterable):
        return cls(itertools.chain.from_iterable(iterable))

    def without(self, keys):
        return Table(record.without(keys) for record in self)

    @staticmethod
    def outer_merge(table1, table2):
        return Table(
            Record.merge([record1, record2])
            for record1, record2 in itertools.product(table1, table2)
            )

    def unique(self):
        return unique(self)
