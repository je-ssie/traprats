#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon May  4 14:29:02 2026

@author: jessie
"""

import unittest
import os
import tempfile
from PIL import Image
from imgreader import *
from board import *
from tiles import *


class TestBoardParserInit(unittest.TestCase):
    """Tests for BoardParser initialization."""
    
    def setUp(self):
        """Create a temporary test image before each test."""
        self.temp_dir = tempfile.mkdtemp()
        self.test_image_path = os.path.join(self.temp_dir, "test_board.png")
        
        # Create a simple 100x100 green image (land)
        img = Image.new('RGB', (100, 100), color=(80, 140, 80))
        img.save(self.test_image_path)
    
    def tearDown(self):
        """Clean up temporary files after each test."""
        if os.path.exists(self.test_image_path):
            os.remove(self.test_image_path)
        os.rmdir(self.temp_dir)
    
    def test_init_loads_image(self):
        """Test that initialization loads the image correctly."""
        parser = BoardParser(self.test_image_path, rows=10, cols=10)
        
        self.assertEqual(parser.width, 100)
        self.assertEqual(parser.height, 100)
        self.assertEqual(parser.rows, 10)
        self.assertEqual(parser.cols, 10)
    
    def test_init_calculates_tile_dimensions(self):
        """Test that tile dimensions are calculated correctly."""
        parser = BoardParser(self.test_image_path, rows=10, cols=10)
        
        self.assertEqual(parser.tile_width, 10.0)
        self.assertEqual(parser.tile_height, 10.0)
    
    def test_init_non_square_tiles(self):
        """Test initialization with non-square tile dimensions."""
        parser = BoardParser(self.test_image_path, rows=5, cols=10)
        
        self.assertEqual(parser.tile_width, 10.0)
        self.assertEqual(parser.tile_height, 20.0)
    
    def test_init_invalid_path_raises_error(self):
        """Test that invalid image path raises an error."""
        with self.assertRaises(FileNotFoundError):
            BoardParser("nonexistent_image.png", rows=10, cols=10)
            
            
class TestGetTileBounds(unittest.TestCase):
    """Tests for _get_tile_bounds method."""
    
    def setUp(self):
        """Create a temporary test image."""
        self.temp_dir = tempfile.mkdtemp()
        self.test_image_path = os.path.join(self.temp_dir, "test_board.png")
        
        img = Image.new('RGB', (100, 100), color=(80, 140, 80))
        img.save(self.test_image_path)
        
        self.parser = BoardParser(self.test_image_path, rows=10, cols=10)
    
    def tearDown(self):
        """Clean up temporary files."""
        os.remove(self.test_image_path)
        os.rmdir(self.temp_dir)
    
    def test_first_tile_bounds(self):
        """Test bounds for the first tile (0, 0)."""
        x1, y1, x2, y2 = self.parser._get_tile_bounds(0, 0)
        
        self.assertEqual(x1, 0)
        self.assertEqual(y1, 0)
        self.assertEqual(x2, 10)
        self.assertEqual(y2, 10)
    
    def test_middle_tile_bounds(self):
        """Test bounds for a middle tile."""
        x1, y1, x2, y2 = self.parser._get_tile_bounds(5, 5)
        
        self.assertEqual(x1, 50)
        self.assertEqual(y1, 50)
        self.assertEqual(x2, 60)
        self.assertEqual(y2, 60)
    
    def test_last_tile_bounds(self):
        """Test bounds for the last tile."""
        x1, y1, x2, y2 = self.parser._get_tile_bounds(9, 9)
        
        self.assertEqual(x1, 90)
        self.assertEqual(y1, 90)
        self.assertEqual(x2, 100)
        self.assertEqual(y2, 100)

class TestColorMatches(unittest.TestCase):
    """Tests for _color_matches method."""
    
    def setUp(self):
        """Create a temporary test image."""
        self.temp_dir = tempfile.mkdtemp()
        self.test_image_path = os.path.join(self.temp_dir, "test_board.png")
        
        img = Image.new('RGB', (100, 100), color=(80, 140, 80))
        img.save(self.test_image_path)
        
        self.parser = BoardParser(self.test_image_path, rows=10, cols=10)
    
    def tearDown(self):
        """Clean up temporary files."""
        os.remove(self.test_image_path)
        os.rmdir(self.temp_dir)
    
    def test_land_color_matches(self):
        """Test that land color is detected correctly."""
        # Land range: r(40-120), g(100-180), b(40-120)
        self.assertTrue(self.parser._color_matches(80, 140, 80, 'land'))
        self.assertTrue(self.parser._color_matches(40, 100, 40, 'land'))
        self.assertTrue(self.parser._color_matches(120, 180, 120, 'land'))
    
    def test_land_color_outside_range(self):
        """Test that colors outside land range don't match."""
        self.assertFalse(self.parser._color_matches(200, 200, 200, 'land'))
        self.assertFalse(self.parser._color_matches(0, 0, 0, 'land'))
    
    def test_water_color_matches(self):
        """Test that water color is detected correctly."""
        # Water range: r(0-30), g(40-100), b(70-130)
        self.assertTrue(self.parser._color_matches(15, 70, 100, 'water'))
        self.assertTrue(self.parser._color_matches(0, 40, 70, 'water'))
        self.assertTrue(self.parser._color_matches(30, 100, 130, 'water'))
    
    def test_water_color_outside_range(self):
        """Test that colors outside water range don't match."""
        self.assertFalse(self.parser._color_matches(80, 140, 80, 'water'))
    
    def test_rat_color_matches(self):
        """Test that rat (white) color is detected correctly."""
        # Rat range: r(200-255), g(200-255), b(200-255)
        self.assertTrue(self.parser._color_matches(255, 255, 255, 'rat'))
        self.assertTrue(self.parser._color_matches(200, 200, 200, 'rat'))
        self.assertTrue(self.parser._color_matches(230, 240, 220, 'rat'))
    
    def test_cherry_color_matches(self):
        """Test that cherry (red) color is detected correctly."""
        # Cherry range: r(150-255), g(0-80), b(0-80)
        self.assertTrue(self.parser._color_matches(200, 30, 30, 'cherry'))
        self.assertTrue(self.parser._color_matches(255, 0, 0, 'cherry'))
    
    def test_bee_color_matches(self):
        """Test that bee (yellow/orange) color is detected correctly."""
        # Bee range: r(200-255), g(180-255), b(0-100)
        self.assertTrue(self.parser._color_matches(255, 200, 50, 'bee'))
    
    def test_apple_color_matches(self):
        """Test that apple color is detected correctly."""
        # Apple range: r(200-255), g(200-255), b(0-100)
        self.assertTrue(self.parser._color_matches(230, 230, 50, 'apple'))
    
    def test_portal_sky_color_matches(self):
        """Test that portal_sky color is detected correctly."""
        # Portal sky range: r(100-200), g(200-255), b(220-255)
        self.assertTrue(self.parser._color_matches(150, 230, 240, 'portal_sky'))
    
    def test_portal_blue_color_matches(self):
        """Test that portal_blue color is detected correctly."""
        # Portal blue range: r(30-160), g(80-165), b(200-255)
        self.assertTrue(self.parser._color_matches(100, 120, 230, 'portal_blue'))

