# Copyright (C) 2007-2013 Etienne Robillard <erob@gthcfoundation.org>
# All rights reserved.
#
# Please see the "LICENSE" file included in the BlogEngine source 
# distribution for details on licensing info.

from schevo.schema import *
from schevo.constant import UNASSIGNED
schevo.schema.prep(locals())

# XXX django compat <= 1.3
from notmm.utils.decorators import permalink
from notmm.utils.django_settings import SettingsProxy

# this requires the markdown2 package, available separately
from notmm.utils.markup import convert2markdown

#import hmac
#import hashlib
import base64

settings = SettingsProxy(autoload=True).get_settings()

class SchevoIcon(E.Entity):

    _hidden = True

    name = f.string()
    data = f.image()

    _key(name)

class Category(E.Entity):
    pass

class BlogEntry(E.Entity):
    pass

class Message(E.Entity):
    author = f.entity('Author')
    content = f.string(multiline=True)
    #pub_date = f.datetime()

    class Meta:
        pass

    #_key(sender_name, blogentry)
    #_key(blogentry)

    def x_was_published_today(self):
        #return bool(self.reviewed == True)
        pass


    @permalink
    def get_absolute_url(self):
        # returns the canonical URL representation for this post
        viewName = 'blogengine2.views.details'

        def quickhash(key, value):
            return base64.urlsafe_b64encode(key + ":" + value)
        
        return (viewName, (), dict(
            username=self.author.username,
            oid=quickhash(settings.SECRET_ID, str(self.s.oid)))
            )
        
class Comment(E.Entity):
    
    #sender_name = f.entity('Author')
    sender_name = f.string()
    sender_message = f.string(multiline=True)
    sender_email = f.string()
    sender_website = f.string(required=False, allow_empty=True)
    
    # Path/URL reference for this comment
    path_url = f.string(required=True)
    
    #TODO support more flexible content/object types...
    blogentry = f.entity('Message', required=False)

    reviewed = f.boolean(required=False, default=True)
    pub_date = f.datetime()

    subscribe_comment_thread = f.boolean(required=False, default=False)

    #_key(sender_name, blogentry)
    #_key(blogentry)

    def x_is_published(self):
        return bool(self.reviewed == True)

    ### Public methods
    def convert_to_html(self, name='sender_message'):
        return convert2markdown(getattr(self, name))
    
    def __repr__(self):
        return "<%s: %s>" % (self.sender_name, self.blogentry)

class Author(E.Entity):
    #user = f.entity
    username = f.string()
    email = f.string(required=False)

    homepage_url = f.string(required=False)
    blog_url = f.string(required=False)
    
    #twitter_username = f.string(required=False)

    _key(username, email)

    #def x_blogentries(self):
    #    return [casting.movie
    #            for casting in self.m.movie_castings()]
    
    def __str__(self):
        return self.username

