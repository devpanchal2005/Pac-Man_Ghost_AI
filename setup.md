# Setup & Running Guide

This guide explains how to configure your environment and run the Pac-Man project.

## Why did running `python main.py` directly fail?
If you see `ModuleNotFoundError: No module named 'pygame'`, it is because Python is running in your global system environment where Pygame is not installed. To resolve this, you must run the game using the project's virtual environment.

---

## How to Run the Game

You can run the game using either of the following two methods:

### Method 1: Direct Execution (Recommended / Easiest)
You can run the game directly by pointing to the Python interpreter inside the virtual environment:

```bash
.venv/bin/python3 main.py
```

### Method 2: Activating the Virtual Environment
Alternatively, you can activate the virtual environment first and then run python normally:

1. **Activate the virtual environment**:
   - **Linux / macOS**:
     ```bash
     source .venv/bin/activate
     ```
   - **Windows (Command Prompt)**:
     ```cmd
     .venv\Scripts\activate.bat
     ```
   - **Windows (PowerShell)**:
     ```powershell
     .venv\Scripts\Activate.ps1
     ```

2. **Run the game**:
   ```bash
   python main.py
   ```

3. **Deactivate when finished**:
   ```bash
   deactivate
   ```

---

## Environment Details & Manual Installation

If you ever need to recreate the environment from scratch, run these commands:

1. **Create the virtual environment**:
   ```bash
   python3 -m venv .venv
   ```

2. **Install Pygame Community Edition**:
   We use `pygame-ce` because it has pre-built wheels and full compatibility with newer Python versions (such as Python 3.14).
   ```bash
   .venv/bin/pip install pygame-ce
   ```
