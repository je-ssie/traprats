#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon May  4 16:38:55 2026

@author: jessie
"""

import unittest
import tempfile
import os
import math
from PIL import Image

from board import *
from tiles import *
from imgreader import *


class TestBoardInit(unittest.TestCase):
    """Tests for Board initialization."""

    def test_init_basic(self):
        """Test basic initialization with rows, cols, walls."""
        board = Board(rows=5, cols=5, walls=3)

        self.assertEqual(board.rows, 5)
        self.assertEqual(board.cols, 5)
        self.assertEqual(board.walls, 3)
        self.assertEqual(len(board.grid), 5)
        self.assertEqual(len(board.grid[0]), 5)

    def test_init_grid_tiles(self):
        """Test that grid is initialized with Tile objects."""
        board = Board(rows=3, cols=3, walls=2)

        for row in range(3):
            for col in range(3):
                self.assertIsInstance(board.grid[row][col], Tile)
                self.assertEqual(board.grid[row][col].pos, (row, col))

    def test_init_empty_lists(self):
        """Test that wall_pos and portals are initialized as empty lists."""
        board = Board(rows=5, cols=5, walls=3)

        self.assertEqual(board.wall_pos, [])
        self.assertEqual(board.portals, [])

    def test_init_rat_pos_none(self):
        """Test that rat_pos is None initially."""
        board = Board(rows=5, cols=5, walls=3)

        self.assertIsNone(board.rat_pos)

    def test_init_score_negative_infinity(self):
        """Test that initial score is negative infinity."""
        board = Board(rows=5, cols=5, walls=3)

        self.assertEqual(board.score, -math.inf)

    def test_init_with_puzzle_name(self):
        """Test initialization with puzzle_name."""
        board = Board(rows=5, cols=5, walls=3, puzzle_name="test_puzzle")

        self.assertEqual(board.puzzle_name, "test_puzzle")

    def test_init_different_dimensions(self):
        """Test initialization with non-square dimensions."""
        board = Board(rows=10, cols=15, walls=5)

        self.assertEqual(board.rows, 10)
        self.assertEqual(board.cols, 15)
        self.assertEqual(len(board.grid), 10)
        self.assertEqual(len(board.grid[0]), 15)

    def test_init_zero_walls(self):
        """Test initialization with zero walls."""
        board = Board(rows=5, cols=5, walls=0)

        self.assertEqual(board.walls, 0)

    def test_init_single_cell(self):
        """Test initialization with 1x1 board."""
        board = Board(rows=1, cols=1, walls=0)

        self.assertEqual(board.rows, 1)
        self.assertEqual(board.cols, 1)
        self.assertEqual(len(board.grid), 1)
        self.assertEqual(len(board.grid[0]), 1)


class TestBoardStr(unittest.TestCase):
    """Tests for Board __str__ method."""

    def test_str_basic(self):
        """Test string representation of basic board."""
        board = Board(rows=2, cols=2, walls=0)

        result = str(board)

        # Should have 2 lines (one per row)
        lines = result.strip().split('\n')
        self.assertEqual(len(lines), 2)

    def test_str_contains_tile_types(self):
        """Test that string contains tile type characters."""
        board = Board(rows=2, cols=2, walls=0)

        result = str(board)

        # Default tiles should have their type character
        self.assertIsInstance(result, str)
        self.assertGreater(len(result), 0)


class TestIsValidPosition(unittest.TestCase):
    """Tests for is_valid_position method."""

    def setUp(self):
        """Create a basic board for testing."""
        self.board = Board(rows=5, cols=5, walls=3)

    def test_valid_position_center(self):
        """Test that center position is valid."""
        self.assertTrue(self.board.is_valid_position((2, 2)))

    def test_valid_position_corners(self):
        """Test that corner positions are valid."""
        self.assertTrue(self.board.is_valid_position((0, 0)))
        self.assertTrue(self.board.is_valid_position((0, 4)))
        self.assertTrue(self.board.is_valid_position((4, 0)))
        self.assertTrue(self.board.is_valid_position((4, 4)))

    def test_invalid_position_negative_row(self):
        """Test that negative row is invalid."""
        self.assertFalse(self.board.is_valid_position((-1, 2)))

    def test_invalid_position_negative_col(self):
        """Test that negative column is invalid."""
        self.assertFalse(self.board.is_valid_position((2, -1)))

    def test_invalid_position_row_out_of_bounds(self):
        """Test that row >= rows is invalid."""
        self.assertFalse(self.board.is_valid_position((5, 2)))
        self.assertFalse(self.board.is_valid_position((10, 2)))

    def test_invalid_position_col_out_of_bounds(self):
        """Test that col >= cols is invalid."""
        self.assertFalse(self.board.is_valid_position((2, 5)))
        self.assertFalse(self.board.is_valid_position((2, 10)))

    def test_invalid_position_none(self):
        """Test that None position is invalid."""
        self.assertFalse(self.board.is_valid_position(None))

    def test_invalid_position_fixed_wall(self):
        """Test that fixed wall position is invalid."""
        self.board.grid[2][2] = Wall((2, 2), fixed=True)

        self.assertFalse(self.board.is_valid_position((2, 2)))

    def test_valid_position_non_fixed_wall(self):
        """Test that non-fixed wall position is valid."""
        self.board.grid[2][2] = Wall((2, 2), fixed=False)

        self.assertTrue(self.board.is_valid_position((2, 2)))


class TestGetNeighbors(unittest.TestCase):
    """Tests for get_neighbors method."""

    def setUp(self):
        """Create a basic board for testing."""
        self.board = Board(rows=5, cols=5, walls=3)

    def test_neighbors_center(self):
        """Test neighbors of center position."""
        neighbors = self.board.get_neighbors((2, 2))

        expected = [(2, 3), (2, 1), (1, 2), (3, 2)]
        self.assertEqual(sorted(neighbors), sorted(expected))

    def test_neighbors_corner(self):
        """Test neighbors of corner position."""
        neighbors = self.board.get_neighbors((0, 0))

        expected = [(0, 1), (1, 0)]
        self.assertEqual(sorted(neighbors), sorted(expected))

    def test_neighbors_edge(self):
        """Test neighbors of edge position."""
        neighbors = self.board.get_neighbors((0, 2))

        expected = [(0, 3), (0, 1), (1, 2)]
        self.assertEqual(sorted(neighbors), sorted(expected))

    def test_neighbors_with_fixed_wall(self):
        """Test that fixed walls are not included as neighbors."""
        self.board.grid[2][3] = Wall((2, 3), fixed=True)

        neighbors = self.board.get_neighbors((2, 2))

        self.assertNotIn((2, 3), neighbors)
        self.assertIn((2, 1), neighbors)
        self.assertIn((1, 2), neighbors)
        self.assertIn((3, 2), neighbors)

    def test_neighbors_with_portal(self):
        """Test that portal destinations are included as neighbors."""
        portal = Portal((1, 1), (3, 3), color='portal_blue')
        self.board.portals.append(portal)
        self.board.grid[1][1] = portal
        self.board.grid[3][3] = portal

        neighbors = self.board.get_neighbors((1, 1))

        # Should include portal destination
        self.assertIn((3, 3), neighbors)

    def test_neighbors_portal_bidirectional(self):
        """Test that portals work in both directions."""
        portal = Portal((1, 1), (3, 3), color='portal_blue')
        self.board.portals.append(portal)
        self.board.grid[1][1] = portal
        self.board.grid[3][3] = portal

        neighbors_from_entry = self.board.get_neighbors((1, 1))
        neighbors_from_exit = self.board.get_neighbors((3, 3))

        self.assertIn((3, 3), neighbors_from_entry)
        self.assertIn((1, 1), neighbors_from_exit)


class TestGetValidTiles(unittest.TestCase):
    """Tests for get_valid_tiles method."""

    def test_all_tiles_valid_empty_board(self):
        """Test that all tiles are valid on empty board."""
        board = Board(rows=3, cols=3, walls=0)

        valid = board.get_valid_tiles()

        self.assertEqual(len(valid), 9)

    def test_valid_tiles_with_fixed_wall(self):
        """Test that fixed walls are excluded."""
        board = Board(rows=3, cols=3, walls=0)
        board.grid[1][1] = Wall((1, 1), fixed=True)

        valid = board.get_valid_tiles()

        self.assertEqual(len(valid), 8)
        self.assertNotIn((1, 1), valid)

    def test_valid_tiles_with_multiple_fixed_walls(self):
        """Test with multiple fixed walls."""
        board = Board(rows=3, cols=3, walls=0)
        board.grid[0][0] = Wall((0, 0), fixed=True)
        board.grid[1][1] = Wall((1, 1), fixed=True)
        board.grid[2][2] = Wall((2, 2), fixed=True)

        valid = board.get_valid_tiles()

        self.assertEqual(len(valid), 6)
        self.assertNotIn((0, 0), valid)
        self.assertNotIn((1, 1), valid)
        self.assertNotIn((2, 2), valid)

    def test_valid_tiles_returns_list(self):
        """Test that method returns a list."""
        board = Board(rows=3, cols=3, walls=0)

        valid = board.get_valid_tiles()

        self.assertIsInstance(valid, list)

    def test_valid_tiles_positions_are_tuples(self):
        """Test that positions are tuples."""
        board = Board(rows=3, cols=3, walls=0)

        valid = board.get_valid_tiles()

        for pos in valid:
            self.assertIsInstance(pos, tuple)
            self.assertEqual(len(pos), 2)


class TestGetEdgeTiles(unittest.TestCase):
    """Tests for get_edge_tiles method."""

    def test_edge_tiles_3x3(self):
        """Test edge tiles on 3x3 board."""
        board = Board(rows=3, cols=3, walls=0)

        edges = board.get_edge_tiles()

        # All tiles except center should be edges
        expected = {(0, 0), (0, 1), (0, 2),
                    (1, 0),         (1, 2),
                    (2, 0), (2, 1), (2, 2)}
        self.assertEqual(edges, expected)

    def test_edge_tiles_5x5(self):
        """Test edge tiles on 5x5 board."""
        board = Board(rows=5, cols=5, walls=0)

        edges = board.get_edge_tiles()

        # Should have 16 edge tiles (perimeter of 5x5)
        self.assertEqual(len(edges), 16)

    def test_edge_tiles_excludes_fixed_wall(self):
        """Test that fixed walls on edges are excluded."""
        board = Board(rows=3, cols=3, walls=0)
        board.grid[0][0] = Wall((0, 0), fixed=True)

        edges = board.get_edge_tiles()

        self.assertNotIn((0, 0), edges)

    def test_edge_tiles_returns_set(self):
        """Test that method returns a set."""
        board = Board(rows=3, cols=3, walls=0)

        edges = board.get_edge_tiles()

        self.assertIsInstance(edges, set)

    def test_edge_tiles_1x1(self):
        """Test edge tiles on 1x1 board."""
        board = Board(rows=1, cols=1, walls=0)

        edges = board.get_edge_tiles()

        self.assertEqual(edges, {(0, 0)})

    def test_edge_tiles_non_square(self):
        """Test edge tiles on non-square board."""
        board = Board(rows=2, cols=4, walls=0)

        edges = board.get_edge_tiles()

        # All tiles in 2x4 board are edge tiles
        self.assertEqual(len(edges), 8)


class TestBuildAdjacencyGraph(unittest.TestCase):
    """Tests for build_adjacency_graph method."""

    def test_simple_2x2_board(self):
        """Test adjacency graph on 2x2 board."""
        board = Board(rows=2, cols=2, walls=0)
        valid_tiles = board.get_valid_tiles()
        pos_to_i = {pos: i for i, pos in enumerate(valid_tiles)}

        adj = board.build_adjacency_graph(valid_tiles, pos_to_i)

        self.assertEqual(len(adj), 4)
        # Each corner should have 2 neighbors
        for neighbors in adj:
            self.assertEqual(len(neighbors), 2)

    def test_adjacency_with_fixed_wall(self):
        """Test that fixed walls break adjacency."""
        board = Board(rows=3, cols=3, walls=0)
        board.grid[1][1] = Wall((1, 1), fixed=True)

        valid_tiles = board.get_valid_tiles()
        pos_to_i = {pos: i for i, pos in enumerate(valid_tiles)}

        adj = board.build_adjacency_graph(valid_tiles, pos_to_i)

        # Center is not in valid tiles
        self.assertEqual(len(valid_tiles), 8)

    def test_adjacency_with_portal(self):
        """Test that portals add adjacency connections."""
        board = Board(rows=5, cols=5, walls=0)
        portal = Portal((0, 0), (4, 4), color='portal_blue')
        board.portals.append(portal)
        board.grid[0][0] = portal
        board.grid[4][4] = portal

        valid_tiles = board.get_valid_tiles()
        pos_to_i = {pos: i for i, pos in enumerate(valid_tiles)}

        adj = board.build_adjacency_graph(valid_tiles, pos_to_i)

        # Check that (0,0) has (4,4) as neighbor via portal
        idx_00 = pos_to_i[(0, 0)]
        idx_44 = pos_to_i[(4, 4)]

        self.assertIn(idx_44, adj[idx_00])
        self.assertIn(idx_00, adj[idx_44])

    def test_adjacency_returns_list_of_lists(self):
        """Test that method returns list of lists."""
        board = Board(rows=3, cols=3, walls=0)
        valid_tiles = board.get_valid_tiles()
        pos_to_i = {pos: i for i, pos in enumerate(valid_tiles)}

        adj = board.build_adjacency_graph(valid_tiles, pos_to_i)

        self.assertIsInstance(adj, list)
        for neighbors in adj:
            self.assertIsInstance(neighbors, list)


class TestBoardWithSpecialTiles(unittest.TestCase):
    """Tests for board with special tile types."""

    def test_board_with_bee(self):
        """Test board with bee tile."""
        board = Board(rows=3, cols=3, walls=0)
        board.grid[1][1] = Bee((1, 1))

        self.assertIsInstance(board.grid[1][1], Bee)
        self.assertTrue(board.is_valid_position((1, 1)))

    def test_board_with_cherry(self):
        """Test board with cherry tile."""
        board = Board(rows=3, cols=3, walls=0)
        board.grid[1][1] = Cherry((1, 1))

        self.assertIsInstance(board.grid[1][1], Cherry)
        self.assertTrue(board.is_valid_position((1, 1)))

    def test_board_with_apple(self):
        """Test board with apple tile."""
        board = Board(rows=3, cols=3, walls=0)
        board.grid[1][1] = Apple((1, 1))

        self.assertIsInstance(board.grid[1][1], Apple)
        self.assertTrue(board.is_valid_position((1, 1)))

    def test_board_with_rat(self):
        """Test board with rat position set."""
        board = Board(rows=3, cols=3, walls=0)
        board.grid[1][1] = Tile((1, 1), has_rat=True)
        board.rat_pos = (1, 1)

        self.assertEqual(board.rat_pos, (1, 1))


class TestStats(unittest.TestCase):
    """Tests for stats method."""

    def test_stats_output(self):
        """Test that stats prints expected information."""
        import io
        import sys

        board = Board(rows=5, cols=5, walls=3, puzzle_name="test")
        board.score = 42

        # Capture stdout
        captured = io.StringIO()
        sys.stdout = captured

        board.stats()

        sys.stdout = sys.__stdout__
        output = captured.getvalue()

        self.assertIn("test", output)
        self.assertIn("5", output)
        self.assertIn("3", output)
        self.assertIn("42", output)


class TestSolvePuzzle(unittest.TestCase):
    """Tests for solve_puzzle method."""

    def test_solve_simple_puzzle(self):
        """Test solving a simple puzzle."""
        board = Board(rows=3, cols=3, walls=4)
        board.rat_pos = (1, 1)
        board.grid[1][1] = Tile((1, 1), has_rat=True)

        result = board.solve_puzzle()

        self.assertIsNotNone(result)
        self.assertIsInstance(result, tuple)
        self.assertEqual(len(result), 2)

    def test_solve_returns_wall_positions(self):
        """Test that solve returns wall positions."""
        board = Board(rows=3, cols=3, walls=4)
        board.rat_pos = (1, 1)
        board.grid[1][1] = Tile((1, 1), has_rat=True)

        wall_pos, score = board.solve_puzzle()

        self.assertIsInstance(wall_pos, list)

    def test_solve_respects_wall_limit(self):
        """Test that solution doesn't exceed wall limit."""
        board = Board(rows=5, cols=5, walls=4)
        board.rat_pos = (2, 2)
        board.grid[2][2] = Tile((2, 2), has_rat=True)

        wall_pos, score = board.solve_puzzle()

        self.assertLessEqual(len(wall_pos), 4)

    def test_solve_doesnt_place_wall_on_rat(self):
        """Test that no wall is placed on rat position."""
        board = Board(rows=3, cols=3, walls=4)
        board.rat_pos = (1, 1)
        board.grid[1][1] = Tile((1, 1), has_rat=True)

        wall_pos, score = board.solve_puzzle()

        self.assertNotIn((1, 1), wall_pos)

    def test_solve_doesnt_place_wall_on_portal(self):
        """Test that no wall is placed on portal positions."""
        board = Board(rows=5, cols=5, walls=4)
        board.rat_pos = (2, 2)
        board.grid[2][2] = Tile((2, 2), has_rat=True)

        portal = Portal((0, 0), (4, 4), color='portal_blue')
        board.portals.append(portal)
        board.grid[0][0] = portal
        board.grid[4][4] = portal

        wall_pos, score = board.solve_puzzle()

        self.assertNotIn((0, 0), wall_pos)
        self.assertNotIn((4, 4), wall_pos)

    def test_solve_updates_board_score(self):
        """Test that solving updates board score."""
        board = Board(rows=3, cols=3, walls=4)
        board.rat_pos = (1, 1)
        board.grid[1][1] = Tile((1, 1), has_rat=True)

        initial_score = board.score
        board.solve_puzzle()

        self.assertNotEqual(board.score, initial_score)
        self.assertNotEqual(board.score, -math.inf)

    def test_solve_places_walls_in_grid(self):
        """Test that walls are placed in the grid after solving."""
        board = Board(rows=3, cols=3, walls=4)
        board.rat_pos = (1, 1)
        board.grid[1][1] = Tile((1, 1), has_rat=True)

        wall_pos, score = board.solve_puzzle()

        for pos in wall_pos:
            row, col = pos
            self.assertIsInstance(board.grid[row][col], Wall)


