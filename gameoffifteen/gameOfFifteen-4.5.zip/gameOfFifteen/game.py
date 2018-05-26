#!/usr/bin/python3
# -*- coding: UTF-8 -*-


"""Modul contains the game logic and its solutions."""


__license__ = "Copyright 2018 by Vikarowitsch"
__author__ = "Vikarowitsch"


from movedirection import MoveDirection


class Game:

    """Game logic."""

    row_count = 4
    column_count = 4
    standard_solution = [[1,  5,  9, 13], [2,  6, 10, 14], [3,  7, 11, 15], [4,  8, 12,  0]]
    vertical_solution = [[1,  2,  3,  4], [5,  6,  7,  8], [9, 10, 11, 12], [13, 14, 15,  0]]
    spiral_solution = [[1, 12, 11, 10], [2, 13,  0,  9], [3, 14, 15,  8], [4,  5,  6,  7]]
    zick_zack_solution = [[4,  5, 12, 13], [3,  6, 11, 14], [2,  7, 10, 15], [1,  8,  9,  0]]
    horse_path_solution = [[15,  4,  9,  0], [10,  7, 12,  1], [3, 14,  5,  8], [6, 11,  2, 13]]

    def __init__(self):
        """Implement the object creation."""
        self.matrix = [[0 for x in range(Game.column_count)] for y in range(Game.row_count)]
        index = 0
        for row in range(0, Game.row_count):
            for column in range(0, Game.column_count):
                index = index + 1
                if index < Game.row_count * Game.column_count:
                    self.matrix[column][row] = index
                else:
                    self.matrix[column][row] = 0

    def value_at(self, column, row):
        """Return a value in the matrix."""
        return self.matrix[column][row]

    def __row_index_of_hole(self):
        """Return the row of the hole."""
        for row in range(0, Game.row_count):
            for column in range(0, Game.column_count):
                if self.value_at(column, row) == 0:
                    return row

    def __column_index_of_hole(self):
        """Return the column of the hole."""
        for row in range(0, Game.row_count):
            for column in range(0, Game.column_count):
                if self.value_at(column, row) == 0:
                    return column

    def print(self):
        """Print the current matrix for debugging."""
        for row in range(0, Game.row_count):
            for column in range(0, Game.column_count):
                print(repr(self.value_at(column, row)).rjust(2), end=' ')
            print("\n")
        print("\n")

    def shuffle(self):
        """Shuffle a given matrix."""
        for _shuffleIndex in range(0, 10000):
            move_direction = MoveDirection.get_random_direction()
            move_direction = self.__verify_or_change(move_direction)
            self.__move_hole(move_direction)

    def row_of_value(self, number):
        """Return the row of a specified value."""
        for row in range(0, Game.row_count):
            for column in range(0, Game.column_count):
                if self.value_at(column, row) == number:
                    return row

    def column_of_value(self, number):
        """Return the column of a specified value."""
        for row in range(0, Game.row_count):
            for column in range(0, Game.column_count):
                if self.value_at(column, row) == number:
                    return column

    def is_move_possible(self, number):
        """Return True if a move is possible."""
        selected_row = self.row_of_value(number)
        selected_column = self.column_of_value(number)
        hole_row = self.row_of_value(0)
        hole_column = self.column_of_value(0)
        if abs(selected_row - hole_row) >= 1 and selected_column == hole_column:
            return True
        if abs(selected_column - hole_column) >= 1 and selected_row == hole_row:
            return True
        return False

    def move_to_hole(self, column, row):
        """Move the column/row to the hole."""
        hole_row = self.row_of_value(0)
        hole_column = self.column_of_value(0)
        self.matrix[hole_column][hole_row] = self.matrix[column][row]
        self.matrix[column][row] = 0

    def __verify_or_change(self, MoveDirection):
        """Return MoveDirection. If not possible reverses it."""
        column_hole = self.__column_index_of_hole()
        if column_hole == 0 and MoveDirection == MoveDirection.Left:
            return MoveDirection.Right
        if column_hole == Game.column_count - 1 and MoveDirection == MoveDirection.Right:
            return MoveDirection.Left
        row_hole = self.__row_index_of_hole()
        if row_hole == 0 and MoveDirection == MoveDirection.Up:
            return MoveDirection.Down
        if row_hole == Game.row_count - 1 and MoveDirection == MoveDirection.Down:
            return MoveDirection.Up
        return MoveDirection

    def __move_hole(self, MoveDirection):
        """Move the hole in this MoveDirection."""
        column_hole = self.__column_index_of_hole()
        row_hole = self.__row_index_of_hole()
        # print("colHole={} row_hole={} MoveDirection={}".format(column_hole, row_hole, MoveDirection))
        if MoveDirection == MoveDirection.Left:
            self.matrix[column_hole][row_hole] = self.matrix[column_hole - 1][row_hole]
            self.matrix[column_hole - 1][row_hole] = 0
        if MoveDirection == MoveDirection.Right:
            self.matrix[column_hole][row_hole] = self.matrix[column_hole + 1][row_hole]
            self.matrix[column_hole + 1][row_hole] = 0
        if MoveDirection == MoveDirection.Up:
            self.matrix[column_hole][row_hole] = self.matrix[column_hole][row_hole - 1]
            self.matrix[column_hole][row_hole - 1] = 0
        if MoveDirection == MoveDirection.Down:
            self.matrix[column_hole][row_hole] = self.matrix[column_hole][row_hole + 1]
            self.matrix[column_hole][row_hole + 1] = 0

    def all_sorted(self):
        """If the matrix is correct sorted, return True."""
        if self.matrix == Game.standard_solution:
            return "Standard Lösung"
        elif self.matrix == Game.vertical_solution:
            return "Vertikale Lösung"
        elif self.matrix == Game.spiral_solution:
            return "Spirale Lösung"
        elif self.matrix == Game.zick_zack_solution:
            return "ZickZack Lösung"
        elif self.matrix == Game.horse_path_solution:
            return "Springer Pfad Lösung"
        else:
            return None
