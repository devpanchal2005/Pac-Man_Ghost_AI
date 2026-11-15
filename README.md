# Pac-Man Ghost AI
A classic Pac-Man clone built to demonstrate classical AI search algorithms through four distinct ghost personalities.

<p align="center">
  <a href="https://devpanchal2005.github.io/Pac-Man_Ghost_AI/"><b>▶ Play it in your browser</b></a>
  &nbsp;·&nbsp;
  <a href="docs/Pac-Man_Ghost_AI.pptx">Project presentation (.pptx)</a>
</p>

<p align="center">
  <img src="https://media.giphy.com/media/hkqefnFjn2MWVl6xvq/giphy.gif" alt="Pac-Man Ghost AI Demo" />
</p>

## Features
- **Arcade-Style Maze Rendering**: A double-stroke neon-blue corridor wall layout rendering system with corner truncation for crisp visual joints.
- **Smooth Grid Movement**: Pac-Man moves smoothly on pixel coordinates while maintaining snap-alignment to tile coordinates, complete with direction turn-queuing.
- **Four Distinct Ghost AIs**: Each of the 4 ghosts implements a unique real-time pathfinding destination algorithm inspired by the original Pac-Man arcade behavior.
- **Power Pellets & Frightened Mode**: Power Pellets trigger Frightened Mode, changing ghost states, altering colors (with a warning flash indicator), and doubling consecutive points.
- **Win/Lose Logic**: Pellet eating counts down to a victory win overlay. A 3-lives HUD system handles collision resets and Game Over screens.
- **In-Game Ghost Control Panel**: An overlay panel allowing users to toggle individual ghost states ON/OFF during gameplay to study specific behaviors.
- **Hybrid Audio System**: Coexistence of file-based retro sound effects (`.ogg` format) alongside procedurally generated sine/triangle wave loops and jingles.
- **Cherry Bonus Item**: A visually distinct cherry item that spawns at a fixed corridor after a set number of pellets are eaten, providing score boosts.
- **Runs in the Browser**: The same Python code is compiled to WebAssembly with [pygbag](https://pypi.org/project/pygbag/) and deployed automatically to GitHub Pages, so no install is needed to play.

---

## AI & Pathfinding Algorithms

### Pathfinding: A* Search vs. BFS & DFS
In this project, ghosts compute short paths to their targets using the **A* Search Algorithm**. 
- **Heuristic**: The algorithm uses the **Manhattan Distance** ($D = |x_1 - x_2| + |y_1 - y_2|$) as its heuristic function to estimate the remaining path cost to the target tile.
- **Why A* over BFS/DFS**:
  - **BFS (Breadth-First Search)** searches uniformly in all directions. While it guarantees the shortest path, it expands a massive number of nodes in open corridors, which is computationally expensive for real-time 60 FPS gameplay with multiple active entities. A* uses heuristic estimates to focus search directions directly toward the target, significantly reducing the node search space.
  - **DFS (Depth-First Search)** does not guarantee the shortest path, can result in irrational back-and-forth loops, and risks exploring long branches in cycles before finding a goal, making it completely unsuitable for real-time pathing.

---

### Ghost Personalities & Targeting Algorithms
Each ghost implements a distinct target-tile selection algorithm. Once a target is chosen, A* determines the next step.

| Ghost | Arcade Persona | Targeting Logic (In-Game Ghost Control Panel Descriptions) |
|---|---|---|
| **Blinky** (Red) | Shadow (Chaser) | **Direct chase** — always targets Pac-Man's current tile. |
| **Pinky** (Pink) | Speedy (Ambusher) | **Ambush** — targets 4 tiles ahead of Pac-Man's facing direction. |
| **Inky** (Cyan) | Bashful (Flanker) | **Flank** — targets a point mirrored through Blinky's position. Uses a combination of Pac-Man's position (2 tiles ahead) and Blinky's vector to surround the player. |
| **Clyde** (Orange) | Pokey (Shy) | **Shy** — chases Pac-Man directly when far (Manhattan distance > 8), but retreats to its fixed bottom-left corner when close. |

---

## Tech Stack
- **Language**: Python 3
- **Graphics Engine**: [Pygame Community Edition](https://pyga.me/) (pygame-ce 2.5.7)
- **Standard Libraries**: `asyncio` (browser-compatible game loop), `math`, `heapq` (for A* priority queues), `array` (for procedural sound buffers), `os`, `sys`, and `random`.
- **Web Build**: [pygbag](https://pypi.org/project/pygbag/) 0.9.3 (Python → WebAssembly)
- **Hosting / CI**: GitHub Pages, deployed by GitHub Actions

---

## Project Structure
```text
.
├── .github/workflows/
│   └── deploy.yml   # GitHub Actions: builds with pygbag and deploys build/web to the gh-pages branch
├── docs/
│   └── Pac-Man_Ghost_AI.pptx  # Project presentation (kept out of the web bundle)
├── sounds/          # Sound effects (.ogg)
├── audio.py         # SoundManager class loading OGG sounds, synthesizing procedural beeps/loops, and routing audio
├── constants.py     # Configuration constants (resolutions, grid properties, retro colors, and timing parameters)
├── fruit.py         # Fruit class handles spawning, timing, and drawing the cherry bonus item
├── ghosts.py        # A* algorithm implementation and base/individual subclasses for Blinky, Pinky, Inky, and Clyde
├── main.py          # Async entrypoint, Pygame setup, events loop, collision handlers, and HUD rendering
├── maze.py          # Classic Pac-Man maze grid layout definition, connectivity checks, and neon-blue tube wall drawing
├── pacman.py        # Pac-Man coordinate tracking, direction queue handling, movement, and wedge-mouth animations
├── favicon.png      # Browser tab icon for the web build
├── pygbag.ini       # pygbag config: folders/files excluded from the web bundle
├── pygbag.tmpl      # Custom pygbag HTML template (black page background)
├── requirements.txt # Project dependency requirements definition
└── LICENSE.txt      # MIT license file
```

---

## Setup & Running Instructions

> **Just want to play?** Open **[devpanchal2005.github.io/Pac-Man_Ghost_AI](https://devpanchal2005.github.io/Pac-Man_Ghost_AI/)** and click the page once to start. The steps below are for running it locally.

### 1. Clone the Repository
Clone this repository to your local system:
```bash
git clone https://github.com/devpanchal2005/Pac-Man_Ghost_AI.git
cd Pac-Man_Ghost_AI
```

### 2. Set Up Virtual Environment
Create and activate a virtual environment to manage dependencies:
- **Linux / macOS**:
  ```bash
  python3 -m venv .venv
  source .venv/bin/activate
  ```
- **Windows (Command Prompt)**:
  ```cmd
  python -m venv .venv
  .venv\Scripts\activate.bat
  ```
- **Windows (PowerShell)**:
  ```powershell
  python -m venv .venv
  .venv\Scripts\Activate.ps1
  ```

### 3. Install Dependencies
Install the required packages listed in `requirements.txt`:
```bash
pip install -r requirements.txt
```

### 4. Run the Game
Execute the python script from the virtual environment:
```bash
python main.py
```

---

## Web Build & Deployment

The game runs in the browser via [pygbag](https://pypi.org/project/pygbag/), which packages the Python code and assets and runs them on a WebAssembly build of CPython.

### Build and test locally
```bash
pip install pygbag==0.9.3
pygbag --template pygbag.tmpl .          # builds and serves at http://localhost:8000
pygbag --build --template pygbag.tmpl .  # build only; output goes to build/web
```

### Automatic deployment
Every push to `main` runs [.github/workflows/deploy.yml](.github/workflows/deploy.yml), which builds the game with pygbag and publishes `build/web` to the `gh-pages` branch. GitHub Pages serves that branch at [devpanchal2005.github.io/Pac-Man_Ghost_AI](https://devpanchal2005.github.io/Pac-Man_Ghost_AI/) (one-time setup: **Settings → Pages → Source: Deploy from a branch → `gh-pages`**).

### Web-specific notes
- `main()` is `async` and yields to the browser once per frame (`await asyncio.sleep(0)`), which pygbag requires.
- In the browser the game renders to a 2× framebuffer with nearest-neighbour scaling to keep pixels sharp; the desktop build is unchanged.
- Sounds are `.ogg`, because pygbag does not allow `.wav`/`.mp3` on the web.
- Browsers block audio until you interact with the page, so the game starts after the first click.
- `pygbag.tmpl` is a copy of pygbag 0.9.3's default template with a black background. If you upgrade pygbag, re-copy the new default template and reapply that change.

---

## Controls

| Action | Control Key / Mouse Button |
|---|---|
| **Move Pac-Man** | Arrow Keys or `W`/`A`/`S`/`D` |
| **Toggle Ghost Control Panel** | `ESC` key or Left-Click the Play/Pause icon (top-right HUD) |
| **Toggle Ghosts (Control Panel Open)** | Left-Click a row inside the panel or press keys `1`, `2`, `3`, `4` |
| **Mute / Unmute Audio** | Left-Click the Speaker/Mute icon (top-right HUD) |
| **Restart Game (Win/Lose Screen)** | Press any keyboard key |

---

## Known Limitations & Future Improvements
- **rec_interval Recalculation**: Ghosts recalculate their A* targets on a 10-frame interval rather than every frame to optimize CPU utilization, occasionally causing a brief latency in target tracking when Pac-Man turns.
- **Single-Stage Structure**: The game loops restarts on victory rather than transitioning to escalating difficulty levels (e.g., faster speeds or shorter frightened mode timers).
- **Classic Intersection Rule Exclusions**: Original arcade behavior (such as ghosts being unable to turn UP at specific intersections) is simplified in this layout to keep path connectivity general.

---

## Credits & License
- **Game Brand**: *Pac-Man* is a trademark of Bandai Namco Entertainment Inc. This codebase is a non-commercial, educational fan project created solely for academic demonstrations of pathfinding and search algorithms.
- **Sound Assets**: Sound wave effects are sourced from public retro game sound packs.
- **Software License**: This project is open-source and distributed under the terms of the MIT License. See [LICENSE.txt](LICENSE.txt) for details.