class TestIsPortalType(unittest.TestCase):
    """Tests for _is_portal_type method."""
    
    def setUp(self):
        """Create a temporary test image."""
        self.temp_dir = tempfile.mkdtemp()
        self.test_image_path = os.path.join(self.temp_dir, "test_board.png")
        
        img = Image.new('RGB', (100, 100), color=(80, 140, 80))
        img.save(self.test_image_path)
        
        self.parser = BoardParser(self.test_image_path, rows=10, cols=10)
    
    def tearDown(self):
        """Clean up temporary files."""
        os.remove(self.test_image_path)
        os.rmdir(self.temp_dir)
    
    def test_portal_types_return_true(self):
        """Test that all portal types return True."""
        portal_types = [
            'portal_sky', 'portal_blue', 'portal_purple',
            'portal_orange', 'portal_red', 'portal_magenta'
        ]
        
        for portal_type in portal_types:
            self.assertTrue(self.parser._is_portal_type(portal_type))
    
    def test_non_portal_types_return_false(self):
        """Test that non-portal types return False."""
        non_portal_types = ['land', 'water', 'rat', 'bee', 'cherry', 'apple']
        
        for tile_type in non_portal_types:
            self.assertFalse(self.parser._is_portal_type(tile_type))
    
    def test_empty_string_returns_false(self):
        """Test that empty string returns False."""
        self.assertFalse(self.parser._is_portal_type(''))
    
    def test_partial_match_returns_false(self):
        """Test that partial matches don't count."""
        self.assertFalse(self.parser._is_portal_type('portal'))
        self.assertFalse(self.parser._is_portal_type('blue_portal'))
        

