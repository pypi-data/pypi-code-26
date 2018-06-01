#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2007-2012 Etienne Robillard 
# All rights reserved.
# Please see the "LICENSE" file for license details. 
"""Views for allowing people to post comments."""

import demjson
from pubsub import pub

from datetime import datetime
from notmm.controllers.schevo import ZODBController
from notmm.http.decorators import post_required
from notmm.utils.wsgilib import HTTPResponse, HTTPRedirectResponse
from notmm.dbapi.orm import decorators
from notmm.utils.template import direct_to_template

from forms import CommentForm


import logging
import signals
log = logging.getLogger(__name__)

def _get_raw_errors(form):
    return dict([(name, u"%s" % error[0]) for name, error in form.errors.iteritems() ])

@post_required
@decorators.with_schevo_database('127.0.0.1:4343', controller_class=ZODBController)
def preview_comment(request, *args, **kwargs):
    #log.debug('in preview_comment')
    
    status = 200
        
    db = request.environ['schevo.db.zodb'] # pointer to the correct db...
    
    new_data = request.POST.copy()
    path_url = new_data.pop('id_path')
    # blogentry.messageid
    if 'messageid' in new_data:
        objectid = new_data.pop('messageid')
        entity = 'blogentry'
    elif 'categoryid' in new_data:
        objectid = new_data.pop('categoryid')
        entity = 'category'
    else:
        raise ValueError('invalid object id in POST data')

    form = CommentForm(new_data)

    if form.is_valid() and form.cleaned_data['captcha'] == 'Trump':
        del form.cleaned_data['captcha']
        # If the form is cleaned from hazardous input, let the user
        # confirm its validity with a form preview then create
        # the entity in the db.

        #print "pointer pointer baby!"
        save_comment(objectid, path_url, db, form.cleaned_data, entity)
        # comment saved, redirect to the blog url
        return HTTPRedirectResponse(path_url)
        #json = demjson.encode(dict(result="comment saved!"))
    else:
        # Form needs to be corrected, return it back
        # print 'form contains errors!'
        raw_errors = _get_raw_errors(form)
        # Translate form errors into a JSON object
        json = demjson.encode(dict(errors=raw_errors))
        status = 403 # Bad request
    return HTTPResponse(str(json), mimetype='application/javascript', status=status)

def save_comment(objectid, path, db, new_data, entity='blogentry'):
    """Save a comment for review/publishing by an admin"""

    if not 'subscribe_comment_thread' in new_data:
        # By default do not subscribe users unless explicitely
        # requested by the comment author
        new_data['subscribe_comment_thread'] = False
    
    # Path to the blog entry/url
    new_data['path_url'] = path
    # Entry oid
    if entity == 'blogentry':
        new_data['blogentry'] = db.Message.findone(messageid=objectid) 
    #elif entity == 'category':
    #    new_data['category'] = db.objects.get_by_oid(objectid)
    else:
        raise ValueError("invalid form data")

    # Date the comment was posted
    new_data['pub_date'] = datetime.now()
    
    try:
        #TODO: use CommentManager class here to save comments
        tx = db.Comment.t.create(**new_data)
        if tx: 
            # TODO: save a log record in $error_log
            # logger = request.environ['logger']
            # logger.info('new comment saved')
            db.execute(tx)
            db.commit()
            # send email here
            pub.sendMessage('new_comment_callback', path_url=new_data['path_url'])
    except:
        #logger.debug('fatal error saving comment: %r' % e)
        raise
    return None    

