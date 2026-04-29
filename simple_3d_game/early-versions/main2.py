from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController
from ursina.shaders import lit_with_shadows_shader
from math import sin
import random

app = Ursina()

# -----------------------------
# Window settings
# -----------------------------
window.title = "Shadow Coin Hunt"
window.borderless = False
window.exit_button.visible = False
window.fps_counter.enabled = True

# This shader lets entities receive shadows.
Entity.default_shader = lit_with_shadows_shader

# -----------------------------
# Game variables
# -----------------------------
score = 0
time_left = 45
game_over = False
second_timer = 0
wave_time = 0
coins = []

# -----------------------------
# UI
# -----------------------------
score_text = Text(text='Score: 0', position=(-0.85, 0.45), scale=2)
timer_text = Text(text='Time: 45', position=(0.55, 0.45), scale=2)
help_text = Text(
    text='WASD move | Space jump | Shift sprint',
    position=(-0.45, -0.47),
    scale=1.2
)
message_text = Text(text='', origin=(0, 0), scale=2, y=0)

# -----------------------------
# World
# -----------------------------
Sky()

ground = Entity(
    model='plane',
    scale=(40, 1, 40),
    texture='white_cube',
    texture_scale=(40, 40),
    color=color.rgb(90, 150, 90),
    collider='box'
)

# Border walls
walls = [
    Entity(model='cube', scale=(40, 4, 1), position=(0, 2, 20), color=color.gray, collider='box'),
    Entity(model='cube', scale=(40, 4, 1), position=(0, 2, -20), color=color.gray, collider='box'),
    Entity(model='cube', scale=(1, 4, 40), position=(20, 2, 0), color=color.gray, collider='box'),
    Entity(model='cube', scale=(1, 4, 40), position=(-20, 2, 0), color=color.gray, collider='box'),
]

# Obstacles and platforms
level_blocks = [
    # crates
    Entity(model='cube', scale=(2, 2, 2), position=(-8, 1, -6), color=color.rgb(120, 85, 50), collider='box'),
    Entity(model='cube', scale=(2, 3, 2), position=(6, 1.5, 4), color=color.rgb(120, 85, 50), collider='box'),
    Entity(model='cube', scale=(2, 4, 2), position=(10, 2, -5), color=color.rgb(120, 85, 50), collider='box'),
    Entity(model='cube', scale=(2, 2, 2), position=(-4, 1, 8), color=color.rgb(120, 85, 50), collider='box'),

    # jump platforms
    Entity(model='cube', scale=(4, 0.5, 4), position=(-10, 2.5, 10), color=color.light_gray, collider='box'),
    Entity(model='cube', scale=(4, 0.5, 4), position=(12, 3.5, 12), color=color.light_gray, collider='box'),
    Entity(model='cube', scale=(4, 0.5, 4), position=(0, 2.5, -12), color=color.light_gray, collider='box'),
]

# -----------------------------
# Lighting
# -----------------------------
sun = DirectionalLight()
sun.look_at(Vec3(1, -1, -1))

# Shadow area: keep shadows focused on the playable part of the map.
shadow_bounds = Entity(
    model='cube',
    scale=(45, 12, 45),
    position=(0, 5, 0),
    visible=False
)
sun.update_bounds(shadow_bounds)

AmbientLight(color=color.rgba(100, 100, 120, 0.35))

# -----------------------------
# Player
# -----------------------------
player = FirstPersonController(
    position=(0, 2, 0),
    origin_y=-0.5,
    speed=6,
    jump_height=2.2,
    gravity=1
)

# Make collisions a little more reliable for the player body.
player.collider = BoxCollider(player, Vec3(0, 1, 0), Vec3(1, 2, 1))
player.cursor.color = color.white

# -----------------------------
# Coin positions
# -----------------------------
spawn_points = [
    Vec3(-12, 1.2, -12),
    Vec3(-6, 1.2, -2),
    Vec3(3, 1.2, 7),
    Vec3(10, 1.2, 10),
    Vec3(14, 1.2, -10),
    Vec3(-14, 1.2, 4),
    Vec3(-10, 3.2, 10),   # on platform
    Vec3(12, 4.2, 12),    # on taller platform
    Vec3(0, 3.2, -12),    # on platform
    Vec3(6, 2.2, 4),      # above crate
]

def spawn_coin(position=None):
    """Create one floating coin."""
    if position is None:
        position = random.choice(spawn_points)

    coin = Entity(
        model='sphere',
        color=color.yellow,
        scale=0.6,
        position=position
    )
    coin.base_y = position.y
    coin.wave_offset = random.uniform(0, 6.28)
    coins.append(coin)

def clear_coins():
    for coin in coins:
        destroy(coin)
    coins.clear()

def refill_coins():
    clear_coins()
    used_positions = random.sample(spawn_points, 6)
    for pos in used_positions:
        spawn_coin(pos)

def reset_game():
    global score, time_left, game_over, second_timer

    score = 0
    time_left = 45
    game_over = False
    second_timer = 0

    player.position = Vec3(0, 2, 0)
    player.rotation = Vec3(0, 0, 0)
    player.camera_pivot.rotation = Vec3(0, 0, 0)

    score_text.text = 'Score: 0'
    timer_text.text = 'Time: 45'
    message_text.text = ''

    refill_coins()

def end_game():
    global game_over
    game_over = True
    message_text.text = f'Game Over!\nFinal Score: {score}\nPress R to restart'

# -----------------------------
# Input
# -----------------------------
def input(key):
    global game_over

    if key == 'r' and game_over:
        reset_game()

# -----------------------------
# Update loop
# -----------------------------
def update():
    global score, time_left, second_timer, wave_time

    if game_over:
        return

    # Sprint when holding Shift
    if held_keys['left shift'] or held_keys['right shift']:
        player.speed = 9
    else:
        player.speed = 6

    # Animate coins
    wave_time += time.dt
    for coin in coins:
        coin.rotation_y += 120 * time.dt
        coin.y = coin.base_y + sin(wave_time * 3 + coin.wave_offset) * 0.15

    # Collect coins
    for coin in coins[:]:
        if distance(player.position, coin.position) < 1.3:
            coins.remove(coin)
            destroy(coin)
            score += 1
            score_text.text = f'Score: {score}'

            # Spawn a new coin somewhere else
            spawn_coin()

    # Timer counts down once per second
    second_timer += time.dt
    if second_timer >= 1:
        second_timer -= 1
        time_left -= 1
        timer_text.text = f'Time: {time_left}'
        if time_left <= 0:
            end_game()

    # If player falls off the map, reset their position
    if player.y < -10:
        player.position = Vec3(0, 2, 0)
        player.rotation = Vec3(0, 0, 0)

# -----------------------------
# Start game
# -----------------------------
refill_coins()

app.run()
