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


def setup_notebook(debug=False):
    """Called at the start of notebook execution to setup the environment.

    This will configure bokeh, and setup the logging library to be
    reasonable."""
    output_notebook(INLINE, hide_banner=True)

    if debug:
        logging.basicConfig(level=logging.DEBUG)
        logging.debug('Running notebook in debug mode.')

    # If JUPYTERHUB_SERVICE_PREFIX environment variable isn't set,
    # this means that you're running JupyterHub not with Hub in k8s,
    # and not using run_local.sh (which sets it to empty).
    if 'JUPYTERHUB_SERVICE_PREFIX' not in os.environ:
        global jupyter_proxy_url
        jupyter_proxy_url = 'localhost:8888'


def show_with_bokeh_server(obj):
    show(obj, notebook_url=jupyter_proxy_url)
