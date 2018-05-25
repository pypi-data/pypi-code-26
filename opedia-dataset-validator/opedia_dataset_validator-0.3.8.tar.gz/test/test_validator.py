from collections import OrderedDict
import opedia_dataset_validator as odv
import pandas as pd

def test_validate_column_generic_required():
    s = pd.Series(['a', ''], dtype=str)
    errors, sfilt = odv.validator.validate_column_generic(s, {}, 'foo')
    assert len(errors) == 0
    assert sfilt.tolist() == ['a']

    s = pd.Series(['a', ''], dtype=str)
    errors, sfilt = odv.validator.validate_column_generic(s, { 'required': True }, 'foo')
    assert len(errors) == 1
    assert sfilt.tolist() == ['a']
    assert errors[0]['row'] == 3

    s = pd.Series(['a', ''], dtype=str)
    errors, sfilt = odv.validator.validate_column_generic(s, { 'required': True, 'na': '' }, 'foo')
    assert len(errors) == 0
    assert sfilt.tolist() == ['a']

    s = pd.Series(['a', 'na', ''], dtype=str)
    errors, sfilt = odv.validator.validate_column_generic(s, { 'required': True, 'na': 'na' }, 'foo')
    assert len(errors) == 1
    assert sfilt.tolist() == ['a']
    assert errors[0]['row'] == 4


def test_validate_column_strings():
    s = pd.Series(['a', 'bb', 'ccc'], dtype=str)
    errors = odv.validator.validate_column_strings(s, { 'max': 2 }, 'foo')
    sorted(errors, key=lambda e: e['row'])
    assert len(errors) == 1
    assert errors[0]['row'] == 4


def test_validate_column_floats():
    # Because we're pinning to pandas 0.22.0 for windows support and there's a
    # bug in 0.22.0 when creating a Series of numbers with dtype=str, must cast
    # after the fact here. Remove when safe to upgrade pandas dependency to
    # 0.23.0. https://github.com/pandas-dev/pandas/issues/16605
    s = pd.Series(['a', 98.6, 99, 100, 0, -1], dtype=str).astype(str)
    errors = odv.validator.validate_column_floats(s, { 'max': 99, 'min': 0 }, 'foo')
    errors = sorted(errors, key=lambda e: e['row'])
    assert len(errors) == 3
    assert errors[0]['row'] == 2
    assert errors[1]['row'] == 5
    assert errors[2]['row'] == 7


def test_validate_column_datetime():
    s = pd.Series(['a', '2018-05-22', '2018-02-29', '2018-05-2'], dtype=str)
    errors = odv.validator.validate_column_datetimes(s, { 'format': 'YYYY-MM-DD' }, 'foo')
    sorted(errors, key=lambda e: e['row'])
    assert len(errors) == 3
    assert errors[0]['row'] == 2
    assert errors[1]['row'] == 4
    assert errors[2]['row'] == 5


def test_validate_filename():
    spec = { 'file_date': 'YYYY-MM-DD' }
    errors = odv.validator.validate_filename('foo/bar/dataset_2018-05-22_v1.0.xlsx', spec)
    assert len(errors) == 0

    errors = odv.validator.validate_filename('foo/bar/dataset_2018-05-22_1.0.xlsx', spec)
    assert len(errors) == 1

    errors = odv.validator.validate_filename('foo/bar/dataset_2018-05-2_v1.0.xlsx', spec)
    assert len(errors) == 1

    errors = odv.validator.validate_filename('foo/bar/2018-05-22_v1.0.xlsx', spec)
    assert len(errors) == 1


def test_validate_sheet_generic():
    spec = {
        'columns': { 'vars_meta_data': OrderedDict([('a', { 'type': 'float' }), ('b', { 'type': 'float' })]) }
    }

    df = pd.DataFrame({ 'a': [], 'b': [] }, dtype=str)
    errors = odv.validator.validate_sheet_generic(df, 'vars_meta_data', spec)
    assert len(errors) == 0

    df = pd.DataFrame({ 'a': [] }, dtype=str)
    errors = odv.validator.validate_sheet_generic(df, 'vars_meta_data', spec)
    assert len(errors) == 1

    df = pd.DataFrame({ 'a': ['a'], 'b': [200] }, dtype=str)
    errors = odv.validator.validate_sheet_generic(df, 'vars_meta_data', spec)
    assert len(errors) == 1


def test_validate_sheet_missing():
    errors = odv.validator.validate_sheet_metadata({ 'wrong_sheet': True }, None)
    assert len(errors) == 1

    errors = odv.validator.validate_sheet_vars({ 'wrong_sheet': True }, None)
    assert len(errors) == 1

    errors = odv.validator.validate_sheet_data({ 'wrong_sheet': True }, None)
    assert len(errors) == 1


# TODO: test for data sheet custom column correspondence to vars_meta_data and
# basic presence test for custom columns in data.
