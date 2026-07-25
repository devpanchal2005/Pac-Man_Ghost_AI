# constants.py

# Grid cell resolution in logical pixels
TILE_SIZE = 24

# Maze Grid Dimensions
MAZE_COLS = 28
MAZE_ROWS = 31

# HUD layout spacing
HUD_ROWS = 3
HUD_HEIGHT = HUD_ROWS * TILE_SIZE  # 72 pixels

# Total Virtual Resolution (Logical Canvas)
TOTAL_ROWS = MAZE_ROWS + HUD_ROWS  # 34 rows total
VIRTUAL_WIDTH = MAZE_COLS * TILE_SIZE  # 672 pixels
VIRTUAL_HEIGHT = TOTAL_ROWS * TILE_SIZE  # 816 pixels

# Initial Window Dimensions (Resizable)
SCREEN_WIDTH = VIRTUAL_WIDTH
SCREEN_HEIGHT = VIRTUAL_HEIGHT

# Target Frame Rate
FPS = 60

# Classic Arcade Color Palette (RGB format)
COLOR_BACKGROUND = (0, 0, 0)            # Pure black background
COLOR_WALL = (33, 33, 222)              # Bright neon blue for wall outlines
COLOR_PATH = (0, 0, 0)                  # Black corridors
COLOR_PELLET = (255, 255, 255)          # White/off-white dots
COLOR_POWER_PELLET = (255, 255, 255)    # White glowing power pellets
COLOR_PACMAN = (255, 255, 0)            # Arcade Yellow

# Ghost House Colors
COLOR_GHOST_HOUSE = (0, 0, 0)           # Black interior
COLOR_GHOST_DOOR = (255, 182, 255)      # Light pink door bar

# Classic Ghost Colors
COLOR_GHOST_RED = (255, 0, 0)           # Blinky (Shadow)
COLOR_GHOST_PINK = (255, 184, 255)      # Pinky (Speedy)
COLOR_GHOST_CYAN = (0, 255, 255)        # Inky (Bashful)
COLOR_GHOST_ORANGE = (255, 184, 81)     # Clyde (Pokey)

# HUD Text
COLOR_HUD_TEXT = (255, 255, 255)        # Retro Arcade White
