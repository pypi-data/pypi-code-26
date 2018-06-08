import re
import html


def uncapitalize_name(name):
    """
        >>> uncapitalize_name("Href")
        'href'
        >>> uncapitalize_name("HttpEquiv")
        'http-equiv'

    """

    return re.sub( '(?<!^)(?=[A-Z])', '-', name).lower()


def escape(s, quote=None):
    """
    Replace special characters "&", "<" and ">" to HTML-safe sequences.
    If the optional flag quote is true (the default), the quotation mark
    characters, both double quote (") and single quote (') characters are also
    translated.
    """
    return html.escape(s, quote)


def versioned(filename):
    """

        >>> versioned('/js/custom.js', src='data', dist='/static')
        '/static/js/custom_8si2je97h2.js'
    """
    pass