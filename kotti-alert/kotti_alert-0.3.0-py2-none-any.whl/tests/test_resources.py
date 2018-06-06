# -*- coding: utf-8 -*-

"""
Created on 2016-07-01
:author: Oshane Bailey (b4.oshany@gmail.com)
"""

from pytest import raises


def test_model(root, db_session):
    from kotti_alert.resources import Alert

    cc = Alert(alert_type=u'warning')
    assert cc.alert_type == u'warning'

    root['cc'] = cc = Alert()
    assert cc.name == 'cc'

    with raises(TypeError):
        cc = Alert(doesnotexist=u'Foo')
