import datetime
import hashlib
import json
import os
import re

import urllib.request

from scripting import parse, extensions

_JSON_OPENING_CHARS = [',', '[', '{', ':']
_JSON_CLOSING_CHARS = [',', '}', ']']
_COMMENTS_REGEX = re.compile(r'/\*.*?\*/', re.DOTALL)
_INCLUDE_DIRECTIVE = re.compile(
    r'\/\*\#INCLUDE(.*?)\*/|\/\*\ \#INCLUDE(.*?)\*/|\/\/\#INCLUDE(.*\ ?)|\/\/\ \#INCLUDE(.*\ ?)',
    re.IGNORECASE | re.MULTILINE)
_PARENT_FILE_KEY = "parent_file"
_PARENT_FILE_STRING_SRC = "__string__"


def load(json_file_path, encoding=None, cls=None, object_hook=None, parse_float=None,
         parse_int=None, parse_constant=None, object_pairs_hook=None, error_on_include_file_not_found=False,
         error_on_invalid_value=False, **kw):
    """Decodes a JSON source file into a dictionary"""
    file_full_path = os.path.abspath(json_file_path)
    file_path = os.path.dirname(file_full_path)
    with open(file_full_path, encoding=encoding) as f:
        json_source = f.read()
    # Inject source file path
    if kw is None:
        kw = {}
    kw[_PARENT_FILE_KEY] = file_full_path
    return loads(json_source, encoding=encoding, cls=cls, object_hook=object_hook, parse_float=parse_float,
                 parse_int=parse_int, parse_constant=parse_constant, object_pairs_hook=object_pairs_hook,
                 error_on_include_file_not_found=error_on_include_file_not_found,
                 error_on_invalid_value=error_on_invalid_value, includes_path=file_path, **kw)


def loads(json_string, encoding=None, cls=None, object_hook=None, parse_float=None,
          parse_int=None, parse_constant=None, object_pairs_hook=None,
          error_on_include_file_not_found=False, error_on_invalid_value=False, includes_path=None, **kw):
    """Decodes a provided JSON source string into a dictionary"""
    _json_includes_cache = {}
    if json_string is None or json_string.strip(' ') == '':
        raise AttributeError('No JSON source was provided for decoding.')
    if includes_path is None:
        includes_path = os.path.dirname(os.path.realpath(__file__))
    # Initialize Include Cache
    _json_includes_cache = {}
    # Process Include Directives
    if kw is not None and _PARENT_FILE_KEY in kw:
        parent_file_path = kw[_PARENT_FILE_KEY]
    else:
        parent_file_path = _PARENT_FILE_STRING_SRC
    json_source = _include_files(includes_path, json_string, encoding, _json_includes_cache,
                                 error_on_include_file_not_found, [parent_file_path])
    json_source = _remove_comments(json_source)
    # Drop parent file key before calling native json loads since it is not supported
    if kw is not None and _PARENT_FILE_KEY in kw:
        kw.pop(_PARENT_FILE_KEY, None)
    json_source = parse(json_source, error_on_invalid_value)
    return json.loads(json_source, encoding=encoding, cls=cls, object_hook=object_hook, parse_float=parse_float,
                      parse_int=parse_int, parse_constant=parse_constant, object_pairs_hook=object_pairs_hook, **kw)


def dumps(obj, skipkeys=False, ensure_ascii=True, check_circular=True,
          allow_nan=True, cls=None, indent=None, separators=None,
          default=None, sort_keys=False, **kw):
    """Serializes JSON into string."""
    return json.dumps(obj, skipkeys=skipkeys, ensure_ascii=ensure_ascii, check_circular=check_circular,
                      allow_nan=allow_nan, cls=cls, indent=indent, separators=separators,
                      default=default, sort_keys=sort_keys, **kw)


def register_custom_scripting_extension(name, fn):
    """Registers a custom scripting extension function"""
    return extensions.register_extension_function(name, fn)

