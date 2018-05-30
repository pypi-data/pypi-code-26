""" This takes an argument between 0 and 14 and returns info about that level of pH. Additionally, facts about pH."""

__version__ = '0.1'

def version():
    return ("Version 0.1")

def pH(x):
    if x >= 0 and x <= 0.99:
        return ("Most acidic")
    elif x >= 1 and x <= 3.99:
        return ("Very acidic")
    elif x >= 4 and x <= 6.99:
        return ("Slightly acidic")
    elif x >=7 and x <= 7.99:
        return ("Neutral")
    elif x >= 8 and x <= 10.99:
        return ("Slightly basic")
    elif x >= 11 and x <= 13.99:
        return ("Very basic")
    elif x >= 14 and x <= 14:
        return ("Most basic")
    else:
        return ("Outside pH range")

def pHSimilarity(x):
    if x >= 0 and x <= 0.99:
        return ("Battery Acid")
    elif x >= 1 and x <= 1.99:
        return ("Stomach Acid")
    elif x >= 2 and x <= 2.99:
        return ("Vinegar")
    elif x >= 3 and x <= 3.99:
        return ("Lemon Juice")
    elif x >= 4 and x <= 4.99:
        return ("Black Coffee")
    elif x >= 5 and x <= 5.99:
        return ("Black Coffee")
    elif x >= 6 and x <= 6.99:
        return ("Milk")
    elif x >= 7 and x <= 7.99:
        return ("Human Blood")
    elif x >= 8 and x <= 8.99:
        return ("Sea Water")
    elif x >= 9 and x <= 9.99:
        return ("Baking Soda")
    elif x >= 10 and x <= 10.99:
        return ("Great Salt Lake")
    elif x >= 11 and x <= 11.99:
        return ("Ammonia")
    elif x >= 12 and x <= 12.99:
        return ("Soapy Water")
    elif x >= 13 and x <= 13.99:
        return ("Bleach")
    elif x >= 14 and x <= 14.99:
        return ("Liquid Drain Cleaner")
    else:
        return ("Outside pH range")


def humanBloodAlkalineLimit():
    return 7.45

def humanBloodAcidLimit():
    return 7.35