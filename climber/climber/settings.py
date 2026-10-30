"""Numbers shared by the engine and the painter.

Students can read these and experiment, but start with student.py.
All distances are in *world pixels*. Negative Y means higher in the tower.
"""

VIEW_WIDTH = 960
VIEW_HEIGHT = 600
HUD_HEIGHT = 68
START_WINDOW_SIZE = (VIEW_WIDTH, VIEW_HEIGHT + HUD_HEIGHT)
FPS = 60

LEFT_WALL = 105
RIGHT_WALL = 855
GROUND_Y = 700

PLAYER_WIDTH = 28
PLAYER_HEIGHT = 38
RUN_SPEED = 285.0
JUMP_SPEED = 690.0
GRAVITY = 1500.0
MAX_FALL_SPEED = 950.0
CLIMB_SPEED = 195.0

TIER_HEIGHT = 100
PLATFORM_WIDTH = 174
PLATFORM_HEIGHT = 18
PICKUP_SIZE = 14
MARKER_EVERY_TIERS = 5
HECKLER_OFFSET = 150

# A jump reaches approximately JUMP_SPEED**2 / (2 * GRAVITY) = 159 px.
# Platforms are only 100 px apart, so consecutive tiers are reachable.
