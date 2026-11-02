"""Tile collisions, conversations and doors; no battle rules or drawing here."""

import math
import pygame
from .model import Outcome, Placement
from .story import Dialogue, meets
from .student_mechanics import WORLD_MECHANICS

TILE = 32
BLOCKED = "#~"


def tile_center(tile):
    return pygame.Vector2((tile[0] + 0.5) * TILE, (tile[1] + 0.5) * TILE)


class World:
    def __init__(self, rooms, session, room_key=None, spawn=None):
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
        return self.rooms[self.room_key]

    def passable(self, position):
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
        self.toast, self.toast_time = text, seconds

    def change_room(self, destination, landing):
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
        outcome = self.session.resolved.get(self.talking.key) if self.talking else None
        if outcome == Outcome.SPARED:
            return f"{character.name} greets you as a friend. Another practice round? Z: yes. X: later."
        if outcome == Outcome.DEFEATED:
            return f"{character.name} has been practicing for a rematch. Z: accept. X: later."
        return character.invitation

    def visible_objects(self):
        return [
            obj
            for obj in self.room.objects
            if obj.kind != "item" or obj.data["flag"] not in self.session.flags
        ]

    def interactable(self):
        candidates = list(self.room.people) + [
            obj for obj in self.visible_objects() if obj.kind != "trigger"
        ]
        candidates.sort(key=lambda obj: self.position.distance_squared_to(tile_center(obj.tile)))
        return next(
            (obj for obj in candidates if self.position.distance_to(tile_center(obj.tile)) < 55),
            None,
        )

    def run_hook(self, target, name):
        hook = target.data.get(name)
        if hook:
            WORLD_MECHANICS[hook](self, target)

    def interact(self, target):
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
        """Return ('encounter', Placement) or ('door', Exit); App owns transitions."""
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