class TestBoardParserWithSprites(unittest.TestCase):
    """Tests for BoardParser using actual sprite images."""
    
    SPRITE_FOLDER = "sprites"
    
    # Map tile types to sprite filenames (matching your BoardVisualizer)
    SPRITE_FILES = {
        'land': 'land.png',
        'water': 'water.png',
        'rat': 'horse.png',
        'bee': 'bees.png',
        'cherry': 'cherry.png',
        'apple': 'apple.png',
        'portal_sky': 'portal_sky.png',
        'portal_blue': 'portal_blue.png',
        'portal_purple': 'portal_purple.png',
        'portal_orange': 'portal_orange.png',
        'portal_red': 'portal_red.png',
        'portal_magenta': 'portal_magenta.png',
    }
    
    @classmethod
    def setUpClass(cls):
        """Verify sprite folder exists and check available sprites."""
        if not os.path.exists(cls.SPRITE_FOLDER):
            raise unittest.SkipTest(f"Sprite folder '{cls.SPRITE_FOLDER}' not found")
        
        # Track which sprites are available
        cls.available_sprites = {}
        for tile_type, filename in cls.SPRITE_FILES.items():
            path = os.path.join(cls.SPRITE_FOLDER, filename)
            if os.path.exists(path):
                cls.available_sprites[tile_type] = path
            else:
                print(f"Warning: Sprite not found: {path}")
    
    def _create_board_from_sprites(self, tile_grid, tile_size=64):
        """
        Create a test board image from a grid of tile types.
        
        Parameters
        ----------
        tile_grid : list of list of str
            2D grid of tile type names (e.g., [['land', 'water'], ['cherry', 'land']])
        tile_size : int
            Size to use for each tile
        
        Returns
        -------
        str
            Path to the created temporary image
        """
        rows = len(tile_grid)
        cols = len(tile_grid[0])
        
        # Create board image
        board_width = cols * tile_size
        board_height = rows * tile_size
        board_image = Image.new('RGB', (board_width, board_height))
        
        for row_idx, row in enumerate(tile_grid):
            for col_idx, tile_type in enumerate(row):
                if tile_type not in self.available_sprites:
                    self.skipTest(f"Required sprite '{tile_type}' not available")
                
                # Load and resize sprite
                sprite_path = self.available_sprites[tile_type]
                sprite = Image.open(sprite_path).convert('RGB')
                sprite = sprite.resize((tile_size, tile_size), Image.NEAREST)
                
                # Paste onto board
                x = col_idx * tile_size
                y = row_idx * tile_size
                board_image.paste(sprite, (x, y))
        
        # Save to temp file
        temp_path = os.path.join(self.SPRITE_FOLDER, "_test_board_temp.png")
        board_image.save(temp_path)
        
        return temp_path
    
    def tearDown(self):
        """Clean up temporary test images."""
        temp_path = os.path.join(self.SPRITE_FOLDER, "_test_board_temp.png")
        if os.path.exists(temp_path):
            os.remove(temp_path)


