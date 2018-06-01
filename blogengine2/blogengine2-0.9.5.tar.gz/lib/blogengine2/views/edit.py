#!/usr/bin/env python
# Copyright (c) 2009-2012 Etienne Robillard <erob@gthcfoundation.org>
# All rights reserved.
# Please see the "LICENSE" file for license details. 
"""Management views"""

import os
import random
import base64

from notmm.utils.wsgilib import HTTPRedirectResponse
from notmm.controllers.zodb import ZODBController
from notmm.dbapi.orm import decorators
from notmm.utils.django_settings import LazySettings
from notmm.utils.wsgilib import HTTPUnauthorized
from notmm.utils.template import direct_to_template
from blogengine2.contrib.comments import CommentForm
from blogengine2.config import RemoteUser, authorize, UserIn
from blogengine2.contrib.api_v1.forms import EntryForm

settings = LazySettings()

@authorize(UserIn(users=settings.ALLOWED_USERS))
@decorators.with_zodb_database('db_blog', controller_class=ZODBController)
def edit(request, oid, template_name="blogengine2/api/edit.mako"):
    
    # Initial template dict
    ctx = dict(message="Welcome, %s"%request.remote_user)
    
    # Get the messageid
    k,messageid = base64.urlsafe_b64decode(str(oid)).split(':')

    # Get the current zodb database
    db = request.environ['schevo.db.zodb'] # schevo.db.blogengine
    #db._sync()

    # Retrieve the object (entity) using the given messageid
    obj = db.Message.findone(messageid=messageid)
    if obj is not None:
        datadict = obj.s.field_map()
        form = EntryForm(data=datadict.value_map())
    
        ctx['form'] = form
        ctx['oid'] = obj._oid
        ctx['title'] = obj.content

    if request.method == 'POST':
        #handle POST request
        new_data = request.POST.copy()
        form = EntryForm(db, new_data)
        if form.is_valid():
            # Continue with schevo model validation
            cleaned_data = form.cleaned_data
            if 'category' in cleaned_data:
                cleaned_data['category'] = db.Category.findone(name=cleaned_data['category'])
            tx = obj.t.update(**cleaned_data)  # create the schevo transaction object
            if tx is not None:
                try:
                    db.execute(tx)  # execute the transaction/commit
                except Exception:
                    # error doing the transaction
                    ctx['message'] = 'internal server error'

                return HTTPRedirectResponse('/blog/')
    return direct_to_template(request, template_name, extra_context=ctx)
