import sys


class King(object):
    def __init__(self, name):
        self.name = name

    def __str__(self):
        return self.name

    def __repr__(self):
        return '<King (%s)>' % self

this_module = sys.modules[__name__]
sys.modules[__name__] = King('Vinayak Kaniyarakkal')
