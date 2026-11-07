"""The pygame shell: keyboard, draw, sound, and a deterministic headless mode."""

from __future__ import annotations

from . import settings, student
from .physics import Controls, Game, update


def run_headless(frames: int = 240, *, room: str | None = None) -> int:
    """Test the physics without installing pygame or opening a window."""
    game = Game(start=room)
    for index in range(frames):
        update(game, Controls(right=index < 80,
                              jump_pressed=index in (10, 90),
                              jump_held=index in range(10, 26) or index in range(90, 104),
                              dash_pressed=index == 35), 1 / settings.FPS)
    print(f"room={game.room_key} frames={frames} x={game.player.x:.1f} "
          f"y={game.player.y:.1f} deaths={game.deaths} berries={game.berries}")
    return 0


def run_graphical(*, frames: int = 0, screenshot: str | None = None,
                  room: str | None = None) -> int:
    import pygame as pg

    from .art import Painter
    from .audio import SAMPLE_RATE, SoundBoard

    pg.mixer.pre_init(frequency=SAMPLE_RATE, size=-16, channels=2, buffer=512)
    pg.init()
    sound = None
    try:
        logical_size = (settings.WIDTH, settings.HEIGHT + settings.HUD_HEIGHT)
        screen = pg.display.set_mode(logical_size, pg.RESIZABLE)
        canvas = pg.Surface(logical_size)
        pg.display.set_caption(student.GAME_TITLE)
        clock = pg.time.Clock()
        painter = Painter(pg)
        sound = SoundBoard(pg)
        game = Game(start=room)
        paused = False
        current_time = 0.0
        count = 0
        running = True
        while running:
            dt = min(clock.tick(settings.FPS) / 1000, settings.MAX_FRAME)
            jump_pressed = False
            dash_pressed = False
            restart = False
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    running = False
                if event.type == pg.KEYDOWN and not getattr(event, "repeat", False):
                    if event.key in (pg.K_ESCAPE, pg.K_q):
                        running = False
                    elif event.key in (pg.K_SPACE, pg.K_z):
                        jump_pressed = True
                    elif event.key in (pg.K_x, pg.K_LSHIFT, pg.K_RSHIFT):
                        dash_pressed = True
                    elif event.key == pg.K_r:
                        restart = True
                    elif event.key == pg.K_h:
                        painter.help = not painter.help
                    elif event.key == pg.K_p:
                        paused = not paused
                    elif event.key == pg.K_m:
                        sound.toggle()
            if not running:
                break
            if restart:
                game.restart()
                painter.trail.clear()
            pressed = pg.key.get_pressed()
            controls = Controls(
                left=bool(pressed[pg.K_a] or pressed[pg.K_LEFT]),
                right=bool(pressed[pg.K_d] or pressed[pg.K_RIGHT]),
                up=bool(pressed[pg.K_w] or pressed[pg.K_UP]),
                down=bool(pressed[pg.K_s] or pressed[pg.K_DOWN]),
                jump_pressed=jump_pressed,
                jump_held=bool(pressed[pg.K_SPACE] or pressed[pg.K_z]),
                dash_pressed=dash_pressed,
                grab_held=bool(pressed[pg.K_c]),
            )
            if not paused and not painter.help:
                update(game, controls, dt)
                sound.play(game.events)
                current_time += dt
            painter.draw(canvas, game, current_time, paused=paused, muted=sound.muted)
            # Preserve the game's aspect ratio at any window size.
            size = screen.get_size()
            scale = min(size[0] / logical_size[0], size[1] / logical_size[1])
            draw_size = (max(1, round(logical_size[0] * scale)),
                         max(1, round(logical_size[1] * scale)))
            screen.fill((6, 12, 27))
            frame = pg.transform.scale(canvas, draw_size)
            screen.blit(frame, ((size[0] - draw_size[0]) // 2,
                                (size[1] - draw_size[1]) // 2))
            pg.display.flip()
            count += 1
            if frames and count >= frames:
                break
        if screenshot:
            pg.image.save(canvas, screenshot)
        return 0
    finally:
        if sound is not None:
            sound.close()
        pg.quit()
