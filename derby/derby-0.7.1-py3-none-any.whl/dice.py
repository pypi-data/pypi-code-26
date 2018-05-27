class Dice:
    def __init__(self, expr, dice, history=None, bonus=0):
        self.expr = expr 
        self.dice = dice
        self.history = history or dice
        self.bonus = bonus

    @property 
    def value(self):
        return sum(self.dice) + self.bonus

    def __gt__(self, other):
        return self.value > other

    def __ge__(self, other):
        return self.value >= other

    def __lt__(self, other):
        return self.value < other

    def __le__(self, other):
        return self.value <= other

    def __eq__(self, other):
        if isinstance(other, Dice):
            return self.value == other.value
        return self.value == other # sum is either dice or number

    def __repr__(self):
        return self.expr

