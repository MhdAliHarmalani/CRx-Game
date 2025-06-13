# CRx Game Clone

A Python implementation of the CRx game using Pygame. This is a strategy game where players take turns placing orbs on a grid, trying to eliminate their opponents' orbs.

## Game Rules

1. The game is played on an 8x8 grid
2. Players take turns placing orbs on the grid
3. You can only place orbs in empty cells or cells containing your own orbs
4. Each cell has a critical mass:
   - Corner cells: 2 orbs
   - Edge cells: 3 orbs
   - Inner cells: 4 orbs
5. When a cell reaches critical mass, it explodes and distributes orbs to adjacent cells
6. The game continues until one player is eliminated

## Project Structure

```
.
├── requirements.txt
├── README.md
├── run_game.py      # Main entry point script
├── src/
│   ├── __init__.py
│   ├── constants.py    # Game constants and configuration
│   ├── cell.py        # Cell class implementation
│   ├── game.py        # Main game logic
│   └── main.py        # Game initialization
└── tests/
    ├── __init__.py
    ├── conftest.py    # Test configuration
    ├── test_cell.py   # Cell tests
    └── test_game.py   # Game tests
```

## Installation

1. Make sure you have Python 3.12+ installed
2. Create a virtual environment (recommended):
   ```bash
   python -m venv venv
   ```
3. Activate the virtual environment:
   - On Windows:
     ```bash
     venv\Scripts\activate
     ```
   - On macOS/Linux:
     ```bash
     source venv/bin/activate
     ```
4. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Running the Game

1. Make sure your virtual environment is activated
2. Run the game:
   ```bash
   python run_game.py
   ```

## Running Tests

1. Make sure your virtual environment is activated
2. Run all tests:
   ```bash
   pytest
   ```
3. Run tests with coverage:
   ```bash
   pytest --cov=src
   ```

## Test Coverage

The test suite covers:
- Cell initialization and critical mass calculation
- Orb placement and explosion mechanics
- Game state management
- Player turn handling
- Grid drawing
- Chain reactions
- Cell conversion during explosions

## How to Play

- Click on a cell to place an orb
- Players take turns automatically
- The current player's color is shown in the orbs and background
- Try to eliminate your opponent's orbs by creating chain reactions

## Controls

- Left click: Place an orb
- Close window to exit
