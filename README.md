# traprats
software carpentry final project

## Installation

### Setting up the environment

It is **recommended** to create a new virtual environment to prevent version conflicts:

Create a new virtual environment:

```
conda create -n traprats-env
```

Activate the environment (mac):

```
conda activate traprats-env
```

### Required packages

Install the required packages:

```
pip install pillow numpy ortools
```

## Usage

### GUI Mode

The easiest way to use the solver:

```
python play_traprats.py
```

**Steps:**

1. Click **"Upload Image"** to select a puzzle screenshot
2. Enter the number of **Rows**, **Columns**, and **Walls**
3. Click **"Load Board"** to parse the image
4. Click **"Solve Puzzle"** to find the optimal solution
5. View the solution and score

### Command line mode

For direct execution without the GUI, modify and run `board.py`:

1. Open `board.py` and find the `main()` function
2. Modify the variables:

```python
def main():
    image_file = "your_puzzle.png"  # Path to your puzzle image
    ROWS = 11                        # Number of rows
    COLS = 17                        # Number of columns
    WALLS = 11                       # Number of placeable walls
    ...
```

3. Run the script:

```
python board.py
```

## Project structure

```
traprats/
│
├── board.py                 # Board class - stores puzzle and solves it
├── tiles.py                 # Tile classes (Tile, Wall, Bee, Cherry, Apple, Portal)
├── imgreader.py             # Image parsing to read puzzle from PNG
├── play_traprats.py         # GUI application
│
├── sprites/                 # Tile sprites for visualization
│   ├── land.png
│   ├── water.png
│   ├── horse.png
│   ├── cherry.png
│   ├── bees.png
│   ├── apple.png
│   ├── portal_sky.png
│   ├── portal_blue.png
│   ├── portal_purple.png
│   ├── portal_orange.png
│   ├── portal_red.png
│   ├── portal_magenta.png
│   └── ...
│
├── boards/                  # Example puzzle images for testing
│   ├── 1_board.png
│   ├── 2_board.png
│   └── ...
│
├── unittest_tiles.py        # Unit tests for tiles.py
├── unittest_board.py        # Unit tests for board.py
├── unittest_imgreader.py    # Unit tests for imgreader.py
│
└── README.md                # This file
```
## How it works

### Image parsing

The `imgreader.py` module converts puzzle screenshots into a structured board representation.

**Process:**

1. **Grid Division**: The input image is divided into equal-sized tiles based on the specified rows and columns

2. **Color Sampling**: For each tile, only the center area (25% of tile area) is scanned to avoid edge artifacts and tile borders

3. **Tile Classification**: Each pixel's RGB values are compared against predefined color ranges for each tile type

4. **Threshold Detection**: A tile is classified when a sufficient percentage of sampled pixels fall within a tile type's color range

5. **Portal Pairing**: Portals of the same color are automatically detected and paired together

**Supported Tile Types:**

| Tile | Description | Detection |
|------|-------------|-----------|
| 🟩 Land | Empty traversable space | Green color range |
| 🟦 Water | Fixed walls, impassable | Blue color range |
| 🐴 Rat/Horse | Player starting position | White/gray color range |
| 🐝 Bees | -5 points if enclosed | Yellow/orange color range |
| 🍒 Cherries | +3 points if enclosed | Red color range |
| 🍎 Apples | +10 points if enclosed | Yellow color range |
| 🌀 Portals | Teleportation links (6 colors) | Various color ranges |

**Portal Colors Supported:**
Up to 6 portals are supported.

- Sky
- Blue
- Purple
- Orange
- Red
- Magenta

### Puzzle Solving

sabrina fill out 

### Visualization

The `BoardVisualizer` class renders the board state as an image.

**Process:**

1. Creates a blank canvas based on board dimensions and tile size
2. Iterates through each tile position in the grid
3. Loads the corresponding sprite from the `sprites/` folder
4. Places the sprite at the correct position on the canvas
6. Outputs the final composed image

## Comparisons with existing solution codes

sabrina fill this out


## Acknowledgments

- [enclose.horse](https://enclose.horse) - The original puzzle game
- [Google OR-Tools](https://developers.google.com/optimization) - Constraint programming solver
- [Pillow](https://pillow.readthedocs.io/) - Image processing library
- [NumPy](https://numpy.org/) - Numerical computing library
