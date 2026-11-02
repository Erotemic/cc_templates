"""Student-facing maps, story progression, hooks, and directional sprite behavior."""

import contextlib
import io
import os
from pathlib import Path
import subprocess
import sys
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
os.environ.setdefault("PYGAME_HIDE_SUPPORT_PROMPT", "1")

from undercode.app import Game, Scene
from undercode.content import ROOMS
from undercode.controls import Controls
from undercode.model import Outcome, Session
from undercode.sprites import VIEW_CASES
from teacher.solutions import choose_player_view as player_view
from teacher.solutions import warm_light
from undercode.story import Dialogue, StoryError, build_story, meets
from undercode.building import (
    level,
    spawn,
    person,
    door,
    sign,
    item,
    rest,
    trigger,
    terrain,
    choice,
    branch,
)
from undercode.world import tile_center


CONFIRM = Controls(confirm=True)


def finish_dialogue(world):
    for _ in range(100):
        if world.dialogue is None:
            return
        world.update(0, CONFIRM)
    raise AssertionError("Dialogue did not finish")


def go_through(game, door):
    game.world.position = tile_center(door.tile)
    game.world.door_cooldown = 0
    game.update(0)
    for _ in range(50):
        game.update(1 / 60)


class StoryTests(unittest.TestCase):
    def test_complete_story_with_choices_key_gate_and_changed_greeting(self):
        game = Game(level="studio")
        world = game.world
        keeper = world.room.people[0]
        world.position = tile_center(keeper.tile)
        game.update(0, CONFIRM)
        self.assertIsNotNone(world.dialogue)
        before = world.position.copy()
        game.update(0.1, Controls(x=1))
        self.assertEqual(world.position, before)
        finish_dialogue(world)
        self.assertIn("promised_help", game.session.flags)
        self.assertIsNone(world.talking)  # This is a story-only neighbor.
        gate = next(d for d in world.room.exits if d.destination == "nook")
        go_through(game, gate)
        self.assertEqual(world.room_key, "studio")
        self.assertIsNone(game.transition)
        self.assertIn("bookmark", world.toast)
        item = next(o for o in world.room.objects if o.kind == "item")
        world.position = tile_center(item.tile)
        game.update(0, CONFIRM)
        self.assertIn("bookmark", game.session.flags)
        self.assertNotIn(item, world.visible_objects())
        finish_dialogue(world)
        go_through(game, gate)
        self.assertEqual(world.room_key, "nook")
        self.assertEqual(world.position, tile_center(world.room.spawns[gate.landing]))
        ending = next(o for o in world.room.objects if o.kind == "sign")
        world.position = tile_center(ending.tile)
        game.update(0, CONFIRM)
        self.assertNotIn("finished_story", game.session.flags)
        finish_dialogue(world)
        self.assertIn("finished_story", game.session.flags)
        go_through(game, world.room.exits[0])
        self.assertEqual(world.room_key, "studio")
        world.interact(keeper)
        self.assertIn("What will you write next?", " ".join(" ".join(world.dialogue.pages).split()))
        self.assertFalse(world.dialogue.choices)
        self.assertEqual(game.scene, Scene.WORLD)
        game.restart()
        self.assertEqual(game.world.room_key, "studio")
        self.assertFalse(game.session.flags)

    def test_cancel_and_choice_completion_have_explicit_commit_points(self):
        session = Session()
        data = {"text": ["First page", "Second page"], "set_flags": ["read"]}
        dialogue = Dialogue("Note", data, session)
        dialogue.update(CONFIRM)
        dialogue.update(Controls(cancel=True))
        self.assertNotIn("read", session.flags)
        dialogue = Dialogue("Note", data, session)
        dialogue.update(CONFIRM)
        dialogue.update(CONFIRM)
        self.assertIn("read", session.flags)
        choice = Dialogue(
            "Keeper",
            {
                "text": "Choose",
                "choices": [
                    {"label": "Later", "text": "Goodbye"},
                    {"label": "Yes", "text": "Thank you", "set_flags": ["promised"]},
                    {"label": "Hidden", "requires": "unknown"},
                ],
            },
            session,
        )
        self.assertEqual(len(choice.choices), 2)
        choice.update(Controls(menu_y=1))
        choice.update(CONFIRM)
        self.assertIn("promised", session.flags)
        choice.update(Controls(cancel=True))
        self.assertIn("promised", session.flags)

    def test_conditions_and_battle_outcomes(self):
        session = Session()
        session.flags.add("key")
        self.assertTrue(meets(session, "key"))
        self.assertFalse(meets(session, ["key", "promise"]))
        for outcome in Outcome:
            session.resolved["guard"] = outcome
            self.assertEqual(meets(session, "spared:guard"), outcome == Outcome.SPARED)
            self.assertEqual(meets(session, "defeated:guard"), outcome == Outcome.DEFEATED)
        session.resolved["guard"] = Outcome.SPARED
        branch = Dialogue(
            "Guard",
            {
                "text": "A stranger",
                "branches": [
                    {"requires": ["key", "spared:guard"], "text": "A friend"},
                    {"requires": "key", "text": "A visitor"},
                ],
            },
            session,
        )
        self.assertEqual(branch.pages, ["A friend"])

    def test_story_character_can_lead_to_an_encounter_after_dialogue(self):
        game = Game(level="studio")
        person = ROOMS["courtyard"].people[0]
        from dataclasses import replace

        person = replace(person, data={"text": "One story first."})
        world = game.world
        world.interact(person)
        self.assertIsNotNone(world.dialogue)
        finish_dialogue(world)
        self.assertEqual(world.talking, person)
        game.update(0, CONFIRM)
        for _ in range(50):
            game.update(1 / 60)
        self.assertEqual(game.scene, Scene.BATTLE)
        self.assertEqual(game.battle.character.key, person.character)

    @patch.dict(
        next(o for o in ROOMS["studio"].objects if o.kind == "trigger").data,
        {"on_enter": warm_light},
    )
    def test_completed_mechanic_trigger_runs_on_entry_and_reentry(self):
        game = Game(level="studio")
        world = game.world
        trigger = next(o for o in world.room.objects if o.kind == "trigger")
        game.session.player.hp = 5
        world.position = tile_center(trigger.tile)
        for _ in range(20):
            game.update(1 / 60)
        self.assertEqual(game.session.player.hp, 8)
        world.position += (32, 0)
        game.update(0)
        world.position -= (32, 0)
        game.update(0)
        self.assertEqual(game.session.player.hp, 11)
        # The same named extension boundary can be used by a sign's Z interaction.
        from dataclasses import replace

        sign = next(o for o in world.room.objects if o.kind == "sign")
        sign = replace(sign, data={"name": "Light", "on_interact": warm_light, "text": "Warm!"})
        world.interact(sign)
        self.assertEqual(game.session.player.hp, 14)


