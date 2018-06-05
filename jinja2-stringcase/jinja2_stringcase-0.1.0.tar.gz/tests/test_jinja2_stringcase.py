#!/usr/bin/env python
# -*- coding: utf-8 -*-


import pytest


@pytest.fixture(scope='module')
def env():
    from jinja2 import Environment
    return Environment(extensions=['jinja2_stringcase.StringCaseExtension'])


@pytest.mark.parametrize('filter_name,input_val,output_val', [
    ('snakecase', 'AbcXyz', 'abc_xyz'),
    ('camelcase', 'abc_xyz', 'abcXyz'),
    ('capitalcase', 'abc', 'Abc'),
    ('constcase', 'abcXyz', 'ABC_XYZ'),
    ('lowercase', 'Abc', 'abc'),
    ('pascalcase', 'abc_xyz', 'AbcXyz'),
    ('pathcase', 'abc_xyz', 'abc/xyz'),
    ('sentencecase', 'abc_xyz', 'Abc xyz'),
    ('spinalcase', 'abc_xyz', 'abc-xyz'),
    ('titlecase', 'abc_xyz', 'Abc Xyz'),
    ('trimcase', 'abc_xyz', 'abc_xyz'),
    ('uppercase', 'abc_xyz', 'ABC_XYZ'),
    ('alphanumcase', 'Abc _1xyz', 'Abc_1xyz'),
])
def test_filter(env, filter_name, input_val, output_val):
    assert env.from_string(
        ''.join(['{{ "', input_val, '"|', filter_name, '}}'])
    ).render() == output_val
