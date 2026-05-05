# traprats
Software Carpentry final project -- Jessie Huh and Sabrina Chen

An automated solver for the [enclose.horse](https://enclose.horse) puzzle game. This tool parses puzzle images, solves them using constraint programming, and visualizes the solutions.

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
* installing conda version of ortools-python causes version issues, so at least for ortools please pip install it.

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

The solver uses constraint programming (Google OR-Tools CP-SAT) to find optimal wall placements that maximixe the score of enclosed tiles.

Given a grid with a rat, special tiles (cherries, apples, bees), and a limited number of walls to place, find wall posiitons that:

1. Enclose the rat (the rat cannot reach any edge tile)
2. Maximize the score (sum of weights of all reachable tiles)
3. Respect constraints (walls cannot be placed on the rat, portals, or special tiles)

The decision variables can be found in the table below:

| Variable | Type | Description |
|------|-------------|-----------|
| `is_wall[i]` | Boolean | Whether a wall is placed at tile `i` |
| `is_reachable[i]` | Boolean | Whether the rat can reach tile `i` |
| `order[i]` | Integer (0 to n) | Distance from rat to tile i (for connectivity) |
| `comes_from[ j--> i]` | Boolean | Whether tile i is reached from neighbor `j` |

The constraints are as follows:

1. Wall budget: Total walls placed must be less than or equal to allowed walls.
2. Enclosure: All edge tile must be unreachable.
3. Mutual exclusion: A wall tile cannot be reachable.
4. Rat source: Rat position is always reachable with order = 0.
5. No walls on special tiles: Walls cannot be placed on rat, portals, apples, cherries, or bees.
6. Connectivity via ordering: Each reachable tile (except for rat) must have exactly one neighbor with `order = neighbor + 1`, ensuring all reachable tiles form a connected region from the rat.

Portals are integrated into the adjacency graph. By stepping onto a portal tile, it adds the exit location as a neighbor.

Then, we maximize the weighted sum of reachable tiles.


### Visualization

The `BoardVisualizer` class renders the board state as an image.

**Process:**

1. Creates a blank canvas based on board dimensions and tile size
2. Iterates through each tile position in the grid
3. Loads the corresponding sprite from the `sprites/` folder
4. Places the sprite at the correct position on the canvas
6. Outputs the final composed image

## Comparisons with existing solution codes

Existing repos have implemented their own solution algorithms. Our approach differs as it uses constraint programming and is able to solve puzzles with portals. More detail can be found below:

| Aspect | Our Algorithm | Pink10000's ILP Solver |
|------|-------------|-----------|
| Framework | OR-Tools CP-SAT | PuLP with CBC/GLPK |
| Connectivity | Ordering + `comes_from` booleans | Single-commodity flow with big-M bounds |
| Variables | `is_wall, is_reachable, order, comes_from` | `W, E, R` (Wall/Escapable/Reachable) + flow `f` |
| Big-M Usage | None | M = width x height for flow bounds |
| Escapability | Implicit (edge tiles forced unreachable) | Explicit `E` variables with propagation |
| Portal Handling | Added to adjacency graph | Deduplicated links + boundary escapability shortcuts |

In summary, ILP flow solvers model escapability explicitly and use flow conservation to enforce connectivity. Our CP approach uses ordering constraints which avoids big-M numerical issues. Another solver does use CP-SAT but only models puzzles with cherries.

## Acknowledgments

- [enclose.horse](https://enclose.horse) - The original puzzle game
- [Google OR-Tools](https://developers.google.com/optimization) - Constraint programming solver
- [Pillow](https://pillow.readthedocs.io/) - Image processing library
- [NumPy](https://numpy.org/) - Numerical computing library
- [ILP Solver](https://github.com/pink10000/eh_ilp_solver/blob/main/enclose_engine/solver.py) - enclose.horse solver using ILP solver
- [CP-SAT Cherry Solver](https://github.com/langarus/enclosure.horse-solution/blob/master/solve.py) - enclose.horse solver using CP-SAT for boards with cherries