def _include_files(include_files_path, string, encoding=None, cache=None, error_on_file_not_found=False,
                   parent_file_paths=None):
    """Include all files included in current json string"""
    try:
        includes = re.finditer(_INCLUDE_DIRECTIVE, string)
        # Files Cache
        if cache is None:
            cache = {}
        if parent_file_paths is None:
            parent_file_paths = []
        for match_num, match in enumerate(includes):
            if len(match.groups()) > 0:
                for value in match.groups():
                    if value is None:
                        continue
                    http_download = False
                    include_call_string = str(match.group())
                    property_name = ""
                    file_name = _remove_enclosing_chars(value)
                    default_value = None
                    file_expected_checksum = None
                    if ":" in file_name:
                        values = file_name.split(":",1)
                        property_name = values[0]
                        file_name = values[1]
                        if '|' in file_name:
                            file_properties = file_name.split('|')
                            file_properties_count = len(file_properties)
                            file_name = file_properties[0].strip(' ')
                            if file_properties_count > 1:
                                default_value = file_properties[1].strip(' ')
                            elif file_properties >= 2:
                                file_expected_checksum = file_properties[2].strip(' ')
                    if 'http://' in file_name or 'https://' in file_name:
                        http_download = True
                        include_file_path = _download_file(file_name, include_files_path)
                        # TODO: Create file with download information and checksum
                    else:
                        include_file_path = os.path.normpath(os.path.join(include_files_path, file_name))
                    if os.path.abspath(include_file_path):
                        # Cache File if not already cached.
                        if include_file_path not in cache:
                            try:
                                if include_file_path in cache.keys() or include_file_path in parent_file_paths:
                                    raise IncludeRecursionError(include_file_path)
                                parent_file_list = parent_file_paths + [include_file_path]
                                with open(include_file_path, "r", encoding=encoding) as f:
                                    cache[include_file_path] = {
                                        "src": ""
                                    }
                                    if file_expected_checksum is not None:
                                        if not _check_file_checksum(include_file_path, file_expected_checksum):
                                            raise IOError("Include File has checksum does not match expected.")
                                    included_file_source = _include_files(include_files_path, f.read(), encoding, cache,
                                                                          error_on_file_not_found,
                                                                          parent_file_list)
                                cache[include_file_path]["src"] = included_file_source
                            except IOError as ex:
                                if error_on_file_not_found:
                                    raise IOError("Included file '{0}' was not found.".format(include_file_path))
                                else:
                                    if default_value is not None:
                                        cache[include_file_path] = { "src": default_value }
            # Extract content from include file removing comments, end of lines and tabs
            if include_file_path in cache:
                included_source = cache[include_file_path]["src"]
                included_source = _remove_comments(included_source).strip(' ').strip('\r\n').strip('\n').strip(
                    '\t')
            else:
                included_source = ""
            # Add Property Name if specified
            if property_name is not None and property_name.strip(' ') != '':
                included_source = "\"{0}\": {1}".format(property_name, included_source)
            # Add Comma if needed and determine if property is required
            included_source_first_char = _get_first_char(included_source)
            included_source_last_char = _get_last_char(included_source)
            included_source_surrounding_src = string.split(include_call_string)
            included_source_surrounding_src_count = len(included_source_surrounding_src) - 1
            for i in range(0, included_source_surrounding_src_count):
                included_call_pre_last_char = _get_last_char(
                    _remove_comments(included_source_surrounding_src[i]))
                # Add comma at the beginning of the included code if required
                if included_call_pre_last_char not in _JSON_OPENING_CHARS and included_source_first_char != ',':
                    included_source = "," + included_source
                # Add Trailing comma if code following the included statement does not have one.
                if included_source.strip(' ') != '' and i < included_source_surrounding_src_count:
                    if included_source_last_char != ',' and _get_first_char(
                            _remove_comments(
                                included_source_surrounding_src[i + 1])) not in _JSON_CLOSING_CHARS:
                        included_source = included_source + ','
            string = string.replace(include_call_string, included_source)
        return string
    except IncludeError:
        raise
    except IncludeRecursionError:
        raise
    except Exception as ex:
        raise IncludeError(exception=ex)

def _download_file(url, local_path):
    file_name = url[url.rfind("/")+1:]
    if not file_name.endswith('.json'):
        file_name = f"{file_name}.json"
    info_file_name = file_name.replace('.json', '.http.json')
    local_file_path = os.path.join(local_path, file_name)
    info_file_path = os.path.join(local_path, info_file_name)
    try:
        file_size = 0
        file_checksum = ""
        with urllib.request.urlopen(url) as r:
            with open(local_file_path, 'wb') as f:
                data = r.read()
                f.write(data)
                file_size = len(data)
            with open(info_file_path, 'w') as f:
                data = {
                    "date": datetime.datetime.utcnow().isoformat(),
                    "url": url,
                    "file_name": file_name,
                    "size": file_size,
                    "checksum": _get_file_checksum(local_file_path)
                }
                f.write(json.dumps(data))
    except Exception as ex:
        raise IOError(f"Include file could not be downloaded from {url}. Ready: {ex}.")
    return local_file_path


def _get_file_checksum(file_path):
    hash_md5 = hashlib.md5()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()


def _check_file_checksum(file_path, checksum):
    return _get_file_checksum(file_path).lower() == checksum.lower()


def _process_value_calls(json_source, error_on_invalid_value=False):
    cached_values = {}
    if not ("$." in json_source or "this." in json_source):
        return json_source
    # Process ref or dyn value calls
    dyn_ref_calls = re.finditer(_DYN_REF_VALUE_CALL, json_source)
    # Files Cache 
    for match_num, match in enumerate(dyn_ref_calls):
        if len(match.groups()) > 0:
            for value in match.groups():
                if value is None:
                    continue
                print(value)
    return json_source


def _remove_comments(string):
    """Removes all comments"""
    string = re.sub(re.compile("/\*.*?\*/", re.DOTALL), "", string)
    string = re.sub(re.compile("//.*?\n"), "", string)
    return string


def _remove_enclosing_chars(string):
    return string.replace("<", "").replace(">", "").replace("\"", "").replace("'", "").strip(" ")


def _get_last_char(string):
    return string.replace(' ', '').replace('\r\n', '').replace('\n', '')[-1:]


def _get_first_char(string):
    return string.replace(' ', '').replace('\r\n', '').replace('\n', '')[:1]


class IncludeRecursionError(Exception):
    def __init__(self, origin=None):
        super().__init__()
        self._origin = origin

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        return "Inclusion Recursion Found in file {0}.".format(self._origin)


class IncludeError(Exception):
    def __init__(self, message=None, exception: Exception = None):
        super().__init__()
        # TODO: Exception should be added to the stack...
        self._message = ""
        if message is not None:
            self._message = message
        if exception is not None:
            self._message = str(exception)
            self.args = exception.args
            self.__context__ = exception.__context__
            self.__traceback__ = exception.__traceback__
            self.__cause__ = exception.__cause__

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        return "Invalid Included directive. {0}".format(self._message)
