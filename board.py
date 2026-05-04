#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Apr 19 15:14:10 2026

@author: sabrinachen
"""

from tiles import Tile, Cherry, Bee, Apple, Wall, Portal
import math
from ortools.sat.python import cp_model
from imgreader import *


class Board:
    """
    Represents a puzzle board with tiles, walls, portals, and a rat.
    This class manages the game grid by creating boards from images or
    manually, finding optimal wall palcements using constraint programming, and
    visualizing the board state.

    rows : int
        The number of rows in the board grid.

    cols : int
        The number of columns in the board grid.

    grid : list of list of Tile
        2D array representing the board, where each cell contains a Tile object
        or one of its derived classes (Wall, Portal, Bee, Cherry, Apple).

    walls : int
        The number of walls that can be placed on the board.

    wall_pos : list of tuple
        List of (row, col) positions where walls have been placed.

    portals : list of Portal
        List of Portal objects on the board for teleportation.

    rat_pos : tuple of int or None
        The (row, col) position of the rat, or None if not placed.

    puzzle_name : str or None
        Identifier name for the puzzle.

    score : float
        The current score of the board. Initialized to negative infinity.

    Methods
    -------
    create_board_from_image(image_path, rows, cols, walls=0)
        Parses an image file to create the board layout.

    is_valid_position(pos)
        Checks if a position is within bounds and not blocked.

    get_neighbors(pos)
        Returns all adjacent and portal-connected positions.

    get_valid_tiles()
        Returns all positions where the rat can potentially move.

    get_edge_tiles()
        Returns all positions on the board's border.

    build_adjacency_graph(valid_tiles, pos_to_i)
        Constructs a graph of connected tiles for pathfinding.

    solve_puzzle()
        Uses constraint programming to find optimal wall placements.

    visualize_board()
        Displays the board graphically using sprites.

    stats()
        Prints puzzle statistics to console.
    """

    def __init__(self, rows, cols, walls, puzzle_name=None, image_path=None):
        """
        Initialize a new Board instance.

        Parameters
        ----------
        rows : int
            The number of rows in the board grid.
        cols : int
            The number of columns in the board grid.
        walls : int
            The number of walls that can be placed on the board.
        puzzle_name : str, optional
            Identifier name for the puzzle. The default is None.
        image_path : str, optional
            Path to an image file to parse for board layout.
            The default is None.
        """
        # Store board dimensions.
        self.rows = rows
        self.cols = cols

        # Initialize grid with empty tiles at each position
        self.grid = [[Tile((i, j)) for j in range(cols)] for i in range(rows)]

        # Store the number of placeable walls.
        self.walls = walls

        # Track positions where walls have been placed.
        self.wall_pos = []

        # List of portal objects and rat position
        self.portals = []
        self.rat_pos = None

        # If an image path is provided, parse it to create the board
        if image_path:
            self.create_board_from_image(image_path, rows, cols, walls)

            # Create the puzzle name from the image filename.
            self.puzzle_name = image_path.replace('.png', '')

        # Override puzzle name if provided.
        if puzzle_name:
            self.puzzle_name = puzzle_name

        # Initialize score to negative infinity.
        self.score = -math.inf

    def create_board_from_image(self, image_path, rows, cols, walls=0):
        """
        Create a Board object from an image file.

        Parameters
        ----------
        image_path : str
            Path to the image file to parse.
        rows : int
            Expected number of rows in the puzzle.
        cols : int
            Expected number of columns in the puzzle.
        walls : int, optional
            Number of placeable walls. The default is 0.

        Raises
        -------
        Exception
            Prints error message if image parsing fails.
        """
        try:
            # Create parser instance for the image.
            parser = BoardParser(image_path, rows, cols)
            data = parser.parse()

            # First pass: create all non-portal tiles.
            for row in range(rows):
                for col in range(cols):
                    pos = (row, col)

                    # Check each tile type and create appropriate object.
                    if pos in data['water']:
                        self.grid[row][col] = Wall(pos, fixed=True)
                    elif pos == data['rat_pos']:
                        self.grid[row][col] = Tile(pos, has_rat=True)
                        self.rat_pos = pos
                    elif pos in data['bees']:
                        self.grid[row][col] = Bee(pos)
                    elif pos in data['cherries']:
                        self.grid[row][col] = Cherry(pos)
                    elif pos in data['apples']:
                        self.grid[row][col] = Apple(pos)
                    elif data['grid'][row][col] != 'portal':
                        self.grid[row][col] = Tile(pos)

            # Second pass: create portal pairs with color information.
            for portal_data in data['portals']:
                entry_pos = portal_data['entry']
                exit_pos = portal_data['exit']
                color = portal_data['color']  # e.g., 'portal_sky'

                # Create portal with color information.
                portal = Portal(entry_pos, exit_pos, color=color)
                self.portals.append(portal)

                # Place the same portal object at both positions.
                entry_row, entry_col = entry_pos
                exit_row, exit_col = exit_pos
                self.grid[entry_row][entry_col] = portal
                self.grid[exit_row][exit_col] = portal
        except Exception as e:
            print(f"Error occurred: {e}")

    def __str__(self):
        """
        Return a string representation of the board.

        Returns
        -------
        grid_str : str
            A multi-line string showing the board layout with each row on a
            separate line and tiles separated by spaces.

        """
        grid_str = ""

        # Iterate through each row.
        for row in self.grid:
            row_str = ""
            # Concatenate each tile's type character,
            for tile in row:
                row_str += tile.type + " "

            # Add a new line after each row.
            grid_str += row_str + "\n"

        return grid_str

    def is_valid_position(self, pos):
        """
        Check if a position is valid for movement.

        A position is valid if it is within the board boundaries and
        not occupied by a fixed wall (water).

        Parameters
        ----------
        pos : tuple of int or None
            The (row, col) position to check.

        Returns
        -------
        bool
            True if the position is valid for movement, False otherwise.

        """
        
        # Handle input None.
        if pos is None:
            return False
        
        x, y = pos
        
        # Check if the position is within the boundary of the puzzle.
        if not (0 <= x < self.rows and 0 <= y < self.cols):
            return False

        # Check if the position contains a fixed wall (water).
        if isinstance(self.grid[x][y], Wall) and self.grid[x][y].fixed:
            return False

        return True

    def get_neighbors(self, pos):
        """
        Get all neighboring positions accessible from the given position.

        Parameters
        ----------
        pos : tuple of int
            The (row, col) position to find neighbors for.

        Returns
        -------
        neighbors : list of tuple
            List of (row, col) positions that can be reached from the
            given position in one move.

        """
        x, y = pos
        
        # Define the four directions: up, down, left, right.
        directions = [(0, 1), (0, -1), (-1, 0), (1, 0)]

        neighbors = []   # Initialize list of valid neighbors.

        # Check each adjacent position in 4 directions are valid moves.
        for dx, dy in directions:
            n_pos = (x + dx, y + dy)

            # Only add if the position is valid for movement.
            if self.is_valid_position(n_pos):
                neighbors.append(n_pos)

        # Checks for portals and handles accordingly.
        # Portals allow for teleportation between entry and exit positions.
        for portal in self.portals:
            if portal.pos == pos and self.is_valid_position(portal.new_pos):
                # Current position is portal entry, add exit as neighbor.
                neighbors.append(portal.new_pos)
            elif portal.new_pos == pos and self.is_valid_position(portal.pos):
                # Current position is portal exit, add entry as neighbor.
                neighbors.append(portal.pos)
            
        return neighbors

    def get_valid_tiles(self):
        """
        Get all valid tile positions on the board (positions rat could move).

        Returns
        -------
        valid : list of tuple
            List of all (row, col) positions that are valid for movement.

        """
        valid = []

        # Check every position on the grid.
        for i in range(self.rows):
            for j in range(self.cols):
                if self.is_valid_position((i, j)):
                    valid.append((i, j))
                    
        return valid

    def get_edge_tiles(self):
        """
        Get all valid tile positions on the board's edge.

        Returns
        -------
        edges : set of tuple
            Set of all valid (row, col) positions on the board's border.

        """
        edges = set()

        # Check every position on the grid.
        for i in range(self.rows):
            for j in range(self.cols):
                
                # Position is on the edge if in the first/law row or column.
                if i in (0, self.rows - 1) or j in (0, self.cols - 1):
                    if self.is_valid_position((i, j)):
                        edges.add((i, j))
                        
        return edges

    def build_adjacency_graph(self, valid_tiles, pos_to_i):
        """
        Build an adjacency list representation of the board graph.
        
        Creates a graph where nodes are tile indices and edges connect adjacent
        tiles (including portal connections).

        Parameters
        ----------
        valid_tiles : list of tuple
            List of all valid (row, col) positions on the board.
        pos_to_i : dict
            Mapping from (row, col) position to integer indicies.

        Returns
        -------
        adj : list of list of ind
            Adjacency list where adj[i] contains indices of all tiles adjacent
            to tile i.
        """
        n = len(valid_tiles)

        # Initialize empty adjacency list for each tile.
        adj = [[] for _ in range(n)]

        # Build adjacency relationships for each tile.
        for i, pos in enumerate(valid_tiles):
            
            # Get neighbors (adjacent + portal connections).
            neighbors = self.get_neighbors(pos)

            # Add edges to valid neighbors.
            for neighbor in neighbors:
                if neighbor in pos_to_i:
                    j = pos_to_i[neighbor]
                    
                    # Avoid duplicate edges.
                    if j not in adj[i]:
                        adj[i].append(j)
        return adj

    def solve_puzzle(self):
        """
        Find optimal wall placements to maximize score using Google OR-Tools.
        
        Solution must enclose the rat, maximize the total score of enclosed
        tiles, and be within the wall limit.

        Returns
        -------
        tuple
            A tuple containing list of tuple for positions where walls were
            placed and float for the score.
        """
        # Initialize the constraint programming model.
        model = cp_model.CpModel()

        # Get all valid positions and edge positions.
        valid_tiles = self.get_valid_tiles()
        edge_tiles = self.get_edge_tiles()

        # Create bidirectional mapping between positions and indices.
        pos_to_i = {pos: i for i, pos in enumerate(valid_tiles)}
        n = len(valid_tiles)

        # Build the adajcency graph with portal connections.
        adj = self.build_adjacency_graph(valid_tiles, pos_to_i)

        # Decision variables.
        # is_wall[i] = 1 if wall is placed at valid_tiles[i].
        is_wall = [model.NewBoolVar(f'wall_{i}') for i in range(n)]

        # is_reachable[i] = 1 if rat can reach valid_tiles[i].
        is_reachable = [model.NewBoolVar(f'reach_{i}') for i in range(n)]

        # order[i] = distance from rat (for connectivity verification)
        # Ensures that reachable tiles are connected.
        order = [model.NewIntVar(0, n, f'order_{i}') for i in range(n)]

        # Basic constraints.
        # 1. Wall cannot be placed on rat's position.
        rat_i = pos_to_i[self.rat_pos]
        model.Add(is_wall[rat_i] == 0)

        # 2. Wall cannot be placed on portal positions.
        for portal in self.portals:
            if portal.pos in pos_to_i:
                model.Add(is_wall[pos_to_i[portal.pos]] == 0)
            if portal.new_pos in pos_to_i:
                model.Add(is_wall[pos_to_i[portal.new_pos]] == 0)

        # 3. Rat's starting position is always reachable with order 0.
        model.Add(is_reachable[rat_i] == 1)
        model.Add(order[rat_i] == 0)

        # 4. Limited number of walls can be placed.
        model.Add(sum(is_wall) <= self.walls)

        # 5. A Wall tile is not reachable.
        for i in range(n):
            model.AddImplication(is_wall[i], is_reachable[i].Not())

        # 6. Unreachable tiles have maximum order value.
        for i in range(n):
            model.Add(order[i] == n).OnlyEnforceIf(is_reachable[i].Not())

        # Enclosure constraint.
        # 7. Rat must be enclosed (no edge tile is reachable).
        for edge_pos in edge_tiles:
            if edge_pos in pos_to_i:
                edge_i = pos_to_i[edge_pos]
                model.Add(is_reachable[edge_i] == 0)

        # Reachability and connnectivity constraints.
        for i, pos in enumerate(valid_tiles):

            # 8. Walls cannot be placed on special tiles.
            tile = self.grid[pos[0]][pos[1]]
            if isinstance(tile, (Apple, Bee, Cherry)):
                model.Add(is_wall[i] == 0)
            
            # Skip rat position.
            if pos == self.rat_pos:
                continue
            
            # Get all the neighbors of this tile.
            neighbor_i = adj[i]

            # 9. If no neighbors exist, tile is unreachable.
            if not neighbor_i:
                model.Add(is_reachable[i] == 0)
                continue
            
            # 10. If any neighbor j is reachable AND not blocked,
            # then i must be reachable (ensures all tiles are connected).
            for j in neighbor_i:
                model.AddBoolOr(
                    [is_reachable[j].Not(),    # j is not reachable, OR
                     is_wall[j],               # j has a wall, OR
                     is_wall[i],               # i has a wall, OR
                     is_reachable[i]])         # i is reachable

            # 11. If a tile is reachable, its order is equal to one neighbor's 
            # order + 1.

            # Create "comes_from" variables for each neighbor.
            comes_from = []
            for j in neighbor_i:
                comes_from_j = model.NewBoolVar(f'comes_from_{j}_to_{i}')
                comes_from.append(comes_from_j)

                # If comes_from_j is true: order[i] = order[j] + 1.
                model.Add(order[i] == order[j] + 1).OnlyEnforceIf(comes_from_j)
                
                # comes_from_j implies both tiles are reachable and not walls.
                model.AddImplication(comes_from_j, is_reachable[j])
                model.AddImplication(comes_from_j, is_wall[j].Not())
                model.AddImplication(comes_from_j, is_reachable[i])
                model.AddImplication(comes_from_j, is_wall[i].Not())

            # Create a helper variable for "tile i is active"
            # (reachable and not wall).
            tile_i_active = model.NewBoolVar(f'tile_{i}_active')
            model.AddBoolAnd([is_reachable[i], is_wall[i].Not()]
                             ).OnlyEnforceIf(tile_i_active)
            model.AddBoolOr([is_reachable[i].Not(), is_wall[i]]
                            ).OnlyEnforceIf(tile_i_active.Not())

            # If active, must come from at least one neighbor.
            model.AddBoolOr(comes_from).OnlyEnforceIf(tile_i_active)

            # Can only come from at most one neighbor (prevents conflicting orders).
            model.Add(sum(comes_from) <= 1).OnlyEnforceIf(tile_i_active)

        # Extract weights for each valid tile.
        weights = []
        for i, pos in enumerate(valid_tiles):
            x, y = pos
            tile = self.grid[x][y]
            
            # Get weight attributes, default to 0 if not present.
            weights.append(int(getattr(tile, "weight", 0)))

        # Calculate bounds for total score variable.
        min_total = sum(w for w in weights if w < 0)
        max_total = sum(w for w in weights if w > 0)

        # Create score variable bounded by possible min/max.
        total_score = model.NewIntVar(
            min_total if min_total != 0 else 0, max_total if max_total != 0 else 0, "total_score")
        
        # Score is the sum of weights of all reachable tiles.
        model.Add(total_score == sum(
            weights[i] * is_reachable[i] for i in range(n)))
        
        # Maximize total score.
        model.Maximize(total_score)

        # Solve the puzzle.
        solver = cp_model.CpSolver()
        
        # Set solver parameters.
        solver.parameters.max_time_in_seconds = 60    # Time limit.
        solver.parameters.num_search_workers = 8      # Parallel workers.

        # Run the solver.
        status = solver.Solve(model)

        # Process the solution.
        if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
            # Clear any previous wall positions.
            self.wall_pos = []
            
            # Record placed walls and update the board grid.
            for i in range(n):
                if solver.Value(is_wall[i]) == 1:
                    self.wall_pos.append(valid_tiles[i])
                    x, y = valid_tiles[i]
                    
                    # Create a non-fixed wall.
                    self.grid[x][y] = Wall((x, y), False)
            
            # Mark reachable tiles as enclosed.
            for i in range(len(is_reachable)):
                if solver.Value(is_reachable[i]) == 1:
                    row, col = valid_tiles[i]
                    
                    # Don't modify wall tiles.
                    if type(self.grid[row][col]) is not Wall:
                        self.grid[row][col].setEnclosed()

            # Store the score.
            self.score = solver.ObjectiveValue()
            return self.wall_pos, self.score
        else:
            # No solution found within constraints.
            print(f"No solution found! Status: {solver.StatusName(status)}")
            return [], 0

    def visualize_board(self):
        """
        Display the board using sprite images.

        Raises
        ------
        Exception
            Caught and printed if visualization fails.

        """
        try:
            # Create visualizer with sprites directory and tile size.
            viz = BoardVisualizer("sprites/", tile_size=64)
            
            # Display the board with puzzle name as title.
            viz.show(self, self.puzzle_name)
        except Exception as e:
            print(f"Visualization failed: {e}")

    def stats(self):
        """Print puzzle statistics to the console."""
        print(f"Puzzle: {self.puzzle_name}")
        print(f"Size: {self.rows} x {self.cols}")
        print(f"# of walls allowed: {self.walls}")
        print(f"Board score: {self.score}")


def main():
    """Main function to demonstrate puzzle solving"""

    # Modify this part to test different puzzles.
    image_file = "114_board.png"
    ROWS = 11
    COLS = 17
    WALLS = 11

    # Create board from image file.
    board = Board(ROWS, COLS, WALLS, image_path=image_file)
    print("Loaded puzzle successfully.")

    # Display initial board before solving.
    # Uncomment below to see unsolved puzzle.
    # board.visualize_board()

    # Solve puzzle.
    result = board.solve_puzzle()
    
    # Print puzzle statistics.
    board.stats()

    # Uncomment to see string version of board.
    # print(board)
    
    # Display the solved board.
    board.visualize_board()


if __name__ == "__main__":
    main()
