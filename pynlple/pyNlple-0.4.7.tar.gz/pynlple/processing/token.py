# -*- coding: utf-8 -*-
import re


def has_capital_letter(token):
    return any(l.isupper() for l in token)


def first_capital_letter(token):
    return len(token) > 0 and token[0].isupper()


def only_first_capital_letter(token):
    return first_capital_letter(token) and not has_capital_letter(token[1:])


def has_not_first_capital_letter(token):
    return not first_capital_letter(token) and has_capital_letter(token[1:])


def one_capital_letter(token):
    return sum(l.isupper() for l in token) == 1


def more_than_one_capital_letter(token):
    return sum(l.isupper() for l in token) > 1


def all_capital(token):
    return token.isupper()


def all_lower(token):
    return token.islower()


newline_pattern = re.compile(r'\r\n?')
def is_newline(token):
    return newline_pattern.fullmatch(token) is not None


multidot_pattern = re.compile(r'\.\.+')
def is_multiple_dot(token):
    return multidot_pattern.fullmatch(token) is not None


digital_sequence_pattern = re.compile(r'^[\.]?[\d][\d\.,\-:]*$')
def is_a_digital_sequence(token):
    return digital_sequence_pattern.fullmatch(token) is not None