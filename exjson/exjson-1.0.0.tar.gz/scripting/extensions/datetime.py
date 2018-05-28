from datetime import datetime, timedelta

from dateutil.tz import tzlocal

_DATETIME_FORMAT_MAP = [
    (0, "dddd", "%A"),  # Weekday as locale’s full name. Ex. "Monday"
    (1, "ddd", "%a"),  # Weekday as locale’s abbreviated name. Ex. "Mon"
    # "": "%w",  # Weekday as a decimal number, where 0 is Sunday and 6 is Saturday. Ex. "1"
    (3, "dd", "%d"),  # Day of the month as a zero-padded decimal number. Ex. "30"
    (4, "d", "%-d"),  # Day of the month as a decimal number. (Platform specific) Ex. "30"
    (5, "MMMM", "%B"),  # Month as locale’s full name. Ex. "September"
    (6, "MMM", "%b"),  # Month as locale’s abbreviated name. Ex. "Sep"
    (7, "MM", "%m"),  # Month as a zero-padded decimal number. Ex. "09"
    (8, "M", "%-m"),  # Month as a decimal number. (Platform specific) Ex. "9"
    (9,"yyyy", "%Y"),  # Year with century as a decimal number. Ex. "2013"
    (10, "y", "%y"),  # Year without century as a zero-padded decimal number. Ex. "13"
    (11, "HH", "%H"),  # Hour (24-hour clock) as a zero-padded decimal number. Ex. "07"
    (12, "H", "%-H"),  # Hour (24-hour clock) as a decimal number. (Platform specific) Ex. "7"
    (13, "hh", "%I"),  # Hour (12-hour clock) as a zero-padded decimal number. Ex. "07"
    (14, "h", "%-I"),  # Hour (12-hour clock) as a decimal number. (Platform specific) Ex. "7"
    (15, "tt", "%p"),  # Locale’s equivalent of either AM or PM. Ex. "AM"
    (16, "mm", "%M"),  # Minute as a zero-padded decimal number. Ex. "06"
    (17, "m", "%-M"),  # Minute as a decimal number. (Platform specific) Ex. "6"
    (18, "ss", "%S"),  # Second as a zero-padded decimal number. Ex. "05"
    (19, "s", "%-S"),  # Second as a decimal number. (Platform specific) Ex. "5"
    (20, "f", "%f"),  # Microsecond as a decimal number, zero-padded on the left. Ex. "000000"
    (21, "zzz", "%Z"),  # Time zone name (empty string if the object is naive). Ex. ""
    (22, "z", "%z"),  # UTC offset in the form +HHMM or -HHMM (empty string if the the object is naive). Ex. ""
    # "": "%j",  # Day of the year as a zero-padded decimal number. Ex. "273"
    # "": "%-j",  # Day of the year as a decimal number. (Platform specific) Ex. "273"
    # "": "%U",
    # Week number of the year (Sunday as the first day of the week) as a zero padded decimal number. All days in a new year preceding the first Sunday are considered to be in week 0. Ex. "39"
    # "": "%W",
    # Week number of the year (Monday as the first day of the week) as a decimal number. All days in a new year preceding the first Monday are considered to be in week 0. Ex. "39"
    (27, "F", "%c"),  # Locale’s appropriate date and time representation. Ex. "Mon Sep 30 07:06:05 2013"
    (28, "D", "%x"),  # Locale’s appropriate date representation. Ex. "09/30/13"
    (29, "T", "%X"),  # Locale’s appropriate time representation. Ex. "07:06:05"
    (30, "Z", "%Y-%m-%dT%H:%m:%s.%f%z")  # Full ISO-8601
]

_formats_cache = {}

def _get_now():
    """Gets current date, time and local timezone"""
    return datetime.now(tzlocal())


def _get_now_utc():
    """Gets current UTC date and time"""
    return datetime.utcnow()


def now(*args):
    """Gets current date and time."""
    now = _get_now()
    frmt = None
    if len(args) > 0:
        frmt = args[0]
    return _format(now, frmt)

def now_utc(*args):
    """Gets current UTC date and time."""
    now = _get_now_utc()
    frmt = None
    if len(args) > 0:
        frmt = args[0]
    return _format(now, frmt)


def now_add(*args):
    """Adds or subtract Time to """
    result = _add_time(_get_now(), *args) 
    return result


def now_utc_add(*args):
    result = _add_time(_get_now_utc(), *args)
    return result

def _add_time(date, *args):
    result = date
    format = None
    operations = {}
    if len(args) == 0:
        raise AttributeError("now_add: Nothing to add. No parameters were provided.")
    for i in range(0, len(args)):
        if i == len(args) - 1:
            format = args[i]
            break
        else:
            op = args[i].split('=')
            if len(op) < 2:
                raise AttributeError("$.now().add(): Error. invalid attribute")
            value = int(op[1])
            if op[0] not in operations.keys():
                operations[op[0]] = {'uom': op[0], 'value': value, 'add': value >= 0}
            else:
                operations[op[0]]["value"] = operations[op[0]]["value"] + value
    for operation in operations:
        uom = operations[operation]["uom"]
        value = operations[operation]["value"]
        add = operations[operation]["add"]
        if uom == "days":
            if add:
                result = result + timedelta(days=value)
            else:
                result = result - timedelta(days=value)
        elif uom == "weeks":
            if add:
                result = result + timedelta(weeks=value)
            else:
                result = result - timedelta(weeks=value)
        elif uom == "months":
            if add:
                result = result + timedelta(days=value*365/12)
            else:
                result = result - timedelta(days=value*365/12)
        elif uom == "years":
            if add:
                result = result + timedelta(days=value*365)
            else:
                result = result - timedelta(days=value*365)
        elif uom == "hours":
            if add:
                result = result + timedelta(hours=value)
            else:
                result = result - timedelta(hours=value)
        elif uom == "minutes":
            if add:
                result = result + timedelta(minutes=value)
            else:
                result = result - timedelta(minutes=value)
        elif uom == "seconds":
            if add:
                result = result + timedelta(seconds=value)
            else:
                result = result - timedelta(seconds=value)
        elif uom == "quarters":
            raise AttributeError("$.now().add(). Error. Quarters formulas are not supported yet.")
        else:
            raise AttributeError(f"$.now().add(). Error. {uom} is not supported.")
    if format is None:
        return result.isoformat()
    return _format(result, format)


def _format(dt: datetime, format=None):
    """Formats the provided datetime. Default ISO8601+TZ."""
    global _formats_cache
    if format is not None:
        if format not in _formats_cache.keys():
            _formats_cache[format] = _convert_universal_format(format)
        return dt.strftime(_formats_cache[format])
    if dt.utcoffset() is None:
        return dt.isoformat() + "-00:00"
    else:
        return dt.isoformat()


def _convert_universal_format(format):
    """Converts Universal Date Time Format to Python strftime format string"""
    i = 0
    tokens_count = 0
    token_string = format
    python_format = format
    token_map = _DATETIME_FORMAT_MAP
    for f in token_map:
        # Prevents iteration from continuing after all mapped tokens are found.
        # If not evaluated this way logic may replace already mapped tokens like %"d" or %"m", etc...
        if f[1] in token_string:
            #print(f"token_string = {token_string}")
            #print(f"python_format = {python_format}")
            token_string = token_string.replace(f[1], "")
            python_format = python_format.replace(f[1], f[2])
            #print(f"python_format = {python_format} ({f[1]} -> {f[2]})\n")
            del token_map[i]
        i += 1
    return python_format
