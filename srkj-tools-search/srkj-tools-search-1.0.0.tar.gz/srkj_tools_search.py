#  !/usr/bin/env  python
#  -*- coding:utf-8 -*-
# @Time   :  2018.
# @Author :  燊荣科技
# @Email  :  41322013@qq.com
# @Blog   :  http://www.srkj.xin
# @Note   :
# def search4vowels():
#     """Display any vowels found in an asked-for word."""
#     vowels = set('aeiou')
#     word = input("请输入内容：")
#     found = vowels.intersection(set(word))
#     for vowel in found:
#         print(vowel)
#
#
# def search4vowels(word):
#     """Display any vowels found in an asked-for word."""
#     vowels = set('aeiou')
#     found = vowels.intersection(set(word))
#     for vowel in found:
#         print(vowel)
#
#
# def search4vowels(word):
#     """Display any vowels found in an asked-for word."""
#     vowels = set('aeiou')
#     found = vowels.intersection(set(word))
#     return bool(found)
#
#
# def search4vowels(word):
#     """Display any vowels found in an asked-for word."""
#     vowels = set('aeiou')
#     found = vowels.intersection(set(word))
#     return found
#
#
# def search4vowels(word):
#     """Display any vowels found in an asked-for word."""
#     vowels = set('aeiou')
#     return vowels.intersection(set(word))
#
#
# def search4vowels(word: str) -> set:
#     """Display any vowels found in an asked-for word."""
#     vowels = set('aeiou')
#     return vowels.intersection(set(word))


def search4vowels(phrase: str) -> set:
    """Display any vowels found in an asked-for word."""
    # vowels = set('aeiou')
    # return vowels.intersection(set(phrase))
    return set('aeiou').intersection(set(phrase))


def search4letters(phrase: str, letters: str = 'aeiou') -> set:
    """Return a set of the 'letters' found in 'phrease'."""
    return set(letters).intersection(set(phrase))


# print(search4letters(letters='xyz', phrase='galaxy'))
