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

def draw_ghost(surface, color, center, radius, direction_name, frightened=False):
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
        
    # Scalloped bottom from right to left (creates 3 prominent rounded feet pointing down)
    num_scallops = 3
    scallop_width = (radius * 2.0) / num_scallops
    wave_amp = radius * 0.35  # Prominent waves
    
    for s in range(num_scallops):
        x_start = x + radius - s * scallop_width
        x_end = x + radius - (s + 1) * scallop_width
        
        num_seg = 8
        for j in range(num_seg + 1):
            t = j / num_seg
            px = x_start + (x_end - x_start) * t
            # Rounded bump pointing down
            py = y + radius - wave_amp + math.sin(t * math.pi) * wave_amp
            points.append((px, py))
            
    # Draw solid filled body
    pygame.draw.polygon(surface, color, points)
    # Draw a thin black outline for contrast
    pygame.draw.polygon(surface, (0, 0, 0), points, 1)
    
    if frightened:
        # Frightened face: two small white circles and a wavy zigzag frown mouth
        left_eye_center = (int(x - radius * 0.22), int(y - radius * 0.15))
        right_eye_center = (int(x + radius * 0.22), int(y - radius * 0.15))
        eye_r = max(2, int(radius * 0.15))
        
        # Draw eyes (1px black outline + white fill)
        pygame.draw.circle(surface, (0, 0, 0), left_eye_center, eye_r + 1)
        pygame.draw.circle(surface, (255, 255, 255), left_eye_center, eye_r)
        
        pygame.draw.circle(surface, (0, 0, 0), right_eye_center, eye_r + 1)
        pygame.draw.circle(surface, (255, 255, 255), right_eye_center, eye_r)
        
        # Wavy zigzag mouth: short horizontal line of 3-4 connected zigzag segments
        mx = x
        my = y + radius * 0.35
        mw = radius * 0.65
        mh = radius * 0.15
        
        mouth_points = [
            (mx - mw / 2.0, my + mh / 2.0),
            (mx - mw / 4.0, my - mh / 2.0),
            (mx, my + mh / 2.0),
            (mx + mw / 4.0, my - mh / 2.0),
            (mx + mw / 2.0, my + mh / 2.0)
        ]
        
        # Draw outline (4px black) then line (2px white) for contrast
        mouth_points = [(int(px), int(py)) for px, py in mouth_points]
        pygame.draw.lines(surface, (0, 0, 0), False, mouth_points, 4)
        pygame.draw.lines(surface, (255, 255, 255), False, mouth_points, 2)
        return
    
    # 2. Eyes
    dx_eye, dy_eye = 0, 0
    dx_pupil, dy_pupil = 0, 0
    
    eye_shift = radius * 0.15
    pupil_shift = radius * 0.2
    
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
    
    # White sclera (larger and prominent: 32% radius to 65% radius)
    eye_w = radius * 0.65
    eye_h = radius * 0.75
    
    left_rect = pygame.Rect(left_eye_x - eye_w / 2.0, left_eye_y - eye_h / 2.0, eye_w, eye_h)
    right_rect = pygame.Rect(right_eye_x - eye_w / 2.0, right_eye_y - eye_h / 2.0, eye_w, eye_h)
    
    pygame.draw.ellipse(surface, (255, 255, 255), left_rect)
    pygame.draw.ellipse(surface, (255, 255, 255), right_rect)
    
    # Blue pupils (larger for high contrast)
    pupil_color = (0, 0, 255)
    pupil_radius = radius * 0.22
    
    left_pupil_x = left_eye_x + dx_pupil
    left_pupil_y = left_eye_y + dy_pupil
    right_pupil_x = right_eye_x + dx_pupil
    right_pupil_y = right_eye_y + dy_pupil
    
    pygame.draw.circle(surface, pupil_color, (int(left_pupil_x), int(left_pupil_y)), int(pupil_radius))
    pygame.draw.circle(surface, pupil_color, (int(right_pupil_x), int(right_pupil_y)), int(pupil_radius))

