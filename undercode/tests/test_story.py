"""Read these examples to see named room records and a complete story route."""

from dataclasses import replace
import os
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
os.environ.setdefault("PYGAME_HIDE_SUPPORT_PROMPT", "1")
from undercode.app import Game, Scene
from undercode.controls import Controls
from undercode.model import Session
from undercode.dialogue import Conversation, Dialogue, Choice, Branch, available
from undercode.overworld.model import Room, Spawn, Person, Door, Sign, Item, Trigger, Tile
from undercode.overworld.maps import compile_rooms, validate_start, MapError
from undercode.overworld.world import World, tile_center
from undercode.art import folio
from teacher import solutions

CONFIRM = Controls(confirm_pressed=True)


def finish_dialogue(*, world):
    """Confirm every page and the selected reply, with an explicit loop bound."""
    for _ in range(100):
        if world.dialogue is None:
            return
        world.update(seconds=0, controls=CONFIRM)
    raise AssertionError("Conversation did not finish")


def go_through(*, game, door):
    """Touch a door and allow the coordinator's fade to complete."""
    game.world.position = tile_center(tile=door.tile)
    game.world.door_cooldown = 0
    game.update(seconds=0)
    for _ in range(50):
        game.update(seconds=1 / 60)


class StoryTests(unittest.TestCase):
    def test_complete_story_choices_collectible_gate_and_changed_greeting(self):
        game = Game(level="studio")
        world = game.world
        keeper = world.room.people[0]
        world.position = tile_center(tile=keeper.tile)
        game.update(seconds=0, controls=CONFIRM)
        before = world.position.copy()
        game.update(seconds=0.1, controls=Controls(move_x=1))
        self.assertEqual(world.position, before)
        finish_dialogue(world=world)
        self.assertIn("promised_help", game.session.flags)
        self.assertIsNone(world.talking)
        gate = next(obj for obj in world.room.exits if obj.definition.destination_room == "nook")
        go_through(game=game, door=gate)
        self.assertEqual(world.room_key, "studio")
        self.assertIsNone(game.transition)
        item = next(obj for obj in world.room.objects if isinstance(obj.definition, Item))
        world.interact(target=item)
        self.assertIn("bookmark", game.session.flags)
        self.assertNotIn(item, world.visible_objects())
        finish_dialogue(world=world)
        go_through(game=game, door=gate)
        self.assertEqual(world.room_key, "nook")
        ending = next(obj for obj in world.room.objects if isinstance(obj.definition, Sign))
        world.interact(target=ending)
        self.assertNotIn("finished_story", game.session.flags)
        finish_dialogue(world=world)
        self.assertIn("finished_story", game.session.flags)
        go_through(game=game, door=world.room.exits[0])
        world.interact(target=world.room.people[0])
        self.assertIn("What will you write next?", " ".join(" ".join(world.dialogue.pages).split()))
        self.assertFalse(world.dialogue.choices)
        self.assertEqual(game.scene, Scene.WORLD)
        game.restart()
        self.assertFalse(game.session.flags)

    def test_cancel_and_choices_have_explicit_commit_points(self):
        session = Session()
        definition = Dialogue(text=["First", "Second"], set_flags=["read"])
        conversation = Conversation(name="Note", dialogue=definition, session=session)
        conversation.update(controls=CONFIRM)
        conversation.update(controls=Controls(cancel_pressed=True))
        self.assertNotIn("read", session.flags)
        conversation = Conversation(name="Note", dialogue=definition, session=session)
        conversation.update(controls=CONFIRM)
        conversation.update(controls=CONFIRM)
        self.assertIn("read", session.flags)
        conversation = Conversation(
            name="Keeper",
            session=session,
            dialogue=Dialogue(
                text="Choose",
                choices=[
                    Choice(label="Later", text="Goodbye"),
                    Choice(label="Yes", text="Thanks", set_flags=["promised"]),
                    Choice(label="Hidden", text="Secret", required_flag="unknown"),
                ],
            ),
        )
        self.assertEqual(len(conversation.choices), 2)
        conversation.update(controls=Controls(menu_y=1))
        conversation.update(controls=CONFIRM)
        conversation.update(controls=Controls(cancel_pressed=True))
        self.assertIn("promised", session.flags)

    def test_conditions_are_plain_python_and_branches_choose_first_match(self):
        session = Session(flags={"key"})

        def has_key(*, session):
            """A student's condition is a normal function; no expression parser is involved."""
            return "key" in session.flags

        self.assertTrue(available(session=session, when=has_key))
        self.assertFalse(available(session=session, required_flag="promise", when=has_key))
        conversation = Conversation(
            name="Guard",
            session=session,
            dialogue=Dialogue(
                text="Stranger",
                branches=[
                    Branch(text="Friend", when=has_key),
                    Branch(text="Visitor", required_flag="key"),
                ],
            ),
        )
        self.assertEqual(conversation.pages, ["Friend"])

    def test_story_text_can_precede_an_encounter_request(self):
        game = Game()
        person = game.world.room.people[0]
        person = replace(
            person,
            definition=replace(person.definition, dialogue=Dialogue(text="One story first.")),
        )
        game.world.interact(target=person)
        finish_dialogue(world=game.world)
        self.assertEqual(game.world.talking, person)
        game.update(seconds=0, controls=CONFIRM)
        for _ in range(50):
            game.update(seconds=1 / 60)
        self.assertEqual(game.scene, Scene.ENCOUNTER)
        self.assertEqual(game.encounter.opponent.key, person.definition.encounter_id)

    def test_completed_healing_runs_on_entry_and_reentry_not_every_frame(self):
        game = Game(level="studio")
        world = game.world
        trigger = next(obj for obj in world.room.objects if isinstance(obj.definition, Trigger))
        with patch.object(trigger.definition, "on_enter", solutions.warm_light):
            world.session.player.hp = 5
            world.position = tile_center(tile=trigger.tile)
            for _ in range(20):
                game.update(seconds=1 / 60)
            self.assertEqual(world.session.player.hp, 8)
            world.position += (32, 0)
            game.update(seconds=0)
            world.position -= (32, 0)
            game.update(seconds=0)
            self.assertEqual(world.session.player.hp, 11)


