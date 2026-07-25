# fruit.py
import pygame

class Fruit:
    def __init__(self, row=17, col=13):
        self.row = row
        self.col = col
        self.active = False
        self.timer = 0  # 10s @ 60 FPS = 600 frames

    def spawn(self):
        self.active = True
        self.timer = 600

    def update(self):
        if self.active:
            self.timer -= 1
            if self.timer <= 0:
                self.active = False

    def draw(self, surface, tile_size, y_offset):
        if not self.active:
            return
            
        # Draw a beautiful retro cherry fruit centered in the tile
        center_x = int((self.col + 0.5) * tile_size)
        center_y = int((self.row + 0.5) * tile_size + y_offset)
        
        # Red cherry bodies (scaled up and offset side by side to not overlap)
        c1_x = center_x - 9
        c1_y = center_y + 3
        c2_x = center_x + 9
        c2_y = center_y - 1
        
        # Stems (green, thickness 2px)
        stem_color = (20, 180, 20)
        top_x = center_x
        top_y = center_y - 9
        pygame.draw.line(surface, stem_color, (c1_x, c1_y), (top_x, top_y), 2)
        pygame.draw.line(surface, stem_color, (c2_x, c2_y), (top_x, top_y), 2)
        
        # Draw small green leaf near the top of the stem
        leaf_color = (20, 180, 20)
        leaf_pts = [
            (top_x, top_y),
            (top_x - 6, top_y - 3),
            (top_x - 3, top_y - 7)
        ]
        pygame.draw.polygon(surface, (0, 0, 0), leaf_pts, 3) # Outline
        pygame.draw.polygon(surface, leaf_color, leaf_pts)    # Fill
        
        # Cherry body circles (red with thick black borders)
        cherry_color = (230, 20, 20)
        radius = 6
        
        # Draw outer outline first (radius + 2px in black) to prevent heart silhouette merging
        pygame.draw.circle(surface, (0, 0, 0), (c1_x, c1_y), radius + 2)
        pygame.draw.circle(surface, (0, 0, 0), (c2_x, c2_y), radius + 2)
        
        # Draw filled cherry body (radius 6px in red)
        pygame.draw.circle(surface, cherry_color, (c1_x, c1_y), radius)
        pygame.draw.circle(surface, cherry_color, (c2_x, c2_y), radius)
