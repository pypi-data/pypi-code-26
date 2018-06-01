#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2007-2013 Etienne Robillard <erob@gthcfoundation.org>
# All rights reserved.
# Please see the "LICENSE" file for license details. 
"""Details views"""
import logging
import base64
log = logging.getLogger(__name__)

from notmm.controllers.zodb import ZODBController
from notmm.dbapi.orm.decorators import with_schevo_database
from notmm.utils.template import RequestContext
from notmm.utils.wsgilib import HTTPNotFound, HTTPFoundResponse
from notmm.utils.template import direct_to_template
from blogengine2.contrib.comments import CommentForm
from blogengine2.contrib.api_v1.model import MessageManager
#from blogengine.config.global_settings import DATABASE_NAME

#@authorize(RemoteUser())

def redirect(request, **kwargs):
    # redirect the user to the main details view
    if not kwargs['oid'].endswith('='):
        log.debug("Fixing oid...")
        oid = kwargs['oid'] + '='
    else:
        oid = kwargs['oid']
    location = '/blog/%s/view/' % oid
    log.debug("redirecting to %s" % location)
    return HTTPFoundResponse(location)

@with_schevo_database('db_blog', controller_class=ZODBController)
def details(request, **kwargs):
    """Shows the details for a BlogEntry entity (instance of)"""

    db = request.environ['schevo.db.zodb']
    default_manager = MessageManager(connection=db)
    request.environ['schevo.db.default_manager'] = default_manager
    
    if 'extra_context' in kwargs:
        params = kwargs['extra_context'].copy()
    else:
        params = {
            'comment_form' : CommentForm(),
            'oid' : kwargs['oid']}
    
    template_name = kwargs.pop('template_name', 
        'blogengine2/blogentry_detail.mako')
    
    k,oid = base64.urlsafe_b64decode(str(kwargs['oid'])).split(':')
    
    result = db.Message.findone(messageid=oid)
    params['blogentry'] = result # Hack
    if not result:
        #log.debug("No such object!")
        return HTTPNotFound("No such object!")
    votes = result.x.votes()
    if len(votes) >= 1:
        #assert len(votes) == 1
        vote_count = votes[0].count
    else:
        vote_count = 0
    params['vote_count'] = vote_count

    params['result'] = result
    params['path'] = result.get_absolute_url()
    # fetch the related comments for this post
    comments = result.x.comments()
    unpublished_comments = [item for item in comments if not item.x.is_published()]
    published_comments = set(comments).difference(unpublished_comments)
    # List of published (visible) comments
    params['comments'] = list(published_comments)
    # List of unpublished comments 
    params['u_comments_count'] = len(unpublished_comments)
    return direct_to_template(request, template_name, extra_context=params)
        
