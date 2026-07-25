# pacman.py
import math
import pygame
from constants import TILE_SIZE, COLOR_PACMAN

def draw_pacman(surface, color, center, radius, direction_name, mouth_open_angle):
    """
    Draws a filled Pac-Man with a chomping mouth.
    center: (x, y) pixel coordinates.
    radius: Pac-Man's radius.
    direction_name: "UP", "DOWN", "LEFT", "RIGHT".
    mouth_open_angle: the total angle of the mouth opening in radians.
    """
    x, y = center
    if mouth_open_angle <= 0.05:
        # Draw a full circle if the mouth is closed or almost closed
        pygame.draw.circle(surface, color, (int(x), int(y)), int(radius))
        # Draw a thin black outline
        pygame.draw.circle(surface, (0, 0, 0), (int(x), int(y)), int(radius), 1)
        return

    # Determine base rotation angle based on direction
    if direction_name == "RIGHT":
        base_angle = 0.0
    elif direction_name == "DOWN":
        base_angle = math.pi / 2.0
    elif direction_name == "LEFT":
        base_angle = math.pi
    elif direction_name == "UP":
        base_angle = 3.0 * math.pi / 2.0
    else:
        base_angle = 0.0

    # Start angle and end angle of the mouth wedge (relative to base_angle)
    start_angle = base_angle + mouth_open_angle / 2.0
    end_angle = base_angle + 2.0 * math.pi - mouth_open_angle / 2.0

    # Generate points around the circle
    points = [(x, y)] # Start at the center
    num_segments = 32
    for i in range(num_segments + 1):
        angle = start_angle + (end_angle - start_angle) * (i / num_segments)
        px = x + radius * math.cos(angle)
        py = y + radius * math.sin(angle)
        points.append((px, py))

    # Draw the filled polygon
    pygame.draw.polygon(surface, color, points)
    # Draw a thin black outline (1px) around it
    pygame.draw.polygon(surface, (0, 0, 0), points, 1)

