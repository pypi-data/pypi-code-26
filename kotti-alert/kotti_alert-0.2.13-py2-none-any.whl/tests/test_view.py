# -*- coding: utf-8 -*-

"""
Created on 2016-07-01
:author: Oshane Bailey (b4.oshany@gmail.com)
"""

import datetime
from pytest import fixture


@fixture
def dummy_content(root):

    from kotti_alert.resources import Alert

    root['alert'] = alert = Alert(
        title=u'My content',
        description=u'My very custom content is custom',
        priority=2,
        active=True,
        end_date=datetime.date.today()
    )

    return alert


def test_view(dummy_content, dummy_request):

    from kotti_alert.views.view import AlertViews

    views = AlertViews(dummy_content, dummy_request)

    assert views.context.title == u'My content'
