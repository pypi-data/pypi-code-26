#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2017 Etienne Robillard <tkadm30@yandex.com>
# All rights reserved.
# Please see the "LICENSE" file for license details. 
import logging, datetime, urlparse, base64
from BeautifulSoup import BeautifulSoup
from markdown import markdown
log = logging.getLogger(__name__)

import PyRSS2Gen

from notmm.dbapi.orm.decorators import with_schevo_database
from notmm.controllers.zodb import ZODBController
from notmm.utils.wsgilib import HTTPNotFound, HTTPResponse

def url_for(environ, url):
    assert 'HTTP_HOST' in environ
    host = environ['HTTP_HOST']
    s = urlparse.urljoin('https://%s'%host, url, allow_fragments=False)
    return s

@with_schevo_database('db_blog', controller_class=ZODBController)
def index(request, **kwargs):
    db = request.environ['schevo.db.zodb']
    messages = db.Message.find()[15:]
    messages.reverse()
    xml = PyRSS2Gen.RSS2(
        title="BlogEngine2 RSS",
        link=url_for(request.environ, '/blog/'),
        description="Recent posts"
    )
    for msg in messages:
        xml.items.append(PyRSS2Gen.RSSItem(
            title=''.join(BeautifulSoup(msg.content).findAll(text=True)),
            link=url_for(request.environ, msg.get_absolute_url())
            ))
    return HTTPResponse(xml.to_xml(), mimetype='text/xml')

#@authorize(RemoteUser())
@with_schevo_database('127.0.0.1:4343', controller_class=ZODBController)
def rss(request, **kwargs):
    """Shows the details for a BlogEntry entity (instance of)"""
    db = request.environ['schevo.db.zodb']
    k,messageid = base64.urlsafe_b64decode(str(kwargs['oid'])).split(':')
    obj = db.Message.findone(messageid=messageid)
    # fetch the related comments for this post
    if not obj:
        raise HTTPNotFound("no such object")
    comments = obj.x.comments()
    #unpublished_comments = [item for item in comments if not item.x.is_published()]
    #published_comments = set(comments).difference(unpublished_comments)
    xml = PyRSS2Gen.RSS2(
        title = obj.content,
        link = url_for(request.environ, obj.get_absolute_url()),
        description = 'This is a test'
    )
    for comment in comments:
        xml.items.append(PyRSS2Gen.RSSItem(
            title=comment.sender_message,
            link=url_for(request.environ, comment.path_url)
            ))
    return HTTPResponse(xml.to_xml(), mimetype='text/xml')
