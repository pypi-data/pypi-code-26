"""
Simple module for simulating dice rolls.
"""

from __future__ import print_function, absolute_import, unicode_literals

import random
from argparse import ArgumentParser


def get_options():
	parser = ArgumentParser()
	parser.add_argument('-s', '--sides', default=6, type=int)
	parser.add_argument('number', nargs='?', type=int, default=1)
	args = parser.parse_args()
	return args


class Dice(object):
	"""
	>>> d20 = Dice(20)
	>>> 1 <= d20.roll() <= 20
	True
	"""
	def __init__(self, sides):
		self.sides = sides

	def roll(self):
		return random.randint(1, self.sides)


def do_dice_roll():
	"""
	Roll n-sided dice and return each result and the total
	"""
	options = get_options()
	dice = Dice(options.sides)
	rolls = [dice.roll() for n in range(options.number)]
	for roll in rolls:
		print('rolled', roll)
	if options.number > 1:
		print('total', sum(rolls))
