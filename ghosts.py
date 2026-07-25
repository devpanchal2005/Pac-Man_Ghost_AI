# ghosts.py
import math
import heapq
import pygame
from constants import TILE_SIZE

def is_walkable(row, col, state, grid):
    """
    Checks if a tile is walkable for a ghost depending on its current state.
    - Walls (1) are always blocked.
    - Ghost house tiles (3) are walkable during exiting/in_house, but blocked in chasing/frightened.
    """
    height = len(grid)
    width = len(grid[0])
    if not (0 <= row < height and 0 <= col < width):
        return False
    val = grid[row][col]
    if val == 1:
        return False
    if (state == "chasing" or state == "frightened") and val == 3:
        return False
    return True

def a_star(start, goal, state, grid):
    """
    Computes shortest path from start to goal using A*.
    Supports wrap-around tunnels for column boundaries.
    """
    if start == goal:
        return [start]
        
    height = len(grid)
    width = len(grid[0])
    
    # Priority queue stores: (f_score, counter, node)
    queue = []
    counter = 0
    
    g_score = {start: 0}
    h = abs(start[0] - goal[0]) + abs(start[1] - goal[1])
    heapq.heappush(queue, (h, counter, start))
    
    came_from = {}
    
    while queue:
        f, _, current = heapq.heappop(queue)
        
        if current == goal:
            # Reconstruct path
            path = []
            curr = current
            while curr in came_from:
                path.append(curr)
                curr = came_from[curr]
            path.append(start)
            path.reverse()
            return path
            
        curr_row, curr_col = current
        for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nr = curr_row + dr
            nc = curr_col + dc
            
            # Apply wrap-around horizontally
            if nc < 0:
                nc = width - 1
            elif nc >= width:
                nc = 0
                
            if not is_walkable(nr, nc, state, grid):
                continue
                
            tentative_g = g_score[current] + 1
            neighbor = (nr, nc)
            
            if neighbor not in g_score or tentative_g < g_score[neighbor]:
                g_score[neighbor] = tentative_g
                came_from[neighbor] = current
                h_neighbor = abs(nr - goal[0]) + abs(nc - goal[1])
                counter += 1
                heapq.heappush(queue, (tentative_g + h_neighbor, counter, neighbor))
                
    return []

def draw_ghost(surface, color, center, radius, direction_name):
    """
    Draws a classic retro arcade ghost with a rounded top, wavy bottom scallops,
    and direction-pointing white eyes with blue pupils.
    """
    x, y = center
    
    # 1. Main body polygon
    points = []
    
    # Rounded top semi-circle (angles pi to 2*pi)
    num_top_points = 16
    for i in range(num_top_points + 1):
        angle = math.pi + (math.pi * i / num_top_points)
        px = x + radius * math.cos(angle)
        py = y + radius * math.sin(angle)
        points.append((px, py))
        
    # Wavy bottom from right to left (adds scallops pointing down)
    num_bottom_points = 12
    wave_amp = radius * 0.25
    right_x = x + radius
    for i in range(num_bottom_points + 1):
        t = i / num_bottom_points
        px = right_x - (radius * 2.0) * t
        py = y + radius - abs(math.sin(t * 3.0 * math.pi)) * wave_amp
        points.append((px, py))
        
    pygame.draw.polygon(surface, color, points)
    
    # 2. Eyes
    dx_eye, dy_eye = 0, 0
    dx_pupil, dy_pupil = 0, 0
    
    eye_shift = radius * 0.12
    pupil_shift = radius * 0.22
    
    if direction_name == "LEFT":
        dx_eye = -eye_shift
        dx_pupil = -pupil_shift
    elif direction_name == "RIGHT":
        dx_eye = eye_shift
        dx_pupil = pupil_shift
    elif direction_name == "UP":
        dy_eye = -eye_shift
        dy_pupil = -pupil_shift
    elif direction_name == "DOWN":
        dy_eye = eye_shift
        dy_pupil = pupil_shift
        
    # Left & Right Eye center coordinates
    left_eye_x = x - radius * 0.35 + dx_eye
    left_eye_y = y - radius * 0.15 + dy_eye
    right_eye_x = x + radius * 0.35 + dx_eye
    right_eye_y = y - radius * 0.15 + dy_eye
    
    # Ellipse proportions for retro eyes
    eye_w = radius * 0.32
    eye_h = radius * 0.4
    
    left_rect = pygame.Rect(left_eye_x - eye_w / 2.0, left_eye_y - eye_h / 2.0, eye_w, eye_h)
    right_rect = pygame.Rect(right_eye_x - eye_w / 2.0, right_eye_y - eye_h / 2.0, eye_w, eye_h)
    
    pygame.draw.ellipse(surface, (255, 255, 255), left_rect)
    pygame.draw.ellipse(surface, (255, 255, 255), right_rect)
    
    # Blue pupils
    pupil_color = (0, 0, 255)
    pupil_radius = radius * 0.14
    
    left_pupil_x = left_eye_x + dx_pupil * 0.5
    left_pupil_y = left_eye_y + dy_pupil * 0.5
    right_pupil_x = right_eye_x + dx_pupil * 0.5
    right_pupil_y = right_eye_y + dy_pupil * 0.5
    
    pygame.draw.circle(surface, pupil_color, (int(left_pupil_x), int(left_pupil_y)), int(pupil_radius))
    pygame.draw.circle(surface, pupil_color, (int(right_pupil_x), int(right_pupil_y)), int(pupil_radius))