class TestClassifyTileWithSprites(TestBoardParserWithSprites):
    """Test tile classification using actual sprites."""
    
    def test_classify_land_sprite(self):
        """Test classification of land tile using actual sprite."""
        if 'land' not in self.available_sprites:
            self.skipTest("Land sprite not available")
        
        path = self._create_board_from_sprites([['land']])
        parser = BoardParser(path, rows=1, cols=1)
        
        result = parser._classify_tile(0, 0)
        self.assertEqual(result, 'land')
    
    def test_classify_water_sprite(self):
        """Test classification of water tile using actual sprite."""
        if 'water' not in self.available_sprites:
            self.skipTest("Water sprite not available")
        
        path = self._create_board_from_sprites([['water']])
        parser = BoardParser(path, rows=1, cols=1)
        
        result = parser._classify_tile(0, 0)
        self.assertEqual(result, 'water')
    
    def test_classify_rat_sprite(self):
        """Test classification of rat/horse tile using actual sprite."""
        if 'rat' not in self.available_sprites:
            self.skipTest("Rat/horse sprite not available")
        
        path = self._create_board_from_sprites([['rat']])
        parser = BoardParser(path, rows=1, cols=1)
        
        result = parser._classify_tile(0, 0)
        self.assertEqual(result, 'rat')
    
    def test_classify_bee_sprite(self):
        """Test classification of bee tile using actual sprite."""
        if 'bee' not in self.available_sprites:
            self.skipTest("Bee sprite not available")
        
        path = self._create_board_from_sprites([['bee']])
        parser = BoardParser(path, rows=1, cols=1)
        
        result = parser._classify_tile(0, 0)
        self.assertEqual(result, 'bee')
    
    def test_classify_cherry_sprite(self):
        """Test classification of cherry tile using actual sprite."""
        if 'cherry' not in self.available_sprites:
            self.skipTest("Cherry sprite not available")
        
        path = self._create_board_from_sprites([['cherry']])
        parser = BoardParser(path, rows=1, cols=1)
        
        result = parser._classify_tile(0, 0)
        self.assertEqual(result, 'cherry')
    
    def test_classify_apple_sprite(self):
        """Test classification of apple tile using actual sprite."""
        if 'apple' not in self.available_sprites:
            self.skipTest("Apple sprite not available")
        
        path = self._create_board_from_sprites([['apple']])
        parser = BoardParser(path, rows=1, cols=1)
        
        result = parser._classify_tile(0, 0)
        self.assertEqual(result, 'apple')
    
    def test_classify_portal_sky_sprite(self):
        """Test classification of sky portal using actual sprite."""
        if 'portal_sky' not in self.available_sprites:
            self.skipTest("Portal sky sprite not available")
        
        path = self._create_board_from_sprites([['portal_sky']])
        parser = BoardParser(path, rows=1, cols=1)
        
        result = parser._classify_tile(0, 0)
        self.assertEqual(result, 'portal_sky')
    
    def test_classify_portal_blue_sprite(self):
        """Test classification of blue portal using actual sprite."""
        if 'portal_blue' not in self.available_sprites:
            self.skipTest("Portal blue sprite not available")
        
        path = self._create_board_from_sprites([['portal_blue']])
        parser = BoardParser(path, rows=1, cols=1)
        
        result = parser._classify_tile(0, 0)
        self.assertEqual(result, 'portal_blue')
    
    def test_classify_portal_purple_sprite(self):
        """Test classification of purple portal using actual sprite."""
        if 'portal_purple' not in self.available_sprites:
            self.skipTest("Portal purple sprite not available")
        
        path = self._create_board_from_sprites([['portal_purple']])
        parser = BoardParser(path, rows=1, cols=1)
        
        result = parser._classify_tile(0, 0)
        self.assertEqual(result, 'portal_purple')
    
    def test_classify_portal_orange_sprite(self):
        """Test classification of orange portal using actual sprite."""
        if 'portal_orange' not in self.available_sprites:
            self.skipTest("Portal orange sprite not available")
        
        path = self._create_board_from_sprites([['portal_orange']])
        parser = BoardParser(path, rows=1, cols=1)
        
        result = parser._classify_tile(0, 0)
        self.assertEqual(result, 'portal_orange')
    
    def test_classify_portal_red_sprite(self):
        """Test classification of red portal using actual sprite."""
        if 'portal_red' not in self.available_sprites:
            self.skipTest("Portal red sprite not available")
        
        path = self._create_board_from_sprites([['portal_red']])
        parser = BoardParser(path, rows=1, cols=1)
        
        result = parser._classify_tile(0, 0)
        self.assertEqual(result, 'portal_red')
    
    def test_classify_portal_magenta_sprite(self):
        """Test classification of magenta portal using actual sprite."""
        if 'portal_magenta' not in self.available_sprites:
            self.skipTest("Portal magenta sprite not available")
        
        path = self._create_board_from_sprites([['portal_magenta']])
        parser = BoardParser(path, rows=1, cols=1)
        
        result = parser._classify_tile(0, 0)
        self.assertEqual(result, 'portal_magenta')
    
    def test_classify_all_available_sprites(self):
        """Test that all available sprites are classified correctly."""
        for tile_type, sprite_path in self.available_sprites.items():
            with self.subTest(tile_type=tile_type):
                path = self._create_board_from_sprites([[tile_type]])
                parser = BoardParser(path, rows=1, cols=1)
                
                result = parser._classify_tile(0, 0)
                self.assertEqual(result, tile_type, 
                    f"Expected {tile_type}, got {result}")


