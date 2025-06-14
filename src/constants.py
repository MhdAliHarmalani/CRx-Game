"""Game constants."""

# Window settings
WINDOW_SIZE = (800, 800)  # Base window size
MIN_WINDOW_SIZE = (600, 600)  # Minimum window size
FPS = 60

# UI scaling
UI_SCALE_FACTOR = 1.0  # Can be adjusted for different screen sizes
BUTTON_HEIGHT = 35
BUTTON_WIDTH = 80
UI_PADDING = 10
UI_FONT_SIZE = 24

# Grid settings
GRID_SIZE = 6  # Smaller grid for more strategic gameplay

# Calculate cell size based on available space (leaving room for UI)
UI_SPACE = 60  # Space reserved for UI elements
AVAILABLE_SPACE = min(WINDOW_SIZE[0], WINDOW_SIZE[1]) - UI_SPACE
CELL_SIZE = AVAILABLE_SPACE // GRID_SIZE

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
UI_BACKGROUND_COLOR = (40, 40, 50)
UI_TEXT_COLOR = (255, 255, 255)
BUTTON_COLOR = (70, 70, 80)
BUTTON_HOVER_COLOR = (100, 100, 110)

# Animation settings
ANIMATION_SPEED = 1.0  # Multiplier for animation speed
PARTICLE_COUNT = 20  # Number of particles in explosions
