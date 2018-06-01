#!/usr/bin/env python

import os
import demjson
import signals

from pubsub import pub
from notmm.http import post_required
from notmm.controllers.schevo import ZODBController
from notmm.dbapi.orm import decorators
#from notmm.utils.django_settings import LazySettings
from notmm.utils.wsgilib import HTTPResponse, HTTPUnauthorized
from notmm.utils.template import direct_to_template
#from blogengine.config import RemoteUser, authorize
#from blogengine2.forms import EntryForm
#settings = LazySettings()

@post_required
@decorators.with_schevo_database('db_blog', controller_class=ZODBController)
def vote_up(request, *args, **kwargs):
    #import pdb; pdb.set_trace()
    
    #form = EntryForm()
    ctx = {}

    db = request.environ['schevo.db.zodb'] # schevo.db.blogengine
    #db._sync()

    #handle POST request
    assert request.method == 'POST'
    new_data = request.POST.copy()
    #first get the message object
    voteid = new_data['messageid'] # hack
    #import pdb; pdb.set_trace()
    obj = db.Vote.findone(voteid=voteid)
    
    if request.cookies.get('test') == voteid:
        print "The user has already voted"
        count = obj.count
    else:
        tx = obj.t.update()
        count = tx.count = int(obj.count + 1)
        if tx is not None:
            db.execute(tx)  # execute the transaction/commit
            db.commit()
            pub.sendMessage('new_vote_callback', path_url=request.environ['PATH_INFO'])

    ctx['count'] = count
    json = demjson.encode(ctx)
    return HTTPResponse(str(json), 
        mimetype='application/javascript', cookies=[('test', voteid)])

@post_required
@decorators.with_schevo_database('127.0.0.1:4343', controller_class=ZODBController)
def vote_down(request, *args, **kwargs):
    ctx = {}
    db = request.environ['schevo.db.zodb']
    #db._sync()
    new_data = request.POST.copy()
    #first get the message object
    voteid = new_data['messageid'] # hack
    obj = db.Vote.findone(voteid=voteid)
    if request.cookies.get('test') == voteid:
        #print "The user has already voted"
        count = obj.count
    else:
        tx = obj.t.update()
        count = tx.count = int(obj.count - 1)
        if tx is not None:
            db.execute(tx)  # execute the transaction/commit
            db.commit()
    ctx['count'] = count
    json = demjson.encode(ctx)   
    return HTTPResponse(str(json), mimetype='application/javascript',
        cookies=[('test', voteid)])