class MapAuthorTests(unittest.TestCase):
    def setUp(self):
        """Build a tiny story-only NPC; it requires no Opponent or encounter registry."""
        self.definition = Room(
            name="Fresh",
            tiles=["#####", "#@Q.#", "#...D", "#####"],
            legend={
                "@": Spawn(name="entry"),
                "Q": Person(name="Neighbor", portrait=folio, dialogue=Dialogue(text="Hello")),
                "D": Door(destination_room="fresh", destination_spawn="entry"),
            },
        )

    def test_moving_named_spawn_and_adding_another_room(self):
        rooms = compile_rooms(definitions={"fresh": self.definition})
        original = rooms["fresh"].spawns["entry"]
        self.definition.tiles[1] = "#.Q@#"
        rooms = compile_rooms(definitions={"fresh": self.definition})
        self.assertNotEqual(original, rooms["fresh"].spawns["entry"])
        self.assertEqual(rooms["fresh"].exits[0].definition.destination_spawn, "entry")
        second = Room(
            name="Second",
            tiles=["#####", "#@..D", "#####"],
            legend={
                "@": Spawn(name="arrive"),
                "D": Door(destination_room="fresh", destination_spawn="entry"),
            },
        )
        self.definition.legend["D"] = Door(destination_room="second", destination_spawn="arrive")
        rooms = compile_rooms(definitions={"fresh": self.definition, "second": second})
        self.assertEqual(len(rooms), 2)
        self.assertIsNone(rooms["fresh"].people[0].definition.encounter_id)

    def test_python_catches_bad_keyword_and_map_checks_catch_game_errors(self):
        with self.assertRaises(TypeError):
            Person(name="Typo", portrait=folio, battel=False)
        import copy

        cases = [
            (lambda room: room.tiles.__setitem__(1, "#@!.#"), "row 2, column 3"),
            (lambda room: room.tiles.__setitem__(1, "#@Q#"), "equal-length"),
            (lambda room: room.tiles.__setitem__(1, "#@@.#"), "duplicate spawn"),
            (
                lambda room: room.legend.__setitem__(
                    "D", Door(destination_room="missing", destination_spawn="entry")
                ),
                "unknown door",
            ),
            (
                lambda room: room.legend.__setitem__("@", Spawn(name="entry", ground="#")),
                "walkable ground",
            ),
        ]
        for change, message in cases:
            definition = copy.deepcopy(self.definition)
            change(definition)
            with self.subTest(error=message), self.assertRaisesRegex(MapError, message):
                compile_rooms(definitions={"fresh": definition})
        rooms = compile_rooms(definitions={"fresh": self.definition})
        with self.assertRaisesRegex(MapError, "unknown starting marker"):
            validate_start(rooms=rooms, room_key="fresh", spawn_name="missing")

    def test_custom_function_creates_a_new_story_rule_without_an_encounter(self):
        def learn_secret(*, world, obj):
            """A student's new mechanic, unrelated to the supplied mission solutions."""
            world.session.flags.add("knows_secret")
            world.tell(text=f"{obj.definition.name} shared a secret.")

        self.definition.legend["Q"] = Sign(
            name="Secret", dialogue=Dialogue(text="A clue"), on_interact=learn_secret
        )
        self.definition.legend["T"] = Tile(ground="#")
        rooms = compile_rooms(definitions={"fresh": self.definition})
        world = World(rooms=rooms, session=Session(), room_key="fresh", spawn="entry")
        world.interact(
            target=next(obj for obj in world.room.objects if isinstance(obj.definition, Sign))
        )
        self.assertIn("knows_secret", world.session.flags)
        self.assertIn("shared a secret", world.toast)


if __name__ == "__main__":
    unittest.main()
