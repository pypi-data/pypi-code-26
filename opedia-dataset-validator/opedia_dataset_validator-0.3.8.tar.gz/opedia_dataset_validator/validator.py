from __future__ import unicode_literals
from .error import error
from io import open
import arrow
import os
import oyaml as yaml
import pandas as pd
import re
import sys

# Load dataset file specifications
spec_file_name = 'dataset_file_def.yaml'
spec_file_path = os.path.join(os.path.dirname(__file__), spec_file_name)
with open(spec_file_path, encoding='utf-8') as fh:
    spec = yaml.load(fh)


def validate(input_path):
    if (sys.version_info > (3, 0)):
        wb = pd.read_excel(input_path, sheet_name=None, na_values=[],
                       keep_default_na=False, dtype=str)
    else:
        wb = pd.read_excel(input_path, sheet_name=None, na_values=[],
                       keep_default_na=False, dtype=unicode)

    errors = []
    errors.extend(validate_filename(input_path, spec))
    errors.extend(validate_sheet_metadata(wb, spec))
    errors.extend(validate_sheet_vars(wb, spec))
    errors.extend(validate_sheet_data(wb, spec))
    return errors


def validate_column_datetimes(series, colspec, sheet):
    errors = []

    empty_errors, series = validate_column_generic(series, colspec, sheet)
    errors.extend(empty_errors)

    # Now look for format errors in non-empty rows
    present = series[series.str.len() > 0]
    for idx, val in present.iteritems():
        try:
            dt = arrow.get(val, colspec['format'])
        except ValueError as e:
            errors.append(error({
                'message': 'error in datetime string: %s' % e,
                'value': val,
                'row': idx,
                'column': series.name,
                'sheet': sheet
            }))
        except arrow.parser.ParserError as e:
            errors.append(error({
                'message': 'invalid datetime string - should match %s' % colspec['format'],
                'value': val,
                'row': idx,
                'column': series.name,
                'sheet': sheet
            }))

    return errors


def validate_column_floats(series, colspec, sheet):
    errors = []

    empty_errors, series = validate_column_generic(series, colspec, sheet)
    errors.extend(empty_errors)

    # Convert to floats
    converted = pd.to_numeric(series, errors='coerce')

    # Non-numeric strings are now NaN
    # Flag NaN as errors
    nonnumeric_errors = series[pd.isna(converted)]
    for idx, val in nonnumeric_errors.iteritems():
        errors.append(error({
            'message': 'invalid value',
            'value': val,
            'row': idx,
            'column': series.name,
            'sheet': sheet
        }))
    # Check range
    min_errors = None
    max_errors = None
    if colspec.get('min', None) is not None:
        min_errors = series[converted < colspec['min']]
        for idx, val in min_errors.iteritems():
            errors.append(error({
                'message': 'value less than minimum of {}'.format(colspec['min']),
                'value': val,
                'row': idx,
                'column': series.name,
                'sheet': sheet
            }))
    if colspec.get('max', None) is not None:
        max_errors = series[converted > colspec['max']]
        for idx, val in max_errors.iteritems():
            errors.append(error({
                'message': 'value greater than maximum of {}'.format(colspec['max']),
                'value': val,
                'row': idx,
                'column': series.name,
                'sheet': sheet
            }))

    return errors


def validate_column_generic(series, colspec, sheet):
    errors = []

    required = colspec.get('required', None)
    na = colspec.get('na', None)

    if not required:
        # Empty cell is a valid value. Remove empty cells before further checks
        series = series[series.str.len() > 0]
    elif str(na) == '':
        # Empty cell is a valid value. Remove empty cells before further checks
        series = series[series.str.len() > 0]
    else:
        # NA is None or is not the empty string, therefore empty cells are not
        # valid values. Flag as errors.
        empty_errors = series[series.str.len() == 0]
        for idx, val in empty_errors.iteritems():
            errors.append(error({
                'message': 'missing required field',
                'row': idx,
                'column': series.name,
                'sheet': sheet
            }))
        # Now remove empty cells
        series = series[series.str.len() > 0]
        if na is not None:
            # Remove NA values before further checks
            series = series[series != na]

    return (errors, series)


def validate_column_strings(series, colspec, sheet):
    errors = []

    empty_errors, series = validate_column_generic(series, colspec, sheet)
    errors.extend(empty_errors)

    if colspec.get('max', None) is not None:
        maxlen_errors = series[series.str.len() > colspec['max']]
        for idx, val in maxlen_errors.iteritems():
            errors.append(error({
                'message': 'string length > %d' % colspec['max'],
                'value': val,
                'row': idx,
                'column': series.name,
                'sheet': sheet
            }))

    return errors


