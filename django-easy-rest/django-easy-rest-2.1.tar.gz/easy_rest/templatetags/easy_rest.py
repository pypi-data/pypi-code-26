from django import template
from django.conf import settings
from django.utils.safestring import mark_safe

register = template.Library()

# message to say on tag load
load_message = ''
# the static root of this app
root = '/easy_rest/static'

# if easy rest root specified in settings
if hasattr(settings, 'EASY_REST_ROOT_URL'):
    root = "/" + settings.EASY_REST_ROOT_URL + "/static"
else:
    load_message = '<!--{0}-->\n<script>console.warn("{0}")</script>'.format(
        "EASY_REST_ROOT_URL not specified in settings defaulting with easy_rest ")

# js base html
js_base = '<script src="' + root + '/{}"></script>'

# css base html
css_base = '<link rel="stylesheet" href="' + root + '/{}">'


@register.simple_tag()
def load_rest_scripts():
    """
    loads only easy rest scripts
    :return: html with the scripts
    """
    data = _get_rest_scripts()
    if load_message:
        data = load_message + "\n" + data
    return mark_safe(data)


@register.simple_tag()
def load_rest_all():
    """
    load rest scripts along with bootstrap
    :return: html including bootstrap and rest scripts
    """
    data = _get_rest_scripts() + _get_bootstrap()
    if load_message:
        data = load_message + "\n" + data
    return mark_safe(data)


@register.simple_tag()
def load_debug_scripts():
    return load_rest_all()


def _get_rest_scripts():
    """
    :return: html scripts
    """
    files = [
        'jquery-3.2.1.min.js',
        "debugger.js",
        'Request.js',
        'PostHandler.js',
        'Submit.js',
        'fetch/restFetch.js'
    ]
    return '<!--start of easy rest scripts-->\n{}\n<!--end of easy rest scripts-->'.format(
        '\n'.join([js_base.format(file) for file in files])
    )


def _get_bootstrap():
    """
    :return: html scripts
    """
    files = [
        'bootstrap.css',
        'bootstrap-grid.css',
        'bootstrap-reboot.css',
    ]
    data = '\n'.join([css_base.format("bootstrap-4.0.0-alpha.6-dist/css/{}".format(file)) for file in files])
    data += '\n' + css_base.format("bootstrap-4.0.0-alpha.6-dist/js/{}".format("bootstrap.js"))
    return '<!--start bootstrap-->\n{}\n<!--end of bootstrap-->'.format(data)


@register.tag('livecontext')
def live_context(parser, token):
    bits = token.split_contents()[1:]  # first is the template tag name
    url = None
    if bits:
        url = bits[0]

    nodelist = parser.parse(('endlivecontext',))
    parser.delete_first_token()
    return LiveContext(nodelist, url)


class LiveContext(template.Node):
    def __init__(self, nodelist, url):
        self.nodelist = nodelist
        self.url = url

    def render(self, context):
        output = self.nodelist.render(context)
        if self.url:
            return '<div class="fetch-context" data-fetch-url="{}">\n{}\n</div>'.format(self.url, output)
        else:
            return '<div class="fetch-context">\n{}\n</div>'.format(output)
