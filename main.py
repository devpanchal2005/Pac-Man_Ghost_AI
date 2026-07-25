# main.py
import sys
import pygame
from constants import (
    VIRTUAL_WIDTH, VIRTUAL_HEIGHT, FPS, COLOR_BACKGROUND,
    COLOR_HUD_TEXT, HUD_HEIGHT, COLOR_GHOST_RED, COLOR_GHOST_PINK,
    COLOR_GHOST_CYAN, COLOR_GHOST_ORANGE
)
from maze import load_maze, render_maze
from pacman import PacMan
from ghosts import BlinkyGhost, PinkyGhost, InkyGhost, ClydeGhost, draw_ghost

def render_hud(surface, font, current_score=70, high_score=1920):
    """
    Renders the retro arcade HUD matching the reference screenshot:
    - Top-center: HIGH SCORE header, high score number below, current score to the left
    - Top-right: Pause icon (||) and Sound/Speaker icon
    """
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

def render_ghost_control_panel(surface, font, panel_font, bold_font, ghost_states):
    panel_w = 560
    panel_h = 320
    panel_x = (VIRTUAL_WIDTH - panel_w) // 2
    panel_y = (VIRTUAL_HEIGHT - panel_h) // 2

    # Draw semi-transparent background
    panel_surf = pygame.Surface((panel_w, panel_h), pygame.SRCALPHA)
    panel_surf.fill((10, 10, 10, 230))  # Dark gray/black
    pygame.draw.rect(panel_surf, (255, 255, 255), (0, 0, panel_w, panel_h), 2)  # border
    surface.blit(panel_surf, (panel_x, panel_y))

    # Title
    title_surf = bold_font.render("GHOST CONTROL PANEL", True, (255, 255, 0))
    title_rect = title_surf.get_rect(center=(VIRTUAL_WIDTH // 2, panel_y + 25))
    surface.blit(title_surf, title_rect)

    # Subtitle or instructions
    inst_surf = panel_font.render("Click a row or press 1-4 to toggle ghosts. Close to resume.", True, (180, 180, 180))
    inst_rect = inst_surf.get_rect(center=(VIRTUAL_WIDTH // 2, panel_y + 45))
    surface.blit(inst_surf, inst_rect)

    # Rows definitions
    rows_info = [
        {"name": "Blinky", "color": COLOR_GHOST_RED, "desc": "Direct chase — always targets Pac-Man's current tile."},
        {"name": "Pinky", "color": COLOR_GHOST_PINK, "desc": "Ambush — targets 4 tiles ahead of Pac-Man's facing direction."},
        {"name": "Inky", "color": COLOR_GHOST_CYAN, "desc": "Flank — targets a point mirrored through Blinky's position."},
        {"name": "Clyde", "color": COLOR_GHOST_ORANGE, "desc": "Shy — chases when far, retreats to a corner when close."}
    ]

    for idx, info in enumerate(rows_info):
        row_y = panel_y + 75 + idx * 55
        
        # Draw bounding line or box for the row
        pygame.draw.rect(surface, (40, 40, 40), (panel_x + 15, row_y, panel_w - 30, 48), 1)

        # Color Swatch: Use actual ghost sprite!
        swatch_x = panel_x + 30
        swatch_y = row_y + 24
        draw_ghost(surface, info["color"], (swatch_x, swatch_y), 12.0, "RIGHT")

        # Name
        name_surf = bold_font.render(info["name"], True, (255, 255, 255))
        surface.blit(name_surf, (panel_x + 55, row_y + 8))

        # Description
        desc_surf = panel_font.render(info["desc"], True, (200, 200, 200))
        surface.blit(desc_surf, (panel_x + 55, row_y + 28))

        # Toggle state ON/OFF
        is_on = ghost_states[info["name"]]
        status_text = "ON" if is_on else "OFF"
        status_color = (0, 255, 0) if is_on else (255, 0, 0)
        
        status_surf = bold_font.render(status_text, True, status_color)
        status_rect = status_surf.get_rect(center=(panel_x + panel_w - 45, row_y + 24))
        surface.blit(status_surf, status_rect)

def main():
    # Initialize Pygame and Font system
    pygame.init()
    pygame.font.init()

    # Monospace pixel/retro font for arcade HUD
    retro_font = pygame.font.SysFont("monospace", 16, bold=True)
    panel_desc_font = pygame.font.SysFont("monospace", 12, bold=False)
    panel_bold_font = pygame.font.SysFont("monospace", 14, bold=True)

    # Create fullscreen window by default
    screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
    pygame.display.set_caption("Pac-Man Ghost AI - Arcade Renderer")

    # Create fixed logical virtual canvas buffer
    virtual_surface = pygame.Surface((VIRTUAL_WIDTH, VIRTUAL_HEIGHT))

    clock = pygame.time.Clock()
    grid = load_maze()
    pacman = PacMan(grid)
    
    # Initialize all 4 ghosts inside the house (including Clyde)
    blinky = BlinkyGhost(grid, COLOR_GHOST_RED, start_tile=(14, 13), release_delay=0)
    pinky = PinkyGhost(grid, COLOR_GHOST_PINK, start_tile=(14, 12), release_delay=120)
    inky = InkyGhost(grid, COLOR_GHOST_CYAN, start_tile=(14, 14), release_delay=240)
    clyde = ClydeGhost(grid, COLOR_GHOST_ORANGE, start_tile=(14, 15), release_delay=360)
    
    # Enabled states dictionary (default: all ON)
    ghost_states = {"Blinky": True, "Pinky": True, "Inky": True, "Clyde": True}
    
    score = 0
    high_score = 1920

    running = True
    fullscreen = True
    panel_open = False
    while running:
        # Handle Events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left click
                    mx, my = event.pos
                    
                    # Convert to virtual coordinates
                    win_w, win_h = screen.get_size()
                    scale = min(win_w / VIRTUAL_WIDTH, win_h / VIRTUAL_HEIGHT)
                    offset_x = (win_w - max(1, int(VIRTUAL_WIDTH * scale))) // 2
                    offset_y = (win_h - max(1, int(VIRTUAL_HEIGHT * scale))) // 2
                    
                    vx = (mx - offset_x) / scale
                    vy = (my - offset_y) / scale
                    
                    # Check play/pause button (VIRTUAL_WIDTH - 64 <= vx <= VIRTUAL_WIDTH - 30, y: 10 <= vy <= 38)
                    if (VIRTUAL_WIDTH - 64 <= vx <= VIRTUAL_WIDTH - 30) and (10 <= vy <= 38):
                        panel_open = not panel_open
                        
                    # Check row clicks if panel open
                    elif panel_open:
                        panel_w = 560
                        panel_h = 320
                        panel_x = (VIRTUAL_WIDTH - panel_w) // 2
                        panel_y = (VIRTUAL_HEIGHT - panel_h) // 2
                        
                        if panel_x + 15 <= vx <= panel_x + panel_w - 15:
                            for idx, name in enumerate(["Blinky", "Pinky", "Inky", "Clyde"]):
                                row_y = panel_y + 75 + idx * 55
                                if row_y <= vy <= row_y + 48:
                                    ghost_states[name] = not ghost_states[name]
                                    if ghost_states[name]:
                                        if name == "Blinky": blinky.reset()
                                        elif name == "Pinky": pinky.reset()
                                        elif name == "Inky": inky.reset()
                                        elif name == "Clyde": clyde.reset()
                                        
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if panel_open:
                        panel_open = False
                    else:
                        running = False
                elif event.key == pygame.K_f or event.key == pygame.K_F11:
                    # Toggle Fullscreen Mode
                    fullscreen = not fullscreen
                    if fullscreen:
                        screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN | pygame.RESIZABLE)
                    else:
                        screen = pygame.display.set_mode((VIRTUAL_WIDTH, VIRTUAL_HEIGHT), pygame.RESIZABLE)
                
                # Keyboard 1-4 ghost toggles if panel open
                elif panel_open:
                    if event.key == pygame.K_1:
                        ghost_states["Blinky"] = not ghost_states["Blinky"]
                        if ghost_states["Blinky"]: blinky.reset()
                    elif event.key == pygame.K_2:
                        ghost_states["Pinky"] = not ghost_states["Pinky"]
                        if ghost_states["Pinky"]: pinky.reset()
                    elif event.key == pygame.K_3:
                        ghost_states["Inky"] = not ghost_states["Inky"]
                        if ghost_states["Inky"]: inky.reset()
                    elif event.key == pygame.K_4:
                        ghost_states["Clyde"] = not ghost_states["Clyde"]
                        if ghost_states["Clyde"]: clyde.reset()
                        
                # Pac-Man keyboard inputs (WASD or Arrow Keys)
                elif not panel_open:
                    if event.key in (pygame.K_UP, pygame.K_w):
                        pacman.queued_dir = "UP"
                    elif event.key in (pygame.K_DOWN, pygame.K_s):
                        pacman.queued_dir = "DOWN"
                    elif event.key in (pygame.K_LEFT, pygame.K_a):
                        pacman.queued_dir = "LEFT"
                    elif event.key in (pygame.K_RIGHT, pygame.K_d):
                        pacman.queued_dir = "RIGHT"

        # Update states if panel is closed (not paused)
        if not panel_open:
            # Update Pac-Man state and handle pellet consumption
            score_gain = pacman.update()
            score += score_gain
            high_score = max(high_score, score)

            # Determine Pac-Man's active facing direction
            pacman_facing = pacman.current_dir if pacman.current_dir else pacman.last_dir

            # Update enabled ghosts AI and chase targeting
            if ghost_states["Blinky"]:
                blinky.update((pacman.row, pacman.col), pacman_facing)
            if ghost_states["Pinky"]:
                pinky.update((pacman.row, pacman.col), pacman_facing)
            if ghost_states["Inky"]:
                inky.update((pacman.row, pacman.col), pacman_facing, blinky_pos=(blinky.row, blinky.col))
            if ghost_states["Clyde"]:
                clyde.update((pacman.row, pacman.col), pacman_facing, blinky_pos=(blinky.row, blinky.col))

            # Check collision between Pac-Man and any active ghosts
            collision_detected = False
            if ghost_states["Blinky"] and blinky.row == pacman.row and blinky.col == pacman.col:
                collision_detected = True
            if ghost_states["Pinky"] and pinky.row == pacman.row and pinky.col == pacman.col:
                collision_detected = True
            if ghost_states["Inky"] and inky.row == pacman.row and inky.col == pacman.col:
                collision_detected = True
            if ghost_states["Clyde"] and clyde.row == pacman.row and clyde.col == pacman.col:
                collision_detected = True
                
            if collision_detected:
                print("Pac-Man caught!")

        # Clear Virtual Buffer
        virtual_surface.fill(COLOR_BACKGROUND)

        # 1. Render Top Arcade HUD
        render_hud(virtual_surface, retro_font, current_score=score, high_score=high_score)

        # 2. Render Arcade Maze Layout
        render_maze(virtual_surface, grid)

        # 3. Render Pac-Man
        pacman.draw(virtual_surface, HUD_HEIGHT)

        # 4. Render Ghosts
        if ghost_states["Blinky"]:
            blinky.draw(virtual_surface, HUD_HEIGHT)
        if ghost_states["Pinky"]:
            pinky.draw(virtual_surface, HUD_HEIGHT)
        if ghost_states["Inky"]:
            inky.draw(virtual_surface, HUD_HEIGHT)
        if ghost_states["Clyde"]:
            clyde.draw(virtual_surface, HUD_HEIGHT)

        # 5. Render Ghost Control Panel Overlay if open
        if panel_open:
            # Cheap blur trick using downscale-then-upscale
            temp_blur = pygame.transform.smoothscale(virtual_surface, (VIRTUAL_WIDTH // 2, VIRTUAL_HEIGHT // 2))
            pygame.transform.smoothscale(temp_blur, (VIRTUAL_WIDTH, VIRTUAL_HEIGHT), virtual_surface)

            # Darken overlay
            dim_overlay = pygame.Surface((VIRTUAL_WIDTH, VIRTUAL_HEIGHT), pygame.SRCALPHA)
            dim_overlay.fill((0, 0, 0, 160))
            virtual_surface.blit(dim_overlay, (0, 0))

            render_ghost_control_panel(virtual_surface, retro_font, panel_desc_font, panel_bold_font, ghost_states)

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