class Ghost:
    def __init__(self, grid, color):
        self.grid = grid
        self.rows = len(grid)
        self.cols = len(grid[0])
        self.color = color
        
        # Start inside the ghost house
        self.row = 14
        self.col = 13
        
        self.pixel_x = float(self.col * TILE_SIZE)
        self.pixel_y = float(self.row * TILE_SIZE)
        
        self.speed = 2.0  # speed matches Pac-Man
        self.current_dir = "UP"
        
        # States: "in_house", "exiting", "chasing", "frightened"
        self.state = "in_house"
        
        self.target_row = self.row
        self.target_col = self.col
        self.path = []
        
        self.recalc_timer = 0

    def get_next_move(self, grid, start_tile, target_tile):
        """
        To be overridden by subclasses.
        Returns: list of (row, col) coordinates representing the path.
        """
        return []

    def update(self, pacman_pos):
        # 1. State transition from in_house to exiting
        if self.state == "in_house":
            self.state = "exiting"
            self.path = []
            
        # 2. Recalculate chasing path periodically
        if self.state == "chasing":
            self.recalc_timer += 1
            if self.recalc_timer >= 10:
                self.recalc_timer = 0
                start_tile = (self.target_row, self.target_col)
                new_path = self.get_next_move(self.grid, start_tile, pacman_pos)
                if new_path:
                    self.path = new_path
                    
        # 3. Handle grid alignment and target selection
        dx = self.target_col - self.col
        dy = self.target_row - self.row
        
        # Handle wrap-around distance calculation
        if dx > 1:
            dx = -1
        elif dx < -1:
            dx = 1
            
        dest_pixel_x = (self.col + dx) * TILE_SIZE
        dest_pixel_y = (self.row + dy) * TILE_SIZE
        
        if self.pixel_x == dest_pixel_x and self.pixel_y == dest_pixel_y:
            # Wrap pixel positions to grid boundaries
            self.pixel_x = self.pixel_x % (self.cols * TILE_SIZE)
            self.pixel_y = self.pixel_y % (self.rows * TILE_SIZE)
            
            # Snap grid coordinates
            self.col = int(self.pixel_x // TILE_SIZE)
            self.row = int(self.pixel_y // TILE_SIZE)
            
            # Transition from exiting to chasing once the exit door is reached
            if self.state == "exiting" and (self.row, self.col) == (12, 13):
                self.state = "chasing"
                self.path = []
                self.recalc_timer = 10  # Force immediate path recalculation on next frame
                
            # If path is empty, compute new path to target
            if not self.path:
                if self.state == "exiting":
                    self.path = a_star((self.row, self.col), (12, 13), self.state, self.grid)
                elif self.state == "chasing":
                    self.path = self.get_next_move(self.grid, (self.row, self.col), pacman_pos)
                    
            # Pop the first element of path (current node)
            if self.path and self.path[0] == (self.row, self.col):
                self.path.pop(0)
                
            # Set next destination target
            if self.path:
                self.target_row, self.target_col = self.path[0]
                
                # Update current direction based on new target
                d_row = self.target_row - self.row
                d_col = self.target_col - self.col
                if d_col > 1:
                    d_col = -1
                elif d_col < -1:
                    d_col = 1
                    
                if d_row == -1:
                    self.current_dir = "UP"
                elif d_row == 1:
                    self.current_dir = "DOWN"
                elif d_col == -1:
                    self.current_dir = "LEFT"
                elif d_col == 1:
                    self.current_dir = "RIGHT"
            else:
                self.target_row, self.target_col = self.row, self.col
                
            # Recompute destination pixel coordinates immediately
            dx = self.target_col - self.col
            dy = self.target_row - self.row
            if dx > 1:
                dx = -1
            elif dx < -1:
                dx = 1
            dest_pixel_x = (self.col + dx) * TILE_SIZE
            dest_pixel_y = (self.row + dy) * TILE_SIZE

        # 4. Perform movement
        if self.pixel_x < dest_pixel_x:
            self.pixel_x = min(self.pixel_x + self.speed, dest_pixel_x)
        elif self.pixel_x > dest_pixel_x:
            self.pixel_x = max(self.pixel_x - self.speed, dest_pixel_x)
            
        if self.pixel_y < dest_pixel_y:
            self.pixel_y = min(self.pixel_y + self.speed, dest_pixel_y)
        elif self.pixel_y > dest_pixel_y:
            self.pixel_y = max(self.pixel_y - self.speed, dest_pixel_y)

    def draw(self, surface, y_offset):
        center_x = self.pixel_x + TILE_SIZE / 2.0
        center_y = self.pixel_y + TILE_SIZE / 2.0 + y_offset
        radius = TILE_SIZE / 2.0 - 1.0
        draw_ghost(surface, self.color, (center_x, center_y), radius, self.current_dir)

class BlinkyGhost(Ghost):
    def get_next_move(self, grid, start_tile, target_tile):
        """
        Blinky's AI is direct-chase: target Pac-Man directly using A* search.
        """
        return a_star(start_tile, target_tile, self.state, grid)
