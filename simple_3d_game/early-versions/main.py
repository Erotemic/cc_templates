from ursina import *
import random

app = Ursina()

# -----------------------------
# Window settings
# -----------------------------
window.title = "Coin Collector"
window.borderless = False
window.exit_button.visible = False
window.fps_counter.enabled = True

# -----------------------------
# Game variables
# -----------------------------
score = 0
time_left = 30
game_over = False
coins = []

# -----------------------------
# Ground
# -----------------------------
ground = Entity(
    model='plane',
    scale=(20, 1, 20),
    color=color.green,
    texture='white_cube',
    texture_scale=(20, 20),
    collider='box'
)

# -----------------------------
# Player
# -----------------------------
player = Entity(
    model='cube',
    color=color.azure,
    scale=(1, 1, 1),
    position=(0, 0.5, 0),
    collider='box'
)

# -----------------------------
# Camera
# -----------------------------
camera.position = (0, 18, -18)
camera.rotation_x = 35

# -----------------------------
# UI
# -----------------------------
score_text = Text(text='Score: 0', position=(-0.85, 0.45), scale=2)
timer_text = Text(text='Time: 30', position=(0.55, 0.45), scale=2)
message_text = Text(text='', origin=(0, 0), scale=3, y=0)

# -----------------------------
# Functions
# -----------------------------
def spawn_coin():
    """Create one coin at a random position."""
    x = random.randint(-8, 8)
    z = random.randint(-8, 8)

    coin = Entity(
        model='sphere',
        color=color.yellow,
        scale=0.6,
        position=(x, 0.5, z),
        collider='box'
    )
    coins.append(coin)


def reset_game():
    """Reset everything so the player can play again."""
    global score, time_left, game_over

    score = 0
    time_left = 30
    game_over = False

    player.position = (0, 0.5, 0)
    score_text.text = 'Score: 0'
    timer_text.text = 'Time: 30'
    message_text.text = ''

    for coin in coins:
        destroy(coin)
    coins.clear()

    for _ in range(8):
        spawn_coin()


def input(key):
    """Handle keyboard input."""
    if key == 'r' and game_over:
        reset_game()


def update():
    """Runs every frame."""
    global score, time_left, game_over

    if game_over:
        return

    speed = 5

    # Player movement
    if held_keys['w']:
        player.z += speed * time.dt
    if held_keys['s']:
        player.z -= speed * time.dt
    if held_keys['a']:
        player.x -= speed * time.dt
    if held_keys['d']:
        player.x += speed * time.dt

    # Keep player on the ground area
    player.x = clamp(player.x, -9, 9)
    player.z = clamp(player.z, -9, 9)

    # Spin coins
    for coin in coins:
        coin.rotation_y += 100 * time.dt

    # Check if player touches a coin
    for coin in coins[:]:
        if player.intersects(coin).hit:
            coins.remove(coin)
            destroy(coin)
            score += 1
            score_text.text = f'Score: {score}'
            spawn_coin()

    # End the game when time runs out
    if time_left <= 0:
        game_over = True
        message_text.text = f'Game Over!\nFinal Score: {score}\nPress R to restart'


def countdown():
    """Reduce the timer once per second."""
    global time_left

    if not game_over:
        time_left -= 1
        timer_text.text = f'Time: {time_left}'

        if time_left > 0:
            invoke(countdown, delay=1)
        else:
            time_left = 0
            timer_text.text = 'Time: 0'


# -----------------------------
# Start the game
# -----------------------------
for _ in range(8):
    spawn_coin()

invoke(countdown, delay=1)

app.run()
