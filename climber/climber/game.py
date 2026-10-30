"""The pygame window and main event loop. Student mechanics live in student.py."""

from __future__ import annotations

from . import settings, student, synth
from .engine import Controls, Game, update


def _secret_keys(pygame_module) -> tuple[int, ...]:
    """This isn't a key binding shown on the game's help screen."""
    pg = pygame_module
    return (
        pg.K_UP, pg.K_UP, pg.K_DOWN, pg.K_DOWN,
        pg.K_LEFT, pg.K_RIGHT, pg.K_LEFT, pg.K_RIGHT,
        pg.K_b, pg.K_a, pg.K_SPACE, pg.K_RETURN,
    )


def _advance_sequence(sequence: tuple[int, ...], progress: int,
                      pressed: int) -> tuple[int, bool]:
    """Match an ordered key sequence, including overlapping starts.

    The loop remembers only the matching prefix. Extra or incorrect keys
    restart at the longest valid prefix rather than permanently failing.
    """
    history = sequence[:progress] + (pressed,)
    if history[-len(sequence):] == sequence:
        return 0, True
    for length in range(min(len(history), len(sequence) - 1), 0, -1):
        if history[-length:] == sequence[:length]:
            return length, False
    return 0, False


def _handle_sequence_key(game: Game, sequence: tuple[int, ...],
                         progress: int, pressed: int) -> int:
    """Toggle super mode when the entire sequence is entered."""
    progress, complete = _advance_sequence(sequence, progress, pressed)
    if complete:
        game.super_mode = not game.super_mode
    return progress


def run_graphical(*, frames: int = 0, screenshot: str | None = None) -> int:
    import pygame

    from .art import Painter
    from .audio import SoundBoard

    # Tell SDL to use signed-16 stereo PCM; synth.py creates this format.
    # pre_init must run BEFORE pygame.init() initializes the mixer.
    pygame.mixer.pre_init(frequency=synth.SAMPLE_RATE, size=-16, channels=2, buffer=512)
    pygame.init()
    sound = None
    try:
        window = pygame.display.set_mode(settings.START_WINDOW_SIZE,
                                         pygame.RESIZABLE)
        pygame.display.set_caption(student.GAME_TITLE)
        clock = pygame.time.Clock()
        painter = Painter()
        sound = SoundBoard(pygame)
        game = Game()
        secret_keys = _secret_keys(pygame)
        secret_progress = 0
        running = True
        frame = 0
        while running:
            seconds = min(clock.tick(settings.FPS) / 1000, 0.05)
            jump_pressed = False
            restart_pressed = False
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    # Ignore key-repeat events: each step needs its own press.
                    if not getattr(event, "repeat", False):
                        key = (pygame.K_RETURN if event.key == pygame.K_KP_ENTER
                               else event.key)
                        secret_progress = _handle_sequence_key(
                            game, secret_keys, secret_progress, key)
                    if event.key in (pygame.K_ESCAPE, pygame.K_q):
                        running = False
                    elif event.key in (pygame.K_SPACE, pygame.K_z):
                        jump_pressed = True
                    elif event.key == pygame.K_r:
                        restart_pressed = True
                    elif event.key == pygame.K_h:
                        painter.show_help = not painter.show_help
                    elif event.key == pygame.K_m:
                        sound.toggle_mute()
            if not running:
                break
            keys = pygame.key.get_pressed()
            controls = Controls(
                left=bool(keys[pygame.K_a] or keys[pygame.K_LEFT]),
                right=bool(keys[pygame.K_d] or keys[pygame.K_RIGHT]),
                up=bool(keys[pygame.K_w] or keys[pygame.K_UP]),
                down=bool(keys[pygame.K_s] or keys[pygame.K_DOWN]),
                jump_pressed=jump_pressed,
            )
            update(game, controls, seconds)
            if restart_pressed:
                game.reset()
            sound.play_events(game.events)
            painter.audio_label = sound.label
            painter.draw(game, window, seconds)
            frame += 1
            if frames and frame >= frames:
                running = False
        if screenshot:
            pygame.image.save(window, screenshot)
        return 0
    finally:
        if sound is not None:
            sound.close()
        pygame.quit()


def run_headless(frames: int = 240) -> int:
    """Check simulation without even importing pygame."""
    game = Game()
    for i in range(frames):
        # A repeatable minimal control sequence, not a tower-solving AI.
        controls = Controls(right=i < 90, jump_pressed=i in (1, 48, 100))
        update(game, controls, 1 / settings.FPS)
    print(f"frames={frames} x={game.player.x:.1f} "
          f"y={game.player.y:.1f} tier={game.highest_tier} "
          f"lives={game.hearts} failures={game.failures}")
    return 0
