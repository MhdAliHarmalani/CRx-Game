"""Game constants."""

# Window settings
WINDOW_SIZE = (800, 800)  # Increased window size for better visibility
FPS = 60

# Grid settings

# Smaller grid for more strategic gameplay
GRID_SIZE = 6
# Calculate cell size based on window width
CELL_SIZE = WINDOW_SIZE[0] // GRID_SIZE

# Colors

PLAYER_COLORS = [
    (255, 0, 0),  # Red
    (0, 0, 255),  # Blue
    (0, 255, 0),  # Green
    (255, 255, 0),  # Yellow
]

BACKGROUND_COLORS = [
    (255, 150, 150),  # More vibrant red
    (150, 150, 255),  # More vibrant blue
    (150, 255, 150),  # More vibrant green
    (255, 255, 150),  # More vibrant yellow
]

GRID_LINE_COLOR = (100, 100, 100)

# Animation settings
ANIMATION_SPEED = 1.0  # Multiplier for animation speed
PARTICLE_COUNT = 20  # Number of particles in explosions
