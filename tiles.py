#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Apr 19 15:01:41 2026

@author: sabrinachen
"""


class Tile:
    """
    Represents one tile in the board.

    Attributes
    ----------
    pos : tuple of int
        The (row, column) position of the tile on the grid.

    weight : int
        The value the tile contributes towards the final score.

    enclosed : bool
        Whether the tile is enclosed by a wall.

    has_rat : bool
        Whether the tile contains the rat.

    type : str
        A string representation of the class

    """

    def __init__(self, pos, weight=1, enclosed=False, has_rat=False):
        self.pos = pos
        self.weight = weight     # some tiles if enclosed would have more value
        self.enclosed = enclosed
        self.has_rat = has_rat     # if the tile has the rat
        self.type = "r" if self.has_rat else "."
    
    def setEnclosed(self):
        self.enclosed = True
        if self.type == ".":
            self.type = "*"
        else:
            self.type = self.type.capitalize()
    
    def __repr__(self):
        return f"{self.type}"

class Cherry(Tile):
    def __init__(self, pos, weight=4, enclosed=False):
        super().__init__(pos, weight, enclosed)
        self.type = "c" if not(self.enclosed) else "C"
        
class Bee(Tile):
    def __init__(self, pos, weight=-4, enclosed=False):
        super().__init__(pos, weight, enclosed)
        self.type = "b" if self.enclosed is False else "B"

class Apple(Tile):
    def __init__(self, pos, weight=6, enclosed=False):
        super().__init__(pos, weight, enclosed)
        self.type = "a" if self.enclosed is False else "A"

class Wall:
    """
    Represents a barrier in the board.

    Attributes
    ----------
    pos : tuple of int
        The (row, column) position of the wall on the grid.

    fixed : bool
        Whether the barrier is fixed.
    
    type : str
        A string representation of the class

    Methods
    -------
    set_position(new_pos):

    """

    def __init__(self, pos, fixed=False):
        self.pos = pos
        self.fixed = fixed      # fixed is True means a barrier (e.g. water)
        self.type = "W" if not fixed else "~"
        self.weight = 0
        
    def __repr__(self):
        return f" {self.type} "

class Portal(Tile):
    """
    Represents a teleport connection between two positions.

    Attributes
    ----------
    pos : tuple of int
        The entry (row, column) position of the wall on the grid.

    new_pos : tuple of int
        The exit (row, column) position of the wall on the grid.

    type : str
        A string representation of the class
    """

    def __init__(self, pos, new_pos, enclosed=False):
        super().__init__(pos, enclosed)
        self.new_pos = new_pos   # exit point
        self.type = "p"
