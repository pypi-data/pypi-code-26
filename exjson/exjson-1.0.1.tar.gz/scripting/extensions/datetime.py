from datetime import datetime, timedelta

from dateutil.tz import tzlocal

def get_week(date: datetime.date):
    return date.isocalendar()[1]

def get_week_padded(date: datetime.date):
    return str(get_week(date)).zfill(2)

def get_quarter(date:datetime.date):
    return ((date.month-1)//3)+1

def get_quarter_padded(date:datetime.date):
    return str(get_quarter(date)).zfill(2)


_DATETIME_FORMAT_MAP = [
    ("dddd", "%A", None),  # Weekday as locale’s full name. Ex. "Monday"
    ("ddd", "%a", None),  # Weekday as locale’s abbreviated name. Ex. "Mon"
    ("w", None, get_week), # Weekday as a decimal number, where 0 is Sunday and 6 is Saturday. Ex. "1"
    ("ww", None, get_week_padded), # Weekday as zero padded number
    ("dd", "%d", None),  # Day of the month as a zero-padded decimal number. Ex. "30"
    ("d", "%-d", None),  # Day of the month as a decimal number. (Platform specific) Ex. "30"
    ("MMMM", "%B", None),  # Month as locale’s full name. Ex. "September"
    ("MMM", "%b", None),  # Month as locale’s abbreviated name. Ex. "Sep"
    ("MM", "%m", None),  # Month as a zero-padded decimal number. Ex. "09"
    ("M", "%-m", None),  # Month as a decimal number. (Platform specific) Ex. "9"
    ("yyyy", "%Y", None),  # Year with century as a decimal number. Ex. "2013"
    ("y", "%y", None),  # Year without century as a zero-padded decimal number. Ex. "13"
    ("HH", "%H", None),  # Hour (24-hour clock) as a zero-padded decimal number. Ex. "07"
    ("H", "%-H", None),  # Hour (24-hour clock) as a decimal number. (Platform specific) Ex. "7"
    ("hh", "%I", None),  # Hour (12-hour clock) as a zero-padded decimal number. Ex. "07"
    ("h", "%-I", None),  # Hour (12-hour clock) as a decimal number. (Platform specific) Ex. "7"
    ("tt", "%p", None),  # Locale’s equivalent of either AM or PM. Ex. "AM"
    ("mm", "%M", None),  # Minute as a zero-padded decimal number. Ex. "06"
    ("m", "%-M", None),  # Minute as a decimal number. (Platform specific) Ex. "6"
    ("ss", "%S", None),  # Second as a zero-padded decimal number. Ex. "05"
    ("s", "%-S", None),  # Second as a decimal number. (Platform specific) Ex. "5"
    ("f", "%f", None),  # Microsecond as a decimal number, zero-padded on the left. Ex. "000000"
    ("zzz", "%Z", None),  # Time zone name (empty string if the object is naive). Ex. ""
    ("z", "%z", None),  # UTC offset in the form +HHMM or -HHMM (empty string if the the object is naive). Ex. ""
    ("j", "%j", None),  # Day of the year as a zero-padded decimal number. Ex. "273"
    ("jj", "%-j", None),  # Day of the year as a decimal number. (Platform specific) Ex. "273",
    ("qq", None, get_quarter_padded), # Calendar Year quarter as padded number
    ("q", None, get_quarter), # Calendar Year quarter as integer
    ("F", "%c", None),  # Locale’s appropriate date and time representation. Ex. "Mon Sep 30 07:06:05 2013"
    ("D", "%x", None),  # Locale’s appropriate date representation. Ex. "09/30/13"
    ("T", "%X", None),  # Locale’s appropriate time representation. Ex. "07:06:05"
    ("Z", "%Y-%m-%dT%H:%m:%s.%f%z", None)  # Full ISO-8601
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
        result = dt.strftime(_formats_cache[format][0])
        if _formats_cache[format][1] is not None:
            for token in _formats_cache[format][1]:
                result = result.replace(token, str(_formats_cache[format][1][token](dt)))
        return result
    if dt.utcoffset() is None:
        return dt.isoformat() + "-00:00"
    else:
        return dt.isoformat()


def _convert_universal_format(format):
    """Converts Universal Date Time Format to Python strftime format string"""
    i = 0
    token_string = format
    python_format = format
    token_map = sorted(_DATETIME_FORMAT_MAP, key=lambda t: t[0], reverse=True)
    calculated_tokens = {}
    for f in token_map:
        if f[0] in token_string:
            if f[1] is None and f[2] is not None and hasattr(f[2], '__call__'):
                if f[0] not in calculated_tokens.keys():
                    calculated_tokens[f[0]] = f[2]
            else:
                token_string = token_string.replace(f[0], "")
                python_format = python_format.replace(f[0], f[1])
            del token_map[i]
        i += 1
    return (python_format, calculated_tokens)
