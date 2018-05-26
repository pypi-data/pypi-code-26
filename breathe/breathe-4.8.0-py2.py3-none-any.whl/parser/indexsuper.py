#
# Generated Thu Jun 11 18:43:54 2009 by generateDS.py.
#

import sys
import getopt
from xml.dom import minidom
from xml.dom import Node

#
# User methods
#
# Calls to the methods in these classes are generated by generateDS.py.
# You can replace these methods by re-implementing the following class
#   in a module named generatedssuper.py.

try:
    from generatedssuper import GeneratedsSuper
except ImportError as exp:

    class GeneratedsSuper:
        def format_string(self, input_data, input_name=''):
            return input_data
        def format_integer(self, input_data, input_name=''):
            return '%d' % input_data
        def format_float(self, input_data, input_name=''):
            return '%f' % input_data
        def format_double(self, input_data, input_name=''):
            return '%e' % input_data
        def format_boolean(self, input_data, input_name=''):
            return '%s' % input_data


#
# If you have installed IPython you can uncomment and use the following.
# IPython is available from http://ipython.scipy.org/.
#

## from IPython.Shell import IPShellEmbed
## args = ''
## ipshell = IPShellEmbed(args,
##     banner = 'Dropping into IPython',
##     exit_msg = 'Leaving Interpreter, back to program.')

# Then use the following line where and when you want to drop into the
# IPython shell:
#    ipshell('<some message> -- Entering ipshell.\nHit Ctrl-D to exit')

#
# Globals
#

ExternalEncoding = 'ascii'

#
# Support/utility functions.
#

def showIndent(outfile, level):
    for idx in range(level):
        outfile.write('    ')

def quote_xml(inStr):
    s1 = (isinstance(inStr, basestring) and inStr or
          '%s' % inStr)
    s1 = s1.replace('&', '&amp;')
    s1 = s1.replace('<', '&lt;')
    s1 = s1.replace('>', '&gt;')
    return s1

def quote_attrib(inStr):
    s1 = (isinstance(inStr, basestring) and inStr or
          '%s' % inStr)
    s1 = s1.replace('&', '&amp;')
    s1 = s1.replace('<', '&lt;')
    s1 = s1.replace('>', '&gt;')
    if '"' in s1:
        if "'" in s1:
            s1 = '"%s"' % s1.replace('"', "&quot;")
        else:
            s1 = "'%s'" % s1
    else:
        s1 = '"%s"' % s1
    return s1

def quote_python(inStr):
    s1 = inStr
    if s1.find("'") == -1:
        if s1.find('\n') == -1:
            return "'%s'" % s1
        else:
            return "'''%s'''" % s1
    else:
        if s1.find('"') != -1:
            s1 = s1.replace('"', '\\"')
        if s1.find('\n') == -1:
            return '"%s"' % s1
        else:
            return '"""%s"""' % s1


class MixedContainer:
    # Constants for category:
    CategoryNone = 0
    CategoryText = 1
    CategorySimple = 2
    CategoryComplex = 3
    # Constants for content_type:
    TypeNone = 0
    TypeText = 1
    TypeString = 2
    TypeInteger = 3
    TypeFloat = 4
    TypeDecimal = 5
    TypeDouble = 6
    TypeBoolean = 7
    def __init__(self, category, content_type, name, value):
        self.category = category
        self.content_type = content_type
        self.name = name
        self.value = value
    def getCategory(self):
        return self.category
    def getContenttype(self, content_type):
        return self.content_type
    def getValue(self):
        return self.value
    def getName(self):
        return self.name


class _MemberSpec(object):
    def __init__(self, name='', data_type='', container=0):
        self.name = name
        self.data_type = data_type
        self.container = container
    def set_name(self, name): self.name = name
    def get_name(self): return self.name
    def set_data_type(self, data_type): self.data_type = data_type
    def get_data_type(self): return self.data_type
    def set_container(self, container): self.container = container
    def get_container(self): return self.container


#
# Data representation classes.
#

class DoxygenType(GeneratedsSuper):
    subclass = None
    superclass = None
    def __init__(self, version=None, compound=None):
        self.version = version
        if compound is None:
            self.compound = []
        else:
            self.compound = compound
    def factory(*args_, **kwargs_):
        if DoxygenType.subclass:
            return DoxygenType.subclass(*args_, **kwargs_)
        else:
            return DoxygenType(*args_, **kwargs_)
    factory = staticmethod(factory)
    def get_compound(self): return self.compound
    def set_compound(self, compound): self.compound = compound
    def add_compound(self, value): self.compound.append(value)
    def insert_compound(self, index, value): self.compound[index] = value
    def get_version(self): return self.version
    def set_version(self, version): self.version = version
    def hasContent_(self):
        if (
            self.compound is not None
            ):
            return True
        else:
            return False
    def build(self, node_):
        attrs = node_.attributes
        self.buildAttributes(attrs)
        for child_ in node_.childNodes:
            nodeName_ = child_.nodeName.split(':')[-1]
            self.buildChildren(child_, nodeName_)
    def buildAttributes(self, attrs):
        if attrs.get('version'):
            self.version = attrs.get('version').value
    def buildChildren(self, child_, nodeName_):
        if child_.nodeType == Node.ELEMENT_NODE and \
            nodeName_ == 'compound':
            obj_ = CompoundType.factory()
            obj_.build(child_)
            self.compound.append(obj_)