class TestParseWithSprites(TestBoardParserWithSprites):
    """Test full board parsing using actual sprites."""
    
    def test_parse_simple_land_board(self):
        """Test parsing a board of all land tiles."""
        if 'land' not in self.available_sprites:
            self.skipTest("Land sprite not available")
        
        tile_grid = [
            ['land', 'land', 'land'],
            ['land', 'land', 'land'],
            ['land', 'land', 'land']
        ]
        
        path = self._create_board_from_sprites(tile_grid)
        parser = BoardParser(path, rows=3, cols=3)
        result = parser.parse()
        
        self.assertEqual(result['rows'], 3)
        self.assertEqual(result['cols'], 3)
        self.assertEqual(len(result['water']), 0)
        self.assertIsNone(result['rat_pos'])
    
    def test_parse_board_with_water(self):
        """Test parsing a board containing water tiles."""
        if 'land' not in self.available_sprites or 'water' not in self.available_sprites:
            self.skipTest("Required sprites not available")
        
        tile_grid = [
            ['land', 'water', 'land'],
            ['water', 'land', 'water'],
            ['land', 'water', 'land']
        ]
        
        path = self._create_board_from_sprites(tile_grid)
        parser = BoardParser(path, rows=3, cols=3)
        result = parser.parse()
        
        expected_water = [(0, 1), (1, 0), (1, 2), (2, 1)]
        self.assertEqual(sorted(result['water']), sorted(expected_water))
    
    def test_parse_board_with_rat(self):
        """Test parsing a board containing the rat/horse."""
        if 'land' not in self.available_sprites or 'rat' not in self.available_sprites:
            self.skipTest("Required sprites not available")
        
        tile_grid = [
            ['land', 'land', 'land'],
            ['land', 'rat', 'land'],
            ['land', 'land', 'land']
        ]
        
        path = self._create_board_from_sprites(tile_grid)
        parser = BoardParser(path, rows=3, cols=3)
        result = parser.parse()
        
        self.assertEqual(result['rat_pos'], (1, 1))
    
    def test_parse_board_with_items(self):
        """Test parsing a board with cherries, apples, and bees."""
        required = ['land', 'cherry', 'apple', 'bee']
        for sprite in required:
            if sprite not in self.available_sprites:
                self.skipTest(f"Required sprite '{sprite}' not available")
        
        tile_grid = [
            ['cherry', 'land', 'apple'],
            ['land', 'bee', 'land'],
            ['apple', 'land', 'cherry']
        ]
        
        path = self._create_board_from_sprites(tile_grid)
        parser = BoardParser(path, rows=3, cols=3)
        result = parser.parse()
        
        expected_cherries = [(0, 0), (2, 2)]
        expected_apples = [(0, 2), (2, 0)]
        expected_bees = [(1, 1)]
        
        self.assertEqual(sorted(result['cherries']), sorted(expected_cherries))
        self.assertEqual(sorted(result['apples']), sorted(expected_apples))
        self.assertEqual(sorted(result['bees']), sorted(expected_bees))
    
    def test_parse_board_with_portal_pair(self):
        """Test parsing a board with a pair of portals."""
        if 'land' not in self.available_sprites or 'portal_sky' not in self.available_sprites:
            self.skipTest("Required sprites not available")
        
        tile_grid = [
            ['portal_sky', 'land', 'land'],
            ['land', 'land', 'land'],
            ['land', 'land', 'portal_sky']
        ]
        
        path = self._create_board_from_sprites(tile_grid)
        parser = BoardParser(path, rows=3, cols=3)
        result = parser.parse()
        
        self.assertEqual(len(result['portals']), 1)
        self.assertEqual(result['portals'][0]['color'], 'portal_sky')
        
        portal_positions = [result['portals'][0]['entry'], result['portals'][0]['exit']]
        self.assertIn((0, 0), portal_positions)
        self.assertIn((2, 2), portal_positions)
    
    def test_parse_board_with_multiple_portal_colors(self):
        """Test parsing a board with multiple portal color pairs."""
        required = ['land', 'portal_sky', 'portal_blue']
        for sprite in required:
            if sprite not in self.available_sprites:
                self.skipTest(f"Required sprite '{sprite}' not available")
        
        tile_grid = [
            ['portal_sky', 'land', 'portal_blue'],
            ['land', 'land', 'land'],
            ['portal_blue', 'land', 'portal_sky']
        ]
        
        path = self._create_board_from_sprites(tile_grid)
        parser = BoardParser(path, rows=3, cols=3)
        result = parser.parse()
        
        self.assertEqual(len(result['portals']), 2)
        
        portal_colors = [p['color'] for p in result['portals']]
        self.assertIn('portal_sky', portal_colors)
        self.assertIn('portal_blue', portal_colors)
    
    def test_parse_complex_board(self):
        """Test parsing a complex board with multiple element types."""
        required = ['land', 'water', 'rat', 'cherry', 'bee', 'portal_sky']
        for sprite in required:
            if sprite not in self.available_sprites:
                self.skipTest(f"Required sprite '{sprite}' not available")
        
        tile_grid = [
            ['portal_sky', 'land', 'water', 'land', 'cherry'],
            ['land', 'rat', 'land', 'bee', 'land'],
            ['water', 'land', 'land', 'land', 'water'],
            ['land', 'cherry', 'land', 'bee', 'land'],
            ['land', 'land', 'water', 'land', 'portal_sky']
        ]
        
        path = self._create_board_from_sprites(tile_grid)
        parser = BoardParser(path, rows=5, cols=5)
        result = parser.parse()
        
        # Verify dimensions
        self.assertEqual(result['rows'], 5)
        self.assertEqual(result['cols'], 5)
        
        # Verify rat position
        self.assertEqual(result['rat_pos'], (1, 1))
        
        # Verify water positions
        expected_water = [(0, 2), (2, 0), (2, 4), (4, 2)]
        self.assertEqual(sorted(result['water']), sorted(expected_water))
        
        # Verify cherries
        expected_cherries = [(0, 4), (3, 1)]
        self.assertEqual(sorted(result['cherries']), sorted(expected_cherries))
        
        # Verify bees
        expected_bees = [(1, 3), (3, 3)]
        self.assertEqual(sorted(result['bees']), sorted(expected_bees))
        
        # Verify portals
        self.assertEqual(len(result['portals']), 1)
        self.assertEqual(result['portals'][0]['color'], 'portal_sky')
    
    def test_parse_unpaired_portal_raises_exception(self):
        """Test that single portal raises exception."""
        if 'land' not in self.available_sprites or 'portal_sky' not in self.available_sprites:
            self.skipTest("Required sprites not available")
        
        tile_grid = [
            ['portal_sky', 'land', 'land'],
            ['land', 'land', 'land'],
            ['land', 'land', 'land']
        ]
        
        path = self._create_board_from_sprites(tile_grid)
        parser = BoardParser(path, rows=3, cols=3)
        
        with self.assertRaises(Exception) as context:
            parser.parse()
        
        self.assertIn('Unpaired', str(context.exception))
    
    def test_parse_too_many_same_color_portals_raises_exception(self):
        """Test that 3+ portals of same color raises exception."""
        if 'land' not in self.available_sprites or 'portal_sky' not in self.available_sprites:
            self.skipTest("Required sprites not available")
        
        tile_grid = [
            ['portal_sky', 'land', 'portal_sky'],
            ['land', 'land', 'land'],
            ['portal_sky', 'land', 'land']
        ]
        
        path = self._create_board_from_sprites(tile_grid)
        parser = BoardParser(path, rows=3, cols=3)
        
        with self.assertRaises(Exception) as context:
            parser.parse()
        
        self.assertIn('Too many', str(context.exception))


