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

    weight : int, optional
        The value the tile contributes towards the final score when enclosed.
        Default is 1.

    enclosed : bool, optional
        Whether the tile is enclosed by a wall. Default is False.

    has_rat : bool, optional
        Whether the tile contains the rat. Default is False.

    type : str
        A single-character string representation of the class.

    Methods
    -------
    setEnclosed()
        Marks the tile as enclosed and updates the marker (self.type).

    """

    def __init__(self, pos, weight=1, enclosed=False, has_rat=False):
        """
        Initialize a Tile with position and optional attributes.

        Parameters
        ----------
        pos : tuple of int
            The (row, column) position of the tile on the grid.
        weight : int, optional
            Value the tile contributes towards the final score when enclosed.
            The default is 1.
        enclosed : bool, optional
            Whether the tile is enclosed by a wall. The default is False.
        has_rat : bool, optional
            Whether the tile contains the rat. The default is False.
        """
        self.pos = pos
        self.weight = weight
        self.enclosed = enclosed
        self.has_rat = has_rat

        # Set the marker based on whether the rat is present.
        self.type = "r" if self.has_rat else "."

    def setEnclosed(self):
        """Marks the tile as enclosed and updates the marker (self.type)."""
        self.enclosed = True

        if self.type == ".":
            self.type = "*"   # Empty tiles use "*" to indicate enclosure.
        else:
            self.type = self.type.capitalize()   # Other tiles are capitalized.

    def __repr__(self):
        """
        Returns the string representation of the tile for display.

        Returns
        -------
        str
            The single-character marker for the tile.

        """
        return f"{self.type}"


class Cherry(Tile):
    """
    Represents a tile containing a cherry. Inherits from Tile class.

    Attributes
    ----------
    pos : tuple of int
        The (row, column) position of the cherry on the grid.

    weight : int, optional
        The value the cherry contributes towards the final score when enclosed.
        Default is 4.

    enclosed : bool, optional
        Whether the cherry is enclosed by a wall. Default is False.

    type : str
        A single-character string representation of the class.
        'c' when not enclosed and 'C' when enclosed.
    """

    def __init__(self, pos, weight=4, enclosed=False):
        """Initialize a Cherry tile with position and optional attributes."""
        # Initialize base Tile with cherry-specific weight.
        super().__init__(pos, weight, enclosed)

        # Set the marker based on whether it is enclosed.
        self.type = "c" if not (self.enclosed) else "C"


class Bee(Tile):
    """
    Represents a tile containing a bee. Inherits from Tile class.

    Attributes
    ----------
    pos : tuple of int
        The (row, column) position of the bee on the grid.

    weight : int, optional
        The value the bee contributes towards the final score when enclosed.
        Default is -9.

    enclosed : bool, optional
        Whether the bee is enclosed by a wall. Default is False.

    type : str
        A single-character string representation of the class.
        'b' when not enclosed and 'B' when enclosed.
    """

    def __init__(self, pos, weight=-4, enclosed=False):
        """Initialize a Bee tile with position and optional attributes."""
        # Initialize base Tile with bee-specific weight.
        super().__init__(pos, weight, enclosed)

        # Set the marker based on whether it is enclosed.
        self.type = "b" if self.enclosed is False else "B"


class Apple(Tile):
    """
    Represents a tile containing an apple. Inherits from Tile class.

    Attributes
    ----------
    pos : tuple of int
        The (row, column) position of the apple on the grid.

    weight : int, optional
        The value the apple contributes towards the final score when enclosed.
        Default is 11.

    enclosed : bool, optional
        Whether the apple is enclosed by a wall. Default is False.

    type : str
        A single-character string representation of the class.
        'a' when not enclosed and 'A' when enclosed.
    """

    def __init__(self, pos, weight=11, enclosed=False):
        """Initialize an Apple tile with position and optional attributes."""
        # Initialize base Tile with apple-specific weight.
        super().__init__(pos, weight, enclosed)

        # Set the marker based on whether it is enclosed.
        self.type = "a" if self.enclosed is False else "A"


class Wall:
    """
    Represents a barrier in the board. Walls can be fixed (water) or moveable.

    Attributes
    ----------
    pos : tuple of int
        The (row, column) position of the wall on the grid.

    fixed : bool
        Whether the barrier is fixed (True) or movable (False).

    type : str
        A string representation of the class.
        'W' for moveable walls and '~' for fixed walls (water).

    Methods
    -------
    __repr__()
        Returns a string representatiion for display.
    """

    def __init__(self, pos, fixed=False):
        """Initialize a Wall with position and fixed status."""
        self.pos = pos
        self.fixed = fixed
        self.type = "W" if not fixed else "~"
        self.weight = 0   # walls have no scoring value

    def __repr__(self):
        """
        Return a string representatiion for display.

        Returns
        -------
        str
            A single-character string representation of the class for display.

        """
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

    enclosed : bool, optional
        Whether the portal is enclosed. Default is False.

    type : str
        A string representation of the class.

    weight : int
        The value the portal contributes towards the final score when enclosed.
    """

    def __init__(self, pos, new_pos, color=None, enclosed=False):
        """Initialize a Portal with entry/exit points and optional enclosed."""
        # Initialize base Tile with portal position.
        super().__init__(pos, enclosed=enclosed)

        # Store the destination coordinates for teleportation
        self.new_pos = new_pos

        # Set the marker based on whether it is enclosed.
        self.type = "P" if enclosed else "p"

        # Default weight for portal tiles.
        self.weight = 1

        # Color of the portal (for visualization)
        self.color = color