# end class DoxygenType


class CompoundType(GeneratedsSuper):
    subclass = None
    superclass = None
    def __init__(self, kind=None, refid=None, name=None, member=None):
        self.kind = kind
        self.refid = refid
        self.name = name
        if member is None:
            self.member = []
        else:
            self.member = member
    def factory(*args_, **kwargs_):
        if CompoundType.subclass:
            return CompoundType.subclass(*args_, **kwargs_)
        else:
            return CompoundType(*args_, **kwargs_)
    factory = staticmethod(factory)
    def get_name(self): return self.name
    def set_name(self, name): self.name = name
    def get_member(self): return self.member
    def set_member(self, member): self.member = member
    def add_member(self, value): self.member.append(value)
    def insert_member(self, index, value): self.member[index] = value
    def get_kind(self): return self.kind
    def set_kind(self, kind): self.kind = kind
    def get_refid(self): return self.refid
    def set_refid(self, refid): self.refid = refid
    def build(self, node_):
        attrs = node_.attributes
        self.buildAttributes(attrs)
        for child_ in node_.childNodes:
            nodeName_ = child_.nodeName.split(':')[-1]
            self.buildChildren(child_, nodeName_)
    def buildAttributes(self, attrs):
        if attrs.get('kind'):
            self.kind = attrs.get('kind').value
        if attrs.get('refid'):
            self.refid = attrs.get('refid').value
    def buildChildren(self, child_, nodeName_):
        if child_.nodeType == Node.ELEMENT_NODE and \
            nodeName_ == 'name':
            name_ = ''
            for text__content_ in child_.childNodes:
                name_ += text__content_.nodeValue
            self.name = name_
        elif child_.nodeType == Node.ELEMENT_NODE and \
            nodeName_ == 'member':
            obj_ = MemberType.factory()
            obj_.build(child_)
            self.member.append(obj_)
# end class CompoundType


class MemberType(GeneratedsSuper):
    subclass = None
    superclass = None
    def __init__(self, kind=None, refid=None, name=None):
        self.kind = kind
        self.refid = refid
        self.name = name
    def factory(*args_, **kwargs_):
        if MemberType.subclass:
            return MemberType.subclass(*args_, **kwargs_)
        else:
            return MemberType(*args_, **kwargs_)
    factory = staticmethod(factory)
    def get_name(self): return self.name
    def set_name(self, name): self.name = name
    def get_kind(self): return self.kind
    def set_kind(self, kind): self.kind = kind
    def get_refid(self): return self.refid
    def set_refid(self, refid): self.refid = refid
    def hasContent_(self):
        if (
            self.name is not None
            ):
            return True
        else:
            return False
    def build(self, node_):
        attrs = node_.attributes
        self.buildAttributes(attrs)
        for child_ in node_.childNodes:
            nodeName_ = child_.nodeName.split(':')[-1]
            self.buildChildren(child_, nodeName_)
    def buildAttributes(self, attrs):
        if attrs.get('kind'):
            self.kind = attrs.get('kind').value
        if attrs.get('refid'):
            self.refid = attrs.get('refid').value
    def buildChildren(self, child_, nodeName_):
        if child_.nodeType == Node.ELEMENT_NODE and \
            nodeName_ == 'name':
            name_ = ''
            for text__content_ in child_.childNodes:
                name_ += text__content_.nodeValue
            self.name = name_
# end class MemberType


USAGE_TEXT = """
Usage: python <Parser>.py [ -s ] <in_xml_file>
Options:
    -s        Use the SAX parser, not the minidom parser.
"""

def usage():
    print(USAGE_TEXT)
    sys.exit(1)


def parse(inFileName):
    doc = minidom.parse(inFileName)
    rootNode = doc.documentElement
    rootObj = DoxygenType.factory()
    rootObj.build(rootNode)
    # Enable Python to collect the space used by the DOM.
    doc = None
    sys.stdout.write('<?xml version="1.0" ?>\n')
    rootObj.export(sys.stdout, 0, name_="doxygenindex",
        namespacedef_='')
    return rootObj


def parseString(inString):
    doc = minidom.parseString(inString)
    rootNode = doc.documentElement
    rootObj = DoxygenType.factory()
    rootObj.build(rootNode)
    # Enable Python to collect the space used by the DOM.
    doc = None
    sys.stdout.write('<?xml version="1.0" ?>\n')
    rootObj.export(sys.stdout, 0, name_="doxygenindex",
        namespacedef_='')
    return rootObj


def parseLiteral(inFileName):
    doc = minidom.parse(inFileName)
    rootNode = doc.documentElement
    rootObj = DoxygenType.factory()
    rootObj.build(rootNode)
    # Enable Python to collect the space used by the DOM.
    doc = None
    sys.stdout.write('from index import *\n\n')
    sys.stdout.write('rootObj = doxygenindex(\n')
    rootObj.exportLiteral(sys.stdout, 0, name_="doxygenindex")
    sys.stdout.write(')\n')
    return rootObj


def main():
    args = sys.argv[1:]
    if len(args) == 1:
        parse(args[0])
    else:
        usage()




if __name__ == '__main__':
    main()
    #import pdb
    #pdb.run('main()')
