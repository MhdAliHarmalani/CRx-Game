"""Game constants."""

# Window settings
WINDOW_SIZE = (800, 800)  # Increased window size for better visibility
FPS = 60

# Grid settings
GRID_SIZE = 6  # Smaller grid for more strategic gameplay
CELL_SIZE = WINDOW_SIZE[0] // GRID_SIZE  # Calculate cell size based on window width

# Colors
PLAYER_COLORS = [
    (255, 0, 0),    # Red
    (0, 0, 255)     # Blue
]

BACKGROUND_COLORS = [
    (255, 200, 200),  # Light red
    (200, 200, 255)   # Light blue
]

GRID_LINE_COLOR = (100, 100, 100)

# Animation settings
ANIMATION_SPEED = 1.0  # Multiplier for animation speed
PARTICLE_COUNT = 20    # Number of particles in explosions 