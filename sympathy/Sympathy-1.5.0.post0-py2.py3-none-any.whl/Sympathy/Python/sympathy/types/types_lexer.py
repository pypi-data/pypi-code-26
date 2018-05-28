# types_lexer.py. This file automatically created by PLY (version 3.11). Don't edit!
_tabversion   = '3.10'
_lextokens    = set(('ALIAS', 'ARROW', 'COLON', 'COMMA', 'EOL', 'EQUALS', 'IDENTIFIER', 'LABRACKET', 'LBRACE', 'LBRACKET', 'LPAREN', 'RABRACKET', 'RBRACE', 'RBRACKET', 'RPAREN', 'TABLE', 'TEXT'))
_lexreflags   = 64
_lexliterals  = ''
_lexstateinfo = {'INITIAL': 'inclusive'}
_lexstatere   = {'INITIAL': [('(?P<t_IDENTIFIER>[A-Za-z][A-Za-z0-9-_]*)|(?P<t_EOL>[\\n\\r]+)|(?P<t_LPAREN>\\()|(?P<t_RPAREN>\\))|(?P<t_LBRACKET>\\[)|(?P<t_RBRACKET>\\])|(?P<t_LBRACE>\\{)|(?P<t_RBRACE>\\})|(?P<t_ARROW>->)|(?P<t_EQUALS>=)|(?P<t_LABRACKET><)|(?P<t_RABRACKET>>)|(?P<t_COLON>:)|(?P<t_COMMA>,)', [None, ('t_IDENTIFIER', 'IDENTIFIER'), (None, 'EOL'), (None, 'LPAREN'), (None, 'RPAREN'), (None, 'LBRACKET'), (None, 'RBRACKET'), (None, 'LBRACE'), (None, 'RBRACE'), (None, 'ARROW'), (None, 'EQUALS'), (None, 'LABRACKET'), (None, 'RABRACKET'), (None, 'COLON'), (None, 'COMMA')])]}
_lexstateignore = {'INITIAL': ' '}
_lexstateerrorf = {'INITIAL': 't_error'}
_lexstateeoff = {}
