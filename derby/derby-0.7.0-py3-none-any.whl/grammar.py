grammar = """
// based on https://github.com/lark-parser/lark/blob/master/examples/calc.py
?start: comp

?comp: sum ">"  sum  -> gt
     | sum ">=" sum -> gte
     | sum "<"  sum  -> lt
     | sum "<=" sum -> lte
     | sum "="  sum  -> eq
     | sum "!="  sum  -> ne
     | sum

?sum: grab
    | sum "+" grab -> add
 	| sum "-" grab -> sub

?grab: atom
	| grab "l" atom -> low
	| grab "h" atom -> high

?atom: number "d"i number -> dice
     | number

number: INT

%import common.INT
%import common.WS
%ignore WS
"""
