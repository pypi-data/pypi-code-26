from .grammar import grammar
from .parser import parser
from .expr import dice_expr
from .dice import Dice

def roll(query):
    return parser.parse(query)

__all__ = ['parser']