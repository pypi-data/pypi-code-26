import re
from datetime import datetime
import phonenumbers


COUNTRY_CODE_AU = 'AU'
COUNTRY_CODE_NZ = 'NZ'


bool_mapping = {
    'true': True,
    'false': False,
    't': True,
    'f': False,
    'yes': True,
    'no': False,
    '1': True,
    '0': False,
}

def str_to_bool(value):
  """Handles coersion of most of the common encodings of boolean values as as
  strings. Various bits of common software will encode `True|False` as `1|0`
  and `yes|no`."""
  normalized = value.strip().lower()
  return bool_mapping.get(normalized, None)

# QUESTION: Should we really be converting empty JS arrays to `None`?
nullish = [
    '[]',
    '<null>',
    '_un_',
]

def safe_unicode(value):
  return unicode(value, errors='ignore')

def empty_to_none(value):
  """Empty strings are necessarily used as the encoding of `None` in DSV and
  various other formats, but together with this, some software (like stupid
  JetBrains tooling) can insert values like '<null>'."""
  normalized = value.strip().lower()
  if normalized == '':
    return None
  if normalized in nullish:
    return None
  return value


def zero_to_none(value):
  """Nulls make more sense for some columns than zeros."""
  if value == 0 or (isinstance(value, basestring) and value.strip() == '0'):
    return None
  return value


def create_safe_number_parser(func):

  def parser(value):
    """Safely parse a float or int."""
    value = empty_to_none(value)
    if value is None:
      return None
    value = re.sub(r'[^\d.-]', '', value)
    if value == '':
      return None
    return func(value)

  return parser


parse_float = create_safe_number_parser(float)
parse_int = create_safe_number_parser(float)


DATE_FORMAT = '%Y-%m-%d'

# TODO: If we're using a regex we should be able to support many types...
# such as `20180201`, `2018-02-01` and `2018/02/01` - and we can just
# construct a new date after matching. `datetime.date(year, month , day)`
def parse_date(value):
  """Parses things resmbling or intended to be dates, and encoded as strings.
  This entails cleaning up various formats of timestamps / datastamps, or
  recognising a value as being invalid."""
  date_re = r'\d{4}-?\d{2}-?\d{2}'
  if value is None:
    return None
  match = re.search(date_re, value)
  if match is None:
    return None
  return datetime.strptime(match.group(), DATE_FORMAT)


def format_date(value):
  """Format dates present in the raw data. Not sure we need this... BQ supports
  python datetime objects."""
  if value is None:
    return None
  if value.year < 1900:
    return None  # WTF... python can't format years before 1900!
  return datetime.strftime(value, DATE_FORMAT)


def month_partition_date(value):
  """Tables are partitioned by some date... this sets that partition.
  NOTE: BQ currently only support partitioning by a day."""
  if value is None:
    return None
  return datetime.replace(value, day=1)

LANDLINE = 'LANDLINE'
MOBILE = 'MOBILE'
LANDLINE_MOBILE = 'LANDLINE/MOBILE'
TOLL_FREE = 'TOLL FREE'
PREMIUM_RATE = 'PREMIUM RATE'
SHARED_COST = 'SHARED COST'
VOIP = 'VOIP'
PERSONAL_NUMBER = 'PERSONAL NUMBER'
PAGER = 'PAGER'
UAN = 'UAN'
VOICEMAIL = 'VOICEMAIL'
UNKOWN = 'UNKNOWN'
INVALID = 'INVALID'

NUMBER_TYPE_LOOKUP = [
    LANDLINE, MOBILE,
    LANDLINE_MOBILE,
    TOLL_FREE,
    PREMIUM_RATE,
    SHARED_COST,
    VOIP,
    PERSONAL_NUMBER,
    PAGER,
    UAN,
    VOICEMAIL
]

def parse_phone_number(value, code=COUNTRY_CODE_AU):
  """Parse a phone number - defaulting to aus country code
  SEE: https://pypi.org/project/phonenumberslite/
  SEE: https://github.com/daviddrysdale/python-phonenumbers"""
  # TODO: Catch invalid errors.
  if value is None or value == '':
    return (None, False, None)

  try:
    number = phonenumbers.parse(value, code)
  except phonenumbers.NumberParseException:
    return (value, False, None)

  # Not a possible number - but didn't throw.
  if not phonenumbers.is_possible_number(number):
    return (value, False, None)

  formatted = phonenumbers.format_number(number, phonenumbers.PhoneNumberFormat.NATIONAL)
  is_valid = phonenumbers.is_valid_number(number)

  number_type_enum = phonenumbers.number_type(number)
  if number_type_enum == 99:
    number_type = UNKOWN
  else:
    number_type = NUMBER_TYPE_LOOKUP[number_type_enum]

  return (
      formatted,
      is_valid,
      number_type,
  )

# SEE: Issue #1.
def recordf_phone_number(value, region=COUNTRY_CODE_AU):
  """Parse a phone number into the deterministic format, as a record, and
  include the national prefix."""

  fallback_prefix = phonenumbers.country_code_for_region(region)

  if value is None or value == '':
    return {
        "prefix": fallback_prefix,
        "number": None,
        "type": INVALID,
    }

  try:
    number = phonenumbers.parse(value, region=region)
  except phonenumbers.NumberParseException:
    return {
        "prefix": fallback_prefix,
        "number": value,
        "type": INVALID,
    }

  # Not a possible number - but didn't throw.
  if not phonenumbers.is_possible_number(number):
    return {
        "prefix": fallback_prefix,
        "number": value,
        "type": INVALID,
    }

  formatted = phonenumbers.format_number(
      number,
      phonenumbers.PhoneNumberFormat.NATIONAL)

  number_type_enum = phonenumbers.number_type(number)

  prefix = phonenumbers.country_code_for_region(
      phonenumbers.region_code_for_number(number))

  if prefix == 0 and region is not None:
    prefix = phonenumbers.country_code_for_region(region)

  if number_type_enum == 99:
    number_type = UNKOWN
  else:
    number_type = NUMBER_TYPE_LOOKUP[number_type_enum]

  return {
      "prefix": prefix,
      "number": formatted,
      "type": number_type,
  }
