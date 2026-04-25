#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Apr 19 15:14:10 2026

@author: sabrinachen
"""

import numpy as np
from tiles import *
import math


class Board:

    def __init__(self, rows, cols, walls):
        self.rows = rows
        self.cols = cols
        self.grid = np.full((self.rows, self.cols), None)

        self.walls = walls
        self.wall_pos = []
        self.portals = []

        self.rat_paths = []
        self.rat_pos = None
        
        self.score = -math.inf

    def generate_layout(self, difficulty):    # make an initial layout
        pass

    def place_walls(self):          # place walls
        pass

    def place_portals(self):        # place portal pairs
        pass

    def place_rat(self):        # place rat
        pass
    
    def make_puzzle(self, difficulty):  # creates a puzzle from scratch
        pass

    def get_reachable_area(self, start_pos):
        reachable = {start_pos}
        queue = [start_pos]
        
        while queue:
            curr = queue.pop(0)
            for neighnor in self.get_neighbors(curr, self.wall_pos):
                reachable.add(neighbor)
                queue.append(neighbor)
        
        return reachable

    def is_enclosed(self, reachable_area):   # checks if the rat is enclosed
        # check if the reachable area touches any board edges
        for i, j in reachable_area:
            if i == 0 or i == self.rows - 1 or j == 0 or j == self.cols - 1:
                return False
        return True
        
        pass

    def find_shortest_path_to_edge(self, walls):
        # BFS to find shortest route to a boundary tile
        queue = [(start_pos, [])]
        visited = {start_pos}
        
        while queue:
            (curr, path) = queue.pop(0)
            i, j = curr
            if i == 0 or i == self.rows - 1 or j == 0 or j == self.cols - 1:
                return path
            for n in self.get_neighbors(curr):
                if n not in visited:
                    visited.add(n)
                    queue.append((n, path + [n]))
        return None

    def is_valid_position(self, pos):    # checks bounds and collision with walls
        # check if at the boundary of the puzzle
        if not (0 <= pos[0] < self.rows and 0 < pos[1] < self.cols):
            return False
        
        # check if it is a wall position
        if pos in self.wall_pos:
            return False
        
        # check if there is a barrier (water)
        tile = self.grid[pos[0], pos[1]]
        if isinstance(tile, Wall):
            return False
        
        return True

    def get_neighbors(self, pos):   # gets all the adjacent and portal connected neighbors
        neighbors = []   # initialize list
        directions = [(0,1), (0,-1), (-1,0), (1,0)]   # up, down, left, right
        
        # check if the neighbors in 4 directions are valid moves
        for dir in directions:
            n_pos = (pos[0] + dir[0])
            if self.is_valid_position(n_pos) and n_pos not in self.wall_pos:
                neighbors.append(n_pos)
        
        # checks for portals and handles accordingly
        for portal in self.portals:
            if portal.pos == pos:
                if self.is_valid_position(portal.new_pos) and portal.new_pos not in self.walls:
                    neighbor.append(portal.new_pos)
        
        return neighbors
    
    def get_score(self, enclosed_area):    # calculate the scores
        # scores the enclosed area
        total = 0
        for pos in enclosed_area:
            tile = self.grid[pos[0], pos[1]]
            total += tile.weight
        return total

    def solve_puzzle(self):   # puzzle solver
        
        stack = [self.walls, set()]
        
        # while we still have walls left
        while stack:
            # removes the last entry into the stack and stores it
            walls_left, wall_pos = stack.pop()
            
            # check where the rat can reach
            reachable_area = self.get_all_reachable(self.rat_pos, wall_pos)
        
            # check if the rat has been enclosed
            if self.is_enclosed(reachable_area):
                score = self.get_score(reachable_area)
                
                if score > self.score:
                    self.score = score
                    self.wall_pos = list(wall_pos)
                
                continue  # don't add more walls if rat is enclosed
                            
            # continue to add walls if the rat has not been enlcosed
            if walls_left > 0:
                escape_path = self.find_shortest_path_to_edge(self.rat_pos, wall_pos)
            
                if escape_path:
                    for pos in escape_path:
                        if pos not in wall_pos:
                            new_walls = current_walls.copy()
                            new_walls.add(pos)
                            stack.append((walls_left-1, new_walls))
            
        return self.wall_pos

    def visualize_board(self):    # display the grid
        pass

if __name__ == "__main__":
    board = Board(5, 5, 5)
    board.grid = [[],[],[],[],[]]    