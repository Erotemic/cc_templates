"""Read World.update first: timers → conversation → movement → triggers → interactions.

Coordinates here are pixels inside the current room. Map positions are (column,
row). Drawing adds a screen offset later. This engine never reads pygame keys,
opens a window, or imports encounters. It reports requests for Game to handle.
"""

import math
import pygame
from ..contracts import EncounterRequest, RoomRequest, Outcome, ToneRequest
from ..dialogue import Conversation, Dialogue, available
from .. import student_overworld
from .model import Person, Door, Item, Rest, Trigger, PianoKey

TILE = 32


def tile_center(tile):
    """Convert a (column, row) to a room-pixel Vector2 at the tile's center."""
    return pygame.Vector2((tile[0] + 0.5) * TILE, (tile[1] + 0.5) * TILE)


class World:
    """Changing overworld state: current room, position, facing, dialogue and timers."""

    def __init__(self, *, rooms, session, room_key, spawn):
        """Start at an explicit room/marker, borrowing the session's player and progress."""
        self.rooms = rooms
        self.session = session
        self.room_key = room_key
        self.position = tile_center(tile=rooms[room_key].spawns[spawn])
        self.facing = pygame.Vector2(0, 1)
        self.player_view = "down"
        self.moving = False
        self.walk_time = 0.0
        self.talking = None
        self.dialogue = None
        self.dialogue_target = None
        self.trigger_tiles = set()
        self.piano_key = None  # Student-owned memory: which key was playing last frame?
        self.tones = []
        self.door_cooldown = 0.4
        self.toast = "Arrows: walk. Z: talk, read or rest."
        self.toast_time = 5.0

    @property
    def room(self):
        """Read the current RoomMap; the definitions themselves are not movement state."""
        return self.rooms[self.room_key]

    @property
    def encounter_count(self):
        """Count optional encounter links; peaceful neighbors are not missing encounters."""
        count = 0
        for room in self.rooms.values():
            for person in room.people:
                if person.definition.encounter_id is not None:
                    count += 1
        return count

    @property
    def piano_keys(self):
        """List placed piano records; this locates objects, NOT player/key collisions."""
        return [obj for obj in self.room.objects if isinstance(obj.definition, PianoKey)]

    @property
    def player_rect(self):
        """Expose the player's 18-pixel body for students' collision experiments."""
        rect = pygame.Rect(0, 0, 18, 18)
        rect.center = (round(self.position.x), round(self.position.y))
        return rect

    @staticmethod
    def tile_rect(*, tile):
        """Convert a (column, row) to a room-pixel rectangle; no collision decision here."""
        column, row = tile
        return pygame.Rect(column * TILE, row * TILE, TILE, TILE)

    def play_tone(self, *, hz, duration=0.4):
        """Queue an audio request without importing a mixer into the rule engine."""
        if not math.isfinite(hz) or not 20 <= hz <= 20000:
            raise ValueError("Tone frequency must be between 20 and 20000 Hz.")
        if not math.isfinite(duration) or not 0 < duration <= 5:
            raise ValueError("Tone duration must be between 0 and 5 seconds.")
        self.tones.append(ToneRequest(hz=hz, duration=duration))

    def passable(self, *, position):
        """Test the player's four corners against room edges, walls and water."""
        radius = 9
        for x in (position.x - radius, position.x + radius):
            for y in (position.y - radius, position.y + radius):
                column, row = math.floor(x / TILE), math.floor(y / TILE)
                if not (0 <= row < len(self.room.tiles) and 0 <= column < len(self.room.tiles[0])):
                    return False
                if self.room.tiles[row][column] in "#~":
                    return False
        return True

    def move(self, *, direction, seconds, speed=155):
        """Move at pixels/second, slide along walls, and remember requested facing."""
        if direction.length_squared() > 1:
            direction = direction.normalize()  # Diagonals should not walk faster.
        if direction.length_squared():
            self.facing = direction
        movement = direction * speed * seconds
        steps = max(1, math.ceil(max(abs(movement.x), abs(movement.y)) / 8))
        before = self.position.copy()
        for _ in range(steps):
            # Try X and Y separately. If a wall blocks X, Y can still slide along
            # it. Small steps prevent a long frame from jumping through a wall.
            next_x = self.position + pygame.Vector2(movement.x / steps, 0)
            if self.passable(position=next_x):
                self.position = next_x
            next_y = self.position + pygame.Vector2(0, movement.y / steps)
            if self.passable(position=next_y):
                self.position = next_y
        self.moving = self.position.distance_squared_to(before) > 0.01
        if self.moving:
            self.walk_time += seconds
        # MISSION 1's return value becomes ordinary game state here. Drawing
        # never runs student rules: it simply draws the selected player_view.
        self.player_view = student_overworld.choose_player_view(facing=self.facing)

    def tell(self, *, text, seconds=3.0):
        """Replace the HUD message and start its display timer."""
        self.toast = text
        self.toast_time = seconds

    def change_room(self, *, destination, landing):
        """Apply a named arrival under Game's fade; forget room-local interactions."""
        self.room_key = destination
        self.position = tile_center(tile=self.room.spawns[landing])
        self.talking = None
        self.dialogue = None
        self.dialogue_target = None
        self.trigger_tiles.clear()
        self.piano_key = None
        self.door_cooldown = 0.5  # Arriving must not immediately take a door back.
        self.tell(text=self.room.name)

    def conversation_text(self, *, person):
        """Explain the optional encounter invitation, remembering prior outcomes."""
        outcome = self.session.resolved.get(person.key)
        name = person.definition.name
        if outcome == Outcome.SPARED:
            return f"{name} greets you as a friend. Another practice? Z: yes. X: later."
        if outcome == Outcome.DEFEATED:
            return f"{name} has practiced for a rematch. Z: accept. X: later."
        return person.definition.invitation

    def visible_objects(self):
        """Collected items disappear; the rest of the room remains available to draw."""
        visible = []
        for obj in self.room.objects:
            if isinstance(obj.definition, Item) and obj.definition.flag in self.session.flags:
                continue
            visible.append(obj)
        return visible

    def interactable(self):
        """Find the closest Z-usable object within 55 pixels, or return None."""
        closest, distance = None, 55
        for obj in self.visible_objects():
            if isinstance(obj.definition, (Door, Trigger, PianoKey)):
                continue
            candidate = self.position.distance_to(tile_center(tile=obj.tile))
            if candidate < distance:
                closest, distance = obj, candidate
        return closest

    def interact(self, *, target):
        """Handle one interaction, using record fields rather than hidden option keys."""
        definition = target.definition
        if not available(
            session=self.session, required_flag=definition.required_flag, when=definition.when
        ):
            self.tell(text=definition.locked_text)
            return
        if definition.on_interact is not None:
            definition.on_interact(world=self, obj=target)
        if isinstance(definition, Rest):
            self.session.player.rest()
            self.tell(text="Warm light. HP and cocoa restored.")
        elif isinstance(definition, Item):
            self.session.flags.add(definition.flag)
            self.dialogue = Conversation(
                name=definition.name, dialogue=Dialogue(text=definition.text), session=self.session
            )
            self.dialogue_target = target
        elif definition.dialogue is not None:
            self.dialogue = Conversation(
                name=definition.name, dialogue=definition.dialogue, session=self.session
            )
            self.dialogue_target = target
        elif isinstance(definition, Person) and definition.encounter_id is not None:
            self.talking = target

    def update_conversation(self, *, controls):
        """Consume conversation input and report whether walking must remain paused."""
        if self.dialogue is not None:
            self.moving = False
            self.dialogue.update(controls=controls)
            if self.dialogue.finished:
                target = self.dialogue_target
                if (
                    not self.dialogue.cancelled
                    and isinstance(target.definition, Person)
                    and target.definition.encounter_id is not None
                ):
                    self.talking = target
                self.dialogue = None
                self.dialogue_target = None
            return True
        return False

    def update_triggers(self):
        """Detect entry as a change between last frame's occupied set and this one's."""
        occupied = set()
        for obj in self.room.objects:
            definition = obj.definition
            if not isinstance(definition, Trigger):
                continue
            if self.position.distance_to(tile_center(tile=obj.tile)) < TILE / 2:
                occupied.add(obj.key)
                if obj.key not in self.trigger_tiles and available(
                    session=self.session,
                    required_flag=definition.required_flag,
                    when=definition.when,
                ):
                    definition.on_enter(world=self, obj=obj)
        # Leaving clears membership. Standing still therefore cannot heal every
        # frame, but returning later creates a new entry event.
        self.trigger_tiles = occupied

    def check_doors(self):
        """Return a RoomRequest only when an unlocked door contains the player's center."""
        if self.door_cooldown > 0:
            return None
        for obj in self.room.exits:
            rect = pygame.Rect(obj.tile[0] * TILE, obj.tile[1] * TILE, TILE, TILE)
            if rect.collidepoint(self.position):
                door = obj.definition
                if available(
                    session=self.session, required_flag=door.required_flag, when=door.when
                ):
                    return RoomRequest(
                        destination_room=door.destination_room,
                        destination_spawn=door.destination_spawn,
                    )
                self.tell(text=door.locked_text)
                self.door_cooldown = 1.0
        return None

    def update(self, *, seconds, controls):
        """Advance one frame in a visible order; return a request or None.

        Try tracing one Z press: an open dialogue gets it first, then an
        invitation, then a nearby object. Each branch returns so the SAME press
        cannot close text and also select an encounter action in one frame.
        """
        self.toast_time = max(0, self.toast_time - seconds)
        self.door_cooldown = max(0, self.door_cooldown - seconds)
        if self.update_conversation(controls=controls):
            return None
        if self.talking is not None:
            self.moving = False
            if controls.cancel_pressed:
                self.talking = None
            elif controls.confirm_pressed:
                person = self.talking
                self.talking = None
                return EncounterRequest(
                    encounter_id=person.definition.encounter_id, person_id=person.key
                )
            return None
        self.move(
            direction=pygame.Vector2(controls.move_x, controls.move_y),
            seconds=seconds,
            speed=student_overworld.movement_speed(controls=controls),
        )
        self.update_triggers()
        student_overworld.update_piano(world=self)
        door_request = self.check_doors()
        if door_request is not None:
            return door_request
        if controls.confirm_pressed:
            target = self.interactable()
            if target is not None:
                self.interact(target=target)
        return None
