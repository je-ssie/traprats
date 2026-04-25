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

class Board:

    def __init__(self, rows, cols, walls):
        self.rows = rows
        self.cols = cols
        
        self.grid = [[Tile((i, j)) for j in range(cols)] for i in range(rows)]
                
        self.walls = walls  # placeable walls
        self.wall_pos = []
        self.portals = []

        self.rat_pos = None
        
        self.score = -math.inf

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
            if portal.pos == pos:
                if self.is_valid_position(portal.new_pos):
                    neighbors.append(portal.new_pos)
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
            if pos == self.rat_pos:
                continue
            
            neighbor_i = adj[i]
            
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
                model.AddImplication(comes_from, is_wall[i].Not())
            
            # if tile i is reachable and not a placed wall, exactly one comes_from must be true
            tile_i_active = model.NewBoolVar(f'tile_{i}_active')
            model.AddBoolAnd([is_reachable[i], is_wall[i].Not()]).OnlyEnforceIf(tile_i_active)
            model.AddBoolOr([is_reachable[i].Not(), is_wall[i]]).OnlyEnforceIf(tile_i_active.Not())
            
            # If active, must come from exactly one neighbor (or use at-least-one)
            model.AddBoolOr(comes_from).OnlyEnforceIf(tile_i_active)
            
            # to avoid conflicting order assignments
            model.Add(sum(comes_from) <= 1).OnlyEnforceIf(tile_i_active)
            
        # portal constraints
        # if a portal entrance is reachable and not blocked, portal exit has potential to be blocked
        for portal in self.portals:
            if portal.pos in pos_to_i and portal.new_pos in pos_to_i:
                entrance_i = pos_to_i[portal.pos]
                exit_i = pos_to_i[portal.new_pos]
                
                # if entrance is reachable and exit is on edge, there needs to be a wall somewhere
                if portal.new_pos in edge_tiles:
                    # Either block entrance, block exit, or place wall to prevent reaching entrance
                    # implicitly handled by enclosure constraint
                    pass
                
                # portal connectivity
                # portal entrance is reachable and not walled, exit is reachable (unless walled off), entrance_reachable AND NOT entrance_wall AND NOT exit_wall  --> exit_reachable
                entrance_active = model.NewBoolVar(f'portal_entrance_{entrance_i}_active')
                model.AddBoolAnd([
                    is_reachable[entrance_i], 
                    is_wall[entrance_i].Not(), 
                    is_wall[exit_i].Not()
                ]).OnlyEnforceIf(entrance_active)
                model.AddBoolOr([
                    is_reachable[entrance_i].Not(), 
                    is_wall[entrance_i], 
                    is_wall[exit_i]
                ]).OnlyEnforceIf(entrance_active.Not())
                
                model.AddImplication(entrance_active, is_reachable[exit_i])
        
        # maximize score
        weights = []
        for i, pos in enumerate(valid_tiles):
            x, y = pos
            tile = self.grid[x][y]
            weight = tile.weight if hasattr(tile, 'weight') else 0
            weights.append(weight)
        
        min_weight = min(weights) if weights else 0
        max_weight = max(weights) if weights else 0
        
        # score is the sum of weights of the reachable tiles
        score_terms = []
        for i in range(n):
            term = model.NewIntVar(min(0, min_weight), max(0, max_weight), f'score_term_{i}')
            model.Add(term == weights[i]).OnlyEnforceIf(is_reachable[i])
            model.Add(term == 0).OnlyEnforceIf(is_reachable[i].Not())
            score_terms.append(term)
        
        min_total = sum(w for w in weights if w < 0)  # sum of all negative weights
        max_total = sum(w for w in weights if w > 0)  # sum of all positive weights
        total_score = model.NewIntVar(min_total, max_total, 'total_score')
        model.Add(total_score == sum(score_terms))
        model.Maximize(total_score)
        
        # solve the puzzle
        solver = cp_model.CpSolver()
        solver.parameters.max_time_in_seconds = 60
        solver.parameters.num_search_workers = 8
        
        status = solver.Solve(model)
        
        if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
            self.wall_pos = []
            
            for i in range(n):
                if solver.Value(is_wall[i]) == 1:
                    self.wall_pos.append(valid_tiles[i])
                    x, y = valid_tiles[i]
                    self.grid[x][y] = Wall((x, y), False)
            
            self.score = solver.ObjectiveValue()
            return self.wall_pos, self.score
        else:
            print(f"No solution found! Status: {solver.StatusName(status)}")
            return [], 0
            
    def visualize_board(self):    # display the grid
        pass

if __name__ == "__main__":
    board = Board(15, 12, 11)
    str_b = [".~.~.....~~~", "...~.~~~.~~~", ".......~...~",
             ".~.~..~~...~", ".~....~..~..", ".........~..",
             ".~.~..~..~..", "...~.....~..", "........~~~.",
             ".~.~.....~..", ".~...R......", "............",
             ".~..~~.~..~~", "............", ".~~.~..~~.~.",]
    for i, row in enumerate(str_b):
        for j, tag in enumerate(row):
            if tag == ".":
                board.grid[i][j] = Tile((i, j))
            elif tag == "~":
                board.grid[i][j] = Wall((i, j), fixed=True)
            elif tag == "R":
                board.grid[i][j] = Tile((i, j), has_rat=True)
                board.rat_pos = (i, j)

    print('Initial Board:')
    for i in range(board.rows):
        row_str = ""
        for j in range(board.cols):
            row_str += board.grid[i][j].type + " "
        print(row_str)
    print("Solving\n")
    result = board.solve_puzzle()
    print("Walls placed:", board.wall_pos)
    print("Score:", board.score)
    
    print("\nFinal Board")
    for i in range(board.rows):
        row_str = ""
        for j in range(board.cols):
            row_str += board.grid[i][j].type + " "
        print(row_str)