class TestColorDetectionWithSprites(TestBoardParserWithSprites):
    """Test color detection ratios using actual sprites."""
    
    def test_land_sprite_color_ratio(self):
        """Test that land sprite has high land color ratio."""
        if 'land' not in self.available_sprites:
            self.skipTest("Land sprite not available")
        
        path = self._create_board_from_sprites([['land']])
        parser = BoardParser(path, rows=1, cols=1)
        
        ratio = parser._detect_color_ratio(0, 0, 'land', use_center=True)
        
        # Land sprite should have significant land color
        self.assertGreater(ratio, 0.1, 
            f"Land sprite should have land color ratio > 0.1, got {ratio}")
    
    def test_water_sprite_color_ratio(self):
        """Test that water sprite has high water color ratio."""
        if 'water' not in self.available_sprites:
            self.skipTest("Water sprite not available")
        
        path = self._create_board_from_sprites([['water']])
        parser = BoardParser(path, rows=1, cols=1)
        
        ratio = parser._detect_color_ratio(0, 0, 'water', use_center=True)
        
        self.assertGreater(ratio, 0.03,
            f"Water sprite should have water color ratio > 0.03, got {ratio}")
    
    def test_sprites_dont_match_wrong_colors(self):
        """Test that sprites don't significantly match wrong color types."""
        if 'land' not in self.available_sprites:
            self.skipTest("Land sprite not available")
        
        path = self._create_board_from_sprites([['land']])
        parser = BoardParser(path, rows=1, cols=1)
        
        # Land shouldn't match water
        water_ratio = parser._detect_color_ratio(0, 0, 'water', use_center=True)
        self.assertLess(water_ratio, 0.03,
            f"Land sprite shouldn't match water, got ratio {water_ratio}")
    
    def test_color_sample_on_sprites(self):
        """Test get_color_sample returns valid data for sprites."""
        for tile_type in list(self.available_sprites.keys())[:3]:  # Test first 3 available
            with self.subTest(tile_type=tile_type):
                path = self._create_board_from_sprites([[tile_type]])
                parser = BoardParser(path, rows=1, cols=1)
                
                center_rgb, avg_rgb = parser.get_color_sample(0, 0)
                
                # Verify RGB values are valid
                for rgb in [center_rgb, avg_rgb]:
                    self.assertEqual(len(rgb), 3)
                    for val in rgb:
                        self.assertGreaterEqual(val, 0)
                        self.assertLessEqual(val, 255)