class PacMan:
    def __init__(self, grid):
        self.grid = grid
        self.rows = len(grid)
        self.cols = len(grid[0])
        
        # Pick starting position near bottom-center (row 23, col 13 is classic and walkable)
        self.row = 23
        self.col = 13
        
        # Ensure it is a valid walkable cell
        if self.grid[self.row][self.col] == 1 or self.grid[self.row][self.col] == 3:
            # Fallback scan to find a valid path tile near the bottom-center
            found = False
            for r in range(self.rows - 2, 0, -1):
                for c in range(self.cols // 2 - 2, self.cols // 2 + 2):
                    if self.grid[r][c] != 1 and self.grid[r][c] != 3:
                        self.row = r
                        self.col = c
                        found = True
                        break
                if found:
                    break
        
        # pixel_x and pixel_y represent the top-left corner of Pac-Man's current grid cell
        self.pixel_x = float(self.col * TILE_SIZE)
        self.pixel_y = float(self.row * TILE_SIZE)
        
        # Speed (pixels per frame). 2 pixels per frame is a clean divisor of TILE_SIZE=24
        self.speed = 2.0
        
        # Direction state
        self.current_dir = None  # "UP", "DOWN", "LEFT", "RIGHT" or None
        self.queued_dir = None   # "UP", "DOWN", "LEFT", "RIGHT" or None
        self.last_dir = "RIGHT"  # For rendering orientation when stopped
        
        # Target grid tile for the current movement segment
        self.target_row = self.row
        self.target_col = self.col
        
        # Cache starting position for resetting
        self.start_row = self.row
        self.start_col = self.col
        
        # Animation
        self.chomp_time = 0

    def reset(self):
        self.row = self.start_row
        self.col = self.start_col
        self.pixel_x = float(self.col * TILE_SIZE)
        self.pixel_y = float(self.row * TILE_SIZE)
        self.current_dir = None
        self.queued_dir = None
        self.last_dir = "RIGHT"
        self.target_row = self.row
        self.target_col = self.col
        self.chomp_time = 0

    def is_walkable(self, r, c):
        if not (0 <= r < self.rows and 0 <= c < self.cols):
            return False
        val = self.grid[r][c]
        return val != 1 and val != 3

    def get_next_tile(self, r, c, direction):
        if not direction:
            return r, c
        
        d_row, d_col = 0, 0
        if direction == "UP":
            d_row = -1
        elif direction == "DOWN":
            d_row = 1
        elif direction == "LEFT":
            d_col = -1
        elif direction == "RIGHT":
            d_col = 1
            
        next_r = r + d_row
        next_c = c + d_col
        
        # Horizontal wrap-around for column boundaries
        if next_c < 0:
            next_c = self.cols - 1
        elif next_c >= self.cols:
            next_c = 0
            
        return next_r, next_c

    def update(self):
        # 1. Handle instant reversal (opposite direction)
        if self.queued_dir and self.current_dir:
            opposites = {
                "UP": "DOWN", "DOWN": "UP",
                "LEFT": "RIGHT", "RIGHT": "LEFT"
            }
            if self.queued_dir == opposites.get(self.current_dir):
                # Reverse direction immediately
                self.current_dir = self.queued_dir
                self.row = self.target_row
                self.col = self.target_col
                self.target_row, self.target_col = self.get_next_tile(self.row, self.col, self.current_dir)
                self.last_dir = self.current_dir

        # Calculate logical pixel destination for the current target tile
        dx = self.target_col - self.col
        dy = self.target_row - self.row
        
        # Handle wrap-around distance calculation conceptually
        if dx > 1:
            dx = -1
        elif dx < -1:
            dx = 1
            
        dest_pixel_x = (self.col + dx) * TILE_SIZE
        dest_pixel_y = (self.row + dy) * TILE_SIZE
        
        # Check if we have arrived at the destination pixel coordinates
        if self.pixel_x == dest_pixel_x and self.pixel_y == dest_pixel_y:
            # Wrap pixel positions to grid boundaries if needed
            self.pixel_x = self.pixel_x % (self.cols * TILE_SIZE)
            self.pixel_y = self.pixel_y % (self.rows * TILE_SIZE)
            
            # Snap grid coordinates
            self.col = int(self.pixel_x // TILE_SIZE)
            self.row = int(self.pixel_y // TILE_SIZE)
            
            self.target_row = self.row
            self.target_col = self.col
            
            # Intersection logic: pick the next tile
            # Try queued direction first
            if self.queued_dir:
                next_r, next_c = self.get_next_tile(self.row, self.col, self.queued_dir)
                if self.is_walkable(next_r, next_c):
                    self.current_dir = self.queued_dir
                    self.target_row = next_r
                    self.target_col = next_c
                    self.last_dir = self.current_dir
                else:
                    # Try to continue in current direction
                    if self.current_dir:
                        next_r, next_c = self.get_next_tile(self.row, self.col, self.current_dir)
                        if self.is_walkable(next_r, next_c):
                            self.target_row = next_r
                            self.target_col = next_c
                        else:
                            self.current_dir = None
                    else:
                        self.current_dir = None
            else:
                # No queued direction, try to continue in current direction
                if self.current_dir:
                    next_r, next_c = self.get_next_tile(self.row, self.col, self.current_dir)
                    if self.is_walkable(next_r, next_c):
                        self.target_row = next_r
                        self.target_col = next_c
                    else:
                        self.current_dir = None
                else:
                    self.current_dir = None
            
            # Recalculate target destination immediately so movement begins without a 1-frame gap
            dx = self.target_col - self.col
            dy = self.target_row - self.row
            if dx > 1:
                dx = -1
            elif dx < -1:
                dx = 1
            dest_pixel_x = (self.col + dx) * TILE_SIZE
            dest_pixel_y = (self.row + dy) * TILE_SIZE

        # Move pixel coordinates towards the current destination
        if self.pixel_x < dest_pixel_x:
            self.pixel_x = min(self.pixel_x + self.speed, dest_pixel_x)
        elif self.pixel_x > dest_pixel_x:
            self.pixel_x = max(self.pixel_x - self.speed, dest_pixel_x)
            
        if self.pixel_y < dest_pixel_y:
            self.pixel_y = min(self.pixel_y + self.speed, dest_pixel_y)
        elif self.pixel_y > dest_pixel_y:
            self.pixel_y = max(self.pixel_y - self.speed, dest_pixel_y)

        # 3. Animate chomp only if Pac-Man is actively moving
        if self.current_dir:
            self.chomp_time += 1

        # 4. Pellet consumption: check current grid tile
        score_gain = 0
        power_pellet_eaten = False
        if self.grid[self.row][self.col] == 2:
            self.grid[self.row][self.col] = 0
            score_gain = 10
        elif self.grid[self.row][self.col] == 4:
            self.grid[self.row][self.col] = 0
            score_gain = 50
            power_pellet_eaten = True
            
        return score_gain, power_pellet_eaten

    def draw(self, surface, y_offset):
        # Calculate pixel center for rendering
        center_x = self.pixel_x + TILE_SIZE / 2.0
        center_y = self.pixel_y + TILE_SIZE / 2.0 + y_offset
        
        # Fill about 80-85% of a tile's diameter (24 * 0.42 = 10.08, ~10 pixels radius)
        radius = TILE_SIZE * 0.42
        
        # Calculate chomp opening angle (cycles between 0 and ~70 degrees / 1.2 radians for a readable V)
        mouth_openness = abs(math.sin(self.chomp_time * 0.15))
        mouth_angle = mouth_openness * 1.2
        
        facing = self.current_dir if self.current_dir else self.last_dir
        
        draw_pacman(surface, COLOR_PACMAN, (center_x, center_y), radius, facing, mouth_angle)