def find_nearest_walkable(grid, start_r, start_c, state):
    """
    Performs a BFS starting from (start_r, start_c) to find the closest valid walkable tile.
    Clamps the search within grid bounds.
    """
    height = len(grid)
    width = len(grid[0])
    
    # Clamp starting coordinates to bounds
    start_r = max(0, min(start_r, height - 1))
    start_c = max(0, min(start_c, width - 1))
    
    if is_walkable(start_r, start_c, state, grid):
        return start_r, start_c
        
    queue = [(start_r, start_c)]
    visited = {(start_r, start_c)}
    
    while queue:
        r, c = queue.pop(0)
        
        for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nr = r + dr
            nc = c + dc
            
            # Apply wrap-around horizontally
            if nc < 0:
                nc = width - 1
            elif nc >= width:
                nc = 0
                
            if 0 <= nr < height:
                if (nr, nc) not in visited:
                    visited.add((nr, nc))
                    if is_walkable(nr, nc, state, grid):
                        return nr, nc
                    queue.append((nr, nc))
                    
    return start_r, start_c  # Fallback

class Ghost:
    def __init__(self, grid, color, start_tile=(14, 13), release_delay=0):
        self.grid = grid
        self.rows = len(grid)
        self.cols = len(grid[0])
        self.color = color
        
        self.start_tile = start_tile
        self.row, self.col = start_tile
        
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
        
        # Release delay and timer (in frames)
        self.release_delay = release_delay
        self.release_timer = 0

        # Cache walkable tiles for frightened mode random target
        self.walkable_tiles = []
        for r in range(self.rows):
            for c in range(self.cols):
                if grid[r][c] != 1 and grid[r][c] != 3:
                    self.walkable_tiles.append((r, c))

    def reset(self):
        self.row, self.col = self.start_tile
        self.pixel_x = float(self.col * TILE_SIZE)
        self.pixel_y = float(self.row * TILE_SIZE)
        self.current_dir = "UP"
        self.state = "in_house"
        self.target_row = self.row
        self.target_col = self.col
        self.path = []
        self.recalc_timer = 0
        self.release_timer = 0

    def get_frightened_target(self):
        import random
        if self.walkable_tiles:
            return random.choice(self.walkable_tiles)
        return (1, 1)

    def get_target_tile(self, pacman_pos, pacman_dir, blinky_pos):
        """
        To be overridden by subclasses.
        Returns: (row, col) target tile for pathfinding.
        """
        return pacman_pos

    def get_next_move(self, grid, start_tile, target_tile):
        """
        To be overridden by subclasses.
        Returns: list of (row, col) coordinates representing the path.
        """
        return []

    def update(self, pacman_pos, pacman_dir="RIGHT", blinky_pos=None, frightened_timer=0):
        # Dynamically set speed based on state
        if self.state == "frightened":
            self.speed = 1.5
        else:
            self.speed = 2.0

        # 1. State transition from in_house to exiting after release_delay
        if self.state == "in_house":
            self.release_timer += 1
            if self.release_timer >= self.release_delay:
                self.state = "exiting"
                self.path = []
            else:
                return
            
        # 2. Recalculate chasing or frightened path periodically
        if self.state in ("chasing", "frightened"):
            self.recalc_timer += 1
            if self.recalc_timer >= 10:
                self.recalc_timer = 0
                start_tile = (self.target_row, self.target_col)
                if self.state == "chasing":
                    target_tile = self.get_target_tile(pacman_pos, pacman_dir, blinky_pos)
                else: # frightened
                    target_tile = self.get_frightened_target()
                new_path = self.get_next_move(self.grid, start_tile, target_tile)
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
            
            # Transition from exiting to chasing/frightened once the exit door is reached
            if self.state == "exiting" and (self.row, self.col) == (12, 13):
                if frightened_timer > 0:
                    self.state = "frightened"
                else:
                    self.state = "chasing"
                self.path = []
                self.recalc_timer = 10  # Force immediate path recalculation on next frame
                
            # If path is empty, compute new path to target
            if not self.path:
                if self.state == "exiting":
                    self.path = a_star((self.row, self.col), (12, 13), self.state, self.grid)
                elif self.state == "chasing":
                    target_tile = self.get_target_tile(pacman_pos, pacman_dir, blinky_pos)
                    self.path = self.get_next_move(self.grid, (self.row, self.col), target_tile)
                elif self.state == "frightened":
                    target_tile = self.get_frightened_target()
                    self.path = self.get_next_move(self.grid, (self.row, self.col), target_tile)
                    
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

    def draw(self, surface, y_offset, frightened_timer=0):
        # Do not draw if still waiting in house (or draw them stationary)
        # Requirement: "Start inside the ghost house in 'in_house' state... reuse exiting behavior... Render both"
        # We should draw them at their current position, even if in_house.
        center_x = self.pixel_x + TILE_SIZE / 2.0
        center_y = self.pixel_y + TILE_SIZE / 2.0 + y_offset
        radius = TILE_SIZE * 0.42
        
        # Determine color
        draw_color = self.color
        if self.state == "frightened":
            if frightened_timer > 0 and frightened_timer <= 120:
                # Flash between dark blue and white
                flash = (frightened_timer // 10) % 2 == 0
                if flash:
                    draw_color = (255, 255, 255) # White
                else:
                    draw_color = (33, 33, 222) # Dark blue
            else:
                draw_color = (33, 33, 222) # Dark blue
                
        draw_ghost(surface, draw_color, (center_x, center_y), radius, self.current_dir, frightened=(self.state == "frightened"))

class BlinkyGhost(Ghost):
    def get_target_tile(self, pacman_pos, pacman_dir, blinky_pos):
        return pacman_pos

    def get_next_move(self, grid, start_tile, target_tile):
        return a_star(start_tile, target_tile, self.state, grid)

class PinkyGhost(Ghost):
    def get_target_tile(self, pacman_pos, pacman_dir, blinky_pos):
        pr, pc = pacman_pos
        
        # Direction vector
        dr, dc = 0, 0
        if pacman_dir == "UP":
            dr = -1
        elif pacman_dir == "DOWN":
            dr = 1
        elif pacman_dir == "LEFT":
            dc = -1
        elif pacman_dir == "RIGHT":
            dc = 1
            
        # Target is 4 tiles ahead in Pac-Man's current facing direction.
        # Clamp to furthest walkable tile along the path if we hit a wall.
        target_r, target_c = pr, pc
        for step in range(1, 5):
            nr = pr + dr * step
            nc = pc + dc * step
            
            # Apply wrap-around horizontally for the columns
            if nc < 0:
                nc = self.cols - 1
            elif nc >= self.cols:
                nc = 0
                
            if 0 <= nr < self.rows:
                if is_walkable(nr, nc, self.state, self.grid):
                    target_r, target_c = nr, nc
                else:
                    break
            else:
                break
                
        return target_r, target_c

    def get_next_move(self, grid, start_tile, target_tile):
        return a_star(start_tile, target_tile, self.state, grid)

class InkyGhost(Ghost):
    def get_target_tile(self, pacman_pos, pacman_dir, blinky_pos):
        if not blinky_pos:
            blinky_pos = (14, 13)
            
        pr, pc = pacman_pos
        br, bc = blinky_pos
        
        # 1. Intermediate tile: 2 tiles ahead of Pac-Man
        dr, dc = 0, 0
        if pacman_dir == "UP":
            dr = -1
        elif pacman_dir == "DOWN":
            dr = 1
        elif pacman_dir == "LEFT":
            dc = -1
        elif pacman_dir == "RIGHT":
            dc = 1
            
        ir = pr + dr * 2
        ic = pc + dc * 2
        # Apply wrapping
        ic = ic % self.cols
        
        # 2. Vector from Blinky to Intermediate tile, doubled
        vec_r = ir - br
        vec_c = ic - bc
        
        target_r = br + 2 * vec_r
        target_c = bc + 2 * vec_c
        
        # 3. Clamp target to grid bounds and find nearest walkable tile
        return find_nearest_walkable(self.grid, target_r, target_c, self.state)

    def get_next_move(self, grid, start_tile, target_tile):
        return a_star(start_tile, target_tile, self.state, grid)

class ClydeGhost(Ghost):
    def __init__(self, grid, color, start_tile=(14, 15), release_delay=360):
        super().__init__(grid, color, start_tile, release_delay)

    def get_target_tile(self, pacman_pos, pacman_dir, blinky_pos):
        pr, pc = pacman_pos
        # Manhattan distance on grid coords
        dist = abs(self.row - pr) + abs(self.col - pc)
        
        if dist > 8:
            # Target Pac-Man directly (like Blinky)
            return pacman_pos
        else:
            # Target fixed scatter corner bottom-left (29, 1) which is walkable path
            return (29, 1)

    def get_next_move(self, grid, start_tile, target_tile):
        return a_star(start_tile, target_tile, self.state, grid)
