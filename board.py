#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Apr 19 15:14:10 2026

@author: sabrinachen
"""

from tiles import *
import math
from collections import deque
from ortools.sat.python import cp_model
from imgreader import *

class Board:

    def __init__(self, rows, cols, walls, image_path=None):
        self.rows = rows
        self.cols = cols
        self.grid = [[Tile((i, j)) for j in range(cols)] for i in range(rows)]
        self.walls = walls  # placeable walls
        self.wall_pos = [] # placeable walls
        self.portals = []
        self.rat_pos = None
        self.puzzle_name = ''
        
        if image_path: 
            self.create_board_from_image(image_path, rows, cols, walls)
            self.puzzle_name = image_path.replace('.png', '')
        
        self.score = -math.inf

        
    def create_board_from_image(self, image_path, rows, cols, walls=0):
        """
        Create a Board object from an image.
        """
        parser = BoardParser(image_path, rows, cols)
        data = parser.parse()
        
        # First pass: create all non-portal tiles
        for row in range(rows):
            for col in range(cols):
                pos = (row, col)
                
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
        
        # Second pass: create portal pairs with color information
        for portal_data in data['portals']:
            entry_pos = portal_data['entry']
            exit_pos = portal_data['exit']
            color = portal_data['color']  # e.g., 'portal_sky', 'portal_blue'
            
            # Create portal with color information
            portal = Portal(entry_pos, exit_pos, color=color)
            self.portals.append(portal)
            
            # Place the same portal object at both positions
            entry_row, entry_col = entry_pos
            exit_row, exit_col = exit_pos
            self.grid[entry_row][entry_col] = portal
            self.grid[exit_row][exit_col] = portal
            
            
    def __str__(self):
        grid_str = ""
        for row in self.grid:
            row_str = ""
            for tile in row:
                row_str += tile.type + " "
            grid_str += row_str + "\n"
        return grid_str

    def is_valid_position(self, pos):    # checks bounds and collision with walls
        if pos is None:
            return False
        x, y = pos
        # check if at the boundary of the puzzle
        if not (0 <= x < self.rows and 0 <= y < self.cols):
            return False
        
        # check if it is a wall position or water
        if isinstance(self.grid[x][y], Wall) and self.grid[x][y].fixed:
            return False
        
        return True

    def get_neighbors(self, pos):   # gets all the adjacent and portal connected neighbors
        x, y = pos
        directions = [(0,1), (0,-1), (-1,0), (1,0)]   # up, down, left, right
        
        neighbors = []   # initialize list

        # check if the neighbors in 4 directions are valid moves
        for dx, dy in directions:
            n_pos = (x + dx, y + dy)
            
            # check if move is valid
            if self.is_valid_position(n_pos):
                neighbors.append(n_pos)
        
        # checks for portals and handles accordingly
        for portal in self.portals:
            if portal.pos == pos and self.is_valid_position(portal.new_pos):
                neighbors.append(portal.new_pos)
            elif portal.new_pos == pos and self.is_valid_position(portal.pos):
                neighbors.append(portal.pos)
        return neighbors
    
    def get_valid_tiles(self):
        valid = []
        
        for i in range(self.rows):
            for j in range(self.cols):
                if self.is_valid_position((i, j)):
                    valid.append((i, j))
        return valid
    
    def get_edge_tiles(self):
        edges = set()
        
        for i in range(self.rows):
            for j in range(self.cols):
                if i == 0 or i == self.rows - 1 or j == 0 or j ==self.cols - 1:
                    if self.is_valid_position((i, j)):
                        edges.add((i, j))
        return edges
    
    def get_portal_tiles(self):
        # get all tiles that are portal entrances
        portal_tiles = set()
        
        for portal in self.portals:
            if self.is_valid_position(portal.pos):
                portal_tiles.add(portal.pos)
                
        return portal_tiles
    
    def get_portal_exits(self, pos):
        # get all the tiles that are portal exits
        exits = []
        
        for portal in self.portals:
            if portal.pos == pos and self.is_valid_position(portal.new_pos):
                exits.append(portal.new_pos)
        
        return exits
    
    def build_adjacency_graph(self, valid_tiles, pos_to_i):
        # create a complete adjacency graph including portals
        n = len(valid_tiles)
        
        adj = [[] for _ in range(n)]
        
        for i, pos in enumerate(valid_tiles):
            neighbors = self.get_neighbors(pos)
            
            for neighbor in neighbors:
                if neighbor in pos_to_i:
                    j = pos_to_i[neighbor]
                    if j not in adj[i]:
                        adj[i].append(j)
        return adj

    def solve_puzzle(self):   # puzzle solver
        model = cp_model.CpModel()
        
        valid_tiles = self.get_valid_tiles()
        edge_tiles = self.get_edge_tiles()
        
        # create position to index mapping
        pos_to_i = {pos: i for i, pos in enumerate(valid_tiles)}
        n = len(valid_tiles)
        
        # build the adajcency graph with portal connections
        adj = self.build_adjacency_graph(valid_tiles, pos_to_i)
        
        # decision variables
        # is_wall[i] = 1 if wall is placed
        is_wall = [model.NewBoolVar(f'wall_{i}') for i in range(n)]
        
        # is_reachable[i] = 1 if rat can reach valid_tiles[i]
        is_reachable = [model.NewBoolVar(f'reach_{i}') for i in range(n)]
        
        # order[i] = distance from rate for connectivity
        order = [model.NewIntVar(0, n, f'order_{i}') for i in range(n)]
        
        # constraints
        # wall cannot be placed on rat's position
        rat_i = pos_to_i[self.rat_pos]
        model.Add(is_wall[rat_i] == 0)
        
        # wall cannot be placed on portal positions
        for portal in self.portals:
            if portal.pos in pos_to_i:
                model.Add(is_wall[pos_to_i[portal.pos]] == 0)
            if portal.new_pos in pos_to_i:
                model.Add(is_wall[pos_to_i[portal.new_pos]] == 0)
        
        # rat's starting position is reachable
        model.Add(is_reachable[rat_i] == 1)
        model.Add(order[rat_i] == 0)
        
        # limited number of walls
        model.Add(sum(is_wall) <= self.walls)
        
        # a tile is reachable only if it is not a wall
        for i in range(n):
            model.AddImplication(is_wall[i], is_reachable[i].Not())
        
        # if the tile is not reachable, the order is n (max_value)
        for i in range(n):
            model.Add(order[i] == n).OnlyEnforceIf(is_reachable[i].Not()) 
        
        # enclosure constraint
        # rat must be enclosed (no edge tile is reachable)
        for edge_pos in edge_tiles:
            if edge_pos in pos_to_i:
                edge_i = pos_to_i[edge_pos]
                model.Add(is_reachable[edge_i] == 0)
      
        # reachability with portals
        for i, pos in enumerate(valid_tiles):
            
            # wall cannot be placed on special tiles (cherries, bees, apples)
            tile = self.grid[pos[0]][pos[1]]
            if isinstance(tile, (Apple, Bee, Cherry)):
                model.Add(is_wall[i] == 0)
            
            if pos == self.rat_pos:   # there is no portal where the rat is
                continue
            
            neighbor_i = adj[i]    # all the neighbors of that tile
            
            if not neighbor_i:
                # no neighbors at all so unreachable
                model.Add(is_reachable[i] == 0)
                continue
            
            # for each neighbor j, if neighbor j is reachable AND j is not a placed wall AND i is not a placed wall
            # then tile i must be reachable
            for j in neighbor_i:
                model.AddBoolOr([is_reachable[j].Not(), is_wall[j], is_wall[i], is_reachable[i]])
            
            # constraints for connectivity
            # if reachable, order[i] = min(order[neighbors] + 1)
            # in other words, for each neighbor j, if i comes from j, then order[i] = order[j] + 1
            
            comes_from = []
            for j in neighbor_i:
                comes_from_j = model.NewBoolVar(f'comes_from_{j}_to_{i}')
                comes_from.append(comes_from_j)
                
                # If comes_from_j: order[i] = order[j] + 1, and j is reachable
                model.Add(order[i] == order[j] + 1).OnlyEnforceIf(comes_from_j)
                model.AddImplication(comes_from_j, is_reachable[j])
                model.AddImplication(comes_from_j, is_wall[j].Not())
                model.AddImplication(comes_from_j, is_reachable[i])
                model.AddImplication(comes_from_j, is_wall[i].Not())
            
            # if tile i is reachable and not a placed wall, exactly one comes_from must be true
            tile_i_active = model.NewBoolVar(f'tile_{i}_active')
            model.AddBoolAnd([is_reachable[i], is_wall[i].Not()]).OnlyEnforceIf(tile_i_active)
            model.AddBoolOr([is_reachable[i].Not(), is_wall[i]]).OnlyEnforceIf(tile_i_active.Not())
            
            # If active, must come from exactly one neighbor (or use at-least-one)
            model.AddBoolOr(comes_from).OnlyEnforceIf(tile_i_active)
            
            # to avoid conflicting order assignments
            model.Add(sum(comes_from) <= 1).OnlyEnforceIf(tile_i_active)
        
        # maximize score
        weights = []
        for i, pos in enumerate(valid_tiles):
            x, y = pos
            tile = self.grid[x][y]
            weights.append(int(getattr(tile, "weight", 0)))
            
        min_total = sum(w for w in weights if w < 0)
        max_total = sum(w for w in weights if w > 0)
        
        # score is the sum of weights of the reachable tiles
        total_score = model.NewIntVar(min_total if min_total != 0 else 0, max_total if max_total != 0 else 0, "total_score")
        model.Add(total_score == sum(weights[i] * is_reachable[i] for i in range(n)))
        model.Maximize(total_score)
        
        # solve the puzzle
        solver = cp_model.CpSolver()
        solver.parameters.max_time_in_seconds = 60
        solver.parameters.num_search_workers = 8
    
        status = solver.Solve(model)
        score = 0
    
        
        if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
            self.wall_pos = []
            
            for i in range(n):
                if solver.Value(is_wall[i]) == 1:
                    self.wall_pos.append(valid_tiles[i])
                    x, y = valid_tiles[i]
                    self.grid[x][y] = Wall((x, y), False)
            
            for i in range(len(is_reachable)):
                if solver.Value(is_reachable[i]) == 1:
                    row, col = valid_tiles[i]
                    if type(self.grid[row][col]) is not Wall:
                        self.grid[row][col].setEnclosed()
                    
            self.score = solver.ObjectiveValue()
            return self.wall_pos, self.score
        else:
            print(f"No solution found! Status: {solver.StatusName(status)}")
            return [], 0
            
    def visualize_board(self):    # display the grid
        viz = BoardVisualizer("sprites/", tile_size=64)
        viz.show(self, self.puzzle_name)

if __name__ == "__main__":

    IMAGE_PATH = "31_board.png"
    ROWS = 15
    COLS = 15
    
    # Check specific tile for calibration
    # parser.get_color_sample(5, 6)
    
    # Create board object
    board = Board(ROWS, COLS, 13, IMAGE_PATH)
    
    # result = board.solve_puzzle()
    # print("Walls placed:", board.wall_pos)
    # print("Score:", board.score)
    
    # print(board)
    
    board.visualize_board()
