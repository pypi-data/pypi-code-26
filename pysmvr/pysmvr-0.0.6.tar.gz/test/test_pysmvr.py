import unittest
import os
from pysmvr.core import is_valid, parse, increase, decrease, serialize

class BasicTests(unittest.TestCase):

    #
    # is_valid
    #
    def test_is_valid_with_valid_inputs(self):

      with open(os.path.join(os.path.dirname(__file__), 'resources/valid_versions.txt')) as f:
        versions = f.read().splitlines()

      for v in versions:
        self.assertEqual(is_valid(v), True)

    def test_is_valid_with_invalid_inputs(self):

      with open(os.path.join(os.path.dirname(__file__), 'resources/invalid_versions.txt')) as f:
        versions = f.read().splitlines()

      for v in versions:
        self.assertEqual(is_valid(v), False)

    #
    # parse
    #
    def test_parse_basic_version(self):
      input = '1.2.3'
      expected = {'major': 1, 'minor': 2, 'patch': 3, 'prerelease': None, 'tags': []}

      result = parse(input)

      self.assertDictEqual(result, expected)

    def test_parse_version_with_labels(self):
      input = '1.2.3-foo-bar.1'
      expected = {'major': 1, 'minor': 2, 'patch': 3, 'prerelease': 'foo-bar.1', 'tags': ['foo', 'bar.1']}

      result = parse(input)

      self.assertDictEqual(result, expected)

    #
    # increase
    #
    def test_increase_major_version(self):
      input = {'major': 1, 'minor': 2, 'patch': 3, 'prerelease': 'foo-bar.1', 'tags': ['foo', 'bar.1']}
      expected = {'major': 6, 'minor': 2, 'patch': 3, 'prerelease': 'foo-bar.1', 'tags': ['foo', 'bar.1']}

      result = increase(input, 'major', 5)

      self.assertDictEqual(result, expected)

    def test_increase_minor_version(self):
      input = {'major': 1, 'minor': 2, 'patch': 3, 'prerelease': 'foo-bar.1', 'tags': ['foo', 'bar.1']}
      expected = {'major': 1, 'minor': 7, 'patch': 3, 'prerelease': 'foo-bar.1', 'tags': ['foo', 'bar.1']}

      result = increase(input, 'minor', 5)

      self.assertDictEqual(result, expected)

    def test_increase_patch_version(self):
      input = {'major': 1, 'minor': 2, 'patch': 3, 'prerelease': 'foo-bar.1', 'tags': ['foo', 'bar.1']}
      expected = {'major': 1, 'minor': 2, 'patch': 8, 'prerelease': 'foo-bar.1', 'tags': ['foo', 'bar.1']}

      result = increase(input, 'patch', 5)

      self.assertDictEqual(result, expected)

    #
    # decrease
    #
    def test_decrease_major_version(self):
      input = {'major': 10, 'minor': 9, 'patch': 8, 'prerelease': 'foo-bar.1', 'tags': ['foo', 'bar.1']}
      expected = {'major': 5, 'minor': 9, 'patch': 8, 'prerelease': 'foo-bar.1', 'tags': ['foo', 'bar.1']}

      result = decrease(input, 'major', 5)

      self.assertDictEqual(result, expected)

    def test_decrease_minor_version(self):
      input = {'major': 10, 'minor': 9, 'patch': 8, 'prerelease': 'foo-bar.1', 'tags': ['foo', 'bar.1']}
      expected = {'major': 10, 'minor': 4, 'patch': 8, 'prerelease': 'foo-bar.1', 'tags': ['foo', 'bar.1']}

      result = decrease(input, 'minor', 5)

      self.assertDictEqual(result, expected)

    def test_decrease_patch_version(self):
      input = {'major': 10, 'minor': 9, 'patch': 8, 'prerelease': 'foo-bar.1', 'tags': ['foo', 'bar.1']}
      expected = {'major': 10, 'minor': 9, 'patch': 3, 'prerelease': 'foo-bar.1', 'tags': ['foo', 'bar.1']}

      result = decrease(input, 'patch', 5)

      self.assertDictEqual(result, expected)

    #
    # serialize
    #
    def test_serialize(self):
      input = {'major': 1, 'minor': 2, 'patch': 3, 'prerelease': 'foo-bar.1', 'tags': ['foo', 'bar.1']}
      expected = '1.2.3-foo-bar.1'

      result = serialize(input)

      self.assertEqual(result, expected)

if __name__ == "__main__":
    unittest.main()
