from collections import OrderedDict
import re
import time

from xstatic.main import XStatic

from django import template
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.utils.html import escape
from django.utils.http import urlencode

register = template.Library()

@register.simple_tag
def xstatic(modname, filename):
    try:
        # list of tuples of the form (cdnname, protocol)
        cdns = settings.CDNS
    except AttributeError:
        cdns = []
    if settings.DEBUG:
        filename = filename.replace('.min.', '.')

    if cdns:
        modname = str(modname.replace('-', '_'))
        pkg = __import__('xstatic.pkg', fromlist=[modname])
        mod = getattr(pkg, modname)
        for cdnname, protocol in cdns:
            try:
                base_url = XStatic(mod, provider=cdnname, protocol=protocol).base_url
            except KeyError:
                continue
            if isinstance(base_url, str):
                # base_url is often a str
                return base_url + '/' + filename
            else:
                # But it also can be a dict (which maps relative paths to
                # full urls) (this happens with jquery CDN)
                if filename in base_url:
                    return base_url.get(filename)

    return settings.STATIC_URL + 'xstatic/' + filename


START_TIMESTAMP = time.strftime('%Y%m%d.%H%M%S')

@register.simple_tag
def start_timestamp():
    return START_TIMESTAMP


# {% querystring %} bits originally from django-tables2.
kwarg_re = re.compile(r"(?:(.+)=)?(.+)")

def token_kwargs(bits, parser):
    """
    Based on Django's `~django.template.defaulttags.token_kwargs`, but with a
    few changes:

    - No legacy mode.
    - Both keys and values are compiled as a filter
    """
    if not bits:
        return {}
    kwargs = OrderedDict()
    while bits:
        match = kwarg_re.match(bits[0])
        if not match or not match.group(1):
            return kwargs
        key, value = match.groups()
        del bits[:1]
        kwargs[parser.compile_filter(key)] = parser.compile_filter(value)
    return kwargs

class QuerystringNode(template.Node):
    def __init__(self, updates, removals):
        super(QuerystringNode, self).__init__()
        self.updates = updates
        self.removals = removals

    def render(self, context):
        if not 'request' in context:
            raise ImproperlyConfigured('Missing django.core.context_processors.request')
        params = dict(context['request'].GET)
        for key, value in self.updates.items():
            key = key.resolve(context)
            value = value.resolve(context)
            if key not in ("", None):
                params[key] = value
        for removal in self.removals:
            params.pop(removal.resolve(context), None)
        return escape("?" + urlencode(params, doseq=True))

@register.tag
def querystring(parser, token):
    """
    Creates a URL (containing only the querystring [including "?"]) derived
    from the current URL's querystring, by updating it with the provided
    keyword arguments.

    Example (imagine URL is ``/abc/?gender=male&name=Brad``)::

        {% querystring "name"="Ayers" "age"=20 %}
        ?name=Ayers&gender=male&age=20
        {% querystring "name"="Ayers" without "gender" %}
        ?name=Ayers

    """
    bits = token.split_contents()
    tag = bits.pop(0)
    updates = token_kwargs(bits, parser)
    # ``bits`` should now be empty of a=b pairs, it should either be empty, or
    # have ``without`` arguments.
    if bits and bits.pop(0) != "without":
        raise TemplateSyntaxError("Malformed arguments to '%s'" % tag)
    removals = [parser.compile_filter(bit) for bit in bits]
    return QuerystringNode(updates, removals)