class TestBoardWithImage(unittest.TestCase):
    """Tests for board creation from image (requires sprites)."""

    SPRITE_FOLDER = "sprites"

    @classmethod
    def setUpClass(cls):
        """Check if sprites folder exists."""
        if not os.path.exists(cls.SPRITE_FOLDER):
            raise unittest.SkipTest(
                f"Sprite folder '{cls.SPRITE_FOLDER}' not found")

    def _create_test_board_image(self, tile_grid, tile_size=64):
        """
        Create a test board image from a grid of tile types.

        Parameters
        ----------
        tile_grid : list of list of str
            2D grid of tile type names.
        tile_size : int
            Size of each tile in pixels.

        Returns
        -------
        str
            Path to created temporary image.
        """
        sprite_files = {
            'land': 'land.png',
            'water': 'water.png',
            'rat': 'horse.png',
            'bee': 'bees.png',
            'cherry': 'cherry.png',
            'apple': 'apple.png',
            'portal_sky': 'portal_sky.png',
            'portal_blue': 'portal_blue.png',
        }

        rows = len(tile_grid)
        cols = len(tile_grid[0])

        board_width = cols * tile_size
        board_height = rows * tile_size
        board_image = Image.new('RGB', (board_width, board_height))

        for row_idx, row in enumerate(tile_grid):
            for col_idx, tile_type in enumerate(row):
                sprite_path = os.path.join(
                    self.SPRITE_FOLDER, sprite_files[tile_type])

                if not os.path.exists(sprite_path):
                    self.skipTest(f"Sprite {sprite_path} not found")

                sprite = Image.open(sprite_path).convert('RGB')
                sprite = sprite.resize((tile_size, tile_size), Image.NEAREST)

                x = col_idx * tile_size
                y = row_idx * tile_size
                board_image.paste(sprite, (x, y))

        # Save to temp file
        fd, temp_path = tempfile.mkstemp(suffix='.png')
        os.close(fd)
        board_image.save(temp_path)

        return temp_path

    def test_create_board_from_image_simple(self):
        """Test creating board from simple land-only image."""
        tile_grid = [
            ['land', 'land', 'land'],
            ['land', 'rat', 'land'],
            ['land', 'land', 'land']
        ]

        try:
            temp_path = self._create_test_board_image(tile_grid)
            board = Board(rows=3, cols=3, walls=4, image_path=temp_path)

            self.assertEqual(board.rows, 3)
            self.assertEqual(board.cols, 3)
            self.assertEqual(board.rat_pos, (1, 1))
        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)

    def test_create_board_from_image_with_water(self):
        """Test creating board from image with water."""
        tile_grid = [
            ['land', 'water', 'land'],
            ['land', 'rat', 'land'],
            ['land', 'water', 'land']
        ]

        try:
            temp_path = self._create_test_board_image(tile_grid)
            board = Board(rows=3, cols=3, walls=4, image_path=temp_path)

            # Water should be fixed walls
            self.assertIsInstance(board.grid[0][1], Wall)
            self.assertTrue(board.grid[0][1].fixed)
            self.assertIsInstance(board.grid[2][1], Wall)
            self.assertTrue(board.grid[2][1].fixed)
        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)

    def test_create_board_from_image_with_items(self):
        """Test creating board from image with cherries, bees, apples."""
        tile_grid = [
            ['cherry', 'land', 'apple'],
            ['land', 'rat', 'land'],
            ['bee', 'land', 'land']
        ]

        try:
            temp_path = self._create_test_board_image(tile_grid)
            board = Board(rows=3, cols=3, walls=4, image_path=temp_path)

            self.assertIsInstance(board.grid[0][0], Cherry)
            self.assertIsInstance(board.grid[0][2], Apple)
            self.assertIsInstance(board.grid[2][0], Bee)
        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)

    def test_create_board_from_image_with_portals(self):
        """Test creating board from image with portals."""
        tile_grid = [
            ['portal_blue', 'land', 'land'],
            ['land', 'rat', 'land'],
            ['land', 'land', 'portal_blue']
        ]

        try:
            temp_path = self._create_test_board_image(tile_grid)
            board = Board(rows=3, cols=3, walls=4, image_path=temp_path)

            self.assertEqual(len(board.portals), 1)
            self.assertIsInstance(board.grid[0][0], Portal)
            self.assertIsInstance(board.grid[2][2], Portal)
        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)

    def test_create_board_sets_puzzle_name(self):
        """Test that puzzle_name is set from image path."""
        tile_grid = [
            ['land', 'land', 'land'],
            ['land', 'rat', 'land'],
            ['land', 'land', 'land']
        ]

        try:
            temp_path = self._create_test_board_image(tile_grid)
            board = Board(rows=3, cols=3, walls=4, image_path=temp_path)

            # puzzle_name should be path without .png
            expected_name = temp_path.replace('.png', '')
            self.assertEqual(board.puzzle_name, expected_name)
        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)


