# coding=utf-8

import unittest
from core import *

class WhiteBox(unittest.TestCase):
    def test_LineReader(self):
        s = '\
a = b\r\n\
   \t\f\\\r\n\r\n\n\
   \t\fb = b\n\
! c\n\
# c\n\
# c\\\n\
 c = \\\r\n  b\\\\\r\n\
   \td =  \tb\n\
   \te = b\\\
'
        result = [
            'a = b', # normal with flag skipLF
            # skipWhiteSpace flow, escape line terminator, blank line
            'b = b', # leading whitespaces
            # continous comment lines
            # comment can not escape line terminator
            'c = b\\\\', # escape line terminator, even number of '\'
            'd =  \tb', #
            'e = b', # ends with '\'
        ]
        i = 0
        for line in LineReader(s):
            self.assertEquals(result[i], line)
            i += 1
        i = 0
        for line in LineReader([s]):
            self.assertEquals(result[i], line)
            i += 1

    def test_LineReader2(self):
        s = '\
a = b\n\
# c\\\
'
        result = [
            'a = b', # ends with comment line and '\'
        ]
        i = 0
        for line in LineReader(list(s)):
            self.assertEquals(result[i], line)
            i += 1
        i = 0
        for line in LineReader([s]):
            self.assertEquals(result[i], line)
            i += 1

    def test_loadSingle(self):
        self.assertEquals(loadSingle('key value'), ('key', 'value'))
        self.assertEquals(loadSingle(' \t\fkey value'), ('key', 'value'))

    def test_identifyKeyValue(self):
        def test(string, v1, v2):
            result = identifyKeyValue(string)
            self.assertEquals((v1, v2), result, string + ' -> ' + str(result) + ' but except ' + str((v1, v2)))

        # single seperator
        test('key=value', 3, 4)
        test('key:value', 3, 4)
        test('key value', 3, 4)
        test('key\tvalue', 3, 4)
        test('key\fvalue', 3, 4)

        # escaped
        test('key \\=value', 3, 4)
        test('key \\ value', 3, 4)

        # whitespaces around '='
        test('key =value', 3, 5)
        test('key= value', 3, 5)
        test('key  = value', 3, 7)

        # continous whitespaces as seperator
        test('key    value', 3, 7)
        test('key  \t value', 3, 7)

        # special cases
        test('key:=value', 3, 4)
        test('key:= value', 3, 4)

    def test_loadConvert(self):
        self.assertEquals(loadConvert('s'), 's')
        self.assertEquals(loadConvert('\\u005c'), '\\')
        self.assertEquals(loadConvert('\\u4e2d'), u'中')
        self.assertEquals(loadConvert('\\t'), '\t')
        self.assertEquals(loadConvert('\\r'), '\r')
        self.assertEquals(loadConvert('\\n'), '\n')
        self.assertEquals(loadConvert('\\f'), '\f')
        self.assertEquals(loadConvert('\\b'), 'b')
        self.assertEquals(loadConvert('\\a'), 'a')

    def test_storeConvert(self):
        self.assertEquals(storeConvert('\\'), '\\\\')
        self.assertEquals(storeConvert('  '), '\\ \\ ')
        self.assertEquals(storeConvert(' ', False), '\\ ')
        self.assertEquals(storeConvert('  ', False), '\\  ')
        self.assertEquals(storeConvert('\t'), '\\t')
        self.assertEquals(storeConvert('\n'), '\\n')
        self.assertEquals(storeConvert('\r'), '\\r')
        self.assertEquals(storeConvert('\f'), '\\f')
        self.assertEquals(storeConvert('='), '\\=')
        self.assertEquals(storeConvert(':'), '\\:')
        self.assertEquals(storeConvert('#'), '\\#')
        self.assertEquals(storeConvert('!'), '\\!')
        self.assertEquals(storeConvert(u'\u0019'), '\\u0019')
        self.assertEquals(storeConvert(u'\u00ff'), '\\u00ff')
        self.assertEquals(storeConvert(u'\u00ff', escapeUnicode=False), u'\xff')
        self.assertEquals(storeConvert(u'\u2eff', escapeUnicode=False), u'\u2eff')
        self.assertEquals(storeConvert(u'中'), '\\u4e2d')

    def test_storeComments(self):
        import os
        ls = os.linesep
        class Writer():
            def __init__(self):
                self.buf = ''
            def write(self, s):
                self.buf += s
        def test(string, *args):
            w = Writer()
            storeComments(w, string)
            lines = list(args)
            lines.append('')
            self.assertEquals(w.buf, ls.join(lines))
        test('a', '#a')
        test(u'\u4e2d', '#\\u4e2d')
        test('\r', '#', '#')
        test('\n', '#', '#')
        test('\r\n', '#', '#')
        test('\r\n#', '#', '#')
        test('\r\n!', '#', '!')
        test('\r\n #', '#', '# #')

if __name__ == '__main__':
    unittest.main()