def validate_filename(input_path, spec):
    fn = os.path.basename(input_path)
    errors = []
    filename_re = re.compile(r'^(?P<shortname>.+)_(?P<date>[^_]+)_(?P<version>[^_]+)\.xlsx$')
    m = filename_re.match(fn)
    if not m:
        errors.append(error({
            'message': 'filename does not match format <dataset_short_name>_<dataset_release_date>_v<dataset_version>.xlsx',
            'value': fn
        }))
    else:
        try:
            dt = arrow.get(m.group('date'), spec['file_date'])
        except ValueError as e:
            errors.append(error({
                'message': 'error in filename datatime string: %s' % e,
                'value': m.group('date')
            }))
        except arrow.parser.ParserError as e:
            errors.append(error({
                'message': 'date in filename must be in %s format' % spec['file_date'],
                'value': m.group('date')
            }))
        if not re.match(r'^v.+$', m.group('version')):
            errors.append(error({
                'message': 'version string in filename must start with "v"',
                'value': fn
            }))
    return errors


def validate_sheet_data(wb, spec):
    errors = []

    if not 'data' in wb:
        errors.append(error({
            'message': '"%s" worksheet is missing' % 'data',
            'sheet': 'data'
        }))
        return errors

    df = wb['data']
    errors.extend(validate_sheet_generic(df, 'data', spec))

    # Next check columns in 'data' that were defined in 'vars_meta_data'
    # First make sure that 'vars_meta_data' doesn't have any errors, if it does
    # don't bother with any more checks here
    if len(validate_sheet_vars(wb, spec)) > 0:
        return errors

    # Now check custom data columns
    required_columns = list(spec['columns']['data'].keys())
    df_data = df.drop(required_columns, axis='columns')
    # Collect variable short names from vars_meta_data sheet and check that
    # data columns in 'data' sheet match data columns defined in 'vars' sheet.
    vars_defined = wb['vars_meta_data']['var_short_name'].tolist()
    vars_found = df_data.columns.tolist()
    extra_defined = set(vars_defined).difference(set(vars_found))
    extra_found = set(vars_found).difference(set(vars_defined))
    if extra_defined:
        errors.append(error({
            'message': 'some data variables were defined in the "%s" worksheet but were not found in the "%s" worksheet' % ('vars_meta_data', 'data'),
            'value': ', '.join(extra_defined)
        }))
    if extra_found:
        errors.append(error({
            'message': 'some data variables were found in the "%s" worksheet but were not defined in the "%s" worksheet' % ('data', 'vars_meta_data'),
            'value': ', '.join(extra_found)
        }))

    # Now validate the actual data only on the condition of
    # proper missing values.
    # TODO: Is there any type-checking expected in custom vars?
    vars_missing_value = wb['vars_meta_data']['var_missing_value'].tolist()
    for var, na in zip(vars_defined, vars_missing_value):
        if var not in extra_defined:
            sheet = 'vars_meta_data'
            colspec = { 'required': True, 'na': na }
            empty_errors, _ = validate_column_generic(df_data[var], colspec, 'data')
            errors.extend(empty_errors)

    return errors


def validate_sheet_generic(df, sheet, spec):
    errors = []

    required_columns = list(spec['columns'][sheet].keys())
    if df.columns.tolist()[:len(required_columns)] != required_columns:
        errors.append(error({
            'message': 'the first %d columns of the "%s" worksheet should be %s' % (len(required_columns), sheet, required_columns),
            'value': str(df.columns.tolist()),
            'sheet': sheet
        }))
        return errors

    # Validate cells
    for colname, colspec in spec['columns'][sheet].items():
        v = validator_lookup[colspec['type']]
        errors.extend(v(df[colname], colspec, sheet))

    return errors


def validate_sheet_metadata(wb, spec):
    errors = []

    if not 'dataset_meta_data' in wb:
        errors.append(error({
            'message': '"%s" worksheet is missing' % 'dataset_meta_data',
            'sheet': 'dataset_meta_data'
        }))
        return errors

    df = wb['dataset_meta_data']
    errors.extend(validate_sheet_generic(df, 'dataset_meta_data', spec))

    return errors


def validate_sheet_vars(wb, spec=spec):
    errors = []

    if not 'vars_meta_data' in wb:
        errors.append(error({
            'message': '"%s" worksheet is missing' % 'vars_meta_data',
            'sheet': 'vars_meta_data'
        }))
        return errors

    df = wb['vars_meta_data']
    errors.extend(validate_sheet_generic(df, 'vars_meta_data', spec))

    return errors


# Register column validators in lookup
validator_lookup = {
    'float': validate_column_floats,
    'string': validate_column_strings,
    'datetime': validate_column_datetimes,
    'generic': validate_column_generic
}