class TestDifferentTileSizes(TestBoardParserWithSprites):
    """Test parsing works with different tile sizes."""
    
    def test_small_tiles(self):
        """Test parsing with small tile size (32px)."""
        if 'land' not in self.available_sprites or 'water' not in self.available_sprites:
            self.skipTest("Required sprites not available")
        
        tile_grid = [
            ['land', 'water'],
            ['water', 'land']
        ]
        
        path = self._create_board_from_sprites(tile_grid, tile_size=32)
        parser = BoardParser(path, rows=2, cols=2)
        result = parser.parse()
        
        expected_water = [(0, 1), (1, 0)]
        self.assertEqual(sorted(result['water']), sorted(expected_water))
    
    def test_large_tiles(self):
        """Test parsing with large tile size (128px)."""
        if 'land' not in self.available_sprites or 'cherry' not in self.available_sprites:
            self.skipTest("Required sprites not available")
        
        tile_grid = [
            ['land', 'cherry'],
            ['cherry', 'land']
        ]
        
        path = self._create_board_from_sprites(tile_grid, tile_size=128)
        parser = BoardParser(path, rows=2, cols=2)
        result = parser.parse()
        
        expected_cherries = [(0, 1), (1, 0)]
        self.assertEqual(sorted(result['cherries']), sorted(expected_cherries))


