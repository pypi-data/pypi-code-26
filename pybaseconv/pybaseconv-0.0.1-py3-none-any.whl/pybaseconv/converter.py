from abc import ABC


class BASE(ABC):
    """
    List of supported bases
    """
    BIN = '01'
    OCT = '01234567'
    DEC = '0123456789'
    HEX = '0123456789abcdef'
    FLICKER_BASE_58 = '123456789abcdefghijkmnopqrstuvwxyz' \
                      'ABCDEFGHJKLMNPQRSTUVWXYZ'
    BITCOIN_BASE_58 = '123456789ABCDEFGHJKLMNPQRSTUVWXYZa' \
                      'bcdefghijkmnopqrstuvwxyz'


class Converter(object):

    @property
    def src_base(self):
        return self._src_base

    @property
    def dest_base(self):
        return self._dest_base

    def __init__(self, src_base: str, dest_base: str):
        if '' == src_base or '' == dest_base:
            raise Exception('Invalid base')

        self._src_base = src_base
        self._dest_base = dest_base

    def _is_valid(self, number: str) -> bool:
        """
        checks whether the number is valid,
        i.e all its digits are in the source base
        :param number: the number to check
        :return: is number valid or not
        """
        for i in number:
            try:
                self.src_base.index(i)
            except ValueError:
                return False
        return True

    def convert(self, number: str) -> str:
        """
        convert the given number from the source base to destination one
        :param number: the number to convert
        :return: the representation of the number in the destination base
        """

        if not self._is_valid(number):
            raise Exception(
                'this number contains digits which do not belong to '
                'the source base {}'.format(self.src_base))

        # if the bases are the same, no need to convert
        if self.src_base == self.dest_base:
            return number

        src_base_length = len(self.src_base)
        dest_base_length = len(self.dest_base)
        number_length = len(number)
        output = ''

        # map each digit position in number to its position in the source base
        number_map = {i: self.src_base.index(c) for i, c in enumerate(number)}

        while True:
            divide = 0
            new_length = 0

            for i in range(number_length):
                divide = divide * src_base_length + number_map[i]
                if divide >= dest_base_length:
                    number_map[new_length] = divide // dest_base_length
                    new_length += 1
                    divide = divide % dest_base_length
                elif new_length > 0:
                    number_map[new_length] = 0
                    new_length += 1

            number_length = new_length
            output = self.dest_base[divide] + output

            if new_length == 0:
                break

        return output
