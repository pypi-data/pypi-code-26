# -*- coding: utf-8 -*-

import logging, os, re, urllib.parse
from bl.dict import Dict

LOG = logging.getLogger(__name__)

# pattern from https://gist.github.com/gruber/249502#gistcomment-1328838
PATTERN = r"""\b((?:[a-z][\w\-]+:(?:\/{1,3}|[a-z0-9%])|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}\/)(?:[^\s()<>]|\((?:[^\s()<>]|(?:\([^\s()<>]+\)))*\))+(?:\((?:[^\s()<>]|(?:\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'".,<>?«»“”‘’]))"""
REGEXP = re.compile(PATTERN, re.I+re.U)

class URL(Dict):
    """URL object class. Makes handling URLs very easy. Holds the URL in parsed, unquoted form internally.
    Sample usage:

    >>> u = URL('http://blackearth.us:8888/this/is;really?not=something#important')
    >>> u.scheme, u.host, u.path, u.params, u.qargs, u.fragment
    ('http', 'blackearth.us:8888', '/this/is', 'really', {'not': 'something'}, 'important')
    >>> str(u)
    'http://blackearth.us:8888/this/is;really?not=something#important'
    >>> u
    URL('http://blackearth.us:8888/this/is;really?not=something#important')
    >>> u.qstring
    'not=something'
    >>> u.drop_qarg('not')
    URL('http://blackearth.us:8888/this/is;really#important')
    >>> u                                                 # no change to u 
    URL('http://blackearth.us:8888/this/is;really?not=something#important')
"""

    def __init__(self, url='', **kwargs):
        """create a URL object from the given url cast to str via str(url).
        The given url can be modified with the following key-word arguments:
        * scheme    = the URL scheme (http, file, mailto, etc.)
        * host      = the host server
        * path      = the path on the host server
        * params    = any URL parameters (begins with ;)
        * fragment  = URL fragment (begins with #)
        * query     = URL query (begins with ?)
        * qargs     = an alternative form of query, with the arguments already parsed into a dict
        """
        # 1. parse the url string
        # s = str(url).replace('file://', 'file:')    # needed for file URLs to parse correctly
        args = {k:kwargs[k] for k in ['scheme', 'host', 'path', 'params', 'fragment', 'query', 'qargs'] if kwargs.get(k) not in [None, {}, '']}
        LOG.debug("URL.__init__(%r, %r)" % (url, args))
        pr = urllib.parse.urlparse(str(url))

        # 2. deal with parameters
        self.scheme     = kwargs.get('scheme') or pr.scheme
        self.host       = kwargs.get('host') or pr.netloc
        self.path       = self.normpath(urllib.parse.unquote(kwargs.get('path') or pr.path))
        self.params     = kwargs.get('params') or pr.params
        self.fragment   = kwargs.get('fragment') or pr.fragment

        # 3. deal with query arguments
        d = Dict(**urllib.parse.parse_qs(kwargs.get('query') or pr.query))
        for k in d:
            d[k] = d[k][-1]     # only keep the last instance of an argument
            if d[k] in [None, '']: _=d.pop('k')
        qargs = kwargs.get('qargs') or {}
        self.qargs = d
        for k in qargs.keys():
            if qargs[k] in ['', None]: 
                if k in self.qargs.keys():
                    _=self.qargs.pop(k)
            else:
                self.qargs[k] = qargs[k]

        # 4. deal with file: URL anomalies in urllib
        if self.scheme == 'file' and self.host != '':
            self.path, self.host = self.join(self.host, self.path).path, ''

    def __call__(self, **args):
        """return a new url with the given modifications (immutable design)."""
        u = URL(str(self))
        u.update(**args)
        return u

    def __str__(self):
        pr = (self.scheme, self.host, self.path,
            self.params, self.qstring, self.fragment)
        s = urllib.parse.urlunparse(pr)
        if s[:2]=='//': s = s[2:]       # strip an empty protocol separator from beginning
        return s

    def __repr__(self):
        return """URL('%s')""" % str(self)

    def __contains__(self, key):
        """enable the 'in' operator by casting both terms to str."""
        return str(key) in str(self)

    @property
    def qstring(self):
        return urllib.parse.urlencode(self.qargs)

    @property
    def basename(self):
        """return the basename of the URL's path"""
        return os.path.basename(self.path)

    @property
    def parent(self):
        """return the parent URL, with params, query, and fragment in place"""
        path = '/'.join(self.path.split('/')[:-1])
        s = path.strip('/').split(':')
        if len(s)==2 and s[1]=='':
            return None
        else:
            return self.__class__(self, path=path)

    @classmethod
    def normpath(C, path):
        p = path.replace('\\','/').strip()     # backslash sometimes comes in from Windows.
        if p != '/':
            p = p.rstrip('/')
        return p

    def split(self):
        return str(self).split('/')

    def splitext(self):
        return os.path.splitext(str(self))

    def no_qargs(self):
        u = URL(**self)
        u.qargs = Dict()
        return u

    def drop_qarg(self, key):
        u = URL(self)
        for k in u.qargs.keys():
            if k == key:
                del(u.qargs[k])
        return u

    def quoted(self):
        pr = (self.scheme, self.host, urllib.parse.quote(self.path),
            self.params, self.qstring, self.fragment)
        return urllib.parse.urlunparse(pr)        

    def unquoted(self):
        pr = (self.scheme, self.host, urllib.parse.unquote(self.path),
            self.params, self.qstring, self.fragment)
        return urllib.parse.urlunparse(pr)                

    @classmethod
    def finditer(C, text):
        """search the given text for URLs and return an iterator of matches."""
        return REGEXP.finditer(text)

    @classmethod
    def join(C, *args, **kwargs):
        """join a list of url elements, and include any keyword arguments, as a new URL"""
        u = C('/'.join([str(arg).strip('/') for arg in args]), **kwargs)
        return u

if __name__=='__main__':
    import doctest
    doctest.testmod()
