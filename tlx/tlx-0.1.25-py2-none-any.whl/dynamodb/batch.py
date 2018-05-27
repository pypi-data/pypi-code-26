import csv
import math
import json
import boto3
from decimal import Decimal
from collections import defaultdict


ddbclient = boto3.client('dynamodb')  # For exeption handling


# ------------- I don't know what the following where used for ----------#
def _pull_values(item):
    return {k: _set_types(v) for k, v in item.items()}


_func_map = defaultdict(
    lambda: lambda x: x, {
        'M': _pull_values,
        'N': Decimal,
        'L': lambda values: [_set_types(d) for d in values]
    }
)


def _set_types(v):
    v_key = list(v.keys())[0]
    returned_value = list(v.values())[0]  # Always one from dump
    return _func_map[v_key](returned_value)

#  ------------- END ----------#


def _batch_write1(table, items):
    with table.batch_writer() as batch:
        for item in items:
            batch.put_item(
                Item=_pull_values(item),
            )


def _batch_write2(table, items):
    # Need to unify
    with table.batch_writer() as batch:
        for item in items:
            batch.put_item(
                Item=item,
            )


def load_data(dump_file, table=None):
    """
        Loads the results of a scan opperation into a table.

        Details:
        Takes the output of a `scan` operation such as: `aws dynamodb scan --table-name <TableName>`
        and writes to an existing table. Similar to the `aws dynamodb batch-write-item` command except:
            - No limit to amount of items in the upload (25 with awscli)
            - Take the output of a table scan, requiring no reformatting
    """

    table = get_ddb_table(table)
    items = json.load(dump_file)['Items']
    _batch_write1(table, items)


def get_ddb_table(table):
    """Takes either a string or an existing boto3 Table object.  If neither raises Exception"""

    try:  # test is boto3 Table object
        _ = table.name  # noqa: F841
    except AttributeError:
        if isinstance(table, str):
            dynamodb = boto3.resource('dynamodb')
            table = dynamodb.Table(table)
        else:
            raise Exception("Table must be either a boto3 Table object or a string not: {}".format(type(table)))
    return table


def load_from_csv(csv_file, table):
    """ CSV must conform to the following format:
            first row:  Field names
            second row: Field types

        N.B Only works for flat data structures. i.e Maps/Lists/Sets are not supported
    """

    table = get_ddb_table(table)

    with open(csv_file, newline='') as csvfile:
        data = list(csv.reader(csvfile))

    field_names, types = data[0], data[1]

    # Throws KeyError if missing. Only string and number are supported for csv
    _this_func_map = {
        'N': lambda x: Decimal(x if x else 'Nan'),
        'S': lambda x: str(x),
    }

    # Decimal Conversion if string field
    ddata = []
    for d in data[2:]:
        itm = {}
        for k, t, v in zip(field_names, types, d):
            value = _this_func_map[t](v)
            if t == 'N' and (math.isnan(value) or math.isinf(value)):
                # Remove Inf and Nan, DynamoDB does support them
                continue
            itm[k] = value
        ddata.append(itm)

    try:
        _batch_write2(table, ddata)
    except KeyError:
        raise Exception("load_from_csv only supports Dynamo Types {}".format(list(_func_map)))
