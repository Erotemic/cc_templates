#!/usr/bin/env python3
"""UnderCode — run with Python + pygame. No installation/build step required."""

import argparse
import os
from pathlib import Path
import sys


def main(argv=None):
    """Read launch options, run the pygame loop, and return an exit status.

    argv is a list of command-line arguments, or None to use the terminal's
    arguments. --list, --check and --check-sprites return before opening a
    window. For play, this function turns keyboard events into Controls,
    updates Game, draws through View, and sends queued sound names to Audio.
    Normal completion returns 0; failed exercise/content checks return 1.
    Invalid arguments or startup failures raise SystemExit with an explanation.
    """
    parser = argparse.ArgumentParser(description=__doc__)
    entry = parser.add_mutually_exclusive_group()
    entry.add_argument("--encounter", metavar="KEY", help="Start directly with a character")
    entry.add_argument(
        "--practice", metavar="PATTERN", help="Preview a defense pattern immediately"
    )
    entry.add_argument("--level", metavar="KEY", help="Preview a letter-map level")
    parser.add_argument("--entry", metavar="MARKER", help="Named spawn in --level")
    parser.add_argument(
        "--check-sprites", action="store_true", help="Check the directional-sprite exercise"
    )
    parser.add_argument("--seed", type=int, default=7, help="Repeatable encounter randomness")
    parser.add_argument(
        "--check",
        action="store_true",
        help="Validate content and simulate pattern/strike factories",
    )
    parser.add_argument(
        "--list", action="store_true", help="List character, practice and level keys"
    )
    parser.add_argument("--mute", action="store_true", help="Do not open an audio device")
    parser.add_argument(
        "--headless", action="store_true", help="Use dummy SDL devices for an automated check"
    )
    parser.add_argument("--frames", type=int, help="Exit after this many frames")
    parser.add_argument("--screenshot", type=Path, help="Save the last logical frame to a PNG")
    args = parser.parse_args(argv)
    if args.frames is not None and args.frames <= 0:
        parser.error("--frames must be positive")
    if args.headless:
        os.environ["SDL_VIDEODRIVER"] = "dummy"
        os.environ["SDL_AUDIODRIVER"] = "dummy"
        if args.frames is None:
            args.frames = 120
    os.environ.setdefault("PYGAME_HIDE_SUPPORT_PROMPT", "1")
    try:
        import pygame
    except ImportError:
        raise SystemExit(
            "UnderCode needs pygame. Use your existing pygame install, or run:\n"
            "  python -m pip install pygame-ce\nThen run main.py again with that interpreter."
        )
    from undercode.story import StoryError

    try:
        from undercode.app import Game
    except StoryError as error:
        parser.error(str(error))
    from undercode.audio import Audio
    from undercode.controls import Controls
    from undercode.content import CHARACTERS, WEAPONS, PATTERNS, ROOMS
    from undercode.student import GAME_TITLE
    from undercode.validate import validate_content
    from undercode.view import View, WIDTH, HEIGHT

    if args.entry and not args.level:
        parser.error("--entry needs --level")
    if args.level and args.level not in ROOMS:
        parser.error(f"Unknown level {args.level!r}. Choose: {', '.join(ROOMS)}")
    if args.entry and args.entry not in ROOMS[args.level].spawns:
        parser.error(f"Unknown entry {args.entry!r}. Choose: {', '.join(ROOMS[args.level].spawns)}")
    if args.check_sprites:
        from undercode.sprites import VIEW_CASES
        from undercode.student_sprites import choose_player_view

        errors = 0
        for facing, expected in VIEW_CASES:
            actual = choose_player_view(facing)
            ok = actual == expected
            errors += not ok
            print(
                f"{'OK' if ok else 'TRY AGAIN'}: facing {facing}: {actual!r}; expected {expected!r}"
            )
        print(f"{len(VIEW_CASES) - errors}/{len(VIEW_CASES)} sprite cases passed.")
        return int(bool(errors))
    character_keys = {c.key for c in CHARACTERS}
    if args.encounter and args.encounter not in character_keys:
        parser.error(
            f"Unknown character {args.encounter!r}. Choose: {', '.join(sorted(character_keys))}"
        )
    if args.practice and args.practice not in PATTERNS:
        parser.error(f"Unknown pattern {args.practice!r}. Choose: {', '.join(PATTERNS)}")
    if args.list:
        print("Characters:", ", ".join(c.key for c in CHARACTERS))
        print("Patterns:", ", ".join(PATTERNS))
        for key, room in ROOMS.items():
            print(f"Level {key}: {room.name}; entries: {', '.join(room.spawns)}")
        return 0
    if args.check:
        errors = validate_content(CHARACTERS, WEAPONS, PATTERNS, ROOMS)
        if errors:
            for error in errors:
                print("ERROR:", error)
            return 1
        print(
            f"UnderCode content OK: {len(CHARACTERS)} characters, {len(WEAPONS)} techniques, "
            f"{len(PATTERNS)} patterns, {len(ROOMS)} rooms. Factories simulated successfully."
        )
        return 0

    pygame.font.init()
    try:
        pygame.display.init()
        window = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
    except pygame.error as error:
        pygame.quit()
        raise SystemExit(
            f"Cannot open the UnderCode window: {error}\nRun from a desktop terminal, or use --headless for checks."
        )
    if not args.headless and pygame.display.get_driver() in ("dummy", "offscreen"):
        pygame.quit()
        raise SystemExit(
            "No visible desktop is available. Run from a desktop terminal, or use SSH display forwarding.\n"
            "For an automated check: python main.py --headless --mute --frames 120"
        )
    pygame.display.set_caption(GAME_TITLE + " | F1 guide | M sound")
    surface = pygame.Surface((WIDTH, HEIGHT))
    game = Game(args.seed, args.encounter, args.practice, args.level, args.entry)
    view = View()
    audio = Audio(enabled=not args.mute)
    clock = pygame.time.Clock()
    alive, focused, frame = True, True, 0
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
    held = set()
    try:
        while alive and (args.frames is None or frame < args.frames):
            dt = 1 / 60 if args.headless else min(clock.tick(60) / 1000, 0.05)
            confirm, cancel, mx, my = False, False, 0, 0
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    alive = False
                elif event.type == pygame.KEYDOWN:
                    held.add(event.key)
                    if getattr(event, "repeat", False):
                        continue
                    if event.key == pygame.K_ESCAPE:
                        alive = False
                    elif event.key == pygame.K_F1:
                        game.help_open = not game.help_open
                    elif event.key == pygame.K_m:
                        audio.toggle()
                    elif event.key == pygame.K_r:
                        game.restart()
                    elif event.key == pygame.K_TAB:
                        game.change_weapon()
                    elif event.key in (pygame.K_z, pygame.K_RETURN, pygame.K_SPACE):
                        confirm = True
                    elif event.key in (pygame.K_x, pygame.K_BACKSPACE):
                        cancel = True
                    elif event.key in directions:
                        mx, my = directions[event.key]
                elif event.type == pygame.KEYUP:
                    held.discard(event.key)
                elif event.type == getattr(pygame, "WINDOWFOCUSLOST", -1) and not args.headless:
                    focused = False
                    held.clear()
                elif event.type == getattr(pygame, "WINDOWFOCUSGAINED", -1):
                    focused = True
            dx = int(bool(held & {pygame.K_RIGHT, pygame.K_d})) - int(
                bool(held & {pygame.K_LEFT, pygame.K_a})
            )
            dy = int(bool(held & {pygame.K_DOWN, pygame.K_s})) - int(
                bool(held & {pygame.K_UP, pygame.K_w})
            )
            if focused:
                game.update(dt, Controls(dx, dy, mx, my, confirm, cancel))
            for cue in game.cues:
                audio.play(cue)
            game.cues.clear()
            audio.scene(game.scene.name)
            game.sound_label = audio.label
            view.draw(surface, game, focused)
            viewport = surface.get_rect().fit(window.get_rect())
            window.fill((9, 12, 23))
            window.blit(pygame.transform.smoothscale(surface, viewport.size), viewport)
            pygame.display.flip()
            frame += 1
        if args.screenshot:
            args.screenshot.parent.mkdir(parents=True, exist_ok=True)
            pygame.image.save(surface, str(args.screenshot))
    finally:
        pygame.quit()
    return 0


if __name__ == "__main__":
    sys.exit(main())
