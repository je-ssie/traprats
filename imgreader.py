

import numpy as np
import os
from PIL import Image, ImageDraw


class BoardParser:
    """
    Parses an image of the enclose.horse game board using Pillow.

    This class analyzes a screenshot or image of a game board and identifies
    different tile types based on color detection. It extracts positions of
    all game elements.

    Attributes
    ----------
    COLOR_RANGES : dict
        Class-level dictionary defining RGB color ranges for each tile type.
        Each entry maps a tile name to a dict with 'r', 'g', 'b' keys containing
        (min, max) tuples for acceptable color values.
    image : PIL.Image
        The loaded board image in RGB format.
    width : int
        Width of the image in pixels.
    height : int
        Height of the image in pixels.
    pixels : PixelAccess
        Pixel access object for reading individual pixel colors.
    rows : int
        Number of tile rows in the board.
    cols : int
        Number of tile columns in the board.
    tile_height : float
        Height of each tile in pixels.
    tile_width : float
        Width of each tile in pixels.
    """

    # Color ranges in RGB (min_r, max_r, min_g, max_g, min_b, max_b)
    COLOR_RANGES = {
        'water': {
            'r': (0, 30),
            'g': (40, 100),
            'b': (70, 130)
        },
        'rat': {
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
        'portal_sky': {
            'r': (100, 200),
            'g': (200, 255),
            'b': (220, 255)
        },
        'portal_blue': {
            'r': (30, 160),
            'g': (80, 165),
            'b': (200, 255)
        },
        'portal_purple': {
            'r': (120, 210),
            'g': (30, 160),
            'b': (190, 255)
        },
        'portal_orange': {
            'r': (70, 255),
            'g': (90, 200),
            'b': (30, 180)
        },
        'portal_red': {
            'r': (190, 255),
            'g': (30, 160),
            'b': (70, 180)
        },
        'portal_magenta': {
            'r': (200, 255),
            'g': (30, 160),
            'b': (170, 240)
        },

        'land': {
            'r': (40, 120),
            'g': (100, 180),
            'b': (40, 120)
        }
    }

    def __init__(self, image_path, rows, cols):
        """
        Initialize the parser with a board image.

        Loads the image, calculates tile dimensions, and prepares for parsing.

        Parameters
        ----------
        image_path : str
            Path to the board image file.
        rows : int
            Number of rows in the board grid.
        cols : int
            Number of columns in the board grid.

        Returns
        -------
        None
        """
        self.image = Image.open(image_path).convert('RGB')
        self.width, self.height = self.image.size
        self.pixels = self.image.load()

        self.rows = rows
        self.cols = cols

        # dimensions of each tile
        self.tile_height = self.height / self.rows
        self.tile_width = self.width / self.cols

    def _get_tile_bounds(self, row, col):
        """
        Get the pixel boundaries for a specific tile.

        Parameters
        ----------
        row : int
            Row index of the tile (0-indexed).
        col : int
            Column index of the tile (0-indexed).

        Returns
        -------
        tuple of int
            A tuple (x1, y1, x2, y2) representing the left, top, right, and
            bottom pixel coordinates of the tile boundary.
        """
        x1 = int(col * self.tile_width)
        x2 = int((col + 1) * self.tile_width)
        y1 = int(row * self.tile_height)
        y2 = int((row + 1) * self.tile_height)
        return x1, y1, x2, y2

    def _color_matches(self, r, g, b, color_name):
        """
        Check if an RGB color falls within the defined range for a color type.

        Parameters
        ----------
        r : int
            Red component value (0-255).
        g : int
            Green component value (0-255).
        b : int
            Blue component value (0-255).
        color_name : str
            Name of the color type to check against (must be a key in COLOR_RANGES).

        Returns
        -------
        bool
            True if the RGB values fall within the specified color range,
            False otherwise.
        """

        ranges = self.COLOR_RANGES[color_name]

        # return True if all r,g,b falls within the range of the given color
        return (ranges['r'][0] <= r <= ranges['r'][1] and
                ranges['g'][0] <= g <= ranges['g'][1] and
                ranges['b'][0] <= b <= ranges['b'][1])

    def _detect_color_ratio(self, row, col, color_name, use_center=False):
        """
        Calculate the percentage of pixels in a tile that match a specific color.

        Parameters
        ----------
        row : int
            Row index of the tile.
        col : int
            Column index of the tile.
        color_name : str
            Name of the color type to detect (must be a key in COLOR_RANGES).
        use_center : bool, optional
            If True, only analyze the center 25% of the tile area to avoid
            edge artifacts (default: False).

        Returns
        -------
        float
            Ratio of matching pixels to total pixels (0.0 to 1.0).
        """
        x1, y1, x2, y2 = self._get_tile_bounds(row, col)

        if use_center:
            # checks just the center of the tile (25% of original area)
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

                # check if current pixel falls within the color range
                if self._color_matches(r, g, b, color_name):
                    match_count += 1

                total_count += 1

        # percentage of pixels that match the color
        return match_count / total_count if total_count > 0 else 0

    def _classify_tile(self, row, col):
        """
        Classify the type of tile at a given grid position.

        Uses color detection ratios and predefined thresholds to determine
        the tile type. Checks items in priority order: rat, portals, apple,
        cherry, bee, water, then defaults to land.

        Parameters
        ----------
        row : int
            Row index of the tile.
        col : int
            Column index of the tile.

        Returns
        -------
        str
            The classified tile type. One of: 'land', 'water', 'rat', 'bee',
            'cherry', 'apple', 'portal_sky', 'portal_blue', 'portal_purple',
            'portal_orange', 'portal_red', 'portal_magenta'.
        """
        # portal types to check
        portal_types = ['portal_sky', 'portal_blue', 'portal_purple',
                        'portal_orange', 'portal_red', 'portal_magenta']

        # detection with thresholds
        detections = {
            'rat': self._detect_color_ratio(row, col, 'rat', use_center=True),
            'apple': self._detect_color_ratio(row, col, 'apple', use_center=True),
            'cherry': self._detect_color_ratio(row, col, 'cherry', use_center=True),
            'bee': self._detect_color_ratio(row, col, 'bee', use_center=True),
            'water': self._detect_color_ratio(row, col, 'water', use_center=True)
        }

        # add portal type detections
        for portal_type in portal_types:
            detections[portal_type] = self._detect_color_ratio(
                row, col, portal_type, use_center=True)

        # thresholds
        thresholds = {
            'rat': 0.15,
            'apple': 0.10,
            'cherry': 0.02,
            'bee': 0.01,
            'water': 0.03
        }

        # add portal thresholds
        for portal_type in portal_types:
            thresholds[portal_type] = 0.4
            if portal_type == 'portal_sky':
                thresholds[portal_type] = 0.25

        # priority order (check portals before other items)
        priority = ['rat'] + portal_types + ['apple', 'cherry', 'bee', 'water']

        for item in priority:
            # if the percentage is over the threshold, classify as that tile
            if detections[item] > thresholds[item]:
                return item

        # if none of the special tiles were detected, it is land
        return 'land'

    def _is_portal_type(self, tile_type):
        """
        Check if a tile type string represents any kind of portal.

        Parameters
        ----------
        tile_type : str
            The tile type string to check.

        Returns
        -------
        bool
            True if the tile type starts with 'portal_', False otherwise.
        """
        return tile_type.startswith('portal_')

    def parse(self):
        """
        Parse the entire board image and extract all game elements.

        Iterates through every tile position, classifies each tile, and
        collects positions of all special elements. Pairs portals of the
        same color together.

        Parameters
        ----------
        None

        Returns
        -------
        dict
            Dictionary containing parsed board information with keys:
            - 'rows' : int - Number of rows in the board
            - 'cols' : int - Number of columns in the board
            - 'grid' : list of list of str - 2D grid of tile type strings
            - 'water' : list of tuple - Positions of water tiles as (row, col)
            - 'rat_pos' : tuple or None - Position of the rat as (row, col)
            - 'bees' : list of tuple - Positions of bees as (row, col)
            - 'cherries' : list of tuple - Positions of cherries as (row, col)
            - 'apples' : list of tuple - Positions of apples as (row, col)
            - 'portals' : list of dict - Paired portals, each with 'entry',
              'exit', and 'color' keys
            - 'portals_by_color' : dict - Portal positions grouped by color type
        """
        grid = []
        water_positions = []
        rat_pos = None
        bee_positions = []
        cherry_positions = []
        apple_positions = []

        # dictionary to collect portals by color
        portal_types = ['portal_sky', 'portal_blue', 'portal_purple',
                        'portal_orange', 'portal_red', 'portal_magenta']
        portals_by_color = {pt: [] for pt in portal_types}

        for row in range(self.rows):
            grid_row = []
            for col in range(self.cols):

                # classify current tile
                tile_type = self._classify_tile(row, col)
                pos = (row, col)

                # record position in corresponding tile list
                if tile_type == 'water':
                    water_positions.append(pos)
                elif tile_type == 'rat':
                    rat_pos = pos
                elif tile_type == 'bee':
                    bee_positions.append(pos)
                elif tile_type == 'cherry':
                    cherry_positions.append(pos)
                elif tile_type == 'apple':
                    apple_positions.append(pos)
                elif self._is_portal_type(tile_type):
                    portals_by_color[tile_type].append(pos)

                # store portal generically in grid for string representation
                grid_tile = 'portal' if self._is_portal_type(
                    tile_type) else tile_type
                grid_row.append(grid_tile)
            grid.append(grid_row)

        # pair portals by color, each pair becomes (entry, exit, color)
        portals = []
        for portal_type, positions in portals_by_color.items():
            if len(positions) == 2:
                portals.append({
                    'entry': positions[0],
                    'exit': positions[1],
                    'color': portal_type
                })
            elif len(positions) > 2:
                raise Exception(f"Too many positions for {portal_type}")
            elif len(positions) == 1:
                raise Exception(
                    f"Warning: Unpaired {portal_type} at {positions[0]}")

        return {
            'rows': self.rows,
            'cols': self.cols,
            'grid': grid,
            'water': water_positions,
            'rat_pos': rat_pos,
            'bees': bee_positions,
            'cherries': cherry_positions,
            'apples': apple_positions,
            'portals': portals,
            'portals_by_color': portals_by_color
        }

    def get_color_sample(self, row, col):
        """
        Get detailed color information for a specific tile (for debugging).

        Prints the center pixel color, average color, detection ratios for
        all color types, and the final classification.

        Parameters
        ----------
        row : int
            Row index of the tile.
        col : int
            Column index of the tile.

        Returns
        -------
        tuple
            A tuple containing:
            - center_rgb : tuple of int - RGB values of the center pixel
            - avg_rgb : tuple of int - Average RGB values across all pixels in tile
        """
        x1, y1, x2, y2 = self._get_tile_bounds(row, col)

        # center pixel
        center_x = (x1 + x2) // 2
        center_y = (y1 + y2) // 2
        center_rgb = self.pixels[center_x, center_y]

        # average color
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
        print("  Detection ratios:")
        for color_name in self.COLOR_RANGES:
            ratio = self._detect_color_ratio(
                row, col, color_name, use_center=True)
            print(f"    {color_name}: {ratio:.3f}")
        print(f"  Classified as: {self._classify_tile(row, col)}")

        return center_rgb, avg_rgb

    def visualize_detection(self, output_path):
        """
        Create and save a visualization showing detected tile types.

        Draws colored rectangles and labels over each tile to indicate
        the detected tile type.

        Parameters
        ----------
        output_path : str
            File path where the visualization image will be saved.

        Returns
        -------
        PIL.Image
            The visualization image with detection overlays.
        """

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

                # add label
                label = tile_type[0].upper()
                draw.text((x1 + 5, y1 + 5), label, fill=color)

        vis_image.save(output_path)
        print(f"Saved visualization to {output_path}")

        return vis_image


class BoardVisualizer:
    """
    Visualizes an enclosed.horse game board using pre-saved sprite images.

    This class loads sprite images from a specified folder and renders
    a Board object as an RGB image by mapping each tile type to its
    corresponding sprite. 

    Attributes
    ----------
    tile_size : int
        The size (in pixels) of each tile sprite (tiles are square).
    sprites : dict
        Dictionary mapping tile type identifiers to numpy arrays of sprite images.
    sprite_files : dict
        Dictionary mapping tile type identifiers to sprite filenames.
    """

    def __init__(self, sprite_folder="sprites", tile_size=64):
        """
        Initialize the BoardVisualizer with sprite images.

        Parameters
        ----------
        sprite_folder : str, optional
            Path to the folder containing sprite image files (default: "sprites").
        tile_size : int, optional
            Size in pixels to scale sprites to; sprites are square (default: 64).

        Returns
        -------
        None
        """
        self.tile_size = tile_size
        self.sprites = {}

        # map tile types to sprite filenames
        # these are all saved in folder /sprites
        self.sprite_files = {
            '.': 'land.png',
            '~': 'water.png',
            'r': 'rat.png',
            'b': 'bees.png',
            'c': 'cherry.png',
            'a': 'apple.png',
            'portal_sky': 'portal_sky.png',
            'portal_blue': 'portal_blue.png',
            'portal_purple': 'portal_purple.png',
            'portal_orange': 'portal_orange.png',
            'portal_red': 'portal_red.png',
            'portal_magenta': 'portal_magenta.png',
            'W': 'wall.png',
            '*': 'enclosed.png',   # enclosed land
            'C': 'enc_cherry.png',
            'R': 'enc_rat.png',
            'B': 'enc_bee.png',
            'A': 'enc_apple.png',
            'PORTAL_SKY': 'enc_portal_sky.png',
            'PORTAL_BLUE': 'enc_portal_blue.png',
            'PORTAL_PURPLE': 'enc_portal_purple.png',
            'PORTAL_ORANGE': 'enc_portal_orange.png',
            'PORTAL_RED': 'enc_portal_red.png',
            'PORTAL_MAGENTA': 'enc_portal_magenta.png'
        }

        self._load_sprites(sprite_folder)

    def _load_sprites(self, folder):
        """
        Load all sprite images from the specified folder.

        Loads each sprite file defined in sprite_files, resizes them to
        tile_size, and stores them as numpy arrays. Creates a magenta
        fallback sprite for any missing images.

        Parameters
        ----------
        folder : str
            Path to the folder containing sprite image files.

        Returns
        -------
        None
        """
        for tile_type, filename in self.sprite_files.items():
            filepath = os.path.join(folder, filename)

            if os.path.exists(filepath):
                # load and resize sprite
                sprite = Image.open(filepath).convert('RGB')
                sprite = sprite.resize(
                    (self.tile_size, self.tile_size), Image.NEAREST)
                self.sprites[tile_type] = np.array(sprite)
            else:
                raise FileNotFoundError(f"{filepath} not found.")

        # create fallback sprite (magenta for missing)
        fallback = np.full((self.tile_size, self.tile_size, 3), [
                           255, 0, 255], dtype=np.uint8)
        self.sprites['?'] = fallback

    def render(self, board):
        """
        Render the board to an RGB image array.

        Iterates through each tile in the board grid and places the
        corresponding sprite at the appropriate position in the output image.

        Parameters
        ----------
        board : Board
            The board object to render. Must have 'rows', 'cols', and 'grid'
            attributes, where grid contains tile objects with 'type' and
            optionally 'color' attributes.

        Returns
        -------
        image : np.ndarray
            The rendered image as a numpy array with shape 
            (board.rows * tile_size, board.cols * tile_size, 3) and dtype uint8.
        """

        height = board.rows * self.tile_size
        width = board.cols * self.tile_size

        # create empty image
        image = np.zeros((height, width, 3), dtype=np.uint8)

        # draw each tile
        for row in range(board.rows):
            for col in range(board.cols):

                tile = board.grid[row][col]

                # determine which sprite to use based on tile type
                if tile.type == 'p':
                    sprite_type = tile.color
                elif tile.type == 'P':  # enclosed portal
                    sprite_type = tile.color.upper()
                else:
                    sprite_type = tile.type

                # get sprite (or fallback)
                sprite = self.sprites.get(sprite_type, self.sprites['?'])

                # calculate position of tile on board
                y1 = row * self.tile_size
                y2 = y1 + self.tile_size
                x1 = col * self.tile_size
                x2 = x1 + self.tile_size

                # place sprite
                image[y1:y2, x1:x2] = sprite

        return image

    def show(self, board, img_name):
        """
        Display the rendered board in the system's default image viewer.

        Parameters
        ----------
        board : Board
            The board object to render and display.
        img_name : str
            Title to display for the image window.

        Returns
        -------
        None
        """
        image = self.render(board)

        # use PIL to show window in default image viewer
        pil_image = Image.fromarray(image)
        pil_image.show(title=img_name)

    def save(self, board, output_path, puzzle_name=None):
        """
        Save the rendered board as a PNG image.

        Parameters
        ----------
        board : Board
            The board to render and save.
        output_path : str
            Path where the image will be saved.
        puzzle_name : str, optional
            Name to display on the image (not implemented, for future use).

        Returns
        -------
        str
            The path where the image was saved.
        """
        rendered = self.render(board)
        image = Image.fromarray(rendered)
        image.save(output_path)
        return output_path


if __name__ == "__main__":
    from board import *

    IMAGE_PATH = "52_board.png"
    ROWS = 17
    COLS = 17

    board = Board(ROWS, COLS, 13, image_path=IMAGE_PATH)
    # parser = BoardParser(IMAGE_PATH, ROWS, COLS)
    # parser.print_grid()
    # parser.get_color_sample(11, 1)
    # for portal in board.portals:
    #     print(portal.color)
    # viz = BoardVisualizer("sprites/", tile_size=64)
    board.visualize_board()
