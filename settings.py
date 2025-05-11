# Window settings
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
TILE_SIZE = 32
FPS = 60
LEVEL_WIDTH = 3200  # 4x window width for longer levels
LEVEL_HEIGHT = 600

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (0, 0, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)
SKY_BLUE = (135, 206, 235)
BROWN = (139, 69, 19)

# Camera settings
CAMERA_SLACK = 200

# Player settings
PLAYER_WIDTH = 32
PLAYER_HEIGHT = 48
PLAYER_SPEED = 5
JUMP_POWER = -15
GRAVITY = 0.8
PLAYER_SPAWN_X = 100  # Added this
PLAYER_SPAWN_Y = 400  # Added this
STARTING_LIVES = 3
PLAYER_INVULNERABILITY_TIME = 1000  # milliseconds of invulnerability after getting hit

# Platform settings
MIN_PLATFORM_WIDTH = 96   # 3 tiles
MAX_PLATFORM_WIDTH = 256  # 8 tiles
PLATFORM_HEIGHT = 32
MIN_GAP_WIDTH = 64       # 2 tiles - minimum gap the player needs to jump
MAX_GAP_WIDTH = 128      # 4 tiles - maximum jumpable gap
MAX_JUMP_HEIGHT = 120    # Used for level generation calculations

# Enemy settings
ENEMY_WIDTH = 32
ENEMY_HEIGHT = 32
ENEMY_SPEED = 2
ENEMY_BOUNCE_HEIGHT = -8  # How high player bounces after killing enemy

# Coin settings
COIN_SIZE = 20

# Powerup settings
POWERUP_SIZE = 32