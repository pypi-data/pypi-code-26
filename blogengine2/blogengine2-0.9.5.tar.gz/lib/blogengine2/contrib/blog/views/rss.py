#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2007-2013 Etienne Robillard <erob@gthcfoundation.org>
# All rights reserved.
# Please see the "LICENSE" file for license details. 
import logging, datetime, urlparse
log = logging.getLogger(__name__)

import PyRSS2Gen

from notmm.dbapi.orm.decorators import with_schevo_database
from notmm.utils.wsgilib import HTTPNotFound, HTTPResponse
from notmm.utils.cache import cached
from blogengine.config.global_settings import DATABASE_NAME


def url_for(environ, url):
    assert 'HTTP_HOST' in environ
    host = environ['HTTP_HOST']
    s = urlparse.urljoin('http://%s'%host, url, allow_fragments=False)
    return s

#@authorize(RemoteUser())
@cached(time=1200)
@with_schevo_database(DATABASE_NAME)
def view_rss(request, **kwargs):
    """Shows the details for a BlogEntry entity (instance of)"""
    db = request.environ['schevo.db.'+DATABASE_NAME]
    obj = db.BlogEntry.findone(slug=kwargs['slug'])
    # fetch the related comments for this post
    comments = obj.x.comments()
    unpublished_comments = [item for item in comments if not item.x.is_published()]
    published_comments = set(comments).difference(unpublished_comments)
    xml = PyRSS2Gen.RSS2(
        title = obj.title,
        link = url_for(request.environ, obj.get_absolute_url()),
        description = obj.short_description
    )
    for comment in comments:
        xml.items.append(PyRSS2Gen.RSSItem(
            title=comment.sender_message,
            link=url_for(request.environ, comment.path_url)
            ))
    return HTTPResponse(xml.to_xml(), mimetype='text/xml')
