#-- powertools.yaml

'''
process yaml files
'''

from powertools import AutoLogger
log = AutoLogger()
from powertools.print import rprint
from powertools import term

from collections import OrderedDict
from collections import namedtuple
from collections import defaultdict
from pathlib import Path
from functools import partial


#----------------------------------------------------------------------------------------------#
### YAML Anchors, references, nested values    - https://gist.github.com/bowsersenior/979804

import ruamel.yaml as yaml
try :
    from ruamel.yaml import CLoader as Loader, CDumper as Dumper
except ImportError :
    from ruamel.yaml import Loader, Dumper
import sys

yaml.representer.RoundTripRepresenter.add_representer(
    OrderedDict,
    yaml.representer.RoundTripRepresenter.represent_ordereddict )

from ruamel.yaml.comments import CommentedMap

from ruamel.yaml import dump as yaml_dump



#----------------------------------------------------------------------------------------------#
### Customized YAML loading to avoid some issues with ruamel.yaml

### OrderedDictYYAMLLoader - https://gist.github.com/enaeseth/844388
class OrderedDictYAMLLoader(  Loader ) :
    """
    A YAML loader that loads mappings into ordered dictionaries.
    """

    def __init__( self, *args, **kwargs ) :
        Loader.__init__( self, *args, **kwargs )

        self.add_constructor( u'tag:yaml.org,2002:map', type( self ).construct_yaml_map )
        self.add_constructor( u'tag:yaml.org,2002:omap', type( self ).construct_yaml_map )

    def construct_yaml_map( self, node ) :
        data = CommentedMap( )
        yield data
        value = self.construct_mapping( node )
        data.update( value )

    def construct_mapping( self, node, deep=False ) :
        if isinstance( node, yaml.MappingNode ) :
            self.flatten_mapping( node )
        else :
            raise yaml.constructor.ConstructorError(
                None, None,
                'expected a mapping node, but found %s' % node.id,
                node.start_mark )

        mapping = CommentedMap( )
        for key_node, value_node in node.value :
            key = self.construct_object( key_node, deep=deep )
            try :
                hash( key )
            except TypeError as exc :
                raise yaml.constructor.ConstructorError( 'while constructing a mapping',
                                                         node.start_mark, 'found unacceptable key (%s)' % exc,
                                                         key_node.start_mark )
            value = self.construct_object( value_node, deep=deep )
            mapping[key] = value
        return mapping


#----------------------------------------------------------------------------------------------#
#### YAML Transformer

import re
split_fields = re.compile(
r"""
    (?P<indent>\s*)
    (?P<dash>-?\s*)
    (?P<key>[^\s]*)\s?
    (?P<value>[^\s]*)
""", re.VERBOSE)

class LineFields(namedtuple('LineFields', ['indent', 'dash', 'key', 'value'])):
    rank        = property( lambda self: len( self.indent ) + len( self.dash ) )
    min_padding = property( lambda self: self.rank + len( self.key ) + 2 )

COMMENT_BAR = '################################################################################################\n'

noop = lambda s:s

match_dot = re.compile('^(\.)(.*)')
def _value_color(s):
    m = match_dot.match(s)
    if m is not None:
        a = m.group(1)
        b = m.group(2)
        return term.red(a) + term.dyellow(b)
    else:
        return term.dyellow(s)

##############################
def alignment_and_breaks( yaml_output:str, color=False ):
    '''
        align key-values in mappings at the same depth,
        add line breaks between
        if color=True, add ansi terminal codes
    '''

    ### switch colors on or off
    dash_color      = noop
    key_color       = noop
    value_color     = noop
    section_color   = noop
    if color:
        dash_color      = term.cyan
        section_color   = term.white
        # key_color       = term.dwhite
        value_color     = _value_color

    ### parse
    lines = list()
    for line in yaml_output.splitlines(True):
        m       = split_fields.match(line)
        lf = LineFields(
            m.group('indent'),
            m.group('dash'),
            m.group('key'),
            m.group('value')
        )
        lines.append(lf)

    ### find padding: max of mins
    rankpadding     = defaultdict(int)
    flines          = list()
    for line in lines:
        line:LineFields
        null_value  = len(line.value) == 0
        is_list     = len(line.dash)  >  0

        ### count terminal codes in the padding
        dash        = dash_color(line.dash)
        if is_list and null_value:
            key     = value_color(line.key)
            value   = line.value
        elif null_value:
            key     = section_color(line.key)
            value   = line.value
        else:
            key     = key_color(line.key)
            value   = value_color(line.value)

        newline     = LineFields(line.indent, dash, key, value)
        flines.append(newline)

        ### update
        if not is_list \
        and not null_value \
        and rankpadding[line.rank] < newline.min_padding:
            rankpadding[line.rank] = newline.min_padding


    # log.info('max_len:')
    # rprint(padding)

    ### reconstruct
    result      = COMMENT_BAR
    prevline    = LineFields(' ','','','')
    header_keys = [f'{k}:' for k in ['__name__', '__version__', '__protocol__']]

    for fline, line in zip(flines, lines):
        line:LineFields

        empty_line  = '\n' if any(case(line, prevline)    # todo: make this pluggable
            for case in [
                lambda l, p: p.rank > l.rank,
                lambda l, p: p.key.startswith('~') and len(l.dash) > 0,
                lambda l, p: p.key in header_keys and l.key not in header_keys,
            ]
        )        else ''

        padding     = rankpadding[line.rank]
        left        = fline.indent + fline.dash + fline.key
        padded_line = f'{left:<{padding}} {fline.value}'
        result     += f'{empty_line}{padded_line}\n'

        prevline = line
        # lens        = LineFields(*(len(v) for v in line))
        # log.info(f'{line.indent_len:>3} {line.padding:>3} {padding[line.indent_len]:>3} {lens} {line}')
        # log.info('') if empty_line == '\n' else None

    result += '\n\n' + COMMENT_BAR
    return result


#----------------------------------------------------------------------------------------------#

##############################
def load( filename:Path ) :
    result = None
    with filename.open( ) as file:
        result = yaml.load(file, Loader=OrderedDictYAMLLoader )
        # result = yaml.load(file, Loader=yaml.RoundTripLoader )  # todo: fix issues with RoundTripLoader

    return result


##############################

yml                     = yaml.YAML()
yml.explicit_start      = False
yml.indent              = 2
yml.block_seq_indent    = 0
yml.typ                 = 'safe'
yml.tags                = False

def dump( filepath: Path, data ) :
    ''' write YAML to filepath'''
    with open( str(filepath), 'w' ) as file :
        yml.dump( data, file, transform = alignment_and_breaks )
        # yml.dump( data, file )


import io
def yformat( data, color=True ) :
    ''' format YAML for printing to terminal '''

    f = io.StringIO()
    yml.dump( data, f, transform = partial(alignment_and_breaks, color=True) )
    # yml.dump( data, f )
    return f.getvalue()


#----------------------------------------------------------------------------------------------#
