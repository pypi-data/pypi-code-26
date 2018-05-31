import re
from datetime import datetime

import phonenumbers

DATE_FORMAT = '%Y-%m-%d'
COUNTRY_CODE_AU = 'AU'

bool_mapping = {
    'true': True,
    't': True,
    'yes': True,
    'false': False,
    'f': False,
    'no': False
}

def str_to_bool(value):
  """Typical values of boolean columns contained in bool_mapping"""
  normalized = value.strip().lower()
  return bool_mapping.get(normalized, None)

def empty_to_none(value):
  """Empty strings need to be coerced"""
  stripped = value.strip()
  if stripped == '' or stripped == '[]' or stripped == '<null>':
    return None
  return stripped


def zero_to_none(value):
  """Nulls make more sense for some columns than zeros."""
  if value is None or value == 0 or (isinstance(value, basestring) and value.strip() == '0'):
    return None
  return value


def create_safe_number_parser(func):

  def parser(value):
    """Safely parse a float."""
    value = empty_to_none(value)
    if value is None:
      return None
    value = re.sub(r'[^\d.-]', '', value)
    return func(value)

  return parser


parse_float = create_safe_number_parser(float)
parse_int = create_safe_number_parser(float)


def parse_date(value):
  """Parse dates that present the raw data."""
  chars = r'[a-zA-Z]'
  if value is None:
    return None

  if re.search(chars, value):
    value = re.split(chars, value)[0]

  return datetime.strptime(value.strip(), DATE_FORMAT)


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
NUMBER_TYPE_LOOKUP = [LANDLINE, MOBILE, LANDLINE_MOBILE]

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
  number_type = NUMBER_TYPE_LOOKUP[number_type_enum]

  return (
      formatted,
      is_valid,
      number_type,
  )
