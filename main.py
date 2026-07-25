# main.py
import sys
import pygame
from constants import (
    VIRTUAL_WIDTH, VIRTUAL_HEIGHT, FPS, COLOR_BACKGROUND,
    COLOR_HUD_TEXT, HUD_HEIGHT
)
from maze import load_maze, render_maze
from pacman import PacMan

def render_hud(surface, font, current_score=70, high_score=1920):
    """
    Renders the retro arcade HUD matching the reference screenshot:
    - Top-left: Hamburger menu icon (3 horizontal white bars)
    - Top-center: HIGH SCORE header, high score number below, current score to the left
    - Top-right: Pause icon (||) and Sound/Speaker icon
    """
    # 1. Top-Left Hamburger Menu Icon (3 horizontal parallel bars)
    icon_x = 16
    icon_y = 16
    bar_w = 26
    bar_spacing = 8
    line_thickness = 3
    for i in range(3):
        y = icon_y + i * bar_spacing
        pygame.draw.line(surface, COLOR_HUD_TEXT, (icon_x, y), (icon_x + bar_w, y), line_thickness)

    # 2. Top-Center Scores
    # Header: "HIGH SCORE"
    high_score_lbl = font.render("HIGH SCORE", True, COLOR_HUD_TEXT)
    lbl_rect = high_score_lbl.get_rect(center=(VIRTUAL_WIDTH // 2, 16))
    surface.blit(high_score_lbl, lbl_rect)

    # High score value (centered under "HIGH SCORE")
    high_val_surf = font.render(str(high_score), True, COLOR_HUD_TEXT)
    high_val_rect = high_val_surf.get_rect(center=(VIRTUAL_WIDTH // 2, 36))
    surface.blit(high_val_surf, high_val_rect)

    # Current score value (to the left of HIGH SCORE)
    curr_val_surf = font.render(str(current_score), True, COLOR_HUD_TEXT)
    curr_val_rect = curr_val_surf.get_rect(center=(VIRTUAL_WIDTH // 2 - 120, 36))
    surface.blit(curr_val_surf, curr_val_rect)

    # 3. Top-Right Icons: Pause (||) and Speaker
    # Pause Icon (||)
    pause_x = VIRTUAL_WIDTH - 54
    pause_y = 16
    bar_w = 4
    bar_h = 16
    gap = 6
    pygame.draw.rect(surface, COLOR_HUD_TEXT, (pause_x, pause_y, bar_w, bar_h))
    pygame.draw.rect(surface, COLOR_HUD_TEXT, (pause_x + bar_w + gap, pause_y, bar_w, bar_h))

    # Sound/Speaker Icon
    spk_x = VIRTUAL_WIDTH - 24
    spk_y = 16
    # Speaker body
    pygame.draw.polygon(surface, COLOR_HUD_TEXT, [
        (spk_x, spk_y + 4),
        (spk_x + 4, spk_y + 4),
        (spk_x + 9, spk_y),
        (spk_x + 9, spk_y + 16),
        (spk_x + 4, spk_y + 12),
        (spk_x, spk_y + 12)
    ])
    # Sound waves
    pygame.draw.arc(surface, COLOR_HUD_TEXT, (spk_x + 6, spk_y + 3, 8, 10), -1.0, 1.0, 2)
    pygame.draw.arc(surface, COLOR_HUD_TEXT, (spk_x + 8, spk_y, 12, 16), -1.0, 1.0, 2)

def main():
    # Initialize Pygame and Font system
    pygame.init()
    pygame.font.init()

    # Monospace pixel/retro font for arcade HUD
    retro_font = pygame.font.SysFont("monospace", 16, bold=True)

    # Create fullscreen window by default
    screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
    pygame.display.set_caption("Pac-Man Ghost AI - Arcade Renderer")

    # Create fixed logical virtual canvas buffer
    virtual_surface = pygame.Surface((VIRTUAL_WIDTH, VIRTUAL_HEIGHT))

    clock = pygame.time.Clock()
    grid = load_maze()
    pacman = PacMan(grid)
    score = 0
    high_score = 1920

    running = True
    fullscreen = True

    while running:
        # Handle Events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_f or event.key == pygame.K_F11:
                    # Toggle Fullscreen Mode
                    fullscreen = not fullscreen
                    if fullscreen:
                        screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN | pygame.RESIZABLE)
                    else:
                        screen = pygame.display.set_mode((VIRTUAL_WIDTH, VIRTUAL_HEIGHT), pygame.RESIZABLE)
                
                # Pac-Man keyboard inputs (WASD or Arrow Keys)
                elif event.key in (pygame.K_UP, pygame.K_w):
                    pacman.queued_dir = "UP"
                elif event.key in (pygame.K_DOWN, pygame.K_s):
                    pacman.queued_dir = "DOWN"
                elif event.key in (pygame.K_LEFT, pygame.K_a):
                    pacman.queued_dir = "LEFT"
                elif event.key in (pygame.K_RIGHT, pygame.K_d):
                    pacman.queued_dir = "RIGHT"

        # Update Pac-Man state and handle pellet consumption
        score_gain = pacman.update()
        score += score_gain
        high_score = max(high_score, score)

        # Clear Virtual Buffer
        virtual_surface.fill(COLOR_BACKGROUND)

        # 1. Render Top Arcade HUD
        render_hud(virtual_surface, retro_font, current_score=score, high_score=high_score)

        # 2. Render Arcade Maze Layout
        render_maze(virtual_surface, grid)

        # 3. Render Pac-Man
        pacman.draw(virtual_surface, HUD_HEIGHT)

        # 3. Dynamic Aspect-Ratio Scaling to Fit Window Screen
        win_w, win_h = screen.get_size()
        scale = min(win_w / VIRTUAL_WIDTH, win_h / VIRTUAL_HEIGHT)

        scaled_w = max(1, int(VIRTUAL_WIDTH * scale))
        scaled_h = max(1, int(VIRTUAL_HEIGHT * scale))

        offset_x = (win_w - scaled_w) // 2
        offset_y = (win_h - scaled_h) // 2

        # Scale virtual surface to calculated dimensions
        scaled_surface = pygame.transform.smoothscale(virtual_surface, (scaled_w, scaled_h))

        # Clear physical screen with pure black and blit centered scaled canvas
        screen.fill(COLOR_BACKGROUND)
        screen.blit(scaled_surface, (offset_x, offset_y))

        # Update Display Surface
        pygame.display.flip()

        # Cap Frame Rate at 60 FPS
        clock.tick(FPS)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
