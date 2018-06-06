import unittest

from src.safe_coerce import (
    empty_to_none,
    str_to_bool,
    parse_int,
    parse_float,
    zero_to_none,
    parse_date,
    format_date,
    month_partition_date,
    parse_phone_number,
)

class TestUtilityFns(unittest.TestCase):
  def test_empty_to_none(self):
    empty = ''
    empty_arr = '[]'
    null_val = '<null>'
    test_str = 'Not empty   '

    self.assertTrue(empty_to_none(empty) is None)
    self.assertTrue(empty_to_none(empty_arr) is None)
    self.assertTrue(empty_to_none(null_val) is None)
    self.assertEqual(empty_to_none(test_str), 'Not empty')

  def test_str_to_bool(self):
    empty = ''
    true_char = 'T'
    false_char = 'F'
    true = 'True'
    false = 'False'
    yes_val = 'Yes'
    no_val = 'No'

    self.assertTrue(str_to_bool(empty) is None)
    self.assertTrue(str_to_bool(true_char))
    self.assertFalse(str_to_bool(false_char))
    self.assertTrue(str_to_bool(true))
    self.assertFalse(str_to_bool(false))
    self.assertTrue(str_to_bool(yes_val))
    self.assertFalse(str_to_bool(no_val))

  def test_parse_int(self):
    empty = ''
    one = '3.14'

    self.assertTrue(parse_float(empty) is None)
    self.assertTrue(parse_float(one) == 3.14)

  def test_zero_to_none(self):
    value = zero_to_none(parse_int('0000'))
    self.assertTrue(value is None)

    value = zero_to_none(None)
    self.assertTrue(value is None)

    value = zero_to_none('  0')
    self.assertTrue(value is None)

  # TODO: There are more methods to be tested here.
  def test_parse_date(self):
    date_string = '2018-04-30'
    time_string = '2018-05-16T18:30:00+12:00'
    date = parse_date(date_string)
    time_to_date = parse_date(time_string)

    self.assertTrue(date.year == 2018)
    self.assertTrue(date.month == 4)
    self.assertTrue(date.day == 30)

    self.assertTrue(time_to_date.year == 2018)
    self.assertTrue(time_to_date.month == 5)
    self.assertTrue(time_to_date.day == 16)

    # Doesn't fail on `None` (none of the date functions should).
    self.assertTrue(parse_date(None) is None)

  def test_month_partition_date(self):
    date_string = '1987-12-08'
    parsed = parse_date(date_string)
    partition = month_partition_date(parsed)

    self.assertTrue(partition.day == 1)
    self.assertTrue(partition.month == 12)
    self.assertTrue(partition.year == 1987)

  def test_format_date(self):
    date_string = '1987-11-03'
    parsed = parse_date(date_string)
    string = format_date(parsed)

    self.assertTrue(string == date_string)

    # A really dumb error case (these values do occur).
    date_result = parse_date('0117-11-03')
    self.assertTrue(format_date(date_result) is None)

  def test_parse_phone_number(self):
    value = '+61410 892 488'
    parsed = parse_phone_number(value)
    self.assertTrue(parsed == ('0410 892 488', True, 'MOBILE'))

    value = '+61 2 9262 3700'
    parsed = parse_phone_number(value)
    self.assertTrue(parsed == ('(02) 9262 3700', True, 'LANDLINE'))

    value = '(02) 9262 3700'
    parsed = parse_phone_number(value)
    self.assertTrue(parsed == ('(02) 9262 3700', True, 'LANDLINE'))

    # The following are not at all parsable.
    value = 'NOT AT ALL PARSABLE'
    number, is_valid, number_type = parse_phone_number(value)

    self.assertTrue(value == number)
    self.assertTrue(is_valid is False)
    self.assertTrue(number_type is None)

    value = '7000' # NOTE: This will parse - but enum would be 99.
    number, is_valid, number_type = parse_phone_number(value)

    self.assertTrue(value == number)
    self.assertTrue(is_valid is False)
    self.assertTrue(number_type is None)

    value = '1800 CALL GAVIN NOW' # NOTE: This will parse - but enum would be 99.
    number, is_valid, number_type = parse_phone_number(value)

    self.assertTrue(value == number)
    self.assertTrue(is_valid is False)
    self.assertTrue(number_type is None)

    # Safe handling of empty strings or nulls.
    value = None
    number, is_valid, number_type = parse_phone_number(value)

    self.assertTrue(number is None)
    self.assertTrue(is_valid is False)
    self.assertTrue(number_type is None)

    value = ''
    number, is_valid, number_type = parse_phone_number(value)

    self.assertTrue(number is None)
    self.assertTrue(is_valid is False)
    self.assertTrue(number_type is None)

if __name__ == '__main__':
  unittest.main()
