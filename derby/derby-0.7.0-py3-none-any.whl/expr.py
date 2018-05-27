from heapq import nsmallest, nlargest
from random import randint
from .dice import Dice

def dice_expr(t, times, size):
    return Dice(f'{times}d{size}', [randint(1, size) for _ in range(times)])

def low_expr(t, dice, value):
    return Dice(dice.expr+f'l{value}', nsmallest(value, dice.dice), dice.history)

def high_expr(t, dice, value):
    return Dice(dice.expr+f'h{value}', nlargest(value, dice.dice), dice.history)

def sub_expr(t, dice, value):
    if isinstance(value, Dice):
        return Dice(dice.expr+f'-{value}', dice.dice+value.dice, dice.bonus-value.value)
    return Dice(dice.expr+f'-{value}', dice.dice, dice.history, dice.bonus-value)

def add_expr(t, dice, value):
    if isinstance(value, Dice):
        return Dice(dice.expr+f'+{value}', dice.dice+value.dice, dice.bonus+value.value)
    return Dice(dice.expr+f'+{value}', dice.dice, dice.history, dice.bonus+value)

