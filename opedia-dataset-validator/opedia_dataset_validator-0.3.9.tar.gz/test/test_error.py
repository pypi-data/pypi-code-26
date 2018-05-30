import opedia_dataset_validator as odv
import os

def test_error_defaults():
    print(os.getcwd())
    e = odv.error.error({
        'sheet': 's1',
        'column': 'c1'
    })
    assert e == {
        'sheet': 's1',
        'column': 'c1',
        'row': -1,
        'message': '-',
        'value': '-',
    }

def test_error_row_add():
    e = odv.error.error({
        'row': 1
    })
    assert e['row'] == 3

def test_filter_first_seen():
    es = [
        odv.error.error({ 'sheet': 's1', 'column': 'c1', 'message': 'm1' }),
        odv.error.error({ 'sheet': 's1', 'column': 'c1', 'message': 'm1' }),
        odv.error.error({ 'sheet': 's1', 'column': 'c1', 'message': 'm2' })
    ]
    filt = odv.error.filter_first_seen(es)
    assert len(filt) == 2
    assert filt[0]['sheet'] == 's1'
    assert filt[0]['column'] == 'c1'
    assert filt[0]['message'] == 'm1'
    assert filt[1]['sheet'] == 's1'
    assert filt[1]['sheet'] == 's1'
    assert filt[1]['message'] == 'm2'
