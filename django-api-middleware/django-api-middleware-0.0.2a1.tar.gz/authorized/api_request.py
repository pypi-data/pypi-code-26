"""
======================
Custom Requests Module
======================
A 'mask' for the original python requests module, without affecting the original functionality.
A header is appended each time a request is made.
"""
from django.http import JsonResponse
import requests
from authorized import api_token
from authorized import api_check
def request(method, url, is_external=False, **kwargs):
    r"""Constructs and sends a :class:`Request <Request>`.

    :param method: method for the new :class:`Request` object.
    :param url: URL for the new :class:`Request` object.
    :param params: (optional) Dictionary or bytes to be sent in the query string for the :class:`Request`.
    :param data: (optional) Dictionary or list of tuples ``[(key, value)]`` (will be form-encoded), bytes, or file-like object to send in the body of the :class:`Request`.
    :param json: (optional) json data to send in the body of the :class:`Request`.
    :param headers: (optional) Dictionary of HTTP Headers to send with the :class:`Request`.
    :param cookies: (optional) Dict or CookieJar object to send with the :class:`Request`.
    :param files: (optional) Dictionary of ``'name': file-like-objects`` (or ``{'name': file-tuple}``) for multipart encoding upload.
        ``file-tuple`` can be a 2-tuple ``('filename', fileobj)``, 3-tuple ``('filename', fileobj, 'content_type')``
        or a 4-tuple ``('filename', fileobj, 'content_type', custom_headers)``, where ``'content-type'`` is a string
        defining the content type of the given file and ``custom_headers`` a dict-like object containing additional headers
        to add for the file.
    :param auth: (optional) Auth tuple to enable Basic/Digest/Custom HTTP Auth.
    :param timeout: (optional) How many seconds to wait for the server to send data
        before giving up, as a float, or a :ref:`(connect timeout, read
        timeout) <timeouts>` tuple.
    :type timeout: float or tuple
    :param allow_redirects: (optional) Boolean. Enable/disable GET/OPTIONS/POST/PUT/PATCH/DELETE/HEAD redirection. Defaults to ``True``.
    :type allow_redirects: bool
    :param proxies: (optional) Dictionary mapping protocol to the URL of the proxy.
    :param verify: (optional) Either a boolean, in which case it controls whether we verify
            the server's TLS certificate, or a string, in which case it must be a path
            to a CA bundle to use. Defaults to ``True``.
    :param stream: (optional) if ``False``, the response content will be immediately downloaded.
    :param cert: (optional) if String, path to ssl client cert file (.pem). If Tuple, ('cert', 'key') pair.
    :return: :class:`Response <Response>` object
    :rtype: requests.Response
    """
    kwargs = append_header(**kwargs)
    response = requests.request(method, url, **kwargs)
    if is_external:
        # If request is external no verification of origin will be done
        return response
    else:
        # Otherwise a header verification will be done.
        return process_response_header(response)

def get(url, params=None, is_external=False, **kwargs):
    r"""Sends a GET request.

    :param url: URL for the new :class:`Request` object.
    :param params: (optional) Dictionary or bytes to be sent in the query string for the :class:`Request`.
    :param headers: (optional) Dictionary of HTTP Headers to send with the :class:`Request`.
    :param \*\*kwargs: Optional arguments that ``request`` takes.
    :return: :class:`Response <Response>` object
    :rtype: requests.Response
    """
    kwargs = append_header(**kwargs)
    response = requests.get(url, params=params, **kwargs)
    if is_external:
        # If request is external no verification of origin will be done
        return response
    else:
        # Otherwise a header verification will be done.
        return process_response_header(response)

def options(url, is_external=False, **kwargs):
    r"""Sends an OPTIONS request.

    :param url: URL for the new :class:`Request` object.
    :param \*\*kwargs: Optional argpostuments that ``request`` takes.
    :return: :class:`Response <Response>` object
    :rtype: requests.Response
    """
    kwargs = append_header(**kwargs)
    response = requests.options(url, **kwargs)
    if is_external:
        # If request is external no verification of origin will be done
        return response
    else:
        # Otherwise a header verification will be done.
        return process_response_header(response)

