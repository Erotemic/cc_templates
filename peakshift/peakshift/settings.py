"""The units in Peakshift are pixels and seconds. Try changing a number!"""

TILE = 32
COLS = 24
ROWS = 15
WIDTH = TILE * COLS
HEIGHT = TILE * ROWS
HUD_HEIGHT = 68
FPS = 60

PLAYER_W = 20
PLAYER_H = 26
RUN_SPEED = 235.0       # Maximum horizontal speed (pixels/second)
RUN_ACCEL = 2350.0      # How quickly walking reaches full speed
AIR_ACCEL = 1800.0
FRICTION = 2600.0
GRAVITY = 1700.0
MAX_FALL = 740.0
JUMP_SPEED = 590.0
JUMP_CUT = 0.52        # Releasing jump early produces a shorter jump
COYOTE_TIME = 0.095    # Short grace period after leaving a ledge
JUMP_BUFFER = 0.105    # Remember a jump press shortly before landing
WALL_SLIDE = 115.0
WALL_JUMP_X = 310.0
WALL_JUMP_Y = 560.0
WALL_LOCK = 0.13
DASH_SPEED = 520.0
DASH_SECONDS = 0.17

STEP = 1 / 120          # Physics substep; reduces collision tunnelling
MAX_FRAME = 0.05

SKY = (19, 27, 52)
STONE = (78, 94, 124)
HERO = (255, 218, 121)
SCARF = (255, 112, 151)
ACCENT = (130, 222, 241)
