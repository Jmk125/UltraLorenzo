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

# Movement physics (tweakable)
PLAYER_WALK_SPEED = 5          # Walking speed
PLAYER_RUN_SPEED = 8            # Running speed
PLAYER_WALK_ACCELERATION = 1.0  # How fast player reaches walk speed
PLAYER_RUN_ACCELERATION = 1.5   # How fast player reaches run speed
PLAYER_WALK_DECELERATION = 0.8  # Friction when stopping from walk
PLAYER_RUN_DECELERATION = 0.6   # Friction when stopping from run

# Jump physics (tweakable)
JUMP_POWER = -15                # Normal jump strength
JUMP_POWER_RUNNING = -16        # Running jump (barely higher)
GRAVITY = 0.8                   # Gravity strength

# Spawn and stats
PLAYER_SPAWN_X = 100
PLAYER_SPAWN_Y = 400
STARTING_LIVES = 3
PLAYER_INVULNERABILITY_TIME = 1000  # milliseconds of invulnerability after getting hit

# Upgrade bonuses (tweakable)
UPGRADE_SPEED_BOOST = 0.3      # Speed increase per Fleet Boots upgrade
UPGRADE_JUMP_BOOST = 0.5       # Jump power increase per Sky Shoes upgrade
UPGRADE_SCORE_MULTIPLIER = 0.15  # Score multiplier increase per Treasure Sense upgrade
UPGRADE_MAX_SPEED = 3          # Max speed increase allowed
UPGRADE_MAX_SCORE_MULT = 3.0   # Max score multiplier allowed

# Fireball ability (tweakable)
FIREBALL_ENABLED = True        # Enable/disable fireball ability
FIREBALL_SPEED = 6             # Horizontal speed of fireball
FIREBALL_BOUNCE_POWER = -8     # Vertical bounce strength (negative = upward)
FIREBALL_GRAVITY = 0.6         # Gravity applied to fireball
FIREBALL_MAX_DISTANCE = 400    # Maximum travel distance before disappearing
FIREBALL_COOLDOWN = 1000       # Cooldown in milliseconds
FIREBALL_DAMAGE = 1            # Damage dealt to enemies
FIREBALL_SIZE = 12             # Size of fireball sprite

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

# Parallax scrolling (tweakable)
PARALLAX_MOUNTAIN = 0.2  # Mountains move at 20% of camera speed (far background)
PARALLAX_CLOUD = 0.3     # Clouds move at 30% of camera speed
PARALLAX_HILL = 0.5      # Hills move at 50% of camera speed (closer to foreground)