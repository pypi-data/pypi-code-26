from .exceptions import ResponseContentCouldNotFormat
import json


def response_format(content):
    """
    format different type contents as str
    :return THE_TYPE_OF_CONTENT, CONTENT_FORMATTED
    """
    if isinstance(content, str):
        return "text/html", content
    elif isinstance(content, list) or isinstance(content, dict):
        return "application/json", json.dumps(content)
    else:
        try:
            return "text/plain", str(content)
        except:
            raise ResponseContentCouldNotFormat()
