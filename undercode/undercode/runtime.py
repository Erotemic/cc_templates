"""The pygame adapter: receive events → update one frame → draw → play sounds.

Read run for the loop. read_input handles keyboard mechanics separately from
game rules: held arrows continue movement; KEYDOWN creates single action presses.
Engines receive Controls and seconds, never pygame's global keyboard state.
"""

import os
from pathlib import Path
from .controls import Controls
from .settings import GAME_TITLE, WIDTH, HEIGHT


def read_input(*, pygame, held):
    """Return (Controls, commands); update the set of keys currently held.

    commands contains window-level actions, not story/encounter events. A repeat
    keydown keeps a key held but must not confirm another menu choice.
    """
    commands = []
    confirm_pressed = cancel_pressed = False
    menu_x = menu_y = 0
    directions = {
        pygame.K_LEFT: (-1, 0),
        pygame.K_a: (-1, 0),
        pygame.K_RIGHT: (1, 0),
        pygame.K_d: (1, 0),
        pygame.K_UP: (0, -1),
        pygame.K_w: (0, -1),
        pygame.K_DOWN: (0, 1),
        pygame.K_s: (0, 1),
    }
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            commands.append("quit")
        elif event.type == pygame.KEYDOWN:
            held.add(event.key)
            if getattr(event, "repeat", False):
                continue
            if event.key in (pygame.K_z, pygame.K_RETURN, pygame.K_SPACE):
                confirm_pressed = True
            elif event.key in (pygame.K_x, pygame.K_BACKSPACE):
                cancel_pressed = True
            elif event.key in directions:
                menu_x, menu_y = directions[event.key]
            else:
                command = {
                    pygame.K_ESCAPE: "quit",
                    pygame.K_F1: "help",
                    pygame.K_F2: "debug",
                    pygame.K_m: "mute",
                    pygame.K_r: "restart",
                    pygame.K_TAB: "weapon",
                }.get(event.key)
                if command is not None:
                    commands.append(command)
        elif event.type == pygame.KEYUP:
            held.discard(event.key)
        elif event.type == getattr(pygame, "WINDOWFOCUSLOST", -1):
            held.clear()
            commands.append("unfocused")
        elif event.type == getattr(pygame, "WINDOWFOCUSGAINED", -1):
            commands.append("focused")
    right_held = bool(held & {pygame.K_RIGHT, pygame.K_d})
    left_held = bool(held & {pygame.K_LEFT, pygame.K_a})
    down_held = bool(held & {pygame.K_DOWN, pygame.K_s})
    up_held = bool(held & {pygame.K_UP, pygame.K_w})
    controls = Controls(
        move_x=int(right_held) - int(left_held),
        move_y=int(down_held) - int(up_held),
        menu_x=menu_x,
        menu_y=menu_y,
        confirm_pressed=confirm_pressed,
        cancel_pressed=cancel_pressed,
        sprint_held=bool(held & {pygame.K_LSHIFT, pygame.K_RSHIFT}),
    )
    return controls, commands


def run(*, game, headless=False, mute=False, frames=None, screenshot=None):
    """Open the school-friendly window and run until quit or the requested frame limit."""
    if headless:
        os.environ["SDL_VIDEODRIVER"] = "dummy"
        os.environ["SDL_AUDIODRIVER"] = "dummy"
        frames = frames or 120
    os.environ.setdefault("PYGAME_HIDE_SUPPORT_PROMPT", "1")
    import pygame
    from .audio import Audio
    from .view import View

    pygame.font.init()
    try:
        pygame.display.init()
        window = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
        if not headless and pygame.display.get_driver() in ("dummy", "offscreen"):
            raise SystemExit(
                "No visible desktop is available. Use a desktop terminal or --headless for checks."
            )
        pygame.display.set_caption(GAME_TITLE + " | F1 guide | M sound")
        surface = pygame.Surface((WIDTH, HEIGHT))
        view, audio, clock = View(), Audio(enabled=not mute), pygame.time.Clock()
        held = set()
        alive, focused, frame = True, True, 0
        while alive and (frames is None or frame < frames):
            seconds = 1 / 60 if headless else min(clock.tick(60) / 1000, 0.05)
            controls, commands = read_input(pygame=pygame, held=held)
            for command in commands:
                if command == "quit":
                    alive = False
                elif command == "help":
                    game.help_open = not game.help_open
                elif command == "debug":
                    game.debug_open = not game.debug_open
                elif command == "mute":
                    audio.toggle()
                elif command == "restart":
                    game.restart()
                elif command == "weapon":
                    game.change_weapon()
                elif command == "unfocused" and not headless:
                    focused = False
                elif command == "focused":
                    focused = True
            if focused:
                game.update(seconds=seconds, controls=controls)
            for cue in game.cues:
                audio.play(cue)
            game.cues.clear()
            audio.scene(game.scene.name)
            game.sound_label = audio.label
            view.draw(surface=surface, game=game, focused=focused)
            viewport = surface.get_rect().fit(window.get_rect())
            window.fill((9, 12, 23))
            window.blit(pygame.transform.smoothscale(surface, viewport.size), viewport)
            pygame.display.flip()
            frame += 1
        if screenshot is not None:
            path = Path(screenshot)
            path.parent.mkdir(parents=True, exist_ok=True)
            pygame.image.save(surface, str(path))
    except pygame.error as error:
        raise SystemExit(
            f"Cannot open/run the UnderCode window: {error}. Try --headless for checks."
        ) from error
    finally:
        pygame.quit()
    return 0