def head(url, is_external=False, **kwargs):
    r"""Sends a HEAD request.

    :param url: URL for the new :class:`Request` object.
    :param \*\*kwargs: Optional arguments that ``request`` takes.
    :return: :class:`Response <Response>` object
    :rtype: requests.Response
    """
    kwargs = append_header(**kwargs)
    response = requests.head(url, **kwargs)
    if is_external:
        # If request is external no verification of origin will be done
        return response
    else:
        # Otherwise a header verification will be done.
        return process_response_header(response)

def post(url, data=None, json=None, is_external=False, **kwargs):
    r"""Sends a POST request.APIRequests

    :param url: URL for the new :class:`Request` object.
    :param data: (optional) Dictionary (will be form-encoded), bytes, or file-like object to send in the body of the :class:`Request`.
    :param json: (optional) json data to send in the body of the :class:`Request`.
    :param \*\*kwargs: Optional arguments that ``request`` takes.
    :return: :class:`Response <Response>` object
    :rtype: requests.Response
    """
    kwargs = append_header(**kwargs)
    response = requests.post(url, data=data, json=json, **kwargs)
    if is_external:
        # If request is external no verification of origin will be done
        return response
    else:
        # Otherwise a header verification will be done.
        return process_response_header(response)

def put(url, data=None, is_external=False, **kwargs):
    r"""Sends a PUT request.

    :param url: URL for the new :class:`Request` object.
    :param data: (optional) Dictionary (will be form-encoded), bytes, or file-like object to send in the body of the :class:`Request`.
    :param json: (optional) json data to send in the body of the :class:`Request`.
    :param \*\*kwargs: Optional arguments that ``request`` takes.
    :return: :class:`Response <Response>` object
    :rtype: requests.Response
    """
    kwargs = append_header(**kwargs)
    response = requests.put(url, data=data, **kwargs)
    if is_external:
        # If request is external no verification of origin will be done
        return response
    else:
        # Otherwise a header verification will be done.
        return process_response_header(response)

def patch(url, data=None, is_external=False, **kwargs):
    r"""Sends a PATCH request.

    :param url: URL for the new :class:`Request` object.
    :param data: (optional) Dictionary (will be form-encoded), bytes, or file-like object to send in the body of the :class:`Request`.
    :param json: (optional) json data to send in the body of the :class:`Request`.
    :param \*\*kwargs: Optional arguments that ``request`` takes.
    :return: :class:`Response <Response>` object
    :rtype: requests.Response
    """
    kwargs = append_header(**kwargs)
    response = requests.patch(url, data=data, **kwargs)
    if is_external:
        # If request is external no verification of origin will be done
        return response
    else:
        # Otherwise a header verification will be done.
        return process_response_header(response)

def delete(url, is_external=False, **kwargs):
    r"""Sends a DELETE request.

    :param url: URL for the new :class:`Request` object.
    :param \*\*kwargs: Optional arguments that ``request`` takes.
    :return: :class:`Response <Response>` object
    :rtype: requests.Response
    """
    kwargs = append_header(**kwargs)
    response = requests.delete(url, **kwargs)
    if is_external:
        # If request is external no verification of origin will be done
        return response
    else:
        # Otherwise a header verification will be done.
        return process_response_header(response)

def append_header(**kwargs):
    """Appends a header with the appropieate values to be evaluated in the middleware.
    """
    if kwargs.get('headers') is None:
        kwargs['headers'] = {'application-token': api_token.generate()}
    else:
        kwargs['headers'].update({'application-token': api_token.generate()})
    return kwargs

def process_response_header(response):
    """Checks if the response is coming from a trusted source
    """
    source = None
    token = api_check.response_header_token(response)
    if token['has_token']:
        token_verified = api_token.verify(token['token'])
        if token_verified['is_valid']:
            source = api_check.is_response_trusted(token_verified['app_name'])
            if source['is_authorized']:
                return response
            else:
                return untrusted_response()
        else:
            return untrusted_response()
    else:
        return untrusted_response()

def untrusted_response():
    """Returns a response object for untrusted resources.
    """
    return JsonResponse({'errors': {'message': 'Response is coming from an untrusted source.'}}, status=599, content_type='application/json;UTF-8;')
