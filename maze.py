# maze.py
import math
import pygame
from constants import TILE_SIZE, HUD_HEIGHT, COLOR_WALL, COLOR_PATH, COLOR_PELLET, COLOR_GHOST_HOUSE, COLOR_GHOST_DOOR

# ==============================================================================
# GRID COORDINATE SYSTEM & PATHFINDING SPECIFICATION
# ==============================================================================
# The grid uses a 2D coordinate system where:
#   - col (column) is the X-axis coordinate (0 to 27)
#   - row (row) is the Y-axis coordinate (0 to 30)
#
# Conversions to Pygame screen pixel coordinates:
#   - pixel_x = col * TILE_SIZE
#   - pixel_y = row * TILE_SIZE
#
# Conversions back to grid coordinates (for pathfinding / entity positions):
#   - col = pixel_x // TILE_SIZE
#   - row = pixel_y // TILE_SIZE
# ==============================================================================

CLASSIC_MAZE_LAYOUT = [
    "1111111111111111111111111111",
    "1222222222222112222222222221",
    "1211112111112112111112111121",
    "1211112111112112111112111121",
    "1211112111112112111112111121",
    "1222222222222222222222222221",
    "1211112112111111112112111121",
    "1211112112111111112112111121",
    "1222222112222112222112222221",
    "1111112111110110111112111111",
    "1111112111110110111112111111",
    "1111112110000000000112111111",
    "1111112110111001110112111111",
    "1111112110133333310112111111",
    "0000002000133333310002000000",
    "1111112110133333310112111111",
    "1111112110111111110112111111",
    "1111112110000000000112111111",
    "1111112110111111110112111111",
    "1111112110111111110112111111",
    "1222222222222112222222222221",
    "1211112111112112111112111121",
    "1211112111112112111112111121",
    "1222112222222002222222112221",
    "1112112112111111112112112111",
    "1112112112111111112112112111",
    "1222222112222112222112222221",
    "1211111111112112111111111121",
    "1211111111112112111111111121",
    "1222222222222222222222222221",
    "1111111111111111111111111111",
]

def validate_maze(grid):
    """Validates row lengths, perimeter boundaries, and path connectivity."""
    height = len(grid)
    if height == 0:
        raise AssertionError("Maze validation failed: Grid is empty.")
    
    expected_width = len(grid[0])
    
    for r_idx, row in enumerate(grid):
        if len(row) != expected_width:
            raise AssertionError(f"Row length mismatch at row index {r_idx}.")

    pellet_positions = [(r, c) for r in range(height) for c in range(expected_width) if grid[r][c] == 2]
    if pellet_positions:
        start = pellet_positions[0]
        queue = [start]
        visited = {start}
        while queue:
            curr_r, curr_c = queue.pop(0)
            for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                nr, nc = curr_r + dr, curr_c + dc
                if 0 <= nr < height and 0 <= nc < expected_width:
                    if grid[nr][nc] != 1 and grid[nr][nc] != 3 and (nr, nc) not in visited:
                        visited.add((nr, nc))
                        queue.append((nr, nc))
        unreachable = [pos for pos in pellet_positions if pos not in visited]
        if unreachable:
            raise AssertionError(f"Isolated pellet cells detected: {unreachable}")

    print("Maze validation passed successfully!")

def load_maze():
    grid = [[int(char) for char in row_str] for row_str in CLASSIC_MAZE_LAYOUT]
    validate_maze(grid)
    return grid

