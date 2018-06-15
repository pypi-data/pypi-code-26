import nose
import sys


def textangle(length=0x200, ch='*'):
    output = ''
    max_length = 80

    if length < max_length:
        length = max_length

    count = 0
    for x in range(length):
        if count < max_length:
            output += ch
        else:
            count = 0
            output += '\n'
            continue

        count += len(ch)

    return output


def test_long_exception_traceback():
    output = textangle()
    raise ValueError(output)


def test_long_exception_stdout_traceback():
    output = textangle()
    output_tty = textangle(ch='_STDOUT_')
    print(output_tty)
    raise ValueError(output)


def test_exception_traceback():
    raise ValueError('I recieved the wrong value. Le whoops.')


def test_exception_failure_ignore_tra():
    assert 1 == 0, 'This should not be in the tra_exception field'


def test_exception_failure_ignore_tra_stdout():
    print('This should not be in the tra_exception field')
    assert 1 == 0, 'Nor should this be in the tra_exception field'


def test_passes():
    assert 0 == 0, 'Zero is not zero. Interesting.'
