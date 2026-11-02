"""Tile collisions, conversations and doors; no battle rules or drawing here."""

import math
import pygame
from .model import Outcome, Placement
from .story import Dialogue, meets

TILE = 32
BLOCKED = "#~"


def tile_center(tile):
    """Convert an internal (column, row) tile to its center as a world-pixel Vector2."""
    return pygame.Vector2((tile[0] + 0.5) * TILE, (tile[1] + 0.5) * TILE)


class World:
    """Own overworld movement, interactions, dialogue, and room-local triggers.

    Position is in room pixels; tile coordinates are (column, row). The model
    reads Controls, calls student mechanics and returns door/battle requests.
    Game handles their fades; View draws this state without changing it.
    """

    def __init__(self, rooms, session, room_key=None, spawn=None):
        """Create world state with rooms and the run's shared session.

        room_key selects a compiled room; spawn is a named marker or an internal
        tile tuple. Omitted values choose the first room/marker. Game passes
        the configured story start explicitly. Start facing down and briefly
        delay doors so an arrival cannot immediately send the player back.
        """
        self.rooms = rooms
        self.session = session
        self.room_key = room_key or next(iter(rooms))
        room_key = self.room_key
        spawn = spawn if spawn is not None else next(iter(self.room.spawns))
        self.position = tile_center(
            self.rooms[room_key].spawns[spawn] if isinstance(spawn, str) else spawn
        )
        self.facing = pygame.Vector2(0, 1)
        self.talking = None
        self.dialogue = None
        self.dialogue_target = None
        self.trigger_tiles = set()
        self.toast = "Walk up to a neighbor. Z / Enter to talk."
        self.toast_time = 5.0
        self.walk_time = 0.0
        self.moving = False
        self.door_cooldown = 0.4

    @property
    def room(self):
        """Return the compiled Room selected by room_key without changing world state."""
        return self.rooms[self.room_key]

    def passable(self, position):
        """Return whether the player's body fits on walkable terrain at position.

        position is a room-pixel Vector2. Test the four corners of a 9-pixel
        half-width body against map bounds, walls, and water. NPCs are not walls.
        """
        radius = 9
        for x in (position.x - radius, position.x + radius):
            for y in (position.y - radius, position.y + radius):
                column, row = math.floor(x / TILE), math.floor(y / TILE)
                if not (0 <= row < len(self.room.tiles) and 0 <= column < len(self.room.tiles[0])):
                    return False
                if self.room.tiles[row][column] in BLOCKED:
                    return False
        return True

    def move(self, direction, dt):
        """Move using a direction Vector2 and dt seconds, sliding along walls.

        Normalize long diagonals, then break movement into small collision steps
        so a slow frame cannot skip a wall. Remember nonzero requested facing
        even when blocked; advance walk_time only when position actually changes.
        """
        if direction.length_squared() > 1:
            direction = direction.normalize()
        if direction.length_squared():
            self.facing = direction
        movement = direction * 155 * dt
        steps = max(1, math.ceil(max(abs(movement.x), abs(movement.y)) / 8))
        before = self.position.copy()
        for _ in range(steps):
            next_x = self.position + pygame.Vector2(movement.x / steps, 0)
            if self.passable(next_x):
                self.position = next_x
            next_y = self.position + pygame.Vector2(0, movement.y / steps)
            if self.passable(next_y):
                self.position = next_y
        self.moving = self.position.distance_squared_to(before) > 0.01
        if self.moving:
            self.walk_time += dt

    def tell(self, text, seconds=3.0):
        """Replace the HUD toast with text and keep it visible for seconds."""
        self.toast, self.toast_time = text, seconds

    def change_room(self, destination, landing):
        """Enter destination at landing, a spawn name or an internal tile tuple.

        Reset conversation/trigger state, delay door use briefly, and announce
        the room. Game calls this at a fade midpoint; it does not create a fade.
        """
        self.room_key = destination
        self.position = tile_center(
            self.room.spawns[landing] if isinstance(landing, str) else landing
        )
        self.talking = None
        self.dialogue = None
        self.dialogue_target = None
        self.trigger_tiles.clear()
        self.door_cooldown = 0.5
        self.tell(self.room.name)

    def conversation_text(self, character):
        """Return this neighbor's invitation or a rematch greeting based on its saved outcome."""
        outcome = self.session.resolved.get(self.talking.key) if self.talking else None
        if outcome == Outcome.SPARED:
            return f"{character.name} greets you as a friend. Another practice round? Z: yes. X: later."
        if outcome == Outcome.DEFEATED:
            return f"{character.name} has been practicing for a rematch. Z: accept. X: later."
        return character.invitation

    def visible_objects(self):
        """Return current room objects, omitting items whose collection flag is already set."""
        return [
            obj
            for obj in self.room.objects
            if obj.kind != "item" or obj.data["flag"] not in self.session.flags
        ]

    def interactable(self):
        """Return the closest person or usable object within 55 pixels, or None; skip triggers."""
        candidates = list(self.room.people) + [
            obj for obj in self.visible_objects() if obj.kind != "trigger"
        ]
        candidates.sort(key=lambda obj: self.position.distance_squared_to(tile_center(obj.tile)))
        return next(
            (obj for obj in candidates if self.position.distance_to(tile_center(obj.tile)) < 55),
            None,
        )

    def run_hook(self, target, name):
        """Call target's on_enter/on_interact Python function if one is configured.

        Read the function from target.data and pass (self, target) to it.
        Story validation has already checked that the hook is callable.
        """
        hook = target.data.get(name)
        if hook:
            hook(self, target)

    def interact(self, target):
        """Apply a Z interaction to a character placement or story object.

        Check requirements first, then run its optional student hook. Open story
        dialogue or a battle invitation, restore at a rest, or collect an item
        immediately. Dialogue completion flags are handled later by Dialogue.
        """
        data = target.data
        if not meets(self.session, data.get("requires")):
            self.tell(data.get("locked_text", "There is more to do before this is ready."))
            return
        self.run_hook(target, "on_interact")
        if isinstance(target, Placement):
            if (
                "text" in data
                or "branches" in data
                or "choices" in data
                or not data.get("battle", True)
            ):
                self.dialogue = Dialogue(
                    data.get("name", target.character.title()), data, self.session
                )
                self.dialogue_target = target
            elif data.get("battle", True):
                self.talking = target
        elif target.kind == "rest":
            self.session.player.rest()
            self.tell("Warm light. HP and cocoa restored.")
        elif target.kind in ("sign", "item"):
            if target.kind == "item":
                self.session.flags.add(data["flag"])
            self.dialogue = Dialogue(data.get("name", target.kind.title()), data, self.session)
            self.dialogue_target = target

    def update(self, dt, controls):
        """Advance dt seconds using this frame's Controls; return a scene request or None.

        Dialogue/invitations pause walking and consume their own confirm presses.
        Otherwise move, run newly entered triggers, check doors and handle Z.
        Return ('encounter', Placement) or ('door', Exit) for Game to fade into;
        this method never changes the active scene itself.
        """
        self.toast_time = max(0, self.toast_time - dt)
        self.door_cooldown = max(0, self.door_cooldown - dt)
        if self.dialogue:
            self.moving = False
            self.dialogue.update(controls)
            if self.dialogue.finished:
                target = self.dialogue_target
                if (
                    not self.dialogue.cancelled
                    and isinstance(target, Placement)
                    and target.data.get("battle", True)
                ):
                    self.talking = target
                self.dialogue = self.dialogue_target = None
            return None
        if self.talking:
            self.moving = False
            if controls.cancel:
                self.talking = None
            elif controls.confirm:
                person = self.talking
                self.talking = None
                return ("encounter", person)
            return None
        self.move(pygame.Vector2(controls.x, controls.y), dt)
        active = set()
        for obj in self.room.objects:
            if (
                obj.kind == "trigger"
                and self.position.distance_to(tile_center(obj.tile)) < TILE / 2
            ):
                active.add(obj.key)
                if obj.key not in self.trigger_tiles and meets(
                    self.session, obj.data.get("requires")
                ):
                    self.run_hook(obj, "on_enter")
        self.trigger_tiles = active
        if self.door_cooldown == 0:
            for exit in self.room.exits:
                if pygame.Rect(exit.tile[0] * TILE, exit.tile[1] * TILE, TILE, TILE).collidepoint(
                    self.position
                ):
                    if meets(self.session, exit.data.get("requires")):
                        return ("door", exit)
                    self.tell(exit.data.get("locked_text", "This door is locked."))
                    self.door_cooldown = 1.0
        if controls.confirm:
            target = self.interactable()
            if target:
                self.interact(target)
        return None