class MapAuthorTests(unittest.TestCase):
    """Exercise the same Python building helpers students use in their levels."""

    def setUp(self):
        """Prepare a tiny Python-authored level with one neighbor and a return door."""
        self.level = level(
            "A new place",
            tiles=["#####", "#@Q.#", "#...D", "#####"],
            legend={
                "@": spawn("entry"),
                "Q": person("echo", battle=False, text="Hello!"),
                "D": door("fresh", "entry"),
            },
        )

    def build(self):
        """Compile the Python registry, using the same entry point as content.py."""
        return build_story({"fresh": self.level}, "fresh", "entry", {"echo"})

    def test_python_registration_and_arbitrary_letters_use_named_markers(self):
        """Moving a spawn letter moves door arrivals without editing coordinate pairs."""
        rooms, start, entry = self.build()
        self.assertEqual((start, entry), ("fresh", "entry"))
        original = rooms["fresh"].spawns[entry]
        self.level["map"][1] = "#.Q@#"
        rooms, _, _ = self.build()
        self.assertNotEqual(rooms["fresh"].spawns[entry], original)
        self.assertEqual(rooms["fresh"].exits[0].landing, "entry")
        self.level["map"][1] = "#@g.#"
        self.level["legend"]["g"] = self.level["legend"].pop("Q")
        rooms, _, _ = self.build()
        self.assertEqual(rooms["fresh"].people[0].character, "echo")
        # New levels are ordinary values registered with a key in student_world.py.
        second = level(
            "A second place",
            ["#####", "#@..D", "#####"],
            {"@": spawn("arrive"), "D": door("fresh", "entry")},
        )
        self.level["legend"]["D"] = door("second", "arrive")
        rooms, _, _ = build_story(
            {"fresh": self.level, "second": second}, "fresh", "entry", {"echo"}
        )
        self.assertEqual(rooms["fresh"].exits[0].destination, "second")
        self.assertEqual(rooms["second"].exits[0].destination, "fresh")

    def test_bad_symbols_fields_shapes_ids_links_and_hooks_have_diagnostics(self):
        """Invalid Python definitions report the level and the failed content rule."""
        import copy

        mutations = [
            (lambda d: d["map"].__setitem__(1, "#@!.#"), "fresh: row 2, column 3"),
            (lambda d: d["map"].__setitem__(1, "#@Q#"), "equal-length"),
            (lambda d: d["legend"]["Q"].__setitem__("character", "missing"), "unknown character"),
            (lambda d: d["legend"]["Q"].__setitem__("battel", False), "unknown field"),
            (lambda d: d["legend"]["D"].__setitem__("to", "missing"), "unknown door level"),
            (lambda d: d["legend"]["D"].__setitem__("entry", "missing"), "no spawn"),
            (lambda d: d["map"].__setitem__(1, "#@@.#"), "duplicate spawn"),
            (lambda d: d["legend"]["Q"].__setitem__("on_interact", "missing"), "Python function"),
            (lambda d: d["legend"]["Q"].__setitem__("text", []), "text needs"),
            (lambda d: d["legend"]["@"].__setitem__("tile", "#"), "walkable ground"),
        ]
        original = copy.deepcopy(self.level)
        for change, message in mutations:
            with self.subTest(message=message):
                self.level = copy.deepcopy(original)
                change(self.level)
                with self.assertRaisesRegex(StoryError, message):
                    self.build()
        self.level = original
        self.level["legend"]["Q"]["id"] = "unique"
        self.level["map"][1] = "#@QQ#"
        with self.assertRaisesRegex(StoryError, "duplicate character"):
            self.build()

    def test_starting_configuration_and_level_types_are_checked(self):
        """Catch bad registry values and starting markers before gameplay begins."""
        for levels, start, entry, message in (
            ({}, "fresh", "entry", "LEVELS"),
            ({"fresh": None}, "fresh", "entry", "level must be a dictionary"),
            ({"fresh": self.level}, "missing", "entry", "unknown START_LEVEL"),
            ({"fresh": self.level}, "fresh", "missing", "unknown START_ENTRY"),
        ):
            with self.subTest(message=message), self.assertRaisesRegex(StoryError, message):
                build_story(levels, start, entry, {"echo"})

    def test_python_story_helpers_drive_dialogue_items_terrain_and_direct_callbacks(self):
        """Compile Python choices/branches and call a function only during interaction."""
        from undercode.world import World

        calls = []

        def greet(world, obj):
            """Example student callback that remembers a fact and records its invocation."""
            calls.append(obj.key)
            world.session.flags.add("greeted")

        definition = level(
            "Python story",
            ["TTTTTTTTT", "T@.CISRTT", "T....s..T", "TTTTTTTTT"],
            {
                "T": terrain("#"),
                "@": spawn("start"),
                "C": person(
                    "echo",
                    battle=False,
                    text="Welcome",
                    on_interact=greet,
                    choices=[choice("Yes", "Thanks", set_flags=["agreed"])],
                    branches=[branch("done", "Welcome back")],
                ),
                "I": item("A key", "key", "Found it"),
                "S": sign("Note", ["First paragraph", "Second paragraph"], set_flags=["done"]),
                "R": rest(),
                "s": trigger(greet, name="Greeting"),
            },
        )
        rooms, _, _ = build_story({"python": definition}, "python", "start", {"echo"})
        self.assertFalse(calls)  # Defining/building a level must not call its mechanics.
        world = World(rooms, Session(), "python", "start")
        world.interact(world.room.people[0])
        self.assertEqual(len(calls), 1)
        self.assertIn("greeted", world.session.flags)
        finish_dialogue(world)
        self.assertIn("agreed", world.session.flags)
        item_obj = next(o for o in world.room.objects if o.kind == "item")
        world.interact(item_obj)
        finish_dialogue(world)
        self.assertIn("key", world.session.flags)
        note = next(o for o in world.room.objects if o.kind == "sign")
        world.interact(note)
        finish_dialogue(world)
        self.assertIn("done", world.session.flags)
        world.interact(world.room.people[0])
        self.assertEqual(world.dialogue.pages, ["Welcome back"])
        self.assertEqual(rooms["python"].tiles[0], "#########")


