import unittest
from hashlib import md5

from src.higher_order_functions import (
    sequence,
    compose,
    create_keyed_tuple,
    create_tupler,
    untuple_keyed_value,
)

def hash_util(*values):
  value = ''.join(map(str, values))
  hash_val = md5(value).hexdigest()
  return hash_val

class TestHigherOrderFns(unittest.TestCase):
  def test_sequence(self):

    def add_one(value):
      return value + 1

    add_two = sequence(add_one, add_one)
    self.assertTrue(add_two(1) == 3)


  def test_compose(self):

    def create_appender(string):
      def append(value):
        return "{}{}".format(value, string)

      return append

    append_b = create_appender('b')
    append_c = create_appender('c')

    append_all = compose(append_c, append_b)

    result = append_all('a')
    self.assertTrue(result == 'abc')

  def test_keyed_tuple_creation(self):
    record = {'a': 1, 'b': 2}

    # Test creation with string keys.
    tupled = create_keyed_tuple(record, 'a')
    self.assertTrue(tupled == (1, record))

    # Test creation with a function to deduce keys.
    tupled = create_keyed_tuple(record, lambda v: v['a'] + v['b'])
    self.assertTrue(tupled == (3, record))


  def test_create_tupler(self):
    record = {'x': 1, 'y': 2}

    # Using string keys.
    tupler = create_tupler('x')
    self.assertTrue(callable(tupler)) # It's a function.
    self.assertTrue(tupler(record) == (1, record))

    # Functions.
    def key_func(record):
      return hash_util(record['x'], record['y'])

    tupler = create_tupler(key_func)
    tupled = tupler(record)
    self.assertTrue(tupled == ('c20ad4d76fe97759aa27a0c99bff6710', record))


  def test_untuple_keyed_value(self):
    record = ('a', 'b')
    self.assertTrue(untuple_keyed_value(record) == 'b')

    record = (1, (1, (1, 2))) # Nested for the sake of it.
    untupler = sequence(
        untuple_keyed_value,
        untuple_keyed_value,
        untuple_keyed_value)

    self.assertTrue(untupler(record) == 2)



if __name__ == '__main__':
  unittest.main()
