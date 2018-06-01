#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2009 Etienne Robillard <erob@gthcfoundation.org>
# All rights reserved.
# Please see the "LICENSE" file for license details. 

from notmm.utils.urlmap import RegexURLMap, url
#from blogengine.template import direct_to_template
#from blogengine.contrib.api_v1.model import (
#    CommentManager, BlogEntryManager, CategoryManager
#    )

urlpatterns = RegexURLMap(label="blogengine")


# Site-wide API functions accessible to registered users (editors, etc.)
urlpatterns.add_routes('blogengine2.views',
    #(r'^posts/add/$', 'add'),
    #url(r'(?P<category>[-\w]+)/(?P<slug>[-\w]+)/edit/$', 'edit'),
    #url(r'(?P<category>[-\w]+)/(?P<slug>[-\w]+)/send_to_friend/$', 'send_to_friend'),
    url(r'(?P<oid>[=\w]+)/vote_up/$', 'vote.vote_up', name="blogengine_vote_up"), # AJAX
    url(r'(?P<oid>[=\w]+)/vote_down/$', 'vote.vote_down', name="blogengine_vote_down"), # AJAX
    
    # Admin views
    url(r'admin/(?P<oid>[=\w]+)/edit/$', 'edit.edit', name="blogengine_edit"),
    url(r'admin/(?P<oid>[=\w]+)/delete/$', 'delete.delete', name="blogengine_delete"),
    url(r'admin/create/$', 'add.add', name="blogengine_add"),
    url(r'admin/category/add/$', 'category.add', name="blogengine_category_add"),
    
    url(r'(?P<oid>[=\w]+)/rss/$', 'rss.rss', name="blogengine_rss_details"),
    url(r'rss/$', 'rss.index', name="blogengine_rss"),

    url(r'(?P<oid>[=\w]+)$', 'detail.redirect', name='blogengine_redirect_hack'),
    url(r'(?P<oid>[=\w]+)/view/$', 'detail.details', name="blogengine_details"),


    url(r'category/$', 'category.index', name="blogengine_category_index"),

    url(r'category/(?P<slug>[-\w]+)/$', 'category.details', name="blogengine_category_details"),
    url(r'$', 'index.index', name="blogengine_index")
)
