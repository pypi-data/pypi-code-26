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
from notmm.utils.wsgilib import HTTPRedirectResponse
from blogengine2.contrib.comments import CommentForm
from blogengine2.config import RemoteUser, authorize
from blogengine2.contrib.api_v1.forms import CategoryForm

#settings = LazySettings()

@decorators.with_schevo_database('db_blog', controller_class=ZODBController)
def details(request, slug, template_name="blogengine2/category_detail.mako", **kwargs):
    db = request.environ['schevo.db.zodb']

    obj = db.Category.findone(slug=slug)
    ctx = {
        'category' : obj
        }
    return direct_to_template(request, template_name, extra_context=ctx)


@decorators.with_schevo_database('db_blog', controller_class=ZODBController)
def index(request, template_name="blogengine2/categories.mako", **kwargs):
    db = request.environ['schevo.db.zodb']
    categories = db.Category.find()
    ctx = {
        'categories' : categories
        }
    return direct_to_template(request, template_name, extra_context=ctx)

@authorize(RemoteUser(), HTTPUnauthorized)
@decorators.with_schevo_database('db_blog', controller_class=ZODBController)
def add(request, template_name="blogengine2/category_add.mako", **kwargs):
    #import pdb; pdb.set_trace()
    
    form = CategoryForm()
    ctx = {
        'form': form,
        'message': 'Use the form below to create a new category.'
    }
    if request.method == 'POST':
        #handle POST request
        new_data = request.POST.copy()
        #print new_data
        form = CategoryForm(new_data)
        if form.is_valid():
            # Continue with schevo model validation
            cleaned_data = form.cleaned_data
            db = request.environ['schevo.db.zodb'] # schevo.db.blogengine
            tx = db.Category.t.create(**cleaned_data)  # create the schevo transaction object
            if tx is not None:
                db.execute(tx)  # execute the transaction/commit
                #db.commit()

            return HTTPRedirectResponse('/')
        else:
            ctx['form'] = form
            ctx['message'] = 'Error saving the new data. Please try again.'

    return direct_to_template(request, template_name, extra_context=ctx)
