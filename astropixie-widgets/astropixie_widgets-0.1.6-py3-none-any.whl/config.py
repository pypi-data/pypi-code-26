import logging
import os
import urllib

from bokeh.io import show, output_notebook
from bokeh.resources import INLINE


def remote_jupyter_proxy_url(port):
    """
    Callable to configure Bokeh's show method when a proxy must be
    configured.

    If port is None we're asking about the URL
    for the origin header.
    """
    if port is None:
        return '*'

    base_url = os.environ['EXTERNAL_URL']
    service_url_path = os.environ['JUPYTERHUB_SERVICE_PREFIX']
    proxy_url_path = 'proxy/%d' % port

    user_url = urllib.parse.urljoin(base_url, service_url_path)
    full_url = urllib.parse.urljoin(user_url, proxy_url_path)
    return full_url


# By default, use the remote_jupyter_proxy_url
jupyter_proxy_url = remote_jupyter_proxy_url


def setup_notebook(debug=False, local=False):
    """Called at the start of notebook execution to setup the environment.

    This will configure bokeh, and setup the logging library to be
    reasonable."""
    output_notebook(INLINE, hide_banner=True)

    if debug:
        logging.basicConfig(level=logging.DEBUG)
        logging.debug('Running notebook in debug mode.')

    if local:
        global jupyter_proxy_url
        jupyter_proxy_url = 'localhost:8888'
    else:
        jupyter_proxy_url = remote_jupyter_proxy_url


def show_with_bokeh_server(obj):
    def jupyter_proxy_url(port):
        # If port is None we're asking about the URL
        # for the origin header.
        if port is None:
            return '*'

        base_url = os.environ['EXTERNAL_URL']
        service_url_path = os.environ['JUPYTERHUB_SERVICE_PREFIX']
        proxy_url_path = 'proxy/%d' % port

        user_url = urllib.parse.urljoin(base_url, service_url_path)
        full_url = urllib.parse.urljoin(user_url, proxy_url_path)
        return full_url

    show(obj, notebook_url=jupyter_proxy_url)
