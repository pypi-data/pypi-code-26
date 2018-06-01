#!/usr/bin/env python
import os
import base64
# support functions
from datetime import datetime
from schevo.constant import CASCADE
from notmm.controllers.zodb import ZODBController
from notmm.dbapi.orm import decorators
from notmm.utils.django_settings import LazySettings
from notmm.utils.wsgilib import HTTPUnauthorized, HTTPRedirectResponse, HTTPServerError
from notmm.utils.template import direct_to_template
#from blogengine.contrib.comments import CommentForm
from blogengine2.config import RemoteUser, authorize, UserIn
from blogengine2.contrib.api_v1.forms import EntryForm

settings = LazySettings()

@authorize(UserIn(users=settings.ALLOWED_USERS))
@decorators.with_schevo_database('db_blog', 
    controller_class=ZODBController)
def delete(request, oid,
    template_name='blogengine2/api/delete.mako'
    ):
    
    db = request.environ['schevo.db.zodb']
    #db._sync()
    k,messageid = base64.urlsafe_b64decode(str(oid)).split(':')
    obj = db.Message.findone(messageid=messageid)
    if obj is not None:
        oid = obj.s.oid
        ctx = {'instance': obj,
                'message': '',
                'deleted': False}
    else:
        return HTTPRedirectResponse('/blog/')

    def on_delete_func(obj, cascade=True):
        if cascade:
            # Delete recursive objects too
            votes = obj.m.votes()
            for vote in votes:
                tx = vote.t.delete()
                db.execute(tx)
            comments = obj.m.comments()
            for comment in comments:
                tx = comment.t.delete()
                db.execute(tx)
        if obj is not None:
            tx = obj.t.delete()
            db.execute(tx)
        return obj, True   
    
    if request.method == 'POST':
        obj, deleted = on_delete_func(obj)
        oid = obj.s.oid
        ctx['message'] = 'Object deleted'
        ctx['deleted'] = deleted
        return HTTPRedirectResponse('/blog/')   
    return direct_to_template(request, template_name, extra_context=ctx)
