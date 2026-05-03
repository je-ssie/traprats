

from PIL import Image
import math

class BoardParser:
    """
    Parses an image of the enclose.horse board using Pillow.
    """
    
    # Color ranges in RGB (min_r, max_r, min_g, max_g, min_b, max_b)
    COLOR_RANGES = {
        'water': {
            'r': (0, 30),
            'g': (40, 100),
            'b': (70, 130)
        },
        'horse': {
            'r': (200, 255),
            'g': (200, 255),
            'b': (200, 255)
        },
        'bee': {
            'r': (200, 255),
            'g': (180, 255),
            'b': (0, 100)
        },
        'cherry': {
            'r': (150, 255),
            'g': (0, 80),
            'b': (0, 80)
        },
        'apple': {
            'r': (200, 255),
            'g': (200, 255),
            'b': (0, 100)
        },
        'portal': {
            'r': (100, 200),
            'g': (200, 255),
            'b': (220, 255)
        },
        'land': {
            'r': (40, 120),
            'g': (100, 180),
            'b': (40, 120)
        }
    }
    
    def __init__(self, image_path, rows, cols):
        """
        Initialize the parser with an image.
        
        Parameters
        ----------
        image_path : str
            Path to the board image
        rows : int
            Number of rows in the board
        cols : int
            Number of columns in the board
        """
        self.image = Image.open(image_path).convert('RGB')
        self.width, self.height = self.image.size
        self.pixels = self.image.load()
        
        self.rows = rows
        self.cols = cols
        
        self.tile_height = self.height / self.rows
        self.tile_width = self.width / self.cols
        
        print(f"Image size: {self.width}x{self.height}")
        print(f"Tile size: {self.tile_width:.1f}x{self.tile_height:.1f}")
    
    def _get_tile_bounds(self, row, col):
        """Get pixel boundaries for a tile."""
        x1 = int(col * self.tile_width)
        x2 = int((col + 1) * self.tile_width)
        y1 = int(row * self.tile_height)
        y2 = int((row + 1) * self.tile_height)
        return x1, y1, x2, y2
    
    def _color_matches(self, r, g, b, color_name):
        """Check if an RGB color matches a color range."""
        ranges = self.COLOR_RANGES[color_name]
        return (ranges['r'][0] <= r <= ranges['r'][1] and
                ranges['g'][0] <= g <= ranges['g'][1] and
                ranges['b'][0] <= b <= ranges['b'][1])
    
    def _detect_color_ratio(self, row, col, color_name, use_center=False):
        """Calculate what percentage of the tile contains a specific color."""
        x1, y1, x2, y2 = self._get_tile_bounds(row, col)
        
        # Optionally use only center region
        if use_center:
            margin_x = (x2 - x1) // 4
            margin_y = (y2 - y1) // 4
            x1 += margin_x
            x2 -= margin_x
            y1 += margin_y
            y2 -= margin_y
        
        match_count = 0
        total_count = 0
        
        for x in range(x1, x2):
            for y in range(y1, y2):
                r, g, b = self.pixels[x, y]
                if self._color_matches(r, g, b, color_name):
                    match_count += 1
                total_count += 1
        
        return match_count / total_count if total_count > 0 else 0
    
    def _classify_tile(self, row, col):
        """
        Classify what type of tile is at the given position.
        
        Returns
        -------
        str : One of 'land', 'water', 'horse', 'bee', 'cherry', 'apple', 'portal'
        """
        # Detection with thresholds
        # Check items in center region (they don't fill the whole tile)
        detections = {
            'horse': self._detect_color_ratio(row, col, 'horse', use_center=True),
            'portal': self._detect_color_ratio(row, col, 'portal', use_center=True),
            'apple': self._detect_color_ratio(row, col, 'apple', use_center=True),
            'cherry': self._detect_color_ratio(row, col, 'cherry', use_center=True),
            'bee': self._detect_color_ratio(row, col, 'bee', use_center=True),
            'water': self._detect_color_ratio(row, col, 'water', use_center=True)
        }
        
        # Thresholds
        thresholds = {
            'horse': 0.15,
            'portal': 0.03,
            'apple': 0.10,
            'cherry': 0.02,
            'bee': 0.01,
            'water': 0.03
        }
        
        # Priority order
        priority = ['horse', 'portal', 'apple', 'cherry', 'bee', 'water']
        
        for item in priority:
            if detections[item] > thresholds[item]:
                return item
        
        return 'land'
    
    def parse(self):
        """
        Parse the entire board image.
        
        Returns
        -------
        dict : Contains all parsed board information
        """
        grid = []
        water_positions = []
        portal_positions = []
        horse_pos = None
        bee_positions = []
        cherry_positions = []
        apple_positions = []
        
        for row in range(self.rows):
            grid_row = []
            for col in range(self.cols):
                tile_type = self._classify_tile(row, col)
                pos = (row, col)
                
                if tile_type == 'water':
                    water_positions.append(pos)
                elif tile_type == 'horse':
                    horse_pos = pos
                elif tile_type == 'bee':
                    bee_positions.append(pos)
                elif tile_type == 'cherry':
                    cherry_positions.append(pos)
                elif tile_type == 'apple':
                    apple_positions.append(pos)
                elif tile_type == 'portal':
                    portal_positions.append(pos)
                
                grid_row.append(tile_type)
            grid.append(grid_row)
        
        # Pair portals
        portal_positions.sort()
        portals = []
        for i in range(0, len(portal_positions) - 1, 2):
            portals.append((portal_positions[i], portal_positions[i + 1]))
        
        return {
            'rows': self.rows,
            'cols': self.cols,
            'grid': grid,
            'water': water_positions,
            'horse_pos': horse_pos,
            'bees': bee_positions,
            'cherries': cherry_positions,
            'apples': apple_positions,
            'portals': portals
        }
    
    def print_grid(self):
        """Print a text representation of the detected grid."""
        symbols = {
            'land': '.',
            'water': '~',
            'horse': 'r',
            'bee': 'b',
            'cherry': 'c',
            'apple': 'a',
            'portal': 'p'
        }
        
        print(f"\nDetected {self.rows}x{self.cols} grid:\n")
        for row in range(self.rows):
            row_str = ""
            for col in range(self.cols):
                tile_type = self._classify_tile(row, col)
                row_str += symbols.get(tile_type, '?') + " "
            print(row_str)
        print()
    
    def get_color_sample(self, row, col):
        """
        Get color information for a specific tile (useful for calibration).
        """
        x1, y1, x2, y2 = self._get_tile_bounds(row, col)
        
        # Center pixel
        center_x = (x1 + x2) // 2
        center_y = (y1 + y2) // 2
        center_rgb = self.pixels[center_x, center_y]
        
        # Average color
        total_r, total_g, total_b = 0, 0, 0
        count = 0
        for x in range(x1, x2):
            for y in range(y1, y2):
                r, g, b = self.pixels[x, y]
                total_r += r
                total_g += g
                total_b += b
                count += 1
        
        avg_rgb = (total_r // count, total_g // count, total_b // count)
        
        print(f"Tile ({row}, {col}):")
        print(f"  Center RGB: {center_rgb}")
        print(f"  Average RGB: {avg_rgb}")
        print(f"  Detection ratios:")
        for color_name in self.COLOR_RANGES:
            ratio = self._detect_color_ratio(row, col, color_name, use_center=True)
            print(f"    {color_name}: {ratio:.3f}")
        print(f"  Classified as: {self._classify_tile(row, col)}")
        
        return center_rgb, avg_rgb
    
    def visualize_detection(self, output_path):
        """Create a visualization showing detected tile types."""
        from PIL import ImageDraw, ImageFont
        
        vis_image = self.image.copy()
        draw = ImageDraw.Draw(vis_image)
        
        colors = {
            'land': (0, 255, 0),       # Green
            'water': (0, 0, 255),       # Blue
            'horse': (255, 255, 255),   # White
            'bee': (255, 200, 0),       # Orange
            'cherry': (255, 0, 0),      # Red
            'apple': (255, 255, 0),     # Yellow
            'portal': (0, 255, 255)     # Cyan
        }
        
        for row in range(self.rows):
            for col in range(self.cols):
                tile_type = self._classify_tile(row, col)
                x1, y1, x2, y2 = self._get_tile_bounds(row, col)
                
                color = colors.get(tile_type, (128, 128, 128))
                draw.rectangle([x1, y1, x2, y2], outline=color, width=2)
                
                # Add label
                label = tile_type[0].upper()
                draw.text((x1 + 5, y1 + 5), label, fill=color)
        
        vis_image.save(output_path)
        print(f"Saved visualization to {output_path}")
        
        return vis_image



import os
import numpy as np
import cv2

class BoardVisualizer:
    """
    Visualizes the board using pre-saved sprite images.
    """
    
    def __init__(self, sprite_folder="sprites", tile_size=64):
        """
        Initialize with sprite images.
        
        Parameters
        ----------
        sprite_folder : str
            Folder containing sprite images
        tile_size : int
            Size to scale sprites to (they'll be square)
        """
        self.tile_size = tile_size
        self.sprites = {}
        
        # Map tile types to sprite filenames
        self.sprite_files = {
            '.': 'land.png',
            '~': 'water.png',
            'r': 'horse.png',      
            'b': 'bees.png',
            'c': 'cherry.png',
            'a': 'apple.png',
            'p': 'portal.png',
            'W': 'wall.png',
            '*': 'enclosed.png',   # enclosed land
            'C': 'enc_cherry.png',
            'R': 'enc_horse.png',
            'B': 'enc_bee.png',
            'A': 'enc_apple.png',
            'P': 'enc_portal.png'
        }
        
        self._load_sprites(sprite_folder)
    
    def _load_sprites(self, folder):
        """Load all sprite images from folder."""
        for tile_type, filename in self.sprite_files.items():
            filepath = os.path.join(folder, filename)
            
            if os.path.exists(filepath):
                # Load and resize sprite
                sprite = Image.open(filepath).convert('RGB')
                sprite = sprite.resize((self.tile_size, self.tile_size), Image.NEAREST)
                self.sprites[tile_type] = np.array(sprite)
            else:
                print(f"Warning: {filepath} not found")
        
        # Create fallback sprite (magenta for missing)
        fallback = np.full((self.tile_size, self.tile_size, 3), [255, 0, 255], dtype=np.uint8)
        self.sprites['?'] = fallback
    
    def load_sprite_from_array(self, tile_type, pixel_array):
        """
        Load a sprite directly from a numpy array or nested list.
        
        Parameters
        ----------
        tile_type : str
            The tile type character ('.', '~', 'H', etc.)
        pixel_array : array-like
            RGB pixel data, shape (height, width, 3)
        """
        sprite = np.array(pixel_array, dtype=np.uint8)
        
        # Resize to tile_size
        sprite_pil = Image.fromarray(sprite)
        sprite_pil = sprite_pil.resize((self.tile_size, self.tile_size), Image.NEAREST)
        
        self.sprites[tile_type] = np.array(sprite_pil)
        print(f"Loaded sprite for '{tile_type}': {sprite.shape}")
    
    def render(self, board, enclosed_tiles=None, placed_walls=None):
        """
        Render the board to an image.
        
        Parameters
        ----------
        board : Board
            The board object to render
        enclosed_tiles : list of tuple, optional
            Positions (row, col) that are enclosed
        placed_walls : list of tuple, optional
            Positions (row, col) where walls were placed
        
        Returns
        -------
        np.ndarray : The rendered image (RGB)
        """
        if enclosed_tiles is None:
            enclosed_tiles = []
        if placed_walls is None:
            placed_walls = []
        
        height = board.rows * self.tile_size
        width = board.cols * self.tile_size
        
        # Create empty image
        image = np.zeros((height, width, 3), dtype=np.uint8)
        
        # Draw each tile
        for row in range(board.rows):
            for col in range(board.cols):
                pos = (row, col)
                tile = board.grid[row][col]
                
                # Determine which sprite to use
                if pos in placed_walls:
                    sprite_type = 'W'
                elif pos in enclosed_tiles:
                    # Use enclosed version if available, otherwise overlay
                    sprite_type = 'E' if 'E' in self.sprites else tile.type
                else:
                    sprite_type = tile.type
                
                # Get sprite (or fallback)
                sprite = self.sprites.get(sprite_type, self.sprites['?'])
                
                # Calculate position
                y1 = row * self.tile_size
                y2 = y1 + self.tile_size
                x1 = col * self.tile_size
                x2 = x1 + self.tile_size
                
                # Place sprite
                image[y1:y2, x1:x2] = sprite
        
        return image
    
    def show(self, board, img_name):
        """Display the board in a window using Pillow."""
        image = self.render(board)
        
        # Use PIL to show - opens in default image viewer
        pil_image = Image.fromarray(image)
        pil_image.show(title=img_name)
        


if __name__ == "__main__":
    IMAGE_PATH = "119_board.png"
    ROWS = 15
    COLS = 17
    
    # Parse and visualize
    parser = BoardParser(IMAGE_PATH, ROWS, COLS)
    parser.print_grid()
    parser.visualize_detection("detected_board.png")
    
    # Check specific tile for calibration
    parser.get_color_sample(5, 7)
    
    # Create board object
    # board = create_board_from_image(IMAGE_PATH, ROWS, COLS, placeable_walls=5)
    
    # board = Board(8, 10, 5)

    # # Add horse
    # board.rat_pos = (4, 5)
    # board.grid[4][5] = Tile((4, 5), has_rat=True)
    
    # # Add items
    # board.grid[2][3] = Bee((2, 3))
    # board.grid[5][7] = Cherry((5, 7))
    # board.grid[3][8] = Apple((3, 8))
    
    # # Add water (mark as ~ type)
    # water_positions = [(0, 0), (0, 1), (1, 0), (6, 8), (6, 9)]
    # for pos in water_positions:
    #     board.grid[pos[0]][pos[1]].type = "~"

    # viz = BoardVisualizer("sprites/", tile_size=64)
    # viz.show(board)
