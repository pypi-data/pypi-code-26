#!/usr/bin/env python
# Copyright (c) 2009-2012 Etienne Robillard <erob@gthcfoundation.org>
# All rights reserved.
# Please see the "LICENSE" file for license details. 
"""Management views"""

import os
import random
# support functions
from datetime import datetime

from notmm.controllers.zodb import ZODBController
from notmm.dbapi.orm import decorators
#from notmm.utils.django_settings import LazySettings
from notmm.utils.wsgilib import HTTPUnauthorized
from notmm.utils.template import direct_to_template
from notmm.utils.django_settings import LazySettings
from blogengine2.contrib.comments import CommentForm
from blogengine2.config import RemoteUser, authorize, UserIn
from blogengine2.contrib.api_v1 import EntryForm

settings = LazySettings()

#@authorize(RemoteUser())
@authorize(UserIn(users=settings.ALLOWED_USERS))
@decorators.with_schevo_database('db_blog', controller_class=ZODBController)
def add(request, template_name="blogengine2/api/add.mako"):
    #import pdb; pdb.set_trace()
    
    db = request.environ['schevo.db.zodb'] # schevo.db.blogengine
    form = EntryForm(db)
    ctx = {
        'form': form,
        'message': 'Use the form below to create a new blog article. When \
        done, hit <b>save</b> to preview your article in a new window.'
    }


    if request.method == 'POST':
        #handle POST request
        new_data = request.POST.copy()
        form = EntryForm(db, new_data)
        if form.is_valid():
            # Continue with schevo model validation
            cleaned_data = form.cleaned_data

            if 'category' in cleaned_data:
                cleaned_data['category'] = db.Category.findone(name=cleaned_data['category'])
            else:
                del cleaned_data['category']

            tx = db.Message.t.create(**cleaned_data)  # create the schevo transaction object
            if tx is not None:
                # model validation fixups
                #tx.category = CategoryManager.objects.get(name=cleaned_data['category'])
                #tx.pub_date = datetime.now()
                # XXX use a HiddenField perhaps?
                # Must be a valid user
                messageid = tx.messageid = random.randint(1, 1000)
                author = db.Author.findone(username=request.user)
                if author is None:
                    raise ValueError("Author object not found: %s" % request.user)
                else:
                    tx.author = author
                db.execute(tx)  # execute the transaction/commit
                #db.commit()
                # create the Vote object
                try:
                    tx = db.Vote.t.create(voteid=messageid, 
                        message=db.Message.findone(messageid=messageid))
                    tx.count = 0 # initialize the counter
                except:
                    raise
                else:
                    db.execute(tx)
                    #db.commit()
                    db._sync()
            #db.close()          # close the database IO descriptor
            #ctx['message'] = 'Article (<strong>%s</strong>) created successfully!' % tx.title
            #Session = request.session # NEW session API (0.4.3)
            #Session.add({'message' : 'article saved!'})
            #Session.save()
            from notmm.utils.wsgilib import HTTPRedirectResponse
            return HTTPRedirectResponse('/blog/')
        else:
            ctx['form'] = form
            ctx['message'] = 'Error saving the new data. Please try again.'

    return direct_to_template(request, template_name, extra_context=ctx)
