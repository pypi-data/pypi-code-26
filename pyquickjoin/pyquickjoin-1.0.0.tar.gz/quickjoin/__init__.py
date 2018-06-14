from collections import defaultdict
import bsddb3 as bsddb

def join_bsddb(file1, file1_key_column, file2, file2_key_column, separator):
    """
Join two files with the given key columns and separator. Read the first
file in fully to create a lookup table. Then iterate through the second
file and if the key column from file2 is found in the lookup table output
a line for each match from file1. The columns output will be the join
field, all the columns from file2 followed by all the columns from file1.

An iterator is returned. Each line does not have a trailing newline
"""
    lookup_table = bsddb.btopen(None, "c")
    for line in file1:
        line_parts = line.rstrip("\n").split(separator)
        key = line_parts.pop(file1_key_column).encode('utf8')
        lookup_table[key] = separator.join(line_parts)

    for line in file2:
        line_parts = line.rstrip("\n").split(separator)
        key = line_parts.pop(file2_key_column).encode('utf8')

        if key in lookup_table:
            (_key, value) = lookup_table.set_location(key)
            while key == _key:
                yield separator.join([key.decode('utf8'), value.decode('utf8'), separator.join(line_parts)])
                try:
                    (_key, value) = lookup_table.next()
                except bsddb.db.DBNotFoundError:
                    (_key, value) = (None, None)

    lookup_table.close()

def join_dict(file1, file1_key_column, file2, file2_key_column, separator):
    """
Join two files with the given key columns and separator. Read the first
file in fully to create a lookup table. Then iterate through the second
file and if the key column from file2 is found in the lookup table output
a line for each match from file1. The columns output will be the join
field, all the columns from file2 followed by all the columns from file1.

An iterator is returned. Each line does not have a trailing newline
"""
    lookup_table = defaultdict(list)
    for line in file1:
        line_parts = line.rstrip("\n").split(separator)
        key = line_parts.pop(file1_key_column)
        lookup_table[key].append(line_parts)

    for line in file2:
        line_parts = line.rstrip("\n").split(separator)
        key = line_parts.pop(file2_key_column)
        for value in lookup_table[key]:
            yield separator.join([key] + value + line_parts)
