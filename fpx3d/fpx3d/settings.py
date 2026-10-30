"""Small collection of game-wide numbers.

The player moves in X/Y, and Z means UP (different from pygame's 2D Y).
All dimensions are Panda3D world units; time is always in seconds.
"""

GAME_TITLE = "Prism Vault"
START = (0.0, -17.0, 0.0)  # x, y, height of the player's feet
EXIT = (0.0, 17.0, 0.0)
MAP_EDGE = 20.0
TIME_LIMIT = 180.0
MAX_HEARTS = 3
EYE_HEIGHT = 1.55
PLAYER_RADIUS = 0.42
PLAYER_HEIGHT = 1.75
WALK_SPEED = 6.5
SPRINT_SPEED = 9.3
JUMP_SPEED = 8.1
SPRING_SPEED = 11.4
GRAVITY = 20.0
MAX_FALL_SPEED = 24.0
MOUSE_SENSITIVITY = 0.12
STAMINA_MAX = 100.0
AUDIO_ENABLED = True
MUSIC_VOLUME = 0.25
SFX_VOLUME = 0.55
