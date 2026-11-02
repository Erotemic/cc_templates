"""An almost-empty pygame project. Change anything you like.

The only framework here is a window, a menu, keyboard input, updates,
and drawing. Pick a style, then turn the little demonstration into YOUR game.

Run with: python main.py
Requires: pygame or pygame-ce
"""

import pygame


WIDTH, HEIGHT = 800, 520
FPS = 60
BACKGROUND = (23, 28, 42)
TEXT_COLOR = (232, 239, 248)
ACCENT = (107, 212, 192)

# These are only example settings. There is no gravity, score, health, enemy,
# or win condition unless you decide to add one.
SPEED = 220  # Pixels per second in the real-time example.
COLUMNS = 10
ROWS = 6


def new_game(mode, size):
    """Make the starting state. Add any variables your game needs here."""
    width, height = size
    return {
        "mode": mode,             # "menu", "real_time", "turns", "choices"
        "x": width / 2,           # Position in the real-time example.
        "y": height / 2,
        "column": COLUMNS // 2,   # Position in the turn-based example.
        "row": ROWS // 2,
        "turns": 0,
        "scene": "start",         # State in the choice-based example.
    }


def on_key_down(game, key, size):
    """Called ONCE per key press. Good for menus and turn-based decisions."""
    mode = game["mode"]

    if mode == "menu":
        choices = {
            pygame.K_1: "real_time",
            pygame.K_2: "turns",
            pygame.K_3: "choices",
        }
        if key in choices:
            return new_game(choices[key], size)
        return game

    if key == pygame.K_ESCAPE:   # Return to the menu.
        return new_game("menu", size)
    if key == pygame.K_r:        # Restart the current example.
        return new_game(mode, size)

    if mode == "turns":
        # A single key press = a single turn. What else could take a turn?
        dx = int(key in (pygame.K_RIGHT, pygame.K_d)) - int(
            key in (pygame.K_LEFT, pygame.K_a))
        dy = int(key in (pygame.K_DOWN, pygame.K_s)) - int(
            key in (pygame.K_UP, pygame.K_w))
        new_column = max(0, min(COLUMNS - 1, game["column"] + dx))
        new_row = max(0, min(ROWS - 1, game["row"] + dy))
        if (new_column, new_row) != (game["column"], game["row"]):
            game["column"] = new_column
            game["row"] = new_row
            game["turns"] += 1
        # IDEA: Walls, puzzles, a second player, an enemy that moves per turn.

    if mode == "choices":
        if key == pygame.K_1:
            game["scene"] = "left"
        elif key == pygame.K_2:
            game["scene"] = "right"
        # IDEA: A story, inventory, questions, branching dialogue, game states.

    return game


def update(game, keys, seconds, size):
    """Called every frame. Best for movement that continues while holding keys."""
    if game["mode"] != "real_time":
        return

    # Holding an arrow key moves continuously; seconds keeps speed steady.
    dx = int(keys[pygame.K_RIGHT] or keys[pygame.K_d]) - int(
        keys[pygame.K_LEFT] or keys[pygame.K_a])
    dy = int(keys[pygame.K_DOWN] or keys[pygame.K_s]) - int(
        keys[pygame.K_UP] or keys[pygame.K_w])
    game["x"] += dx * SPEED * seconds
    game["y"] += dy * SPEED * seconds
    game["x"] = max(12, min(size[0] - 12, game["x"]))
    game["y"] = max(12, min(size[1] - 12, game["y"]))
    # IDEA: Bouncing balls, a timer, a chase game, drawing with the mouse.


def write(screen, font, message, x, y, color=TEXT_COLOR):
    """One helper so you don't have to repeat font rendering boilerplate."""
    screen.blit(font.render(message, True, color), (x, y))


def draw(game, screen, font, title_font):
    """Draw the current frame. Replace these shapes with your own art."""
    width, height = screen.get_size()
    screen.fill(BACKGROUND)
    mode = game["mode"]

    if mode == "menu":
        write(screen, title_font, "YOUR GAME STARTS HERE", 35, 50, ACCENT)
        write(screen, font, "Choose a starting point:", 38, 130)
        write(screen, font, "1 - REAL TIME: move while a key is held", 38, 190)
        write(screen, font, "2 - TURN BASED: move once per key press", 38, 235)
        write(screen, font, "3 - CHOICES: change the game state", 38, 280)
        write(screen, font, "These are examples, not game rules.", 38, 355)
        write(screen, font, "ESC: quit", 38, 405)

    elif mode == "real_time":
        write(screen, font, "REAL TIME  |  Hold arrows / WASD to move", 20, 22)
        pygame.draw.circle(screen, ACCENT,
                           (round(game["x"]), round(game["y"])), 12)
        # IDEA: Add another object. What happens when you touch it?

    elif mode == "turns":
        write(screen, font, "TURN BASED  |  Press arrows / WASD", 20, 22)
        write(screen, font, f"Turns taken: {game['turns']}", 20, 55)
        cell = max(12, min(52, (width - 40) // COLUMNS,
                            (height - 140) // ROWS))
        left = (width - cell * COLUMNS) // 2
        top = (height - cell * ROWS) // 2 + 24
        for row in range(ROWS):
            for column in range(COLUMNS):
                box = pygame.Rect(left + column * cell,
                                  top + row * cell, cell - 2, cell - 2)
                pygame.draw.rect(screen, (58, 69, 88), box, border_radius=3)
        player_box = pygame.Rect(left + game["column"] * cell + 3,
                                 top + game["row"] * cell + 3,
                                 cell - 8, cell - 8)
        pygame.draw.rect(screen, ACCENT, player_box, border_radius=4)
        # IDEA: A board game, a maze, obstacles, a turn-based battle.

    elif mode == "choices":
        write(screen, font, "CHOICES  |  Press 1 or 2", 20, 22)
        write(screen, title_font, "What happens next?", 35, 115, ACCENT)
        write(screen, font, "1 - Choose the left option", 40, 210)
        write(screen, font, "2 - Choose the right option", 40, 255)
        write(screen, font, f"Current state: {game['scene']}", 40, 330)
        # IDEA: Give different scenes their own descriptions and choices.
        # IDEA: Remember earlier choices, add an ending, draw your characters.

    if mode != "menu":
        write(screen, font, "R: start over    ESC: menu", 20, height - 32)
    pygame.display.flip()


def main():
    """The basic game loop: events -> update -> draw -> repeat."""
    pygame.init()
    try:
        screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
        pygame.display.set_caption("My First Game")  # Rename me.
        clock = pygame.time.Clock()
        font = pygame.font.Font(None, 28)
        title_font = pygame.font.Font(None, 42)
        game = new_game("menu", screen.get_size())
        running = True

        while running:
            seconds = min(clock.tick(FPS) / 1000.0, 0.05)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE and game["mode"] == "menu":
                        running = False
                    else:
                        game = on_key_down(game, event.key, screen.get_size())
                # IDEA: Check MOUSEBUTTONDOWN for a click-to-interact game.

            if not running:
                break
            update(game, pygame.key.get_pressed(), seconds, screen.get_size())
            draw(game, screen, font, title_font)
    finally:
        pygame.quit()


if __name__ == "__main__":
    main()
