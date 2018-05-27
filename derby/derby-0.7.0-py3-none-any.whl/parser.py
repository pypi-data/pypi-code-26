from lark import Lark, InlineTransformer, inline_args
from . import grammar
from . expr import *

class DerbyTransformer(InlineTransformer):
    gt =  lambda t, l, r: (l >  r, l, r)
    lt =  lambda t, l, r: (l <  r, l, r)
    gte = lambda t, l, r: (l >= r, l, r)
    lte = lambda t, l, r: (l <= r, l, r)
    eq =  lambda t, l, r: (l == r, l, r)
    ne =  lambda t, l, r: (l != r, l, r)
    
    low = low_expr
    high = high_expr
    add = add_expr
    sub = sub_expr
    dice = dice_expr
    number = int

parser = Lark(grammar, parser='lalr', transformer=DerbyTransformer())