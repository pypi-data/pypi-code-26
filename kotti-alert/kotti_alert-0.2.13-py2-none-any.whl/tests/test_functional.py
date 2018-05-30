# -*- coding: utf-8 -*-

"""
Created on 2016-07-01
:author: Oshane Bailey (b4.oshany@gmail.com)
"""

from pytest import mark


def test_login_required(webtest, root):
    resp = webtest.get('/add_alert')
    assert resp.status_code == 302


@mark.user('admin')
def test_add(webtest, root):

    resp = webtest.get('/add_alert')

    # submit empty form
    form = resp.forms['deform']
    resp = form.submit('save')
    assert 'There was a problem' in resp.body

    # submit valid form
    form = resp.forms['deform']
    form['title'] = 'My Custom Content'
    form['priority'] = 2
    form['active'] = True
    resp = form.submit('save')
    print resp.body
    assert resp.status_code in [302, 200]
    resp = resp.follow()
    assert 'Item was added.' in resp.body


@mark.user('admin')
def test_edit(webtest, root):

    from kotti_alert.resources import Alert

    root['cc'] = Alert(title=u'Content Title', priority=2,
                       active=True, alert_type='info')

    resp = webtest.get('/cc/@@edit')
    form = resp.forms['deform']
    assert form['title'].value == u'Content Title'
    assert form['priority'].value == '2'
    assert form['active'].value == 'true'
    form['active'] = 'false'
    resp = form.submit('save').maybe_follow()
    assert u'Your changes have been saved.' in resp.body