class TestEdgeCases(unittest.TestCase):
    """Tests for edge cases and boundary conditions."""

    def test_large_board(self):
        """Test creation of large board."""
        board = Board(rows=50, cols=50, walls=20)

        self.assertEqual(board.rows, 50)
        self.assertEqual(board.cols, 50)
        self.assertEqual(len(board.grid), 50)
        self.assertEqual(len(board.grid[0]), 50)

    def test_narrow_board(self):
        """Test creation of narrow board."""
        board = Board(rows=1, cols=10, walls=0)

        self.assertEqual(board.rows, 1)
        self.assertEqual(board.cols, 10)

    def test_tall_board(self):
        """Test creation of tall board."""
        board = Board(rows=10, cols=1, walls=0)

        self.assertEqual(board.rows, 10)
        self.assertEqual(board.cols, 1)

    def test_neighbors_1x1_board(self):
        """Test neighbors on 1x1 board."""
        board = Board(rows=1, cols=1, walls=0)

        neighbors = board.get_neighbors((0, 0))

        self.assertEqual(neighbors, [])

    def test_solve_minimal_board(self):
        """Test solving minimal 3x3 board."""
        board = Board(rows=3, cols=3, walls=8)
        board.rat_pos = (1, 1)
        board.grid[1][1] = Tile((1, 1), has_rat=True)

        wall_pos, score = board.solve_puzzle()

        # Should be able to enclose rat with 8 walls around it
        self.assertIsNotNone(wall_pos)


if __name__ == '__main__':
    unittest.main()
