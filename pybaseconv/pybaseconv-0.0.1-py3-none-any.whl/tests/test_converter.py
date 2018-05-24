from pybaseconv.converter import Converter, BASE
from unittest import TestCase


class TestConverter(TestCase):

    def test_construct_converter_with_empty_alphabet_expect_excpetion(self):
        with self.assertRaises(Exception):
            Converter('', BASE.BIN)

    def test_dec_input_contains_character_from_hex_expect_exception(self):
        input = '32ff'

        converter = Converter(BASE.DEC, BASE.BIN)

        with self.assertRaises(Exception):
            converter.convert(input)

    def test_dec_to_dec_returns_same_number(self):
        number = '42'

        converter = Converter(BASE.DEC, BASE.DEC)
        self.assertEqual(number, converter.convert(number))

    def test_dec_to_bin_and_bin_to_dec_return_the_expected_result(self):
        number_to_convert = '42'
        expected_result = '{0:b}'.format(42)

        # test dec to bin
        converter = Converter(BASE.DEC, BASE.BIN)
        self.assertEqual(expected_result, converter.convert(number_to_convert))

        # test bin to dec
        converter = Converter(BASE.BIN, BASE.DEC)
        self.assertEqual(number_to_convert, converter.convert(expected_result))

    def test_dec_to_hex_and_dec_to_hex_return_the_expected_result(self):
        number_to_convert = '100'
        expected_result = '{0:x}'.format(100)

        # test dec to hex
        converter = Converter(BASE.DEC, BASE.HEX)
        self.assertEqual(expected_result, converter.convert(number_to_convert))

        # test hex to dec
        converter = Converter(BASE.HEX, BASE.DEC)
        self.assertEqual(number_to_convert, converter.convert(expected_result))

    def test_dec_to_oct_and_oct_dec_return_the_expected_result(self):
        number_to_convert = '677'
        expected_result = '{0:o}'.format(677)

        # test dec to oct
        converter = Converter(BASE.DEC, BASE.OCT)
        self.assertEqual(expected_result, converter.convert(number_to_convert))

        # test oct to dec
        converter = Converter(BASE.OCT, BASE.DEC)
        self.assertEqual(number_to_convert, converter.convert(expected_result))

    def test_dec_to_fb58_and_fb58_to_dec_return_the_expected_result(self):
        number_to_convert = '839372'
        expected_result = '5ivW'

        # test dec to flicker base58
        converter = Converter(BASE.DEC, BASE.FLICKER_BASE_58)
        self.assertEqual(expected_result, converter.convert(number_to_convert))

        # test flicker base58 to dec
        converter = Converter(BASE.FLICKER_BASE_58, BASE.DEC)
        self.assertEqual(number_to_convert, converter.convert(expected_result))

    def test_bin_to_oct_and_oct_to_bin_return_the_expected_result(self):
        number_to_convert = '1100010100'
        expected_result = '{0:o}'.format(int(number_to_convert, 2))

        converter = Converter(BASE.BIN, BASE.OCT)
        self.assertEqual(expected_result, converter.convert(number_to_convert))

        converter = Converter(BASE.OCT, BASE.BIN)
        self.assertEqual(number_to_convert, converter.convert(expected_result))

    def test_bin_to_hex_and_hex_to_bin_return_the_expected_result(self):
        number_to_convert = '1100010100'
        expected_result = '{0:x}'.format(int(number_to_convert, 2))

        converter = Converter(BASE.BIN, BASE.HEX)
        self.assertEqual(expected_result, converter.convert(number_to_convert))

        converter = Converter(BASE.HEX, BASE.BIN)
        self.assertEqual(number_to_convert, converter.convert(expected_result))

    def test_bin_to_fb58_and_fb58_to_bin_return_the_expected(self):
        number_to_convert = '1100010100'
        expected_result = 'eA'

        converter = Converter(BASE.BIN, BASE.FLICKER_BASE_58)
        self.assertEqual(expected_result, converter.convert(number_to_convert))

        converter = Converter(BASE.FLICKER_BASE_58, BASE.BIN)
        self.assertEqual(number_to_convert, converter.convert(expected_result))

    def test_hex_to_fb58_and_fb58_to_hex_return_the_expected_result(self):
        number_to_convert = '7f886550a'
        expected_result = 'UaaRTy'

        converter = Converter(BASE.HEX, BASE.FLICKER_BASE_58)
        self.assertEqual(expected_result, converter.convert(number_to_convert))

        converter = Converter(BASE.FLICKER_BASE_58, BASE.HEX)
        self.assertEqual(number_to_convert, converter.convert(expected_result))

    def test_hex_to_oct_and_oct_to_hex_return_the_expected_result(self):
        number_to_convert = '7f886550a'
        expected_result = '377041452412'

        converter = Converter(BASE.HEX, BASE.OCT)
        self.assertEqual(expected_result, converter.convert(number_to_convert))

        converter = Converter(BASE.OCT, BASE.HEX)
        self.assertEqual(number_to_convert, converter.convert(expected_result))

    def test_oct_to_fb58_and_fb58_to_oct_return_the_expected_result(self):
        number_to_convert = '313040757'
        expected_result = '5GQ42'

        converter = Converter(BASE.OCT, BASE.FLICKER_BASE_58)
        self.assertEqual(expected_result, converter.convert(number_to_convert))

        converter = Converter(BASE.FLICKER_BASE_58, BASE.OCT)
        self.assertEqual(number_to_convert, converter.convert(expected_result))