def render_maze(screen, grid, y_offset=HUD_HEIGHT):
    """
    Renders the maze grid to the Pygame screen in a double-stroke "tube" style:
    - Pure black background.
    - Double neon-blue wall outlines with rounded corners (offset by 3px).
    - Magenta horizontal door bar across the ghost house door tiles.
    - White dots for pellets.
    """
    height = len(grid)
    if height == 0:
        return
    width = len(grid[0])

    PI = math.pi
    line_width = 2
    r_d = max(3, TILE_SIZE // 4)  # Outer corner rounding radius (6px for TILE_SIZE=24)
    offset = 3                    # Offset between the double lines

    def is_wall(r, c):
        if 0 <= r < height and 0 <= c < width:
            return grid[r][c] == 1
        return False

    # 1. Render Horizontal Wall Segments (excluding boundary edges at r=0 and r=height)
    for r in range(1, height):
        for c in range(width):
            w_top = is_wall(r - 1, c)
            w_bot = is_wall(r, c)
            if w_top != w_bot:
                y = r * TILE_SIZE + y_offset
                x1 = c * TILE_SIZE
                x2 = (c + 1) * TILE_SIZE

                # Check if endpoints meet vertical corners to truncate
                t1 = 0
                t2 = 0
                if (is_wall(r - 1, c - 1) != is_wall(r - 1, c)) or (is_wall(r, c - 1) != is_wall(r, c)):
                    t1 = r_d
                if (is_wall(r - 1, c) != is_wall(r - 1, c + 1)) or (is_wall(r, c) != is_wall(r, c + 1)):
                    t2 = r_d

                # Clamp total truncation to a maximum of 60% of the segment length
                if t1 + t2 > TILE_SIZE * 0.6:
                    scale = (TILE_SIZE * 0.6) / (t1 + t2)
                    t1 = int(t1 * scale)
                    t2 = int(t2 * scale)

                # Draw outer line
                pygame.draw.line(screen, COLOR_WALL, (x1 + t1, y), (x2 - t2, y), line_width)
                
                # Draw inner line (offset toward wall interior)
                y_inner = y + offset if w_bot else y - offset
                pygame.draw.line(screen, COLOR_WALL, (x1 + t1, y_inner), (x2 - t2, y_inner), line_width)

    # 2. Render Vertical Wall Segments (excluding boundary edges at c=0 and c=width)
    for r in range(height):
        for c in range(1, width):
            w_left = is_wall(r, c - 1)
            w_right = is_wall(r, c)
            if w_left != w_right:
                x = c * TILE_SIZE
                y1 = r * TILE_SIZE + y_offset
                y2 = (r + 1) * TILE_SIZE + y_offset

                # Check if endpoints meet horizontal corners to truncate
                t1 = 0
                t2 = 0
                if (is_wall(r - 1, c - 1) != is_wall(r, c - 1)) or (is_wall(r - 1, c) != is_wall(r, c)):
                    t1 = r_d
                if (is_wall(r, c - 1) != is_wall(r + 1, c - 1)) or (is_wall(r, c) != is_wall(r + 1, c)):
                    t2 = r_d

                # Clamp total truncation to a maximum of 60% of the segment length
                if t1 + t2 > TILE_SIZE * 0.6:
                    scale = (TILE_SIZE * 0.6) / (t1 + t2)
                    t1 = int(t1 * scale)
                    t2 = int(t2 * scale)

                # Draw outer line
                pygame.draw.line(screen, COLOR_WALL, (x, y1 + t1), (x, y2 - t2), line_width)
                
                # Draw inner line (offset toward wall interior)
                x_inner = x + offset if w_right else x - offset
                pygame.draw.line(screen, COLOR_WALL, (x_inner, y1 + t1), (x_inner, y2 - t2), line_width)

    # 3. Render Curved Corner Arcs at Intersections (excluding boundary intersections)
    for r in range(1, height):
        for c in range(1, width):
            x = c * TILE_SIZE
            y = r * TILE_SIZE + y_offset

            tl = is_wall(r - 1, c - 1)
            tr = is_wall(r - 1, c)
            bl = is_wall(r, c - 1)
            br = is_wall(r, c)

            has_h_left = (tl != bl)
            has_h_right = (tr != br)
            has_v_top = (tl != tr)
            has_v_bot = (bl != br)

            # Top-Left Quadrant
            if has_h_left and has_v_top:
                if not tl:
                    # Outer arc
                    rect = pygame.Rect(x - r_d, y - r_d, 2 * r_d, 2 * r_d)
                    pygame.draw.arc(screen, COLOR_WALL, rect, PI / 2, PI, line_width)
                    # Inner arc (smaller radius)
                    r_in = r_d - offset
                    if r_in > 0:
                        rect_in = pygame.Rect(x - r_in, y - r_in, 2 * r_in, 2 * r_in)
                        pygame.draw.arc(screen, COLOR_WALL, rect_in, PI / 2, PI, line_width)
                else:
                    # Outer arc
                    rect = pygame.Rect(x - 2 * r_d, y - 2 * r_d, 2 * r_d, 2 * r_d)
                    pygame.draw.arc(screen, COLOR_WALL, rect, 3 * PI / 2, 2 * PI, line_width)
                    # Inner arc (larger radius)
                    r_in = r_d + offset
                    rect_in = pygame.Rect(x - 2 * r_d - offset, y - 2 * r_d - offset, 2 * r_in, 2 * r_in)
                    pygame.draw.arc(screen, COLOR_WALL, rect_in, 3 * PI / 2, 2 * PI, line_width)

            # Top-Right Quadrant
            if has_v_top and has_h_right:
                if not tr:
                    # Outer arc
                    rect = pygame.Rect(x - r_d, y - r_d, 2 * r_d, 2 * r_d)
                    pygame.draw.arc(screen, COLOR_WALL, rect, 0, PI / 2, line_width)
                    # Inner arc (smaller radius)
                    r_in = r_d - offset
                    if r_in > 0:
                        rect_in = pygame.Rect(x - r_in, y - r_in, 2 * r_in, 2 * r_in)
                        pygame.draw.arc(screen, COLOR_WALL, rect_in, 0, PI / 2, line_width)
                else:
                    # Outer arc
                    rect = pygame.Rect(x, y - 2 * r_d, 2 * r_d, 2 * r_d)
                    pygame.draw.arc(screen, COLOR_WALL, rect, PI, 3 * PI / 2, line_width)
                    # Inner arc (larger radius)
                    r_in = r_d + offset
                    rect_in = pygame.Rect(x - offset, y - 2 * r_d - offset, 2 * r_in, 2 * r_in)
                    pygame.draw.arc(screen, COLOR_WALL, rect_in, PI, 3 * PI / 2, line_width)

            # Bottom-Right Quadrant
            if has_h_right and has_v_bot:
                if not br:
                    # Outer arc
                    rect = pygame.Rect(x - r_d, y - r_d, 2 * r_d, 2 * r_d)
                    pygame.draw.arc(screen, COLOR_WALL, rect, 3 * PI / 2, 2 * PI, line_width)
                    # Inner arc (smaller radius)
                    r_in = r_d - offset
                    if r_in > 0:
                        rect_in = pygame.Rect(x - r_in, y - r_in, 2 * r_in, 2 * r_in)
                        pygame.draw.arc(screen, COLOR_WALL, rect_in, 3 * PI / 2, 2 * PI, line_width)
                else:
                    # Outer arc
                    rect = pygame.Rect(x, y, 2 * r_d, 2 * r_d)
                    pygame.draw.arc(screen, COLOR_WALL, rect, PI / 2, PI, line_width)
                    # Inner arc (larger radius)
                    r_in = r_d + offset
                    rect_in = pygame.Rect(x - offset, y - offset, 2 * r_in, 2 * r_in)
                    pygame.draw.arc(screen, COLOR_WALL, rect_in, PI / 2, PI, line_width)

            # Bottom-Left Quadrant
            if has_v_bot and has_h_left:
                if not bl:
                    # Outer arc
                    rect = pygame.Rect(x - r_d, y - r_d, 2 * r_d, 2 * r_d)
                    pygame.draw.arc(screen, COLOR_WALL, rect, PI, 3 * PI / 2, line_width)
                    # Inner arc (smaller radius)
                    r_in = r_d - offset
                    if r_in > 0:
                        rect_in = pygame.Rect(x - r_in, y - r_in, 2 * r_in, 2 * r_in)
                        pygame.draw.arc(screen, COLOR_WALL, rect_in, PI, 3 * PI / 2, line_width)
                else:
                    # Outer arc
                    rect = pygame.Rect(x - 2 * r_d, y, 2 * r_d, 2 * r_d)
                    pygame.draw.arc(screen, COLOR_WALL, rect, 0, PI / 2, line_width)
                    # Inner arc (larger radius)
                    r_in = r_d + offset
                    rect_in = pygame.Rect(x - 2 * r_d - offset, y - offset, 2 * r_in, 2 * r_in)
                    pygame.draw.arc(screen, COLOR_WALL, rect_in, 0, PI / 2, line_width)

    # 4. Render Pellets and Ghost House Door
    for r in range(height):
        for c in range(width):
            cell_val = grid[r][c]
            x = c * TILE_SIZE
            y = r * TILE_SIZE + y_offset

            if cell_val == 2:
                center_x = x + TILE_SIZE // 2
                center_y = y + TILE_SIZE // 2
                pygame.draw.circle(screen, COLOR_PELLET, (center_x, center_y), 3)

            elif cell_val == 0:
                if r + 1 < height and grid[r + 1][c] == 3 and c in (13, 14):
                    gate_y = y + TILE_SIZE // 2
                    pygame.draw.line(screen, COLOR_GHOST_DOOR, (x, gate_y), (x + TILE_SIZE, gate_y), 5)