class TestEdgeCases(TestBoardParserWithSprites):
    """Test edge cases using actual sprites."""
    
    def test_single_tile_board(self):
        """Test parsing a 1x1 board."""
        if 'land' not in self.available_sprites:
            self.skipTest("Land sprite not available")
        
        path = self._create_board_from_sprites([['land']])
        parser = BoardParser(path, rows=1, cols=1)
        result = parser.parse()
        
        self.assertEqual(result['rows'], 1)
        self.assertEqual(result['cols'], 1)
        self.assertEqual(len(result['grid']), 1)
        self.assertEqual(len(result['grid'][0]), 1)
    
    def test_single_row_board(self):
        """Test parsing a board with single row."""
        if 'land' not in self.available_sprites or 'water' not in self.available_sprites:
            self.skipTest("Required sprites not available")
        
        tile_grid = [['land', 'water', 'land', 'water', 'land']]
        
        path = self._create_board_from_sprites(tile_grid)
        parser = BoardParser(path, rows=1, cols=5)
        result = parser.parse()
        
        self.assertEqual(result['rows'], 1)
        self.assertEqual(result['cols'], 5)
        expected_water = [(0, 1), (0, 3)]
        self.assertEqual(sorted(result['water']), sorted(expected_water))
    
    def test_single_column_board(self):
        """Test parsing a board with single column."""
        if 'land' not in self.available_sprites or 'water' not in self.available_sprites:
            self.skipTest("Required sprites not available")
        
        tile_grid = [['land'], ['water'], ['land'], ['water'], ['land']]
        
        path = self._create_board_from_sprites(tile_grid)
        parser = BoardParser(path, rows=5, cols=1)
        result = parser.parse()
        
        self.assertEqual(result['rows'], 5)
        self.assertEqual(result['cols'], 1)
        expected_water = [(1, 0), (3, 0)]
        self.assertEqual(sorted(result['water']), sorted(expected_water))

class TestGetColorSample(unittest.TestCase):
    """Tests for get_color_sample method."""
    
    def setUp(self):
        """Create a temporary test image."""
        self.temp_dir = tempfile.mkdtemp()
        self.test_image_path = os.path.join(self.temp_dir, "test_board.png")
        
        img = Image.new('RGB', (100, 100), color=(80, 140, 80))
        img.save(self.test_image_path)
        
        self.parser = BoardParser(self.test_image_path, rows=10, cols=10)
    
    def tearDown(self):
        """Clean up temporary files."""
        os.remove(self.test_image_path)
        os.rmdir(self.temp_dir)
    
    def test_get_color_sample_returns_tuple(self):
        """Test that get_color_sample returns correct tuple structure."""
        center_rgb, avg_rgb = self.parser.get_color_sample(0, 0)
        
        self.assertIsInstance(center_rgb, tuple)
        self.assertIsInstance(avg_rgb, tuple)
        self.assertEqual(len(center_rgb), 3)
        self.assertEqual(len(avg_rgb), 3)
    
    def test_get_color_sample_solid_color(self):
        """Test color sample on solid color tile."""
        center_rgb, avg_rgb = self.parser.get_color_sample(0, 0)
        
        # For solid color image, center and average should be the same
        self.assertEqual(center_rgb, (80, 140, 80))
        self.assertEqual(avg_rgb, (80, 140, 80))

if __name__ == '__main__':
    unittest.main()