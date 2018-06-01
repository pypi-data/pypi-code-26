#!/usr/bin/env python

from datetime import datetime
from urlparse import parse_qsl
from operator import attrgetter

from notmm.controllers.schevo import ZODBController
from notmm.utils.template import RequestContext
from notmm.dbapi.orm.decorators import with_schevo_database
from notmm.utils.django_settings import LazySettings
from notmm.utils import paginator
from notmm.utils.cache import cached

from blogengine.contrib.api_v1  import CategoryManager
from blogengine.config          import ObjectDoesNotExist
from blogengine.template import direct_to_template
from blogengine.config.global_settings import DATABASE_NAME, BLOGENGINE

settings = LazySettings()

#@cached(time=1200)
@with_schevo_database(DATABASE_NAME, controller_class=ZODBController)
def index(request, *args, **kwargs):
    """View a list of recent blog entries"""
    
    db = request.environ['schevo.db.'+DATABASE_NAME]
    #db._sync()
    Q = getattr(db, 'Q')

    # Get the most recent entries in reverse order
    q1 = Q.Match(db.BlogEntry, 'pub_date', '<=', datetime.today())
    q2 = Q.Match(db.BlogEntry, 'reviewed', '==', True)
    #q3 = Q.Match(db.BlogEntry, 'author', '==', request.session.user)

    # selects elements contained in both sets
    results = Q.Intersection(q1, q2)
    
    # parse the query string
    query_args = parse_qsl(request.environ['QUERY_STRING'])

    # immutable set of all available items
    # ResultSet = SortedQuerySet(..)
    items = sorted(results(), key=attrgetter('pub_date'), reverse=True)
    items_count = len(items)

    if 'page' in query_args:
        page_int = int(query_args['page'])
    
    # Fetch all available categories which contains any
    # published Articles (BlogEntry)
    categories = filter(lambda x: x.get_items_count() > 0, 
        CategoryManager.objects.all())
    # most recent posts at the top 
    categories.sort(lambda x,y: cmp(x.get_items_count(), y.get_items_count()))
    categories.reverse()
 
    # Average (Stephane) programmers are not obligated to use this to
    # make a fucking site in Django.
    theme = kwargs.get('site_theme', 'cleanlayout')
    template = str(theme + '.' + 'index')
    p = paginator.getpaginator(items, settings)
    prev_page, next_page = paginator.getpageinfo(p)

    #import pdb; pdb.set_trace()
    return direct_to_template(request, \
        template_name=BLOGENGINE['VIEWS'].get(template, \
            'blogengine/frontpage.mako'),
        extra_context=RequestContext(request, dict(
            blogentry_set=p.items,
            max_items_count=items_count,
            blog_categories=categories,
            page_num=p.page, 
            page_mod=p.page_count,
            next_page=next_page,
            prev_page=prev_page,
            #feed=get_feed('21') #XXX: fixme (segfault)
            )),
        #extra_headers=extra_headers,
        #cache_enabled=False
        )


