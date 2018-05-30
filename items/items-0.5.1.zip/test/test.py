# -*- coding: utf-8 -*-

from items import *
from collections import OrderedDict
import json
import os
import sys

_PY2 = sys.version_info < (3, 0)
_PY36 = sys.version_info >= (3, 6)


def test_empty():
    it = Item()
    assert list(it.keys()) == []
    assert list(it.values()) == []
    assert list(it.items()) == []
    assert isinstance(it, dict)
    assert isinstance(it, OrderedDict)


def test_simple():
    it = Item(a=1, c=22, b=99, r=4.4, d='this')
    keys = 'a c b r d'.split()
    values =  [1, 22, 99, 4.4, 'this']
    if _PY36:
        assert list(it.keys()) == keys
    else:
        assert set(it.keys()) == set(keys)
    if _PY36:
        assert list(it.values()) == values
    else:
        assert set(it.values()) == set(values)
    assert isinstance(it, dict)
    assert isinstance(it, OrderedDict)


def test_Empty():
    e = Empty
    assert e.more.f.d is Empty
    assert e[1].method().there[33][0].no.attributes[99].here is Empty


def test_from_tuples():
    it = Item.from_tuples([('name', 'Susie'),
                           ('age', 12),
                           ('hobby', 'science'),
                           ('friends', ['Dell', 'Bill'])])
    assert it.name == 'Susie'
    assert it.age == 12
    assert it.hobby == 'science'
    assert it.friends == ['Dell', 'Bill']
    assert len(it) == 4
    

def test_attr_assign():
    it = Item()
    it.a = 12
    it.b = 44
    assert it.a == 12
    assert it.b == 44
    assert it['a'] == 12
    assert it['b'] == 44
    assert list(it.keys()) == ['a', 'b']
    assert list(it.values()) == [12, 44]


def test_attr_del():
    it = Item(a=12, b=44)
    del it.b
    assert it.a == 12
    assert it.b == Empty
    assert len(it) == 1
    del it.a
    assert len(it) == 0
    del it.a
    assert len(it) == 0


def test_composite_1():
    datadir, _ = os.path.split(__file__)
    datapath = os.path.join(datadir, 'testdata', 'data1.json')
    print(datadir)
    print(datapath)
    with open(datapath) as f:
        rawjson = f.read()
        data_i = json.loads(rawjson, object_pairs_hook=Item.from_tuples)
        data_o = json.loads(rawjson, object_pairs_hook=OrderedDict)
    for x, y in zip(data_i, data_o):
        assert list(x.keys()) == list(y.keys())
        assert list(x.values()) == list(y.values())
        

    