class SpriteTaskTests(unittest.TestCase):
    def test_reference_handles_all_directions_diagonals_and_idle(self):
        for facing, expected in VIEW_CASES:
            with self.subTest(facing=facing):
                self.assertEqual(player_view(facing), expected)
        game = Game()
        for direction in ((-1, 0), (1, 0), (0, -1), (0, 1)):
            game.update(0.01, Controls(*direction))
            facing = game.world.facing.copy()
            game.update(0.1)
            self.assertEqual(game.world.facing, facing)

    def test_normal_game_restart_and_command_line(self):
        game = Game(level="studio", entry="entrance")
        game.restart()
        self.assertEqual(game.world.position, tile_center(ROOMS["studio"].spawns["entrance"]))
        result = subprocess.run(
            [
                sys.executable,
                str(ROOT / "main.py"),
                "--headless",
                "--mute",
                "--level",
                "studio",
                "--frames",
                "1",
            ],
            capture_output=True,
            text=True,
            timeout=30,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        # Do not assert the unfinished student's answers: students should be able to solve it.
        with (
            patch("undercode.student_sprites.choose_player_view", player_view),
            contextlib.redirect_stdout(io.StringIO()),
        ):
            import main

            self.assertEqual(main.main(["--check-sprites"]), 0)


if __name__ == "__main__":
    unittest.main()
