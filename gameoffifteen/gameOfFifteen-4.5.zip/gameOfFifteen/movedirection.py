#!/usr/bin/python3
# -*- coding: UTF-8 -*-


"""Modul contains Enum to enumeration directions in the game."""


__license__ = "Copyright 2018 by Vikarowitsch"
__author__ = "Vikarowitsch"


from random import randint
from enum import Enum


class MoveDirection(Enum):

    """Define enumeration for move directions."""

    Left = 1
    Right = 2
    Up = 3
    Down = 4

    def get_random_direction():
        """Return a random direction as a enum."""
        direction = randint(1, 4)
        if direction == 1:
            return MoveDirection.Left
        if direction == 2:
            return MoveDirection.Right
        if direction == 3:
            return MoveDirection.Up
        if direction == 4:
            return MoveDirection.Down
        raise IndexError
