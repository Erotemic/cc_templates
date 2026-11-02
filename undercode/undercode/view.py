"""Choose a renderer and draw cross-system overlays. All layout is in its own system."""

import pygame
from . import art
from .app import Scene
from .presentation import UI
from .settings import WIDTH, HEIGHT


class View(UI):
    """Load each renderer only when used, preserving independent authoring modes."""

    def __init__(self):
        """Initialize common fonts; create no engine and load no content."""
        super().__init__()
        self.world_view = None
        self.encounter_view = None

    def draw(self, *, surface, game, focused=True):
        """Draw the active system, then fade/help/focus overlays without changing rules."""
        surface.fill(art.INK)
        if game.scene == Scene.WORLD:
            if self.world_view is None:
                from .overworld.drawing import WorldView

                self.world_view = WorldView()
            # Display a name only if encounter content has already been loaded.
            # Opening the overworld must not require importing the other system.
            self.world_view.draw(
                surface=surface,
                world=game.world,
                time=game.time,
                sound_label=game.sound_label,
                technique_name=game.technique_name,
            )
        else:
            if self.encounter_view is None:
                from .encounters.drawing import EncounterView

                self.encounter_view = EncounterView()
            self.encounter_view.draw(
                surface=surface,
                encounter=game.encounter,
                time=game.time,
                sound_label=game.sound_label,
            )
        if game.transition is not None:
            veil = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            veil.fill((*art.INK, round(game.transition.opacity * 255)))
            surface.blit(veil, (0, 0))
            if game.transition.opacity > 0.85:
                art.star(surface=surface, center=(WIDTH / 2, HEIGHT / 2), radius=16, color=art.MINT)
        if game.debug_open:
            self.draw_debug(surface=surface, game=game)
        if game.help_open:
            self.draw_help(surface=surface)
        if not focused:
            veil = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            veil.fill((12, 16, 30, 190))
            surface.blit(veil, (0, 0))
            self.text(
                surface=surface,
                text="PAUSED",
                position=(480, 322),
                size=44,
                color=art.PAPER,
                center=True,
            )
            self.text(
                surface=surface,
                text="Click the window to return.",
                position=(480, 366),
                size=26,
                color=art.MINT,
                center=True,
            )

    def draw_debug(self, *, surface, game):
        """F2 exposes state for prediction and tracing; it never changes any rules."""
        self.panel(surface=surface, rect=pygame.Rect(28, 82, 460, 165), border=art.GOLD)
        lines = [f"MODE: {game.scene.name}  HP: {game.session.player.hp}"]
        if game.scene == Scene.WORLD:
            world = game.world
            lines += [
                f"ROOM: {world.room_key}  POSITION: {tuple(round(v) for v in world.position)}",
                f"FACING: {tuple(round(v, 2) for v in world.facing)}  VIEW: {world.player_view}",
            ]
        else:
            lines += [
                f"PHASE: {game.encounter.phase.name}  TURN: {game.encounter.turn}",
                f"UNDERSTANDING: {game.encounter.calm}",
            ]
        lines.append("FLAGS: " + ", ".join(sorted(game.session.flags)))
        for index, line in enumerate(lines):
            self.wrapped(
                surface=surface, text=line, rect=pygame.Rect(40, 94 + index * 34, 435, 30), size=20
            )
